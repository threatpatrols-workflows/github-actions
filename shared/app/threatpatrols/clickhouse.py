#
# Copyright [2025] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

from threatpatrols.exceptions import ThreatPatrolsException

import requests
import base64


class Clickhouse:

    server_url: str
    authorization_header: str

    def __init__(self, username: str, password: str, server_url: str):
        self.server_url = server_url
        self.authorization_header = "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()

    def query(self, sql: str):
        response = requests.post(
            url=self.server_url, headers={"Authorization": self.authorization_header}, data=sql + "\nFORMAT JSON"
        )

        if response.status_code != 200:
            ThreatPatrolsException(response.text)

        try:
            return response.json().get("data", [])
        except Exception as e:
            ThreatPatrolsException(e)
