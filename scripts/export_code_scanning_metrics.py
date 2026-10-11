#!/usr/bin/env python3
"""Export a privacy-conscious snapshot of GitHub Code Scanning metrics."""

from __future__ import annotations

import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any


API_VERSION = "2022-11-28"
PAGE_SIZE = 100
OUTPUT_DIR = Path("code-scanning-metrics")
ALERT_STATES = ("open", "dismissed", "fixed")


def api_get_all(url: str, token: str) -> list[dict[str, Any]]:
    """Fetch every page from a GitHub REST endpoint using the Actions token."""
    collected: list[dict[str, Any]] = []
    page = 1
    while True:
        separator = "&" if "?" in url else "?"
        page_url = f"{url}{separator}{urllib.parse.urlencode({'per_page': PAGE_SIZE, 'page': page})}"
        request = urllib.request.Request(
            page_url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": API_VERSION,
                "User-Agent": "code-scanning-metrics-exporter",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"GitHub API returned HTTP {exc.code} for {urllib.parse.urlsplit(url).path}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach GitHub API: {exc.reason}") from exc

        if not isinstance(payload, list):
            raise RuntimeError(f"Expected a list from GitHub API: {urllib.parse.urlsplit(url).path}")
        collected.extend(payload)
        if len(payload) < PAGE_SIZE:
            return collected
        page += 1
        if page > 1000:
            raise RuntimeError("Stopped after 1000 pages to avoid an unbounded API request.")


def endpoint_url(api_url: str, repository: str, suffix: str, filters: dict[str, str]) -> str:
    query = urllib.parse.urlencode(filters)
    return f"{api_url.rstrip('/')}/repos/{repository}/{suffix}?{query}"


def read_event_context() -> tuple[dict[str, str], int | None]:
    event_name = os.environ.get("GITHUB_EVENT_NAME", "unknown")
    filters: dict[str, str] = {}
    pr_number: int | None = None
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event: dict[str, Any] = {}
    if event_path and Path(event_path).is_file():
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))

    pull_request = event.get("pull_request") or event.get("workflow_run", {}).get("pull_requests", [{}])[0]
    if event_name in {"pull_request", "pull_request_target"} and pull_request:
        pr_number = int(pull_request["number"])
        filters["pr"] = str(pr_number)
    else:
        ref = os.environ.get("GITHUB_REF", "")
        if ref:
            filters["ref"] = ref
    return filters, pr_number


def get_security_severity(alert: dict[str, Any]) -> str:
    level = (alert.get("rule") or {}).get("security_severity_level")
    return str(level or "unknown").lower()


def is_codeql_analysis(analysis: dict[str, Any]) -> bool:
    return str((analysis.get("tool") or {}).get("name", "")).lower() == "codeql"


