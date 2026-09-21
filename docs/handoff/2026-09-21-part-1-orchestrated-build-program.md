# Handoff: Part 1 is ready to build, wave by wave, behind four unmade rulings

2026-09-21. This repository has **no commits**. Every claim below is about a
working tree, and the drift a pick-up should measure is from the tree this brief
describes, not from a commit. The two dated records written earlier today —
`2026-09-21-history-reset-and-the-wording-ruling.md` and the three entries under
`docs/learnings/` — are the evidence this brief rests on and are not restated here.

The direction changed today: the Gas Town bake-off is retired. Part 1 is built
directly, wave by wave, under the orchestration discipline. The bake-off's
dependency analysis survives that retirement and is the wave plan below; its
spec stays local and uncommitted.

## Current state

- **built — the documents the first commit carries.** Seven documents and
  `.gitignore`. All carry the amended wording ("a public governing text").
  re-verify: `git add -A --dry-run` lists exactly 12 paths — `.gitignore`,
  `README.md`, `docs/design.md`, `docs/discipline.md`, three dated entries plus
  the index under `docs/handoff/`, and three dated entries plus the index under
  `docs/learnings/` — and no path under `docs/plans/` or `docs/superpowers/`.

- **built — the history reset.** Branch `main`, no commits, `origin` at this
  repository, the gameplay history mirrored outside the workspace.
  re-verify: `git log --oneline` reports no commits; `git remote get-url origin`
  names this repository.

- **built — the wording rule's amendment.** By operator ruling of 2026-09-21 the
  required phrase is "a public governing text"; nothing else in the rule changed.
  Applied to three documents and four places in the plan.
  re-verify: `for f in README.md docs/design.md docs/discipline.md; do grep -c
  "a public governing text" "$f"; done` prints `1` three times.

- **built — the wording rule holds over the tree, and its twins go red.** The
  gate itself is Task 1.12 and does not exist; the rule was hand-run over exactly
  what a commit would carry, and six planted defects were each refused for their
  own planted reason. This is a hand-run, not a gate: it is evidence the tree is
  clean today, and it is superseded the moment `gates/wording.py` exists.
  re-verify: nothing in-tree re-runs this. Rebuild it or wait for Task 1.12.

- **built — Task 1.5a's operator input is satisfied.** The pinned conformance
  pack commit is reachable on the governing text's default branch, its run
  concluded success, and it yields the 75 pack files Step 1 recorded.
  re-verify: the `re-verify:` line in
  `docs/learnings/2026-09-21-the-pack-pin-became-fetchable-when-the-text-was-published.md`.

- **not started — everything executable.** No `traverse/`, `gates/`, `scripts/`,
  `tests/`, `fixtures/`, `infra/`, `k8s/`, `STATUS.md` or CI workflow.
  re-verify: none of those paths exists.

- **not started — the dry run.** The plan's dry-run section is still the empty
  record written on 2026-09-18. The plan calls it the gate before execution.
  re-verify: `sed -n '/^## Dry run of this document/,/^## Execution/p'
  docs/plans/2026-09-18-build.md` prints the empty record.

- **planned — Part 1, Tasks 1.1 to 1.12**, in six waves (see Reuse map).
- **planned — Task 1.13**, CI on the pushed SHA; it cannot start before the push.
- **blocked — Parts 2 and 3.** Both cloud profiles are still absent. Part 3
  additionally carries a 22:00 local kill switch on its execution day.

## Locked decisions

- **The Gas Town bake-off is retired** (operator, 2026-09-21). Reason: the
  decision was to build Part 1 directly under the orchestration discipline
  rather than to run a two-arm comparison over it. Its spec stays local and
  git-excluded; the waves it derived are reused.
- **The wording rule's required phrase is "a public governing text"** (operator
  ruling, 2026-09-21). Reason: the governing text was published, so the old
  phrase asserted something false. Everything else in the rule is unchanged —
  still named at most once per document, still no rule number, no schema literal
  in prose, no path or commit of it. Pick-up should check the premise: if the
  text ever goes private again, this ruling inverts.
- **The history was replaced rather than continued** (operator, 2026-09-21).
  Reason: a different corpus under the same folder, and the archive states the
  intent. Explicitly **not** a gate requirement — see the learnings entry that
  refutes that reasoning.
- **`docs/plans/` and `docs/superpowers/` are local and git-excluded.** Reason:
  the plan is the one file permitted to name the pinned commit; the bake-off spec
  is unreviewed. Both exclusions live in `.git/info/exclude`, which does not
  survive a re-init — re-create them before any `git add`.
- **Git history is the operator's.** Agents print commit commands and never run
  `git commit` or `git push`. Every infrastructure apply, quota request, registry
  push and filing-service run is an operator-approved action.
- **The three decisions deferred to Part 2** (operator, 2026-09-21): correctness
  identity at `max_num_seqs` 1 only; the hit rate as an upper bound on the
  document portion; the handoff gate's lower bound only. Reason: they are
  serve-sweep questions that cannot be exercised until a cloud lane exists, so
  ruling them today would be ruling them blind.

## Reuse map

- `docs/plans/2026-09-18-build.md` — the one build plan, local and git-excluded.
  9,227 lines, md5 `b60b701433b3b55aaf1579f8c335e9a2` after today's amendment.
  Everything below is in it; do not re-derive anything from the design.
