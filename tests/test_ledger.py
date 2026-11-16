import pytest

from gates.ledger import (LedgerRefusal, derive_status, find_status_literals, group_cells,
                          parse_source_bindings, twin_red_as_planted, unfalsified_checks, validate_row)

def live(result="GREEN", checks=None, **over):
    row = {
        "schema": "datum/gate-verdict/1", "kind": "GATE_VERDICT", "surface": "fetch", "lane": 1,
        "cell": "live", "result": result, "checks": checks or {"c": 0}, "evaluated": {"c": 1},
        "scope": "s", "params": {"run_id": "r"}, "metrics": {}, "gate_sha": "a" * 40,
        "gate_worktree": "clean", "content_hash": "sha256:" + "0" * 64, "content_hash_basis": "b",
        "ran_at": "2026-09-06T00:00:00Z", "runner": "local",
    }
    if result == "RED" and checks is None:
        row["checks"] = {"c": 1}
    if result == "UNEVALUABLE":
        row["unevaluable_reason"] = "why"
        row["checks"], row["evaluated"] = {"c": 0}, {"c": 0}
    row.update(over)
    return row

def twin(checks, expected, **over):
    over.setdefault("result", "RED")
    return live(cell="twin", checks=checks,
                planted={"mutation": "m", "mutated_rows": 1, "expected_violations": expected}, **over)

def test_validate_accepts_good_rows():
    assert validate_row(live(), "x") == []
    assert validate_row(twin({"c": 1}, {"c": 1}), "x") == []
    assert validate_row(live(result="UNEVALUABLE"), "x") == []

def test_validate_rejects_missing_unknown_and_wrong_schema():
    r = live(); del r["gate_sha"]
    assert any("gate_sha" in e for e in validate_row(r, "x"))
    assert any("additional property" in e for e in validate_row(live(run_id="top-level"), "x"))
    assert any("schema" in e for e in validate_row(live(schema="other/gate-verdict/1"), "x"))
    assert any("surface" in e for e in validate_row(live(surface="Fetch Stage"), "x"))

def test_validate_reason_iff_unevaluable():
    r = live(result="UNEVALUABLE"); del r["unevaluable_reason"]
    assert any("unevaluable_reason" in e for e in validate_row(r, "x"))
    assert any("unevaluable_reason" in e for e in validate_row(live(unevaluable_reason="no"), "x"))

def test_validate_cross_field_rules():
    assert any("zero evaluated" in e for e in validate_row(live(evaluated={"c": 0}), "x"))
    assert any("live is GREEN" in e for e in validate_row(live(checks={"c": 2}), "x"))
    assert any("twin is RED" in e for e in validate_row(twin({"c": 0}, {"c": 0}), "x"))
    assert any("worktree was dirty" in e for e in validate_row(live(gate_worktree="dirty"), "x"))
    assert any("evaluated" in e for e in validate_row(live(evaluated={"other": 1}), "x"))

def test_status_literal_scan_catches_nested_and_allows_unevaluable():
    assert find_status_literals(live(result="UNEVALUABLE")) == []
    assert find_status_literals(live(metrics={"note": "CLAIMABLE"})) == ["metrics.note"]
    assert any("authored status literal" in e for e in validate_row(live(scope="PARTIAL"), "x"))

def test_status_literal_scan_matches_words_inside_strings_and_keys():
    assert find_status_literals(live(metrics={"note": "3 filings; sweep PARTIAL by design"})) == ["metrics.note"]
    assert find_status_literals(live(metrics={"CLAIMABLE": 1})) == ["metrics.CLAIMABLE"]
    assert find_status_literals(live(metrics={"note": "claimable, in lower case, is prose"})) == []

def test_patterns_refuse_a_trailing_newline_as_the_shared_checker_does():
    row = live(surface="fetch\n", gate_sha="a" * 40 + "\n", content_hash="sha256:" + "0" * 64 + "\n")
    errs = validate_row(row, "x")
    assert any("surface must match" in e for e in errs)
    assert any("gate_sha is not a 40-hex commit" in e for e in errs)
    assert any("content_hash must be sha256" in e for e in errs)

def test_status_word_boundary_is_ascii_as_in_the_shared_checker():
    assert find_status_literals(live(metrics={"note": "CLAIMABLE\u00e9"})) == ["metrics.note"]
    assert find_status_literals(live(metrics={"note": "\u00e9UNCLAIMED"})) == ["metrics.note"]
    assert find_status_literals(live(metrics={"note": "CLAIMABLEx"})) == []

