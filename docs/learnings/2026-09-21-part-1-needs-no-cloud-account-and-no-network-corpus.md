# Part 1 needs no cloud account, no filing-service access and no exported gold

ts: 2026-09-21T19:44:00Z
commit: none (this repository has no commits yet; the tree is the one described in docs/handoff/2026-09-21-history-reset-and-the-wording-ruling.md)
session: 2026-09-21 pick-up and reset session
status: verified
fact: Part 1 of the build plan, Tasks 1.1 through 1.13, carries no reference to a
  cloud SDK, an infrastructure apply, the filing service, or either named cloud
  profile. It runs over three committed synthetic filings. The only occurrences
  of cloud vocabulary anywhere in that range are a `.gitignore` line, an error
  message reserving a second source scheme for Part 2, and a directory skip-list
  — none of them a dependency. Part 1 declares exactly one operator input, the
  conformance pack's pinned commit. The consequence for scheduling: the absence
  of both cloud profiles, which is a standing blocker recorded since 2026-09-10,
  does not block any of Part 1. It blocks Parts 2 and 3 only.
basis: `awk 'NR>=94 && NR<=4292' docs/plans/2026-09-18-build.md | grep -cE
  'boto3|EDGAR|traverse-platform|traverse-provision'` printed `0`, and the same
  range piped to `grep -c 'Operator input'` printed `1`. Line range 94 to 4292 is
  Part 1, from its heading to the Part 1 self-review. Re-captured at curation:
  the finding landed earlier in the same session, against the same tree, and was
  not stamped when it landed.
re-verify: awk 'NR>=94 && NR<=4292 && /boto3|EDGAR|traverse-platform|traverse-provision/{n++} END{print n+0}' docs/plans/2026-09-18-build.md