- **The wave plan**, derived from the plan's import lines and file lists. Test-time
  fixture reads are not captured in it, which is a known gap:

  | wave | tasks |
  |---|---|
  | W1 | 1.1 |
  | W2 | 1.2, 1.3, 1.4, 1.7 |
  | W3 | 1.5, 1.6, 1.8, 1.10a |
  | W4 | 1.5a, 1.8a, 1.9, 1.12 |
  | W5 | 1.10 |
  | W6 | 1.11 |

  W2, W3 and W4 are each four wide. The end line is unchanged: `pytest`,
  `gates/run.sh` and the STATUS `--check`, all green locally.
- **The plan's own list of what will bite first**, in its dry-run section: the
  rasteriser API is written against a major version whose names may have moved;
  the decode ink test's row window; the fixture seed for escalation selection;
  the fake server's timing margins, which were reasoned and not measured; two
  serving flags assumed present in the pinned build; report-name variation across
  filers. Read that list before the dry run rather than rediscovering it.
- `~/dev/briefs/2026-09-18-gameplay-vlm-serving-docs-archive.md` — every
  gameplay-era document byte for byte, and the only copy of three plans that were
  never committed. Local, unbacked, single machine. Keep it out of any push.
- The gameplay history, mirrored outside the workspace before the reset. Kept
  only until the operator is satisfied; nothing depends on it.

## Invariants

- **Nothing is a claim until its row is on a pushed SHA.** Gates depending on
  other gates are UNEVALUABLE until the rows they depend on are pushed. Violating
  this produces rows that look like evidence and are not.
- **A gate is credited only when its live cell is GREEN and its twin is RED for
  exactly the planted reason.** A check no twin has made fail derives PARTIAL,
  never CLAIMABLE. This is why decision 6 below is not cosmetic.
- **Status is derived, never authored.** A status literal in a row, or typed into
  a page, fails the build. `STATUS.md` holds a hand-written narrative and a
  generated block, compared against a fresh rendering by `--check`.
- **Floors are declared before the run they judge, never set from its own
  numbers.** A run on an instance type with no floor is UNEVALUABLE, not FAIL.
- **Every stage reads one manifest and writes one manifest** and never touches
  another stage's files.
- **`print()` output stays ASCII** (the console is cp1252). All JSON is written
  with sorted keys, LF endings and a trailing newline; hashes are over
  LF-normalised bytes.
- **The word `accuracy` appears in no row, table, page or identifier.** The
  measure is agreement between two surfaces the same filer authored.
- **Nothing tracked names the pinned commit** except `gates/conformance/PIN`
  line 1, once it exists. The plan may, because it is git-excluded.
- **Corrections to dated records are appended as new dated records, never edited
  in place.** The two 2026-09-18 briefs are immutable; today's records supersede
  parts of them and say which.

## Open / next

**First action: put the four rulings to the operator, then dry-run the plan.**
They were assembled and presented today and not answered. The operator chose to
rule the four that gate Part 1 now and defer the other three. Each is marked
*(pending review)* in `docs/design.md`; the plan implements all of them, so
striking one means amending the plan *before* the dry run.

1. **The admission-asof boundary** (Task 1.8a). The design says 23:59:59 of
   `asof_date` in `America/New_York`, the acceptance clock's zone; the
   alternative is a UTC cutoff, which excludes filings accepted late in the
   filer's afternoon. **Carry this warning into whichever is ruled:** a sibling
   repository lost 32 rows to a naive timestamp bound against a timezone-aware
   value, and timezone-aware fixtures made the test vacuous. The
   `future_accepted` twin must exercise that seam or it credits nothing.
2. **The aligner and its controls as a Part 1 build task** (Task 1.10a). Keeping
   it means the aligner is falsified on synthetic fixtures before any real figure
   depends on it; deferring it to Part 2 means it is first written and first
   exercised in the run that consumes it, which is the risk the design names.
3. **Floors declared before any run.** The rule restates a governing-text rule
   and is not in question; what is open is whether floors carrying a stated
   derivation but no cited prior figure satisfy it, or whether each such floor
   must be marked provisional in the emitted row.
4. **The pack surface's fourth twin**, a blanked container-image digest
   falsifying `image_digest_recorded`. Keep the twin, drop the check as a field
   assertion rather than a check, or keep the check and accept PARTIAL on the
   pack surface permanently. Under per-check crediting these are genuinely
   different, not stylistic.

**Then, in order.** The dry run — extract the plan, run its suite under the
pinned toolchain, run the two by-hand steps, fix defects in the *text*, and
record the result in the plan's empty section. Then waves W1 to W6, none of which
needs an operator input beyond the pack pin already satisfied. Then the first
commit and push, which unblocks Task 1.13 and every pushed-SHA claim.

**Blocker in the way of the first action:** none. The rulings need the operator,
and the dry run needs the rulings; nothing else is waiting on a machine, an
account or a credential.

**Not in the way, contrary to the older records:** the absent cloud profiles.
They block Parts 2 and 3 only.

## One thing this brief cannot vouch for

The wave plan was derived from import lines and file lists and does not capture
test-time fixture reads. If a wave's tasks turn out to share a fixture that one
of them writes, the waves are wrong in a way nothing here would have caught. The
dry run is the first thing that would surface it.
