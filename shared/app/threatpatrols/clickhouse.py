#
# Copyright [2025] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

from threatpatrols.exceptions import ThreatPatrolsException

import requests
import base64


def clickhouse_query(query: str, username: str, password: str, server_url: str):

    authorization = "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()

    response = requests.post(
        url=server_url,
        headers={"Authorization": authorization},
        data=query + "\nFORMAT JSON"
    )

    if response.status_code != 200:
        ThreatPatrolsException(response.text)

    try:
        return response.json().get("data", [])
    except Exception as e:
        ThreatPatrolsException(e)
