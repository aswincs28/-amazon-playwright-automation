
import json
import os
import ssl
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from base64 import b64encode

# OpenSearch configuration
OPENSEARCH_URL = "https://localhost:9200"
INDEX_NAME = "amazon-test-results"

USERNAME = os.environ.get("OPENSEARCH_USER", "admin")
PASSWORD = os.environ.get("OPENSEARCH_PASSWORD")

if not PASSWORD:
    raise RuntimeError("Set the OPENSEARCH_PASSWORD environment variable.")

# Read Jenkins/Pytest JUnit report
REPORT_PATH = os.environ.get("JUNIT_REPORT", "reports/junit.xml")

if not os.path.exists(REPORT_PATH):
    raise FileNotFoundError(f"JUnit report not found: {REPORT_PATH}")

root = ET.parse(REPORT_PATH).getroot()

# Handle either <testsuites> or <testsuite> as the root element
testcases = root.findall(".//testcase")
build_number = int(os.environ.get("BUILD_NUMBER", "0"))

context = ssl._create_unverified_context()  # Local self-signed certificate
credentials = b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()

published = 0

for case in testcases:
    failure = case.find("failure")
    error = case.find("error")
    skipped = case.find("skipped")

    if failure is not None or error is not None:
        status = "failed"
        details = (failure if failure is not None else error).get("message", "")
    elif skipped is not None:
        status = "skipped"
        details = skipped.get("message", "")
    else:
        status = "passed"
        details = ""

    duration = float(case.get("time", "0") or 0)

    document = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "test_name": f"{case.get('classname', '')}.{case.get('name', 'unknown')}",
        "status": status,
        "duration": duration,
        "build_number": build_number,
        "details": details,
    }

    request = urllib.request.Request(
        f"{OPENSEARCH_URL}/{INDEX_NAME}/_doc",
        data=json.dumps(document).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {credentials}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request, context=context, timeout=15
        ) as response:
            if response.status in (200, 201):
                published += 1
                print(f"Published: {document['test_name']} [{status}]")
    except urllib.error.HTTPError as exc:
        print(f"OpenSearch error {exc.code}: {exc.read().decode()}")
        raise

print(f"\nSuccessfully published {published} test results to OpenSearch.")