def wait_for_current_analysis(
    analyses_url: str,
    token: str,
    expected_shas: set[str],
    event_name: str,
) -> list[dict[str, Any]]:
    """Give GitHub-managed CodeQL time to publish the analysis for a push/PR."""
    timeout_seconds = int(os.environ.get("CODEQL_WAIT_TIMEOUT_SECONDS", "600"))
    interval_seconds = int(os.environ.get("CODEQL_WAIT_INTERVAL_SECONDS", "30"))
    deadline = time.monotonic() + timeout_seconds
    analyses: list[dict[str, Any]] = []

    # A schedule creates a daily metrics snapshot, not a daily CodeQL scan.
    if event_name == "schedule" or not expected_shas or timeout_seconds <= 0:
        return api_get_all(analyses_url, token)

    while True:
        analyses = api_get_all(analyses_url, token)
        if any(is_codeql_analysis(item) and item.get("commit_sha") in expected_shas for item in analyses):
            return analyses
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return analyses
        print(f"Waiting for GitHub-managed CodeQL analysis; {int(remaining)} seconds remain.")
        time.sleep(min(interval_seconds, remaining))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    if not token or not repository:
        raise RuntimeError("GH_TOKEN/GITHUB_TOKEN and GITHUB_REPOSITORY must be provided by GitHub Actions.")

    filters, pr_number = read_event_context()
    if not filters:
        raise RuntimeError("Could not determine the branch or pull request to query.")

    alerts_url = endpoint_url(api_url, repository, "code-scanning/alerts", filters)
    alert_counts: Counter[tuple[str, str]] = Counter()
    dismissal_reasons: Counter[str] = Counter()
    for state in ALERT_STATES:
        state_alerts = api_get_all(f"{alerts_url}&state={urllib.parse.quote(state)}", token)
        alert_counts[(state, "all")] = len(state_alerts)
        for alert in state_alerts:
            severity = get_security_severity(alert)
            alert_counts[(state, severity)] += 1
            if state == "dismissed":
                dismissal_reasons[str(alert.get("dismissed_reason") or "unspecified")] += 1

    analyses_url = endpoint_url(api_url, repository, "code-scanning/analyses", filters)
    event_name = os.environ.get("GITHUB_EVENT_NAME", "unknown")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event: dict[str, Any] = {}
    if event_path and Path(event_path).is_file():
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    expected_shas = {os.environ.get("GITHUB_SHA", "")}
    if pr_number:
        pull_request = event.get("pull_request") or {}
        for candidate_sha in (
            (pull_request.get("head") or {}).get("sha", ""),
            pull_request.get("merge_commit_sha", ""),
        ):
            if candidate_sha:
                expected_shas.add(candidate_sha)
    expected_shas.discard("")
    analyses = wait_for_current_analysis(analyses_url, token, expected_shas, event_name)
    latest_by_category: dict[str, dict[str, Any]] = {}
    for analysis in analyses:
        category = str(analysis.get("category") or "uncategorized")
        previous = latest_by_category.get(category)
        if previous is None or str(analysis.get("created_at", "")) > str(previous.get("created_at", "")):
            latest_by_category[category] = analysis

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    repository_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    run_id = os.environ.get("GITHUB_RUN_ID", "unknown")
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    run_url = f"{repository_url}/{repository}/actions/runs/{run_id}/attempts/{run_attempt}"
    ref = os.environ.get("GITHUB_REF", "")

    state_summary = {
        state: alert_counts[(state, "all")] for state in ALERT_STATES
    }
    severity_summary = {
        state: {
            severity: count
            for (record_state, severity), count in sorted(alert_counts.items())
            if record_state == state and severity != "all"
        }
        for state in ALERT_STATES
    }
    analysis_rows = []
    for category, analysis in sorted(latest_by_category.items()):
        tool = analysis.get("tool") or {}
        analysis_rows.append(
            {
                "category": category,
                "tool": tool.get("name", "unknown"),
                "tool_version": tool.get("version", "unknown"),
                "created_at": analysis.get("created_at", ""),
                "ref": analysis.get("ref", ""),
                "commit_sha": analysis.get("commit_sha", ""),
                "results_count": analysis.get("results_count", 0),
                "rules_count": analysis.get("rules_count", 0),
                "matched_current_execution": analysis.get("commit_sha") in expected_shas,
                "warning": analysis.get("warning", ""),
                "error": analysis.get("error", ""),
            }
        )

    matched_current_analysis = any(
        is_codeql_analysis(analysis) and analysis.get("commit_sha") in expected_shas
        for analysis in analyses
    )

    snapshot = {
        "schema_version": 1,
        "collected_at_utc": now,
        "repository": repository,
        "event": os.environ.get("GITHUB_EVENT_NAME", "unknown"),
        "ref": ref,
        "pull_request": pr_number,
        "commit_sha": os.environ.get("GITHUB_SHA", ""),
        "workflow_run": run_url,
        "alerts": {
            "counts_by_state": state_summary,
            "counts_by_state_and_security_severity": severity_summary,
            "dismissed_counts_by_reason": dict(sorted(dismissal_reasons.items())),
        },
        "analysis": {
            "latest_category_count": len(analysis_rows),
            "matched_current_execution": matched_current_analysis,
            "expected_commit_shas": sorted(expected_shas),
            "categories": analysis_rows,
        },
        "privacy_note": "Aggregate metrics only; alert identities, locations, dismissing actors, and comments are omitted.",
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    summary_rows = []
    for state in ALERT_STATES:
        severities = sorted(severity for s, severity in alert_counts if s == state and severity != "all")
        for severity in severities:
            summary_rows.append({"state": state, "security_severity": severity, "count": alert_counts[(state, severity)]})
        summary_rows.append({"state": state, "security_severity": "ALL", "count": alert_counts[(state, "all")]})
    write_csv(OUTPUT_DIR / "alerts-summary.csv", ["state", "security_severity", "count"], summary_rows)
    write_csv(
        OUTPUT_DIR / "dismissal-reasons.csv",
        ["dismissal_reason", "count"],
        [{"dismissal_reason": reason, "count": count} for reason, count in sorted(dismissal_reasons.items())],
    )
    write_csv(
        OUTPUT_DIR / "analysis-configurations.csv",
        ["category", "tool", "tool_version", "created_at", "ref", "commit_sha", "results_count", "rules_count", "matched_current_execution", "warning", "error"],
        analysis_rows,
    )

    print(f"Wrote Code Scanning metrics to {OUTPUT_DIR.resolve()}")
    print(f"Latest analysis categories: {len(analysis_rows)}; matched current execution: {matched_current_analysis}")
    print(f"Dismissed alerts in this snapshot: {state_summary['dismissed']}")
    print(f"Snapshot run: {run_url}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(f"Metrics export failed: {error}", file=sys.stderr)
        sys.exit(1)
