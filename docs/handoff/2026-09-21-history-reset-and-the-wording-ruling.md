# Handoff: history reset before the first commit; the wording rule's premise changed

2026-09-21. Two things happened to this repository before its first commit, and
both correct something the 2026-09-18 brief states. That brief is a dated record
and is not edited; this entry supersedes the parts named below and nothing else.

## What changed

- **The git history was replaced.** Until today the working tree sat on the
  gameplay-era repository's four commits, with `origin` still pointing at a
  repository the operator had deleted. The tree is now on an empty history:
  branch `main`, no commits, `origin` at this repository. The four commits were
  mirrored outside the workspace before the reset, and the gameplay-era
  documents were already archived outside this tree; nothing here depends on
  either.
  re-verify: `git log --oneline` reports that `main` has no commits yet, until
  the first commit is made. `git remote get-url origin` names this repository.

- **The governing text was published, and the wording rule's phrase changed with
  it.** The rule was written when the repository was public and the text it
  follows was not. That is no longer true. By operator ruling of this date the
  required phrase becomes "a public governing text"; the rest of the rule is
  unchanged — still named at most once per document, still no rule number, still
  no schema literal in prose, still no path or commit of it.
  re-verify: `for f in README.md docs/design.md docs/discipline.md; do grep -c
  "a public governing text" "$f"; done` prints `1` three times, and the same
  grep for the old wording prints `0` three times.

## What this supersedes in the 2026-09-18 brief

- Its first claim's re-verify line expects six documents and `.gitignore`. This
  entry is a seventh document, so after the first commit `git ls-files` lists
  seven and `.gitignore`, and nothing else. Until that commit it lists nothing.
- Its second re-verify line greps for the old phrase and now prints `0` three
  times. Use the line above instead.
- Its build-plan line records the plan's md5 before the ruling. The plan was
  amended today in four places to carry the new phrase and premise; its line
  count is unchanged at 9,227 and its md5 is now different. The plan remains
  git-excluded and local.
- Everything else in that brief stands, including the seven decisions still
  awaiting a ruling and the day-0 input list.

## Open / next

1. **Rule on the seven pending decisions**, listed under Open items in
   `docs/design.md`. The plan implements all seven; striking one means amending
   the plan before the dry run.
2. **Dry run the build plan**, and record it in the plan. It is still the gate
   before execution, and it is still empty.
3. **Day-0 inputs**, unchanged from the 2026-09-18 brief.
