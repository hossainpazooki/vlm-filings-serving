# vlm-filings-serving

Rendered SEC filings to page tensors to a served vision-language model, with
every number behind a gate that has been seen to fail.

**State: design only.** No pipeline code, gates, or infrastructure exist in
this repository yet. The design is `docs/design.md`; the gate discipline
every document here refers to is restated in `docs/discipline.md`; dated
state and open items are in `docs/handoff/`.

## What it measures

One pipeline of four stages, each reading one manifest and writing one.
fetch moves staged filing PDFs from object storage to local disk. decode
rasterises every page at a declared resolution and classifies the run as
I/O-bound or decode-bound. pack resizes each page into the model's pixel
bounds. serve runs a small vision-language model under vLLM over a fixed set
of questions: one filing's statement pages first and the question last, so
the document is the cacheable prefix.

The serve sweep prices that prefix cache three ways: shared, isolated
between requests, and evicted under a capacity limit. It prices the handoff
of a declared fraction of questions to a larger model. It scores every
extracted figure for agreement with the structured data the same filer
submitted.

## Scope walls

- Claims are rows. Nothing in this README carries a count or a status. Until
  a STATUS.md exists, nothing is claimable.
- A gate is credited only when its live cell is GREEN and its twin, the same
  input with one planted defect, is RED for exactly the planted reason.
- Floors are authored numbers, each naming its source and declared before
  the run it judges. A run on an instance type with no floor is UNEVALUABLE,
  not FAIL. No floor is set from a run's own numbers.
- Every stage reads one manifest and writes one manifest and never touches
  another stage's files.
- Rows from runs that cannot be regenerated are committed and hash-bound;
  the hand-copy seam is otherwise unverified and is said to be.
- Corrections to dated records are appended in place, never erased.
- Agreement, not accuracy: extracted figures are compared with data the
  filer also authored, so the rate measures agreement between two filer
  surfaces and nothing wider.
- Nothing about compliance, cache transfer between models, or routing
  quality. Nothing about multi-region, scale beyond the measured corpus, or
  training. No production claim.

## Discipline

This repository follows DATUM, a public governing text, restated for this
tree in `docs/discipline.md`. Where the design stands against each named
rule, before any code:

| rule | design | code |
|---|---|---|
| rows-not-sentences | carried | none yet |
| three-outcomes | carried | none yet |
| twin-red-as-planted | carried; fixture twins in CI, runtime twins on the rented instance only | none yet |
| checker-controls | carried; the aligner ships with its own controls too | none yet |
| derived-status | carried | none yet |
| identity-triple | carried | none yet |
| pushed-sha | carried | none yet |
| hand-copy-seam | carried; binding file named | none yet |
| probe-the-effect | carried; teardown inventory by tag, run twice | none yet |
| floor-provenance | partial: floors are declared with a derivation, and none yet has a cited prior figure | none yet |
| scope-walls-first | this README | |
| corrections-in-place | carried | |

Every cell is authored. The shared checker that accompanies the governing
text is vendored under `gates/conformance/` before the first row is
emitted. Once CI runs, the `code` column names what refuses each rule: the
vendored shared checker, this repository's checker, or none yet.

## Where things are

`docs/design.md` the design; revised in place with a change log.
`docs/discipline.md` the rules and the verdict row, self-contained.
`docs/handoff/` dated briefs, newest first in `HANDOFF.md`.
`docs/learnings/` one verified fact per dated file, indexed in `LEARNINGS.md`.
