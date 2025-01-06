#
# Copyright [2025] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

import json

from threatpatrols.clickhouse import clickhouse_query
from threatpatrols.github_action import GithubInput, GithubOutput, GithubSummary
from threatpatrols.hash import sha256file

github_output = GithubOutput()
github_summary = GithubSummary()

output_file = GithubInput("output_file", github_summary).get(default="pypi-virgin-packages.json")
query_limit = GithubInput("query_limit").get(default="9999999999")
query_interval_seconds = GithubInput("query_interval_seconds", github_summary).get(default=f"{3600 * 48}")
clickhouse_url = GithubInput("clickhouse_url", github_summary).get(default="https://sql-clickhouse.clickhouse.com/")
clickhouse_username = GithubInput("clickhouse_username", github_summary).get(default="demo")
clickhouse_password = GithubInput("clickhouse_password").get(default="")

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
    and package_timestamp >= NOW() - INTERVAL {query_interval_seconds} SECOND
    limit {query_limit}
"""

data = clickhouse_query(
    query=query, username=clickhouse_username, password=clickhouse_password, server_url=clickhouse_url
)

with open(output_file, "w") as f:
    f.write(json.dumps(data, indent="  "))

github_output.add_item("output_file", output_file)
github_output.write()

github_summary.add_line(f"output_sha256: {sha256file(output_file)}")
github_summary.add_line(f"total_records: {len(data)}")
github_summary.write(sort_lines=True)
