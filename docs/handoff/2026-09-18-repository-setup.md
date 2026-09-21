# Handoff: repository set up as vlm-filings-serving; plan consolidated, not yet dry-run

2026-09-18. This brief describes the tree that the repository's first commit carries. When it was written, that commit had not been made and no history existed for it. The earlier gameplay-era repository was deleted by the operator, and its documents are archived outside this tree. Nothing here depends on them.

## Current state

- **Written, first-commit content.** `README.md`, `docs/design.md`, `docs/discipline.md`, `docs/handoff/HANDOFF.md`, this brief, and `docs/learnings/LEARNINGS.md`, all in their final wording under the public-repo rule. `docs/discipline.md`, `docs/design.md` and the README each name the governing text exactly once; the other documents never name it.
  re-verify: `git ls-files` lists those six files and `.gitignore`, and nothing else. `for f in README.md docs/design.md docs/discipline.md; do grep -c "DATUM, a private governing text" "$f"; done` prints `1` three times.
- **Written, local only.** `docs/plans/2026-09-18-build.md` is the one build plan: 9,227 lines, md5 `812c8fed0560de4d6b8b15a7a1d42853`. It merges the gameplay-era full-build plan with the 2026-09-15 retheme and re-scopes the lane-2 sweep. It is git-excluded by `.git/info/exclude`, so a fresh clone does not contain it.
  re-verify: `git check-ignore -v docs/plans/2026-09-18-build.md` names `.git/info/exclude`. `md5sum docs/plans/2026-09-18-build.md` prints the hash above, unless the plan has been edited since.
- **Checked for syntax only.** All 80 Python blocks in the plan compile; two of them are indented insertion fragments, compiled after dedenting. Every JSON block parses except one prose-described fragment. Every name imported from a module the plan writes is defined somewhere in the plan. None of this runs anything.
- **Not done: the dry run.** The plan's dry-run section is empty. Extracting the plan and running its suite is the gate before execution.
  re-verify: `sed -n '/^## Dry run of this document/,/^## Execution/p' docs/plans/2026-09-18-build.md` prints the empty record.
- **Not started: all code.** There is no `traverse/`, `gates/`, `scripts/`, `tests/`, `fixtures/`, `infra/`, `k8s/`, `STATUS.md` or CI workflow yet.
- **Absent: both AWS identities.** Neither the `traverse-platform` nor the `traverse-provision` profile exists on this machine.
  re-verify: `aws configure list-profiles` prints `default` and `kv-platform-admin` only (checked 2026-09-18).
- **Pinned commit for the shared conformance pack.** The commit that passes Task 1.5a Step 1 was measured on 2026-09-15 and is recorded in the local plan's Task 1.5a. Under the wording rule no tracked file names it except, once written, `gates/conformance/PIN` line 1.
- **Untracked, the operator's call.** `docs/superpowers/specs/2026-09-15-gastown-bakeoff-design.md` is a proposed bake-off over Part 1, revised on 2026-09-18 by a dated section appended to its end.

## Locked decisions

- **Repository `vlm-filings-serving`, codename `traverse`.** The slug is the `repo` tag on every AWS resource and the teardown inventory's filter, so it does not change after the first apply.
- **The public-repo wording rule.** Every document names the governing text at most once. No document carries a path to that text, a commit of it, a rule number from it, or its schema literal in prose. Rules are cited by the names in `docs/discipline.md`.
- **The corpus is rendered SEC filings, with a second model as the adjudicator of a handoff sub-matrix** (the operator's rulings of 2026-09-15). No cache crosses models; the handoff cell prices the recompute floor.
- **Two AWS identities, and the Terraform split follows them.** `traverse-provision` creates IAM roles, and `traverse-platform` does everything else.
- **The shared verdict row, checked by two checkers that must agree.**
- **Synthetic fixtures are committed and pinned.** The PDF generator is deterministic, so the pin is also a freshness check.
- **Rows CI can regenerate are build output; rows from rented instances are committed and hash-bound.**
- **Git history is the operator's.** Agents output commit commands and never run them.

## Pending review (not locked)

Seven decisions the plan introduced on 2026-09-15 are marked *(pending review)* in `docs/design.md` and listed under its Open items. The plan implements all seven, so striking one means amending the plan before the dry run.
1. Correctness identity at `max_num_seqs` 1 only.
2. Gold as-of equal to `asof_date`, with the boundary in America/New_York.
3. The hit rate as an upper bound on the document-portion rate.
4. The aligner as a build task.
5. Floors declared before any run.
6. The pack surface's fourth twin.
7. The handoff gate's lower bound only.

## Open / next

1. **First commit and the new remote**, operator-run.
2. **Rule on the seven pending decisions.**
3. **Dry run the consolidated plan**, and record it in the plan.
4. **Day-0 inputs:**
   - both AWS profiles;
   - the VANTAGE gold export as of the run's date (JSON lines, including `form` for the filing selection);
   - a headless Chromium image pinned by digest;
   - an EDGAR `User-Agent` with a contact;
   - the permission rulings on `eks:*`, `tag:GetResources` and `elasticloadbalancing:Describe*`.
5. **The bake-off**, if it proceeds: its revision section gives the new prerequisite chain.
