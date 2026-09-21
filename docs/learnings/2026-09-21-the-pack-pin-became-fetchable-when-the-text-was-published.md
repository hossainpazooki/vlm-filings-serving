# The pinned conformance pack became fetchable and checkable when the governing text was published

ts: 2026-09-21T19:44:00Z
commit: none (this repository has no commits yet; the tree is the one described in docs/handoff/2026-09-21-history-reset-and-the-wording-ruling.md)
session: 2026-09-21 pick-up and reset session
status: verified
fact: The governing text's repository was made public on or before this date, and
  the commit the build plan pins for the conformance pack is an ancestor of that
  repository's default branch, its continuous-integration run concluded success,
  and a `git archive` at that commit yields 75 files under the pack directory —
  the same count Task 1.5a Step 1 recorded when it was measured on 2026-09-15.
  Task 1.5a's single operator input is therefore satisfiable without any further
  input from the operator. Before publication it was not checkable from here at
  all. The pinned commit is named only in the git-excluded build plan; no tracked
  file carries it, which is why the command below derives it rather than quoting
  it.
basis: with the pin read out of the local plan,
  `gh api repos/<text>/actions/runs` filtered to that head commit printed
  `success`; `gh api repos/<text>/compare/<pin>...main -q '.status'` printed
  `ahead`, meaning the default branch is ahead of the pin and the pin is
  reachable; and `git archive <pin> conformance schema/...` piped to `tar -t`
  yielded 83 entries, of which 7 are directories and 75 are files under the pack
  directory. Re-captured at curation: the finding landed earlier in the same
  session, against the same tree, and was not stamped when it landed.
re-verify: gh api repos/hossainpazooki/datum/compare/$(grep -oE '\b[0-9a-f]{40}\b' docs/plans/2026-09-18-build.md | head -1)...main -q '.status'
