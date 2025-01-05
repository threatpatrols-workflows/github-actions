#
# Copyright [2025] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

import json

from threatpatrols.clickhouse import clickhouse_query
from threatpatrols.github_action import GithubInput, GithubOutput, GithubSummary

github_output = GithubOutput()
github_summary = GithubSummary()

OUTPUT_FILE = GithubInput("OUTPUT_FILE", github_summary).get(default="pypi-virgin-packages.json")
QUERY_LIMIT = GithubInput("QUERY_LIMIT").get(default="9999999999")
QUERY_INTERVAL_SECONDS = GithubInput("QUERY_INTERVAL_SECONDS", github_summary).get(default=f"{3600 * 48}")
CLICKHOUSE_URL = GithubInput("CLICKHOUSE_URL", github_summary).get(default="https://sql-clickhouse.clickhouse.com/")
CLICKHOUSE_USERNAME = GithubInput("CLICKHOUSE_USERNAME", github_summary).get(default="demo")
CLICKHOUSE_PASSWORD = GithubInput("CLICKHOUSE_PASSWORD").get(default="")

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

data = clickhouse_query(query=query, username=CLICKHOUSE_USERNAME, password=CLICKHOUSE_PASSWORD, server_url=CLICKHOUSE_URL)

with open(OUTPUT_FILE, "w") as f:
    f.write(json.dumps(data, indent="  "))

github_output.add_item("results_file", OUTPUT_FILE)
github_output.write()

github_summary.add_line(f" - TOTAL_RECORDS: {len(data)}")
github_summary.write()
