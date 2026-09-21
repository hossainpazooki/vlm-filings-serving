# The wording gate reads the tracked tree, never this repository's history

ts: 2026-09-21T19:44:00Z
commit: none (this repository has no commits yet; the tree is the one described in docs/handoff/2026-09-21-history-reset-and-the-wording-ruling.md)
session: 2026-09-21 pick-up and reset session
status: refuted-assumption
fact: The public wording gate's input is the tracked working tree, not the commit
  history. Its task specification defines `tracked(root)` as "`git ls-files` of
  tracked files and untracked files git does not ignore: what a commit from this
  tree can carry", and nothing in the build plan reads this repository's history
  at all. A document that was committed once and later deleted from the tree
  therefore cannot fail this gate, however it is worded. The assumption this
  refutes, held earlier the same day, was that wording violations surviving in
  old commits would be caught by the gate and had to be removed by replacing the
  history. They would not have been. Replacing the history was a presentational
  choice about a repository that changed corpus, not a gate requirement. The
  live wording problem was in the tree, not the history.
basis: `grep -o 'tracked(root) -> list\[str\][^;]*' docs/plans/2026-09-18-build.md`
  printed the definition quoted above, and
  `grep -cE 'git log|rev-list|fetch-depth' docs/plans/2026-09-18-build.md`
  printed `0`. Re-captured at curation: the finding landed earlier in the same
  session, against the same tree, and was not stamped when it landed.
re-verify: awk '/git log|rev-list|fetch-depth/{n++} END{print n+0}' docs/plans/2026-09-18-build.md
