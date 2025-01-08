# /usr/bin/env python3

import os
import sys
import pathlib
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "shared", "app"))

temp_path = pathlib.Path(f"/tmp/virustotal-url-scan/{uuid.uuid4()}")
os.makedirs(temp_path, exist_ok=True)

os.environ["INPUT_OUTPUT_FILE"] = f"{temp_path}/output.json"
os.environ["INPUT_API_KEY"] = os.getenv("VIRUSTOTAL_API_KEY", "")
os.environ["INPUT_URL"] = "https://www.google.com/favicon.ico"
os.environ["GITHUB_STEP_SUMMARY"] = f"{temp_path}/summary.md"


import main

with open(os.environ["GITHUB_STEP_SUMMARY"], "r") as f:
    print(f.read())
