#
# Copyright [2025] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

import hashlib

CHUNK_BYTES = 65536


def sha256file(file: str):
    sha256 = hashlib.sha256()
    with open(file, "rb") as f:
        while True:
            data = f.read(CHUNK_BYTES)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()
