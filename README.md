# Sound & String — Instrument Store

A Java 21 and Maven sample application for learning the development, testing, and security-analysis lifecycle. It includes a web page for browsing and managing products, a REST API, an in-memory H2 database, and integration tests.

Local folder: `C:\Applications\git\loja-instrumentos`.

## Open in Eclipse

1. In Eclipse, choose **File > Import > Maven > Existing Maven Projects**.
2. Select this folder (the one containing `pom.xml`) and finish the import.
3. Wait for Maven to download the dependencies. Configure a JDK 21 in **Window > Preferences > Java > Installed JREs** if Eclipse does not already have one.
4. Run `InstrumentStoreApplication` as a **Java Application**.
5. Open `http://localhost:8080`.

The repository also includes `.project` and `.classpath` metadata for Eclipse IDEs with m2e; importing it as a Maven project is recommended.

## Run with Maven

JDK 21 is required. The Maven Wrapper downloads and uses Maven 3.10.0, so Maven does not need to be installed on `PATH`. From a terminal in this folder:

```powershell
.\mvnw.cmd clean verify
.\mvnw.cmd spring-boot:run
```

The first command compiles the code and runs the tests. The second starts the application; open `http://localhost:8080`. Sample data returns to its initial state when the application restarts because H2 runs in memory.

## GitHub Actions and repository security

### Current workflow

The `.github/workflows/build.yml` workflow runs Maven `verify` on pushes to `main` and on pull requests targeting `main`. CodeQL uses **Default setup**, managed in GitHub repository settings. While that mode is active, `.github/workflows/codeql.yml` does not control the analysis; GitHub disabled that file when Default setup was enabled.

GitHub Actions responds to events and coordinates workflow runs; Maven compiles the code and runs tests. CodeQL analyzes the code and publishes findings in **Security > Code scanning** and in pull request checks. Default setup controls CodeQL's analysis schedule, not the cron in a workflow YAML file.

The metrics exporter added in PR #12 uses a separate workflow, `.github/workflows/code-scanning-metrics.yml`, to query the GitHub API and publish a JSON/CSV snapshot as an artifact for each run. The workflow runs on pushes to `main`, daily at noon in São Paulo time, and on manual dispatch. To snapshot a specific PR, the maintainer can run the workflow manually on `main` and enter its PR number; the workflow reads the results through the API and does not execute the PR's code. Manual runs are allowed only on the default branch. The daily schedule creates a metrics snapshot; it does not trigger a new CodeQL analysis. `GITHUB_TOKEN` receives read-only access to Code Scanning, pull requests, and contents; no personal access token is used. Artifacts expire after up to 90 days. Snapshots count currently dismissed alerts and are not a permanent event-by-event dismissal log.

### Security feature status

CodeQL/Code Scanning uses **Default setup**, managed in GitHub's interface. Dependabot and Secret Protection remain off until they are tested separately. In public repositories, secret scanning for patterns that alert partner providers may happen automatically even when Secret Protection and owner alerts are off; consult GitHub's documentation before treating that setting as proof that no detection happens.

Copilot Autofix appears enabled in the settings, but it depends on CodeQL alerts to suggest fixes and does not replace an active analysis. It was not changed in this step.

The observed state and separate procedures for maintainers and PR authors are in the [maintainer guide in Word](docs/guia-github-actions-e-seguranca.docx) and [Markdown](docs/guia-github-actions-e-seguranca.md), and the [PR author guide in Word](docs/guia-usuario-prs.docx) and [Markdown](docs/guia-usuario-prs.md). Screenshots are in `docs/capturas/`. These guides remain in Portuguese.

### Agreed testing sequence

> **Reminder:** test and document one GitHub feature at a time to understand what each check does.

Study sequence:

1. Understand GitHub Actions events (`push`, `pull_request`, and `schedule`), jobs, steps, logs, and checks.
2. Observe managed CodeQL and the daily metrics reports in **Actions**, and findings in **Security > Code scanning**.
3. In future steps, test Dependabot and Secret Scanning separately and record each result.

This README and the guides describe the observed state and procedures. CircleCI is not part of the current workflow.

## API

- `GET /api/products` — list products
- `GET /api/products/{id}` — retrieve a product
- `POST /api/products` — create a product
- `PUT /api/products/{id}` — update a product
- `DELETE /api/products/{id}` — delete a product

Example JSON request body: `{"name":"Acoustic guitar","category":"Strings","price":799.90,"stock":8}`.