def test_twin_red_as_planted_union_of_keys():
    assert twin_red_as_planted(twin({"c": 1, "d": 0}, {"c": 1, "d": 0}))
    # A computed zero the plant never named is not the planted reason; the shared checker refuses it too.
    assert not twin_red_as_planted(twin({"c": 1, "d": 0}, {"c": 1}))
    assert not twin_red_as_planted(twin({"c": 1}, {"c": 1, "d": 1}))
    assert not twin_red_as_planted(twin({"c": 2, "d": 0}, {"c": 1, "d": 0}))

def test_unfalsified_live_check_derives_partial():
    lv = live(checks={"c": 0, "d": 0}, evaluated={"c": 1, "d": 1})
    tw = twin({"c": 1, "d": 0}, {"c": 1, "d": 0}, evaluated={"c": 1, "d": 1})
    assert unfalsified_checks([lv, tw]) == ["d"]
    assert derive_status([lv, tw]) == "PARTIAL"
    tw2 = twin({"c": 0, "d": 2}, {"c": 0, "d": 2}, evaluated={"c": 1, "d": 1})
    tw2["planted"]["mutation"] = "m2"
    assert unfalsified_checks([lv, tw, tw2]) == []
    assert derive_status([lv, tw, tw2]) == "CLAIMABLE"

def test_unevaluable_live_takes_precedence_over_per_check_crediting():
    # Per-check crediting applies only to a GREEN live with valid twins. An UNEVALUABLE live derives
    # UNEVALUABLE, never PARTIAL, even beside a check no twin has made fail; the shared checker states the same.
    lv = live(result="UNEVALUABLE")
    lv["checks"], lv["evaluated"] = {"c": 0, "d": 0}, {"c": 0, "d": 0}
    tw = twin({"c": 1, "d": 0}, {"c": 1, "d": 0}, evaluated={"c": 1, "d": 1})
    assert validate_row(lv, "x") == [] and validate_row(tw, "x") == []
    assert unfalsified_checks([lv, tw]) == ["d"]
    assert derive_status([lv, tw]) == "UNEVALUABLE"
    tw0 = twin({"c": 0}, {}, result="UNEVALUABLE", unevaluable_reason="why")
    tw0["checks"], tw0["evaluated"] = {"c": 0, "d": 0}, {"c": 0, "d": 0}
    assert derive_status([lv, tw0]) == "UNEVALUABLE"

def test_derive_status_table():
    assert derive_status([live(), twin({"c": 1}, {"c": 1})]) == "CLAIMABLE"
    assert derive_status([live()]) == "PARTIAL"
    assert derive_status([twin({"c": 1}, {"c": 1})]) == "PARTIAL"
    assert derive_status([]) == "UNCLAIMED"
    assert derive_status([live(result="UNEVALUABLE"), twin({"c": 1}, {"c": 1})]) == "UNEVALUABLE"
    assert derive_status([live(), twin({"c": 0}, {}, result="UNEVALUABLE", unevaluable_reason="w",
                                        evaluated={"c": 0})]) == "UNEVALUABLE"

def test_derive_status_refusals():
    with pytest.raises(LedgerRefusal, match="twin is GREEN"):
        derive_status([live(), twin({"c": 0}, {"c": 1}, result="GREEN")])
    with pytest.raises(LedgerRefusal, match="not for the planted reason"):
        derive_status([live(), twin({"c": 2}, {"c": 1})])
    with pytest.raises(LedgerRefusal, match="live is RED"):
        derive_status([live(result="RED"), twin({"c": 1}, {"c": 1})])
    with pytest.raises(LedgerRefusal, match="more than one live"):
        derive_status([live(), live()])
    with pytest.raises(LedgerRefusal, match="same mutation"):
        derive_status([live(), twin({"c": 1}, {"c": 1}), twin({"c": 1}, {"c": 1})])

def test_group_cells_keys_by_surface_and_lane():
    g = group_cells([live(), live(surface="pack"), live(lane=2)])
    assert set(g) == {("fetch", 1), ("pack", 1), ("fetch", 2)}

def test_parse_source_bindings():
    a, b = "a" * 64, "b" * 64
    text = f"# x\n\n## sha256\n\n{a}  verdicts/a.json\n{b}  verdicts/b.json\n\n## Replay\n"
    assert parse_source_bindings(text) == {"verdicts/a.json": a, "verdicts/b.json": b}
    assert parse_source_bindings("abcd  verdicts/short.json\n") == {}
