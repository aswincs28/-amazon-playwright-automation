# Amazon Playwright Automation

Automated UI testing for Amazon using **Python, Playwright, and pytest**, with test execution in **Jenkins**, result storage in **OpenSearch**, and visualization in **Grafana**.

## Project Overview

This project automates selected Amazon homepage and search-box checks using Playwright. Pytest runs the tests, generates HTML and JUnit XML reports, and Jenkins orchestrates the workflow. A publishing script sends individual test results to OpenSearch, where Grafana visualizes the results.

## Technology Stack

- **Python** — test automation language
- **Playwright** — browser automation
- **pytest** — test runner
- **pytest-playwright** — Playwright integration for pytest
- **pytest-html** — HTML report generation
- **Jenkins** — CI pipeline execution and artifact archiving
- **OpenSearch** — storage and search of test-result documents
- **Grafana** — dashboard and visualization
- **Chromium** — browser used by the tests

## Workflow

1. Jenkins starts the pipeline.
2. The pipeline checks the Python environment and Playwright browser.
3. pytest runs the automated browser tests.
4. The run generates `reports/report.html` and `reports/junit.xml`.
5. `publish_results.py` reads the JUnit XML and publishes individual test results to OpenSearch.
6. Jenkins records test results and archives the reports.
7. Grafana queries OpenSearch and displays test execution activity and result status.

## Project Structure

The exact structure may vary depending on your local files. Main files used by the workflow include:

```text
amazon-automation/
├── tests/
│   ├── test_home.py
│   └── test_search.py
├── reports/
│   ├── report.html
│   └── junit.xml
├── publish_results.py
├── requirements.txt
├── Jenkinsfile          
└── README.md
```

> `reports/` contains generated output. Jenkins may create these files during a build. A local `Jenkinsfile` is optional if the Jenkins job uses an inline Pipeline script.

## Prerequisites

Install or configure these separately from the Python dependencies:

- Python compatible with the versions in `requirements.txt`
- Java runtime required by Jenkins
- Jenkins
- OpenSearch
- Grafana
- Chromium browser installed through Playwright

`pip install -r requirements.txt` installs Python packages only; it does not install Jenkins, OpenSearch, Grafana, Java, or the browser itself.

## Setup

### 1. Open the project directory

```powershell
cd C:\Users\aswin\Desktop\project\amazon-automation
```

### 2. Create and activate a virtual environment (if needed)

```powershell
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, call the virtual environment's Python directly:

```powershell
.\venv\Scripts\python.exe --version
```

### 3. Install Python dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Install Chromium for Playwright

```powershell
python -m playwright install chromium
```

## Run Tests Locally

Run all tests:

```powershell
python -m pytest
```

Generate HTML and JUnit XML reports:

```powershell
New-Item -ItemType Directory -Force reports
python -m pytest --html=reports/report.html --self-contained-html --junitxml=reports/junit.xml
```


## Jenkins Pipeline

The Jenkins job used for this project is named **Amazon-Playwright-Automation**.

The pipeline workflow includes:

- Checking the Python environment
- Checking the Playwright browser installation
- Running pytest
- Publishing test results to OpenSearch
- Recording JUnit results
- Archiving `reports/report.html` and `reports/junit.xml`

The Jenkins UI in the current setup is available at `http://localhost:8081/`.

> The job currently uses an inline Pipeline script. A local `Jenkinsfile` is optional unless you choose to store the pipeline script in source control.

## OpenSearch Results

`publish_results.py` reads the generated JUnit XML and publishes test results to the OpenSearch index:

```text
amazon-test-results
```

The latest recorded pipeline output reported that **10 test-result records** were successfully published.

### Credentials and configuration

- Configure the OpenSearch endpoint and credentials in your local setup and Jenkins credentials.
- The current setup uses a Jenkins secret-text credential with ID `opensearch-password`.
- Do not commit passwords, API keys, or other secrets to source control.
- Ensure the client configuration matches your OpenSearch HTTPS and certificate setup.

Do not put real credentials in this README. Use environment variables or Jenkins credentials when making the project portable.

## Grafana Dashboard

The dashboard is named **Amazon Playwright Automation Dashboard** and contains:

- **Test Execution Over Time** — a time-series view of test execution activity
- **Test Results by Status** — a pie chart grouped by status

The dashboard uses the `grafana-opensearch-datasource` data source and queries the `amazon-test-results*` index pattern. Grafana is available locally at `http://localhost:3000/`.

## Latest Recorded Test Run

Jenkins build **#14** completed successfully on **October 27, 2026**.

| Result | Count |
|---|---:|
| Passed | 9 |
| Skipped | 1 |
| Failed | 0 |
| Total collected | 10 |

The skipped test was `tests/test_search.py::test_amazon_product_search[chromium]`. It did not complete normally during the run, so the results should not be described as 10 passed tests.

## Reports and Artifacts

The pipeline creates or archives:

- `reports/report.html` — HTML report for reviewing test outcomes
- `reports/junit.xml` — JUnit XML consumed by Jenkins and `publish_results.py`

Open these artifacts from the corresponding Jenkins build page.

## Troubleshooting

- **Browser executable missing:** Run `python -m playwright install chromium`.
- **Dependencies missing:** Activate the intended virtual environment and run `python -m pip install -r requirements.txt`.
- **HTML report appears incomplete:** Confirm pytest has finished and open the report generated by the completed run.
- **A test is skipped:** Review the pytest console output and skip reason; external websites may behave differently between runs.
- **No data in Grafana:** Confirm the Jenkins publishing step succeeded, OpenSearch has recent documents, and the dashboard time range includes those documents.
- **OpenSearch Dashboards is unavailable:** It is optional for the current workflow because Grafana is used to visualize OpenSearch results.

## Security Notes

- Keep credentials in Jenkins Credentials or environment variables.
- Never commit passwords, API keys, or tokens.
- Review TLS certificate verification settings before using this setup outside local development.

## License

No license has been specified for this project yet.
