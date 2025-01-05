
import os
import sys
import json

import requests
import base64

CLICKHOUSE_URL = os.getenv("INPUT_CLICKHOUSE_URL", "https://sql-clickhouse.clickhouse.com/")
CLICKHOUSE_USERNAME = os.getenv("INPUT_CLICKHOUSE_USERNAME", "demo")
CLICKHOUSE_PASSWORD = os.getenv("INPUT_CLICKHOUSE_PASSWORD", "")

QUERY_LIMIT = os.getenv("INPUT_QUERY_LIMIT", "9999999999")
QUERY_INTERVAL_SECONDS = os.getenv("INPUT_QUERY_INTERVAL_SECONDS", str(3600 * 48))    # 2 days
OUTPUT_FILE = os.getenv("INPUT_OUTPUT_FILE", "pypi-recent-packages.json")


# Click House
# ===
query = f"""
    select 
        project_name as project,
        release_count as total_packages_count,
        CONCAT('https://pypi.org/project/', project_name, '/#history') as project_url,
        CONCAT('https://files.pythonhosted.org/packages/', pathname) as package_url,
        first_upload_timestamp as package_timestamp
    from (
        select 
            name as project_name,
            min(path) as pathname,
            min(upload_time) as first_upload_timestamp,
            count(*) as release_count
        from pypi.projects 
        group by name
        order by first_upload_timestamp desc
    )
    where 1=1
    and package_timestamp >= NOW() - INTERVAL {QUERY_INTERVAL_SECONDS} SECOND
    limit {QUERY_LIMIT}
"""

authorization = "Basic " + base64.b64encode(f"{CLICKHOUSE_USERNAME}:{CLICKHOUSE_PASSWORD}".encode()).decode()

response = requests.post(
    url=CLICKHOUSE_URL,
    headers={"Authorization": authorization},
    data=query +"\nFORMAT JSON"
)

if response.status_code != 200:
    print(response.text, file=sys.stderr)
    exit(response.status_code)

data = response.json().get("data", [])

with open(OUTPUT_FILE, "w") as f:
    f.write(json.dumps(data, indent="  "))

if os.getenv("GITHUB_OUTPUT"):
    with open(os.getenv("GITHUB_OUTPUT"), "a") as f:
        f.write(f"results_file={OUTPUT_FILE}")

if os.getenv("GITHUB_STEP_SUMMARY"):
    with open(os.getenv("GITHUB_STEP_SUMMARY"), "w") as f:
        f.write(f"""
        TOTAL_RECORDS: {len(data)}
        QUERY_INTERVAL_SECONDS: {QUERY_INTERVAL_SECONDS}
        CLICKHOUSE_URL: {CLICKHOUSE_URL}
        CLICKHOUSE_USERNAME: {CLICKHOUSE_USERNAME}
        OUTPUT_FILE: {OUTPUT_FILE}
""")

print(f"OKAY: total records {len(data)}, saved to {OUTPUT_FILE!r}", file=sys.stderr)
