# The gate discipline

This repository follows DATUM, a public governing text the author shares
across several data-platform repositories. This file restates every part of
it that binds this repository, under stable names that the other documents
and the code comments use. A reader needs nothing outside this tree.

## One sentence

A data platform is credited by what its gates have shown, never by what its
author says, and a gate counts only after it has been seen to fail.

## The rules, in dependency order

Each rule depends on the one before it.

**rows-not-sentences.** Every claim resolves to a machine-checkable verdict
row carrying the identity of the code that produced it and the content it
ran over. Prose points at rows and never carries a count or a status a row
does not carry first.

**three-outcomes.** GREEN, RED, and UNEVALUABLE with a stated reason in its
own field. Unevaluable is neither a soft pass nor a soft fail; it halts
whatever depends on it. A zero evaluated denominator forces UNEVALUABLE.

**twin-red-as-planted.** Every gate ships with a twin: the same input with
exactly one planted defect. The gate is credited only when the live input is
GREEN and the twin is RED for exactly the planted reason, compared key for
key over the union of both key sets. A twin that comes back GREEN, or RED
for a different reason, is a broken gate and the checker refuses to derive
status rather than render a wrong table. A property with several twins needs
every one of them red as planted. Every check the live row reports must also
have been seen to fail: at least one twin red as planted sets it nonzero, or
the surface derives PARTIAL, never CLAIMABLE, and the unfalsified checks are
named. This crediting applies only to a GREEN live with valid twins: a
surface with an UNEVALUABLE row derives UNEVALUABLE, whatever its checks.

**checker-controls.** The thing that checks the rows is itself a gate:
fixture rows that must pass and fixture rows that must each fail for a named
reason run in CI before anything is built. A refusal nobody planted is itself
a failure. The checker states what it cannot check, and "followed" is never
read as "machine-checked" for rules the checker cannot reach.

**derived-status.** The claimability table is computed from rows at build
time. The literals CLAIMABLE, PARTIAL, UNCLAIMED found inside any row fail
the build. The committed rendering is compared against a fresh one in CI.
STATUS.md holds a hand-written dated narrative plus a generated block
between markers; both are checked.

**identity-triple.** A row carries a content hash with its basis written
beside it, the emitter's commit, and whether the emitter's worktree was
clean. A dirty-tree row is evidence about code nobody can check out; this
repository refuses it, which is stricter than the governing text. Hashes are
over LF-normalised bytes where the consumer is newline-insensitive.

**pushed-sha.** A row in a working tree is a draft. For runs CI can
regenerate, the claim is the CI run green on a pushed commit. Gates that
depend on other gates are UNEVALUABLE until the rows they depend on are
pushed.

**hand-copy-seam.** Rows from a rented GPU or a box that no longer exists
are committed, bound file by file to a sha256 in a source file the checker
recomputes; any unlisted, missing, or altered file fails. Rows CI can
regenerate are build output and are not committed.

**probe-the-effect.** A destroy that says it destroyed is a claim about the
action. Teardown is verified by an inventory query by tag that must return
empty, run twice; Terraform state is an index, not a decision. A probe that
would answer the same either way earns nothing.

**floor-provenance.** A floor or tolerance is an authored number and
therefore a status in disguise. Each lives in one file, keyed by the
condition it applies to, with its source written beside it. A floor derived
from a run's own numbers makes that run's pass circular and is labelled
descriptive, not a claim.

**scope-walls-first.** The README names what the repository does not do and
will not claim; a claim ceiling lists what may be claimed after the last
planned run. Precise verbs: we validate, we use as a baseline, we propose.

**corrections-in-place.** Records (rows, STATUS entries, learnings,
handoffs) are corrected by appending next to the error with a date, never
by erasing. A governing text is revised instead, with a section naming what
changed and why.

## The verdict row

The row's field names live in the code that emits and checks them
(`traverse/verdict.py`, `gates/ledger.py`) and in the fixture rows under
`fixtures/rows/`, not in prose. The invariants:

- it names its kind, a versioned schema identifier, its surface, its lane,
  and its cell (live or twin);
- a twin carries its planted expectation (mutation, mutated rows, expected
  violations); a live row carries none;
- its result is exactly GREEN, RED, or UNEVALUABLE, with the reason in its
  own field in the third case and forbidden otherwise;
- every check it reports has an evaluated denominator;
- it is bound to content, code, and worktree;
- repository-specific measurements go under `metrics` and `params` and
  never displace a field above; the row refuses anything else at top level.

## What this repository owes, and where each rule is checked

| rule | checked by | notes |
|---|---|---|
| rows-not-sentences | the vendored shared checker; `gates/ledger.py` | the row's shape |
| three-outcomes | the vendored shared checker; `gates/ledger.py` | zero denominator forces UNEVALUABLE |
| twin-red-as-planted | the vendored shared checker; `gates/ledger.py` | fixture twins in CI; runtime twins on the rented instance; an unfalsified live check derives PARTIAL |
| checker-controls | the vendored shared checker's own controls, mutation included; `tests/test_check_ledger_controls.py` | |
| derived-status | status literals: both checkers; the table: `scripts/build_status.py --check` | the two checkers' derived statuses must agree |
| identity-triple | field form: the vendored shared checker; `gates/ledger.py` | the dirty-tree refusal is this repository's own |
| pushed-sha | CI on `main` | |
| hand-copy-seam | `gates/check_ledger.py --bound` | this repository's own check; committed runs under `runs/` |
| probe-the-effect | `scripts/inventory.py` | teardown surface |
| floor-provenance | `gates/floors.json` source strings | |
| scope-walls-first | README | |
| corrections-in-place | STATUS.md record, `docs/handoff/` | |

The shared conformance checker that accompanies the governing text exists
as code. This repository vendors a copy of it under `gates/conformance/`,
binds every vendored file to one commit of the governing text in a pin file,
verifies that pin before anything vendored runs, runs the checker's own
controls, and then runs it from `gates/run.sh` over every rows directory.
This repository's checker derives the same statuses a second time, and the
build fails when the two disagree. Two refusals belong to this repository
alone, and the shared checker accepts both rows: a row from a dirty
worktree, and a row from a rented runner that lacks its run parameters
(region, price per hour, dataset revision and licence, instance type).
Until CI has run green on a pushed commit, every row in this table states
what is owed, not what ran.
