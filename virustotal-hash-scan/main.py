#
# Copyright [2025] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

import json

from threatpatrols.github_action import GithubInput, GithubOutput, GithubSummary
from threatpatrols.virustotal import VirustotalHashAnalysis
from threatpatrols.hash import sha256file
from threatpatrols.file import file_write

github_output = GithubOutput()
github_summary = GithubSummary()

api_key = GithubInput("api_key").get()
hash_value = GithubInput("hash").get()
output_file = GithubInput("output_file", github_summary).get(default="virustotal-hash-scan.json")

# ===

virus_total = VirustotalHashAnalysis(api_key=api_key)
analysis = virus_total.submit_wait_for_analysis(hash_value)

file_write(filepath=output_file, content=json.dumps(analysis, indent="  "))
github_output.add_item("output_file", output_file)
github_output.write()

attributes = analysis.get("attributes", {})
github_summary.add_line(f"target: {hash_value}")
github_summary.add_line(f"target_type: hash")
github_summary.add_line(f"output_file_sha256: {sha256file(output_file)}")
github_summary.add_line(f"analysis_id: {analysis.get('id')}")
github_summary.add_line(f"vt_analysis_stats_malicious: {attributes.get('last_analysis_stats', {}).get('malicious')}")
github_summary.add_line(f"vt_analysis_stats_suspicious: {attributes.get('last_analysis_stats', {}).get('suspicious')}")
github_summary.add_line(f"vt_analysis_stats_undetected: {attributes.get('last_analysis_stats', {}).get('undetected')}")
github_summary.add_line(f"vt_analysis_stats_harmless: {attributes.get('last_analysis_stats', {}).get('harmless')}")
github_summary.add_line(f"vt_analysis_stats_timeout: {attributes.get('last_analysis_stats', {}).get('timeout')}")
github_summary.add_line(f"vt_reputation: {attributes.get('reputation')}")
github_summary.add_line(f"vt_times_submitted: {attributes.get('times_submitted')}")
# github_summary.add_line(f"vt_http_response_code: {data.get('attributes', {}).get('last_http_response_code')}")
# github_summary.add_line(f"vt_http_response_content_sha256: {data.get('attributes', {}).get('last_http_response_content_sha256')}")
# github_summary.add_line(f"vt_http_response_content_length: {data.get('attributes', {}).get('last_http_response_content_length')}")
github_summary.write(sort_lines=True)
