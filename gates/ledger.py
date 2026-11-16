"""Ledger rules over verdict rows. Pure functions; no I/O except what callers pass in.

Implements the shared row (SCHEMA below) and its crediting rule
(docs/discipline.md). Status is derived here and, independently, by the
vendored shared checker; gates/agree.py fails the build when the two differ.
A live check that no twin red as planted has made fail is not credited. A status literal inside a row is an authored status and fails validation.
A live RED, a GREEN twin, or a twin RED for a reason other than the one planted
is refused: a real surface failing or a plant the gate missed needs a human,
not a table row.
"""

from __future__ import annotations

import re

SCHEMA = "datum/gate-verdict/1"
REQUIRED_FIELDS = (
    "schema", "kind", "surface", "lane", "cell", "result", "checks", "evaluated", "scope",
    "params", "content_hash", "content_hash_basis", "gate_sha", "gate_worktree", "ran_at", "runner",
)
OPTIONAL_FIELDS = ("unevaluable_reason", "planted", "rows", "metrics")
RESULTS = ("GREEN", "RED", "UNEVALUABLE")
STATUS_LITERALS = ("CLAIMABLE", "PARTIAL", "UNCLAIMED")
# The shared checker applies its patterns with JavaScript's RegExp.test, where `$` is the end of the string
# and `\b` is ASCII. Python's `$` also matches before a trailing newline and its `\b` is Unicode-aware,
# hence `\Z` and re.ASCII below.
_SURFACE = re.compile(r"^[a-z0-9][a-z0-9-]*\Z")
_SHA40 = re.compile(r"^[0-9a-f]{40}\Z")
_CONTENT = re.compile(r"^sha256:[0-9a-f]{64}\Z")
_STATUS_WORD = re.compile(r"\b(CLAIMABLE|PARTIAL|UNCLAIMED)\b", re.ASCII)

class LedgerRefusal(Exception):
    pass

def _counts_ok(d) -> bool:
    return isinstance(d, dict) and bool(d) and all(isinstance(v, int) and v >= 0 for v in d.values())

def validate_row(row: dict, rel: str) -> list[str]:
    errs: list[str] = []
    for f in REQUIRED_FIELDS:
        if f not in row:
            errs.append(f"{rel}: missing field {f}")
    for f in sorted(set(row) - set(REQUIRED_FIELDS) - set(OPTIONAL_FIELDS)):
        errs.append(f"{rel}: additional property {f} refused by the shared row; repo-specific values go under params or metrics")
    if errs:
        return errs
    if row["schema"] != SCHEMA:
        errs.append(f"{rel}: schema must be {SCHEMA}, got {row['schema']!r}")
    if row["kind"] != "GATE_VERDICT":
        errs.append(f"{rel}: kind must be GATE_VERDICT")
    if not isinstance(row["surface"], str) or not _SURFACE.match(row["surface"]):
        errs.append(f"{rel}: surface must match ^[a-z0-9][a-z0-9-]*$, got {row['surface']!r}")
    if not isinstance(row["lane"], int) or row["lane"] < 1:
        errs.append(f"{rel}: lane must be an integer >= 1")
    if row["cell"] not in ("live", "twin"):
        errs.append(f"{rel}: cell must be live or twin")
    if row["result"] not in RESULTS:
        errs.append(f"{rel}: result must be one of {RESULTS}, got {row['result']!r}")
    unevaluable = row["result"] == "UNEVALUABLE"
    if unevaluable and not row.get("unevaluable_reason"):
        errs.append(f"{rel}: UNEVALUABLE row must carry unevaluable_reason")
    if not unevaluable and "unevaluable_reason" in row:
        errs.append(f"{rel}: unevaluable_reason is forbidden unless result is UNEVALUABLE")
    if not _counts_ok(row["checks"]) or not _counts_ok(row["evaluated"]):
        errs.append(f"{rel}: checks and evaluated must be non-empty maps of non-negative integers")
    elif set(row["checks"]) != set(row["evaluated"]):
        errs.append(f"{rel}: checks and evaluated must carry the same keys")
    else:
        if any(v == 0 for v in row["evaluated"].values()) and not unevaluable:
            errs.append(f"{rel}: zero evaluated denominator forces UNEVALUABLE, got {row['result']}")
        violations = sum(row["checks"].values())
        if row["cell"] == "live" and violations > 0 and row["result"] == "GREEN":
            errs.append(f"{rel}: live is GREEN with {violations} violations")
        if row["cell"] == "twin" and violations == 0 and row["result"] == "RED":
            errs.append(f"{rel}: twin is RED with no violations")
    if row["gate_worktree"] != "clean":
        errs.append(f"{rel}: worktree was {row['gate_worktree']}; a row from a dirty tree is evidence about code nobody can check out")
    if not isinstance(row["gate_sha"], str) or not _SHA40.match(row["gate_sha"]):
        errs.append(f"{rel}: gate_sha is not a 40-hex commit")
    if not isinstance(row["content_hash"], str) or not _CONTENT.match(row["content_hash"]):
        errs.append(f"{rel}: content_hash must be sha256:<64 hex>")
    if row["cell"] == "twin":
        p = row.get("planted")
        if not isinstance(p, dict) or not all(k in p for k in ("mutation", "mutated_rows", "expected_violations")):
            errs.append(f"{rel}: twin row must carry planted.mutation, planted.mutated_rows, planted.expected_violations")
    if row["cell"] == "live" and "planted" in row:
        errs.append(f"{rel}: live row must not carry planted")
    for hit in find_status_literals(row):
        errs.append(f"{rel}: authored status literal at {hit}; status is derived, never written")
    return errs

