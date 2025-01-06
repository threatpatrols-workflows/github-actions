#
# Copyright [2025] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

import os
from pathlib import Path


def file_write(filepath, content, mode="w", mkdir=True):

    pathname = Path(filepath).parent
    if mkdir and not pathname.exists():
        os.makedirs(pathname, exist_ok=True)

    with open(filepath, mode) as f:
        f.write(content)
