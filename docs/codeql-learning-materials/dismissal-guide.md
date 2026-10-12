# Triage and dismiss code scanning alerts responsibly

This guide explains how to review a CodeQL alert and when a dismissal may be appropriate. The screenshots are examples from the separate Skills Introduction to CodeQL exercise; they are included to show where GitHub displays the check, alert list, and alert details.

> **Scope:** These screenshots show the training repository and its intentionally vulnerable course example. Do not apply the exercise or its alert disposition to the scanner project. The course vulnerability and PR remain in the course repository.

## What the screenshots show

1. The pull request’s CodeQL check reports one new high-severity finding. A failing code-scanning check means the analysis found an alert; it does not by itself mean the build or application failed.
   
   ![Course pull request check showing one high-severity CodeQL alert](.github/images/dismissal-pr-checks.png)

2. The repository’s **Security and quality → Code scanning** page lists the open alert.
   
   ![Course repository Code scanning page with one open alert](.github/images/dismissal-alert-list.png)

3. Opening the alert displays the affected code location, severity, rule details, and the **Dismiss alert** action.
   
   ![Course CodeQL alert details and Dismiss alert action](.github/images/dismissal-alert-detail.png)

## Preferred response: fix the code

Start by examining the alert description, affected lines, severity, rule, and data flow. If the finding is valid and the code can be corrected, fix it and submit the correction through the normal review process. A dismissal closes the finding; it does not remove or repair the vulnerable code.

## When dismissal can be appropriate

Dismiss only after review establishes that no code change is needed—for example, a confirmed false positive, code used only in tests, or an explicitly accepted risk. Choose the reason that accurately describes the decision. GitHub's available reasons can vary by alert and interface.

Before dismissing, record enough context for later review:

- Why the alert does not require a code change.
- Who reviewed and accepted the decision.
- Whether the decision is temporary or permanent.
- Any compensating controls or follow-up work, including an owner and due date when applicable.

## Dismissal workflow

1. Open **Security and quality → Code scanning** and select the alert. For a pull request alert, you can also open it from the code-scanning annotation.
2. Review the location, explanation, severity, rule, and data flow. Confirm the alert is not a valid issue that should be fixed.
3. Select **Dismiss alert** and choose the reason that matches the evidence.
4. Add a concise comment recording the rationale, reviewer, duration, and follow-up or compensating controls.
5. Submit the dismissal, then verify the alert appears in the **Closed** list with the intended reason and comment.

Example comment:

> Reviewed by [reviewer] on [date]. Dismissed as [reason] because [evidence]. This decision is [temporary/permanent]. [Control or follow-up], owned by [person/team], is due [date].

## What dismissal changes

According to GitHub's documentation, dismissing a code-scanning alert:

- Applies the dismissal across branches.
- Removes the alert from the current open-alert count and moves it to **Closed**; it can be reopened later.
- Records the dismissal reason and optional comment in the alert history.
- Prevents the same code from generating that same alert on the next code-scanning run.

Dismissal changes the alert's status; it is not a code fix. Treat it as a documented security exception. If delegated alert dismissal is enabled by the organization or enterprise, submit a request and wait for an authorized reviewer rather than assuming an individual dismissal is final.

For current behavior and interface details, see GitHub's [Resolving code scanning alerts](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/resolve-alerts) and [Triaging code scanning alerts in pull requests](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/triage-alerts-in-pull-requests) guides.
