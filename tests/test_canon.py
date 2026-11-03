import hashlib
from pathlib import Path

from traverse import canon

def test_canonical_bytes_sorts_keys_and_ends_with_lf():
    b = canon.canonical_bytes({"b": 1, "a": [1, 2]})
    assert b == b'{\n  "a": [\n    1,\n    2\n  ],\n  "b": 1\n}\n'

def test_sha256_of_is_prefixed_and_matches_hashlib():
    obj = {"x": "y"}
    expect = hashlib.sha256(canon.canonical_bytes(obj)).hexdigest()
    assert canon.sha256_of(obj) == "sha256:" + expect

def test_write_json_uses_lf_only(tmp_path: Path):
    p = tmp_path / "o.json"
    canon.write_json(p, {"k": "v"})
    assert b"\r" not in p.read_bytes()
    assert p.read_bytes().endswith(b"\n")

def test_lf_sha256_normalises_crlf(tmp_path: Path):
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_bytes(b"one\ntwo\n")
    b.write_bytes(b"one\r\ntwo\r\n")
    assert canon.lf_sha256(a) == canon.lf_sha256(b)
