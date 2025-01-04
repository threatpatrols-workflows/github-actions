
import os
import json

import requests
import base64

CLICKHOUSE_URL = os.getenv("INPUT_CLICKHOUSE_URL", "https://sql-clickhouse.clickhouse.com/")
CLICKHOUSE_USERNAME = os.getenv("INPUT_CLICKHOUSE_USERNAME", "demo")
CLICKHOUSE_PASSWORD = os.getenv("INPUT_CLICKHOUSE_PASSWORD", "")

QUERY_LIMIT = 9999999999
QUERY_INTERVAL_SECONDS = (3600 * 48)  # 2 days

#
# https://sql.clickhouse.com
# ===
query = f"""
    select 
        project_name as project,
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
    and release_count = 1
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
    print(response.text)
    exit(response.status_code)

print(json.dumps(response.json().get("data", []), indent="  "))
