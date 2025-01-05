#
# Copyright [2025] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

import os

def get_input_value(name: str, default=None, in_summary=None):
    env_name = "INPUT_" + name.upper()
    value = os.getenv(env_name, default)
    if in_summary:
        in_summary += " - {name}: {value}\n"
    return value


def write_github_output(**kwargs):
    if os.getenv("GITHUB_OUTPUT"):
        output_content = ""
        for key, value in kwargs.items():
            output_content += f"{key}={value}\n"
        with open(os.getenv("GITHUB_OUTPUT"), "a") as f:
            f.write(output_content.strip())


def write_github_summary(content: str):
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.getenv("GITHUB_STEP_SUMMARY"), "w") as f:
            f.write(content.strip())
