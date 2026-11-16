import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from traverse.verdict import SCHEMA, Check, GateReport, Status, git_state, verdict_row, write_verdict

def _repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                    "--allow-empty", "-m", "init"], cwd=tmp_path, check=True)
    return tmp_path

def _kw(repo: Path, **over) -> dict:
    kw = dict(stage="fetch", lane=1, run_id="r1", content_hash="sha256:aa",
              content_hash_basis="t", metrics={}, runner="local", repo=repo)
    kw.update(over)
    return kw

def test_report_from_checks_derives_status():
    ok = GateReport.from_checks([Check("a", 0, 10)], {}, "s")
    bad = GateReport.from_checks([Check("a", 1, 10)], {}, "s")
    assert ok.status is Status.PASS and bad.status is Status.FAIL

def test_zero_denominator_forces_unevaluable():
    rep = GateReport.from_checks([Check("a", 0, 0), Check("b", 0, 5)], {}, "s")
    assert rep.status is Status.UNEVALUABLE
    assert "a" in rep.reason
    assert {c.name: c.evaluated for c in rep.checks} == {"a": 0, "b": 5}

def test_zero_denominator_keeps_a_measured_failure():
    # One empty domain refuses the report; it does not erase what the other checks measured.
    rep = GateReport.from_checks([Check("a", 0, 0), Check("b", 3, 5)], {}, "s")
    assert rep.status is Status.UNEVALUABLE
    assert {c.name: (c.violations, c.evaluated) for c in rep.checks} == {"a": (0, 0), "b": (3, 5)}

def test_unevaluable_requires_named_checks():
    with pytest.raises(ValueError):
        GateReport.unevaluable("why", {}, "s", checks=[])
    with pytest.raises(ValueError):
        GateReport.from_checks([], {}, "s")

def test_git_state_reports_clean_then_dirty(tmp_path: Path):
    repo = _repo(tmp_path)
    sha, wt = git_state(repo)
    assert len(sha) == 40 and wt == "clean"
    (repo / "x").write_text("x")
    assert git_state(repo)[1] == "dirty"

def test_live_row_shape(tmp_path: Path):
    repo = _repo(tmp_path)
    rep = GateReport.from_checks([Check("throughput_above_floor", 0, 1)], {"instance_type": "local"}, "3 filings")
    row = verdict_row(rep, cell="live", ran_at=datetime(2026, 9, 6, tzinfo=timezone.utc),
                      **_kw(repo, metrics={"wall_s": 1.0}))
    assert row["schema"] == SCHEMA and row["kind"] == "GATE_VERDICT"
    assert row["surface"] == "fetch" and "stage" not in row
    assert row["result"] == "GREEN"
    assert row["checks"] == {"throughput_above_floor": 0}
    assert row["evaluated"] == {"throughput_above_floor": 1}
    assert row["params"] == {"instance_type": "local", "run_id": "r1"} and "run_id" not in row
    assert row["gate_worktree"] == "clean" and len(row["gate_sha"]) == 40
    assert row["ran_at"] == "2026-09-06T00:00:00Z"
    assert "planted" not in row and "unevaluable_reason" not in row

def test_twin_requires_planted_and_live_forbids_it(tmp_path: Path):
    repo = _repo(tmp_path)
    rep = GateReport.from_checks([Check("c", 1, 1)], {}, "s")
    with pytest.raises(ValueError):
        verdict_row(rep, cell="twin", **_kw(repo))
    with pytest.raises(ValueError):
        verdict_row(rep, cell="live", planted={"mutation": "m"}, **_kw(repo))

def test_unevaluable_row_carries_reason_and_zeroed_checks(tmp_path: Path):
    repo = _repo(tmp_path)
    rep = GateReport.unevaluable("no floor for instance type g9.huge", {"instance_type": "g9.huge"}, "s",
                                 checks=[Check("throughput_above_floor", 0, 0)])
    row = verdict_row(rep, cell="live", **_kw(repo))
    assert row["result"] == "UNEVALUABLE"
    assert row["unevaluable_reason"] == "no floor for instance type g9.huge"
    assert row["checks"] == {"throughput_above_floor": 0} and row["evaluated"] == {"throughput_above_floor": 0}

def test_write_verdict_filename_and_lf(tmp_path: Path):
    repo = _repo(tmp_path)
    rep = GateReport.from_checks([Check("c", 0, 1)], {}, "s")
    row = verdict_row(rep, cell="live", ran_at=datetime(2026, 9, 6, 1, 2, 3, tzinfo=timezone.utc),
                      **_kw(repo, stage="pack"))
    p = write_verdict(row, tmp_path / "out")
    assert p.name == "pack-lane1-live-20260906T010203Z.json"
    assert b"\r" not in p.read_bytes()
    assert json.loads(p.read_text())["surface"] == "pack"
    twin = verdict_row(GateReport.from_checks([Check("c", 1, 1)], {}, "s"), cell="twin",
                       planted={"mutation": "plant_x", "mutated_rows": 1, "expected_violations": {"c": 1}},
                       ran_at=datetime(2026, 9, 6, 1, 2, 3, tzinfo=timezone.utc), **_kw(repo, stage="pack"))
    assert write_verdict(twin, tmp_path / "out").name == "pack-lane1-twin-plant_x-20260906T010203Z.json"
