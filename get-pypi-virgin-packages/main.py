#
# Copyright [2025] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

import json

from threatpatrols.clickhouse import clickhouse_query
from threatpatrols.github_action import get_input_value, write_github_output, GithubSummary

github_summary = GithubSummary()

OUTPUT_FILE = get_input_value("OUTPUT_FILE", "pypi-virgin-packages.json", github_summary)
QUERY_LIMIT = get_input_value("QUERY_LIMIT", "9999999999")
QUERY_INTERVAL_SECONDS = get_input_value("QUERY_INTERVAL_SECONDS", f"{3600 * 48}", github_summary)
CLICKHOUSE_URL = get_input_value("CLICKHOUSE_URL", "https://sql-clickhouse.clickhouse.com/", github_summary)
CLICKHOUSE_USERNAME = get_input_value("CLICKHOUSE_USERNAME", "demo", github_summary)
CLICKHOUSE_PASSWORD = get_input_value("CLICKHOUSE_PASSWORD", "")

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

github_summary.add_content(f" - TOTAL_RECORDS: {len(data)}")

write_github_output(results_file=OUTPUT_FILE)
github_summary.write()