def find_status_literals(row: dict) -> list[str]:
    """Every key or string value carrying a status literal as a word. A literal inside a sentence, or
    used as a key, is still a status typed into a row; the vendored shared checker reads it the same way."""
    hits: list[str] = []

    def walk(v, path):
        if isinstance(v, dict):
            for k, x in v.items():
                sub = f"{path}.{k}" if path else str(k)
                if isinstance(k, str) and _STATUS_WORD.search(k):
                    hits.append(sub)
                walk(x, sub)
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, f"{path}[{i}]")
        elif isinstance(v, str) and _STATUS_WORD.search(v):
            hits.append(path)

    walk(row, "")
    return hits

def group_cells(rows: list[dict]) -> dict[tuple[str, int], list[dict]]:
    out: dict[tuple[str, int], list[dict]] = {}
    for r in rows:
        out.setdefault((r["surface"], r["lane"]), []).append(r)
    return out

def twin_red_as_planted(row: dict) -> bool:
    """Key for key over the union of both key sets, every key present on both sides. A check the twin
    computed that the plant never named, even at zero, is not the planted reason."""
    if row["cell"] != "twin" or row["result"] != "RED":
        return False
    expected = row["planted"]["expected_violations"]
    checks = row["checks"]
    return set(expected) == set(checks) and all(checks[k] == expected[k] for k in checks)

def unfalsified_checks(cells: list[dict]) -> list[str]:
    """The live row's check keys that no twin RED as planted sets nonzero. A check that has never been
    seen to fail is not credited; its group derives PARTIAL, never CLAIMABLE."""
    lives = [c for c in cells if c["cell"] == "live"]
    if not lives:
        return []
    falsified = {k for t in cells if t["cell"] == "twin" and twin_red_as_planted(t)
                 for k, v in t["checks"].items() if v > 0}
    return sorted(set(lives[0]["checks"]) - falsified)

def derive_status(cells: list[dict]) -> str:
    lives = [c for c in cells if c["cell"] == "live"]
    twins = [c for c in cells if c["cell"] == "twin"]
    where = f"{cells[0]['surface']} lane {cells[0]['lane']}" if cells else "(no rows)"
    if len(lives) > 1:
        raise LedgerRefusal(f"{where}: more than one live row")
    muts = [t["planted"]["mutation"] for t in twins]
    if len(muts) != len(set(muts)):
        raise LedgerRefusal(f"{where}: two twins plant the same mutation; a duplicated twin cannot count twice")
    for t in twins:
        if t["result"] == "GREEN":
            raise LedgerRefusal(f"{where}: twin is GREEN; the gate did not see its planted defect")
        if t["result"] == "RED" and not twin_red_as_planted(t):
            raise LedgerRefusal(f"{where}: twin RED but not for the planted reason: checks={t['checks']} planted={t['planted']['expected_violations']}")
    for l in lives:
        if l["result"] == "RED":
            raise LedgerRefusal(f"{where}: live is RED; a real surface failing needs a human, not a status")
    if not lives and not twins:
        return "UNCLAIMED"
    if any(c["result"] == "UNEVALUABLE" for c in lives + twins):
        return "UNEVALUABLE"
    if not lives or not twins:
        return "PARTIAL"
    if unfalsified_checks(cells):
        return "PARTIAL"
    return "CLAIMABLE"

_BINDING = re.compile(r"^([0-9a-f]{64})\s{2,}(\S+)\s*$")

def parse_source_bindings(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = _BINDING.match(line.strip())
        if m:
            out[m.group(2)] = m.group(1)
    return out
