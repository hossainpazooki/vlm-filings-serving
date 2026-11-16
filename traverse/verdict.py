"""Verdict rows: the only form in which this repo makes a claim.

Ported from PARALLAX gate/verdict.py and kept to the shared row
(docs/discipline.md, The verdict row) so a row here is a copy, not a
translation, anywhere else in the family. A twin row must carry its planted
mutation; a live row must not. The shared row refuses additional top-level
properties, so run_id lives under params. A check with a zero evaluated
denominator makes the whole report UNEVALUABLE (the three-outcomes rule).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from traverse import canon

SCHEMA = "datum/gate-verdict/1"

class Status(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNEVALUABLE = "UNEVALUABLE"

_RESULT = {Status.PASS: "GREEN", Status.FAIL: "RED", Status.UNEVALUABLE: "UNEVALUABLE"}

@dataclass(frozen=True)
class Check:
    name: str
    violations: int
    evaluated: int

@dataclass
class GateReport:
    status: Status
    checks: list[Check]
    params: dict
    scope: str
    reason: str | None = None

    @classmethod
    def from_checks(cls, checks: list[Check], params: dict, scope: str) -> "GateReport":
        if not checks:
            raise ValueError("a report must name at least one check")
        empty = [c.name for c in checks if c.evaluated == 0]
        if empty:
            # Only the checks with an empty domain are recorded 0/0: a check that was evaluated keeps
            # its counts, so a measured failure stays in the record beside the refusal.
            kept = [c if c.evaluated else Check(c.name, 0, 0) for c in checks]
            return cls(Status.UNEVALUABLE, kept, dict(params), scope,
                       f"zero items evaluated for {', '.join(empty)}")
        status = Status.PASS if all(c.violations == 0 for c in checks) else Status.FAIL
        return cls(status, list(checks), dict(params), scope)

    @classmethod
    def unevaluable(cls, reason: str, params: dict, scope: str, checks: list[Check]) -> "GateReport":
        if not checks:
            raise ValueError("an unevaluable report still names the checks it could not evaluate")
        return cls(Status.UNEVALUABLE, [Check(c.name, 0, 0) for c in checks], dict(params), scope, reason)

def git_state(repo: Path) -> tuple[str, str]:
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
                         text=True, check=True).stdout.strip()
    porcelain = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True,
                               text=True, check=True).stdout.strip()
    return sha, ("dirty" if porcelain else "clean")

def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

def verdict_row(
    report: GateReport,
    *,
    stage: str,
    lane: int,
    cell: str,
    run_id: str,
    content_hash: str,
    content_hash_basis: str,
    metrics: dict,
    runner: str,
    planted: dict | None = None,
    ran_at: datetime | None = None,
    repo: Path | None = None,
) -> dict:
    if cell not in ("live", "twin"):
        raise ValueError(f"cell must be 'live' or 'twin', got {cell!r}")
    if cell == "twin" and planted is None:
        raise ValueError("twin verdict must carry its planted mutation")
    if cell == "live" and planted is not None:
        raise ValueError("live verdict must not carry a planted mutation")

    sha, worktree = git_state(repo or repo_root())
    ran = (ran_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    row = {
        "schema": SCHEMA,
        "kind": "GATE_VERDICT",
        "surface": stage,
        "lane": lane,
        "cell": cell,
        "result": _RESULT[report.status],
        "checks": {c.name: c.violations for c in report.checks},
        "evaluated": {c.name: c.evaluated for c in report.checks},
        "scope": report.scope,
        "params": {**report.params, "run_id": run_id},
        "metrics": metrics,
        "content_hash": content_hash,
        "content_hash_basis": content_hash_basis,
        "gate_sha": sha,
        "gate_worktree": worktree,
        "ran_at": ran.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "runner": runner,
    }
    if report.status is Status.UNEVALUABLE:
        row["unevaluable_reason"] = report.reason or "unstated"
    if planted is not None:
        row["planted"] = planted
    return row

def write_verdict(row: dict, out_dir: Path) -> Path:
    """<surface>-lane<lane>-live-<stamp>.json, or -twin-<mutation>-<stamp>.json: two twins for one
    surface emitted in the same second (a fixture twin and a runtime twin) must not share a name."""
    stamp = row["ran_at"].replace("-", "").replace(":", "")
    cell = "live" if row["cell"] == "live" else f"twin-{row['planted']['mutation']}"
    path = out_dir / f"{row['surface']}-lane{row['lane']}-{cell}-{stamp}.json"
    canon.write_json(path, row)
    return path
