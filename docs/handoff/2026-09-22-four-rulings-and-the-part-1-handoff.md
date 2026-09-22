# Handoff: the four rulings are in, decision 5 amended the plan, and Part 1 waits only on the dry run

2026-09-22. Written for the session that builds Part 1. Read
`2026-09-21-part-1-orchestrated-build-program.md` first; this record changes
three things in it and restates nothing else. The first commit it anticipated
was made and pushed the same evening (`11011bb`, 12 paths, exactly the set it
listed), so its "then the first commit and push" step is done and every dated
record now sits on a pushed SHA. This session did not run the dry run and did
not start a wave.

## What changed since the 2026-09-21 brief

- **built — the pick-up of that brief.** Every re-verify line was run on
  2026-09-22 and held: the phrase once per document, the plan at its recorded
  md5 with an empty dry-run section, no executable path present, the three
  learnings lines returning `0`, `0`, `ahead`, the governing text still public,
  the wording hand-check green with all six twins red as planted. No drift
  beyond the commit itself. No premise of a locked decision was contradicted.
  re-verify: `git log --oneline` shows `11011bb` as the first commit;
  `git ls-tree -r --name-only 11011bb | wc -l` prints `12`.

- **built — the four rulings, taken 2026-09-22.** The operator picked each from
  the alternatives the 2026-09-21 brief laid out. Verbatim:
  - decision 2, the as-of boundary: **"23:59:59 America/New_York"** — as designed.
  - decision 4, the aligner: **"Keep in Part 1"** — Task 1.10a stays in wave W3.
  - decision 5, floors without a cited prior: **"Mark provisional in the row"** —
    "Floor still declared before the run and still judges it; the row carries a
    `provisional: true` field until a cited figure replaces it."
  - decision 6, the pack surface's fourth twin: **"Keep the twin"** — as designed.
  The three deferred on 2026-09-21 (decisions 1, 3, 7) stay deferred.
  re-verify: `grep -c "pending review" docs/design.md` prints `5` (the intro
  line, the Open items heading, and the three deferred paragraphs).

- **built — decision 5's amendment to the plan.** Every floor entry in the two
  floors files carries `"provisional": true` (six in Task 1.6, seven in Task
  2.6; none has a cited prior figure today, so none is false). `load_floors`
  refuses a floor whose `source` is empty or whose `provisional` is not a
  boolean. The fetch-throughput, decode-bottleneck and pack-shape gates write
  `floor_provisional` under `params`, so the row a floor judges says so. One
  test added (Task 1.6 now expects 15, was 14); the README discipline table
  row for floor provenance says the same. Decisions 2, 4 and 6 changed no text.
  The plan's 80 Python blocks still compile; its three JSON fragments that
  never parsed alone (they are inserts, not documents) still do not, as before.
  re-verify: `grep -c '"provisional": true' docs/plans/2026-09-18-build.md`
  prints `13`; `wc -l docs/plans/2026-09-18-build.md` prints `9265`; md5 is
  `fb3b09746399f920f64540333a1b3897`.

- **built — the design records the rulings.** Four `(pending review)` markers
  removed, the Floors paragraph gained one sentence, Open items lists three, and
  Changes carries a 2026-09-22 entry. The wording rule still passes over the
  tracked tree (hand-run; the gate is Task 1.12 and does not exist).
  re-verify: `git diff --stat 11011bb -- docs/design.md` shows only that file
  changed, until the next commit lands; afterwards `git log -1 --format=%s --
  docs/design.md` names the rulings commit.

- **not started — the dry run**, still the empty 2026-09-18 record, and now the
  first action. Nothing gates it any more.
  re-verify: `sed -n '/^## Dry run of this document/,/^## Execution/p'
  docs/plans/2026-09-18-build.md` prints the empty record.

- **not started — waves W1 to W6**, unchanged from the 2026-09-21 brief.

## Locked decisions

The four rulings above, in addition to everything the 2026-09-21 brief locks.
Their stated reason is the design text they confirm; if a floor ever acquires
a cited prior figure, its `provisional` flips to false in the floors file, and
that is a change to a declaration before a run, never a change to a row.

## Reuse map

- `docs/plans/2026-09-18-build.md` — the one plan, local and git-excluded,
  amended today at Tasks 1.6, 1.12, 2.6 and 2.9 and in its header notes. The
  2026-09-21 brief's wave table, "bites first" list and archive pointer hold.
- The scratchpad hand-check and twin scripts that stood in for the wording
  gate are not in the tree and die with the session. Task 1.12 replaces them;
  until then, a session that wants the check rebuilds it from the rule as
  `docs/discipline.md` restates it.

## Invariants

Unchanged from the 2026-09-21 brief. One addition from today: a floor's
`provisional` flag is part of its declaration and is refused when absent,
never defaulted — a defaulted flag would be a status the code authored.

## Open / next

**First action: the dry run**, as the plan's own dry-run section prescribes:
extract, run the suite under the pinned toolchain, run the two by-hand steps,
fix defects in the text, record the result in that section. Two things known
before it starts:
- The only local interpreter is Python 3.14 (`py -0p` lists nothing else);
  the plan's floor is 3.12 and CI pins 3.12. Whether the pinned rasteriser and
  numpy wheels resolve on 3.14 is the first thing the dry run will learn; if
  not, a 3.12 has to be installed first, which is the operator's action. Node
  is 24, above the pack's floor of 20.
- No dependency lockfile exists yet; Task 1.1 writes `pyproject.toml`.

**Then** waves W1 to W6 under the orchestration discipline, a commit block per
wave for the operator, then Task 1.13 on the pushed SHA.

**Blocker in the way of the first action:** none.
