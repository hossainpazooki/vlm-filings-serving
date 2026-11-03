"""Canonical bytes and hashing. The one place that decides what bytes a hash is over.

Every JSON the repo writes goes through write_json: sorted keys, two-space
indent, LF newlines, trailing newline, UTF-8. Every hash of a file the repo
consumes as text goes through lf_sha256, which normalises CRLF to LF first,
because git re-encodes line endings per platform and a pin stricter than its
own parser only ever produces false alarms (identity-triple).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

def canonical_bytes(obj: dict) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_of(obj: dict) -> str:
    return "sha256:" + sha256_hex(canonical_bytes(obj))

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(canonical_bytes(obj))

def read_json(path: Path) -> dict:
    with open(path, "rb") as f:
        return json.loads(f.read().decode("utf-8"))

def lf_sha256(path: Path) -> str:
    return sha256_hex(path.read_bytes().replace(b"\r\n", b"\n"))
