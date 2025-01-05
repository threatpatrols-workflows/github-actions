#
# Copyright [2025] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

import os


class GithubSummary:

    filename: str
    content: str

    def __init__(self, filename=None, content: str = ""):
        if filename:
            self.filename = filename
        else:
            self.filename = os.getenv("GITHUB_STEP_SUMMARY")

        if content:
            self.content = content

    def add_content(self, content):
        self.content += content + "\n"

    def write(self):
        if self.filename:
            with open(self.filename, "w") as f:
                f.write(self.content.strip())


def get_input_value(name: str, default=None, github_summary:GithubSummary=None):
    env_name = "INPUT_" + name.upper()
    value = os.getenv(env_name, default)
    if github_summary:
        github_summary.add_content(" - {name}: {value}\n")
    return value


def write_github_output(**kwargs):
    if os.getenv("GITHUB_OUTPUT"):
        output_content = ""
        for key, value in kwargs.items():
            output_content += f"{key}={value}\n"
        with open(os.getenv("GITHUB_OUTPUT"), "a") as f:
            f.write(output_content.strip())
