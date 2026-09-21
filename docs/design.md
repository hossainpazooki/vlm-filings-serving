# vlm-filings-serving design

Date: 2026-09-15. Revised 2026-09-18; see Changes at the end.
Status: Proposed. Nothing in this document is a claim until a verdict on a pushed SHA backs it.
Codename: traverse. Repository: hossainpazooki/vlm-filings-serving.
Discipline: this design follows DATUM, a public governing text; the rules it assumes are restated by name in docs/discipline.md.

Seven decisions below are marked *(pending review)*. The build plan introduced them on 2026-09-15 and they await the author's ruling; Open items lists them.

## Purpose

A single repository that turns rendered SEC filings into page tensors, measures where the pipeline stalls, serves a small vision-language model over the result for a many-questions-per-document workload, prices the handoff to a larger model at declared escalation rates, and owns the latency, cost, cache and agreement numbers. It exists to answer one question a serving-platform reader will ask: can this person move from object storage throughput to page decode to serving in one week, show numbers rather than describe them, and show what those numbers are worth when the model is wrong.

The reader is a serving-platform or ML-platform reader at a financial institution. Escalation triage (alert adjudication, screening, surveillance review) is a workload in which the handoff rate is a parameter the institution already tracks, rather than something to be discovered from traces. That is the one point at which this repository cites the KV-transfer research program, and it borrows no result from it. The specific target posting is a day-0 decision (Open items); until it is named, this paragraph defines the reader by function. It is not a compliance repository. It uses a compliance-adjacent corpus because that corpus supplies free structured ground truth and a genuine shared-prefix workload, not because the repository makes any compliance claim.

## Why this corpus

An earlier version of this pipeline served gameplay video. Only one stage and the corpus were domain-bound. The stage contract, the verdict emitter, the twin rule, floors with provenance, the generated STATUS block, both lanes, the wall-clock kill switch, the tag-scoped teardown probe and the Terraform identity split do not know what the bytes are, and they carried over unchanged.

Four things follow from filings that video could not supply, and they are the reason for the corpus rather than its theme:

1. The serving sweep gains an agreement axis against filer-submitted structured data. Without it the int4 row says only cheaper and faster, which is true by construction. With it the row is a cost-versus-agreement trade.
2. The prefix-cache cell stops being a predicted zero. The served workload is many questions over one document, and the document is the shared prefix, so the hit rate on the document portion is the measured lever and a cache miss is the recompute cost, stated on the same currency the KV-transfer research program uses.
3. Cache isolation becomes a measured cost. Sharing a prefix cache across tenants is a timing side channel; the cost of not sharing has no gameplay analogue.
4. An escalation pipeline (a small model clears the bulk, a large model adjudicates a declared fraction over the same documents) prices the recompute floor at a model handoff and shows that the floor is paid per document escalated, not per question.

A page-framing-only change was considered and rejected. It would have left both the predicted-zero cache cell and the unanchored int4 row in place.

## Decisions taken

GPU budget is a few rented hours on AWS. Infrastructure is Terraform in one region. Timeline is three days plus a full day 0 (Schedule). Both lanes are attempted; the second lane carries a wall-clock kill switch. Serving target is Qwen2-VL-2B under vLLM, joined by Qwen2-VL-7B-Instruct fp16 as the adjudicator in the handoff sub-matrix. The two share a family and a processor, so the request set is byte-identical across models and visual-token totals are comparable. The two models run sequentially on the same instance, never co-resident; co-residency cost is out of scope and the row says so.

Corpus is SEC EDGAR 10-K and 10-Q filings for filers inside the VANTAGE gold scope, so that structured ground truth exists for every admitted document. Each filing contributes its primary document and the SEC's rendered financial-statement report pages. Target size after rasterisation is 50 to 200 GB. EDGAR is a public record; the fetch verdict's dataset_licence records that and the retrieval terms (fair-access rate limit, declared User-Agent). Synthetic scaling is held behind a gate and opens only if the real corpus proves decode-bound; the synthetic lane duplicates staged documents under new keys and tests throughput, never content.

Corpus preparation is outside the timed runs. EDGAR primary documents and report pages are HTML. On day 0 they are rendered to PDF once with a headless browser pinned by container digest at a fixed viewport, and the PDFs are staged into S3 with checksums and an index carrying each object's accession number, filer id, form, acceptance instant and page role. The timed pipeline begins at S3. The browser render is where nondeterminism would enter, and it is kept out of every gated stage by construction.

Rasterisation is pinned. decode uses one pinned PDF rasteriser at a fixed DPI per declared bucket, and the rasteriser's version and the container digest are recorded. A determinism check re-rasterises a sample and compares content hashes (Gates).

The served document is the filing's financial-statement report pages, at most eight of them, not the primary document. The primary document is fetched, rasterised and packed as throughput corpus and is not served. This keeps a request inside the model's context and makes every request's document a comparable prefix.

The serve workload is one request set, fixed before any run and used identically by every sweep cell. Each request is one document's pages followed by one question. The question set is fixed and small, one question per target tag over a restricted tag set, so the extraction case is a subset of the many-questions-per-document case rather than a second workload. Pages come first and the question last, so the document is the cacheable prefix. Decoding is greedy at temperature zero.

Agreement, not accuracy. Extracted figures are compared with the XBRL facts the same filer submitted, as held in VANTAGE gold keyed by accession number. Both surfaces are filer-authored, so the comparison measures agreement between them, and the word accuracy does not appear in any row, table or page.

The sweep matrix is declared as three sub-matrices before any cell runs: core, handoff and extended. Core is fp16 across max_num_seqs {1, 8} and cache mode {isolated, shared, shared-evicting}: six cells. Handoff is fp16, max_num_seqs 8, shared, across selection policy {random, clustered} and escalation rate {0.1, 0.3}, plus the large-only cell: five cells. Extended is the six core cells under int4. They run in the fixed order core, handoff, extended. The split exists so that a day-1 overrun leaves the earlier sub-matrices claimable and only the later ones UNEVALUABLE.

Escalation is a declared policy, never a learned router: a seeded selection of the fixed request set at the declared rate, drawn uniformly over questions (random) or over whole documents until the rate is met (clustered). Nothing about a handoff transfers cache between models. Per the KV-transfer research program's record, the small model's cache is treated as worthless to the large one, and the large model pays full prefill on first contact with each escalated document. That is the assumption the cell prices; it is cited, not re-measured.

VANTAGE gold is read from a pinned local export keyed by accession number, with the export's row count, content hash and as-of instant recorded in the serve row's params. No code dependency on the PARALLAX reader is taken (Open items). *(pending review)* The export's as-of equals the run's asof_date: gold is point-in-time, and a fact restated after the as-of would otherwise be compared against a page rendered before it.

## Shape

Five stage containers, one driver, one ledger.

fetch pulls staged PDFs from S3 to the local data volume. It is the network I/O stage and emits bytes per second and per-object latency. The fetch manifest carries, per object, the accession number, filer id, form, the SEC acceptance instant with an explicit UTC offset, the page role (primary or statement), and the object checksum.

decode rasterises every page of every admitted document at the DPI declared for its bucket with the pinned rasteriser. It emits pages per second, CPU utilisation, read-wait time and per-document page counts. The I/O-bound versus decode-bound classification is made here: I/O-bound if read wait exceeds half of stage wall time, else decode-bound. decode also re-rasterises a fixed sample of its own pages and records how many content hashes matched; the pack-shape gate credits that record. Because fetch moves PDFs while decode expands them into pages, the classification is expected to land decode-bound; it is reported, not claimed as a finding.

pack resizes each page into the model processor's pixel bounds and writes one page per file. Shapes vary per page. The manifest records each page's shape, dtype, visual-token count and content hash, plus the rasteriser version and the container image digest once. Normalisation to float is deferred to serve; the page on disk is what a reader can hash.

serve runs vLLM over the fixed request set for every cell in the declared matrix. It emits, per cell: p50 and p95 latency per question, tokens per second, GPU utilisation, block-level prefix-cache hit rate, cost per million visual tokens and cost per thousand questions of the stated request set (both computed from the on-demand price recorded at run time), the agreement rate (Gates), and every output text, so the correctness control can compare cells. *(pending review)* The hit rate is the server's overall block-level rate over the cell, read as a counter delta. The question is a few dozen tokens against pages of hundreds, so it is an upper bound on the document-portion rate, and the row names it as that.

The three cache modes:
- isolated gives every request its own salt, so no prefix is shared between requests;
- shared issues each document's first question alone and the rest concurrently, so a document's questions share its prefix within capacity;
- shared-evicting issues the same requests interleaved across documents against a server whose KV capacity is overridden below the documents' total prefix, so the eviction path is exercised.

On one request set, the three modes give the isolation cost and the recompute floor. For each handoff cell, serve runs the small model over the whole request set, then the large model over the escalated subset with the same ordering. It emits the pipeline's cost per thousand questions, the large model's hit rate on the subset, the count of distinct documents escalated, and the agreement rate on the subset under each model.

driver chains the stages by S3 prefix and calls the gates. gates holds deterministic checks over verdict rows, each with a twin that must fail for exactly the planted reason, and the ledger checker, which ships with its own positive and negative controls (fixture rows that must pass, fixture rows that must each fail for a named reason) run in CI before anything is built. infra holds Terraform for the VM lane and the EKS lane. STATUS.md holds a hand-written dated record and a generated claimability block between markers. scripts/build_status.py derives the block from verdict rows, and its --check mode re-renders it and fails the build on any difference.

Every stage reads a manifest, writes a manifest, and never touches another stage's files. That boundary is the Kubernetes contract, present from the first local run.

## Verdict rows

One JSON file per stage per cell. The row is the shared verdict row restated in docs/discipline.md. It carries a versioned schema identifier and refuses additional top-level properties, so everything specific to this repository lives under `params` and `metrics`.

    schema              versioned schema identifier, fixed in traverse/verdict.py
    kind                GATE_VERDICT
    surface             fetch | admission | decode | pack | serve | serve-regression |
                        serve-cache-correctness | serve-cache-economics | serve-agreement |
                        serve-handoff | lane-parity | teardown | cost-backfill
    lane                1 (VM) | 2 (EKS)
    cell                live | twin
    result              GREEN | RED | UNEVALUABLE
    unevaluable_reason  required when UNEVALUABLE, forbidden otherwise
    checks              { check_name: violation_count }, at least one key
    evaluated           { check_name: items_evaluated }, same keys; a zero forces UNEVALUABLE
    planted             twin only: { mutation, mutated_rows, expected_violations }
    scope               what subset, in words
    params              run_id, instance_type, region, price_per_hour_used, dataset_revision,
                        dataset_licence, floors applied, asof_date, dpi_bucket,
                        rasteriser_version, render_digest, quant, max_num_seqs, cache_mode,
                        request_set_sha, gold_table_rows, gold_sha256, gold_asof, tag_set,
                        large_model, escalation_rate, selection_policy, selection_seed
    metrics             stage specific, plus input_manifest_sha, output_manifest_sha, wall_s,
                        bytes_in, bytes_out, items; serve adds pages, visual_tokens_total,
                        hit_rate, cost_per_m_visual_tokens, cost_per_k_questions,
                        agreement_rate, aligned_items, unaligned_items, docs_escalated,
                        questions_escalated, cost_per_k_questions_pipeline,
                        pipeline_over_large_only, large_hit_rate,
                        agreement_rate_small_escalated, agreement_rate_large_escalated
    content_hash        sha256 of the stage's output manifest
    content_hash_basis  what bytes, what canonical order
    gate_sha            commit of the emitter
    gate_worktree       clean | dirty; a dirty row fails this repository's checker
    ran_at              UTC, Z suffix
    runner              local | ci | <instance_type>

Rows that CI can regenerate (the synthetic-filings lane) are build output under gates/out/ and are not committed. Rows from runs that cannot be regenerated (anything on a rented instance) are committed under runs/<run_id>/verdicts/, with a runs/<run_id>/SOURCE.md that binds every file to its sha256 over LF-normalised bytes and records the replay command. The checker recomputes every hash and fails on any unbound, missing or altered file. The hand-copy seam is otherwise unverified and is said to be.

## Gates

fetch-throughput: sustained S3-to-disk throughput above the floor for the instance type. Fixture twin: a throttled throughput figure. Runtime twin: a tc-throttled run. The local floor is a smoke floor. Staged PDFs are small, so the g5 floor bounds a smaller transfer than video would, and the row's scope says so.

admission-asof (manifest level): for a run declared with an asof_date, every object in the fetch manifest was accepted at or before that date. *(pending review)* The boundary is 23:59:59 of asof_date in America/New_York, the acceptance clock's zone. Check: future_accepted. Fixture twin: one filing accepted after the date. This is an admission gate on the data plane, not a serving gate. It says the served corpus is as-of consistent at the declared date and nothing more.

decode-bottleneck: classifies the run as I/O-bound or decode-bound by the rule in Shape. This is a classification, not a pass; the check is that the recorded classification agrees with a recomputation from the raw timings. Fixture twin: a misclassified row. Runtime twin: a cgroup io.max run that must classify I/O-bound. The synthetic-scaling lane opens only on decode-bound. Pages per second is recorded per DPI bucket as a descriptive metric.

pack-shape: every page matches its declared dtype and lies inside the declared pixel bounds on a multiple of the patch factor; the page count equals the decode page count; the decode stage's re-rasterised sample matched hash for hash; the container image digest is recorded. Checks: shape_mismatch, count_mismatch, determinism_mismatch, image_digest_recorded. Fixture twins: one truncated page (sets the first two), one perturbed sample hash (sets the third), one blanked digest (sets the fourth). *(pending review)* The fourth twin is kept because a check no twin has made fail is not credited.

serve-sweep-complete: one check per declared sub-matrix: core_incomplete, handoff_incomplete, extended_incomplete. A hole makes the sweep row RED, so its twin can be shown red as planted. The gates that depend on a complete sub-matrix are UNEVALUABLE until it is complete: a missing core cell leaves the regression and cache-economics gates with nothing to evaluate, and a missing handoff or extended cell makes only the gates over that sub-matrix UNEVALUABLE. Fixture twins: one hole per declared sub-matrix.

serve-regression: for each quant and cache mode, the max_num_seqs=1 cell must be worse than the max_num_seqs=8 cell on cost per million visual tokens, by the margin declared in floors.json and over the identical request set. The unit is per visual token because requests are not comparable per request once page density varies. Check: regression_margin. Fixture twin: equal costs.

serve-cache-correctness: *(pending review)* at max_num_seqs 1, for every request in the set, the output under shared and under shared-evicting must equal the output under isolated, token for token, per quant. Check: output_mismatch. Fixture twin: one perturbed output. This gate is not optional: a hit-rate number with no output-identity check is a vacuous probe. The max_num_seqs 8 cells are not compared token for token. Kernel batch composition is not invariant, and an argmax flip there is not a cache defect. Their per-cell agreement rates are reported and floored by serve-agreement, and the page compares them across batch sizes; no gate does.

serve-cache-economics: in shared mode the block-level hit rate must be at or above the floor, and the shared-evicting cell must show a lower hit rate and a higher cost per thousand questions than the shared cell, per quant and max_num_seqs. Checks: hit_rate_below_floor, evicting_not_worse. Fixture twins: the shared hit rate collapsed; evicting equal to shared. UNEVALUABLE when the server exposes no prefix-cache counters.

serve-agreement: extracted figures are aligned to gold facts by (accession number, tag, period end date, quarters), normalised by the statement's stated scale, USD only, and compared at value level. Each cell's agreement rate must be at or above the floor. Checks: value_mismatch, unaligned. Fixture twins: a gold copy with planted wrong values; one extracted item with no gold fact. *(pending review)* The aligner ships with its own positive and negative controls, a hand-verified fixture of documents and tags on which alignment is known, that must score fully and must drop for exactly the planted reasons on a mismatch copy. It is a CI-reproducible build task, not a day-0 chore, in the pattern of the ledger checker's controls. A low agreement rate on a document outside the controls may be the filer's inconsistency rather than the model's; the row reports the rate, and the page says which of the two it cannot distinguish.

serve-handoff-economics (surface serve-handoff): at equal escalation rate, the clustered cell's pipeline cost per thousand questions must be below the random cell's by at least the margin in floors.json, and no pipeline cost may fall below the small-only cost. Checks: clustering_no_saving, pipeline_below_small_only. Fixture twins: clustered cost equal to random; one pipeline cost planted below small-only. *(pending review)* The pipeline cost is not required to stay below the large-only cost. When prefill dominates, random escalation at 0.3 touches most documents and can cost more than sending everything to the large model; that is a finding, reported as the descriptive ratio pipeline_over_large_only, not a defect. The agreement uplift on escalated items is reported, descriptive and without a floor: with the escalated count in the low hundreds it is not a claim.

lane-parity: EKS numbers within declared tolerance of the VM lane for the shared core cells. Twin: the EKS figures planted thirty percent off the VM's. Explicit outcome UNEVALUABLE with unevaluable_reason quota-not-granted.

teardown: after destroy, an inventory script lists every resource by repository tag across EC2, EBS, EKS, ELB, ECR, S3, IAM and Cost Explorer, and passes only on an empty result. Terraform state is an index, not a decision. UNEVALUABLE until all run verdicts are on a pushed SHA.

cost-backfill: actual billed cost from Cost Explorer, UNEVALUABLE until the data lands, then a dated row. A billed cost is a fact, not a threshold, so no twin can make it fail and the surface derives PARTIAL by design.

A gate that has never gone red is not a gate. Twins are written before the stage they test passes.

There are two kinds of twin, and both are rows. A fixture twin plants one defect into a copy of the metrics and runs in CI on every push. A runtime twin needs the rented instance and Linux, runs once per lane, and is committed under runs/ like any unrepeatable row. A surface is CLAIMABLE only when its live cell is GREEN, every twin cell is RED for exactly the planted reason (compared key for key over the union of both key sets), and every check the live cell reports has been set nonzero by some twin. Four cases are refused by the checker rather than derived into a status: a twin that comes back GREEN, a twin RED for a different reason, a live cell that comes back RED, and two twins planting the same mutation. A real surface failing, or a plant the gate missed, needs a human. A twin over a live cell that was UNEVALUABLE is UNEVALUABLE with the same reason; a gate that could not evaluate cannot be shown red.

Surface status vocabulary, derived and never typed:
- CLAIMABLE;
- PARTIAL when a cell kind is absent or a live check has not been seen to fail;
- UNCLAIMED when there are no rows;
- UNEVALUABLE when any present row is, decided before any check is credited.

Any of these strings found inside a row fails the checker.

## Floors

Floors and tolerances live in gates/floors.json. They are keyed by instance type and, where the unit needs it, by DPI bucket. Every entry carries a source string saying where the number came from. A run on an instance type with no floor is UNEVALUABLE, not FAIL. *(pending review)* Every floor is declared before any run with its derivation, and none is set from a run's own numbers. The fetch floor on g5.xlarge is a declared fraction of the provisioned volume throughput, with that volume's documentation cited. The hit-rate floor is derived from the request set's shape. The agreement, clustering and regression margins are chosen numbers, and their sources say so. None of them yet has a cited prior figure, and each is replaced when one exists.

## Ledger and status

STATUS.md is one file with two parts. The dated narrative record is hand-written and corrected in place with a date, never erased. The claimability table is generated between the markers `<!-- traverse:status:begin -->` and `<!-- traverse:status:end -->` from the rows under gates/out/ and every runs/<run_id>/verdicts/. scripts/build_status.py --check re-renders the block and fails CI if the committed block differs. Nothing outside the block is checked by the builder; nothing inside it is typed by hand.

The README states the scope walls before any code and defers every count to STATUS.md. It carries a Discipline section: a table of the named rules that says, for each, whether the vendored shared checker, this repository's checker, or neither refuses it on the last CI run. A cell naming neither is authored and says so.

Two checkers derive status: the shared conformance checker vendored under gates/conformance/ and pinned file by file to one pushed commit of the governing text, and this repository's gates/ledger.py. The build fails when their derived statuses, or the unfalsified checks they name, disagree. Two refusals belong to this repository alone, and the shared checker accepts both rows: a row from a dirty worktree, and a row from a rented runner that lacks its run parameters.

## Infrastructure

Tagging is the spine. Every resource carries repo, run_id and lane, and the repo tag is vlm-filings-serving. The teardown inventory queries by these tags only.

VM lane:
- one g5.xlarge in us-east-1 from a pinned Deep Learning AMI, with the driver preinstalled;
- a gp3 root volume plus a separate gp3 data volume, IOPS and throughput set in variables;
- an S3 bucket inside the module, with force_destroy and a seven-day lifecycle rule;
- an instance role scoped to the bucket prefix;
- SSM Session Manager, no SSH ingress, no static credentials anywhere;
- the three models' weights pulled in the instance's user data, so day 1 does not wait on them.

The 7B model in fp16 leaves roughly 6 GB of KV cache on a 24 GB card, so few documents stay resident; that is why the handoff rate axis stops at 0.3.

EKS lane:
- a cluster with one managed GPU node group (g5.xlarge, min 0, max 1) and one small CPU node group;
- the NVIDIA device plugin;
- stages as Jobs with ttlSecondsAfterFinished, chained by S3 prefix;
- serving as a Deployment with an HPA on GPU utilisation from the DCGM exporter;
- images in ECR, pinned by digest in the manifests.

The EKS lane runs the core sub-matrix only, against the deployed quant.

Teardown for both lanes: push verdicts, destroy, inventory, commit the teardown verdict. A second inventory pass on day 3 catches stragglers.

## Schedule

Day 0, a full day:
- g5 quota request for the VM and the node group, and the ECR repositories;
- name the target posting (Open items);
- select the filer set inside VANTAGE gold scope and export gold as of the run's as-of date, recording rows and hash;
- render and stage the corpus into S3 under the fair-access limit, unattended, with checksums and the index;
- pin the rasteriser and the render image, and record their digests;
- fix the request set and the tag set, and record request_set_sha;
- confirm the vLLM build honours per-request cache salting: two differently salted requests over one document must not hit.

Day 1, VM lane:
- morning: the local pipeline on 20 to 50 GB, with fetch, admission, decode, pack and their twins;
- afternoon: VM apply, region-local pull of 100 to 200 GB, pipeline rerun and bottleneck classification;
- evening: the sweep in its fixed order (core fp16 first, then handoff, then extended int4), with the correctness control and agreement scoring run per cell as it completes; then push, destroy, inventory. GPU off before sleep.

If the evening runs long, extended is what does not run; the per-sub-matrix split in serve-sweep-complete is what makes that survivable. Halt-gate for the EKS lane: lane one green and quota granted.

Day 2, EKS lane:
- morning: cluster apply, node group, device plugin, images by digest;
- afternoon: Jobs, Deployment, HPA, the core sweep, lane-parity;
- evening: push, destroy, inventory.

Kill switch at 22:00 regardless of state: destroy, record the blocker, ship manifests as UNCLAIMED.

Day 3, evidence and writing:
- fresh-clone reproduction on CPU of the day-1 verdicts, including the aligner controls and the cache-correctness comparison over committed outputs;
- report, and the STATUS.md block from verdicts;
- cost backfill if landed, and the second inventory pass.

## Claim ceiling

After day 3 the repository may claim:
- pipeline throughput and I/O classification on one instance type and one disk configuration, over one corpus at the declared DPI buckets;
- serving latency and cost per million visual tokens for one model on one GPU across the core matrix, and across the extended matrix only if it completed;
- prefix-cache hit rate and its cost delta, under isolation and under eviction, on the stated request set;
- the cost of a model handoff on the stated request set, for one model pair at declared escalation rates and two selection policies, run sequentially on one GPU;
- an agreement rate between the model's extracted figures and filer-submitted XBRL, over the restricted tag set on the stated sample;
- as-of admission of the served corpus at the declared date;
- API-verified teardown of every provisioned resource.

The EKS row is claimable only if lane-parity passed before the kill switch.

Nothing about compliance. Nothing about accuracy in any sense wider than the agreement rate as defined. Nothing about cache transfer between models. Nothing about routing quality: the escalation selector is a seeded draw, not a policy anyone would deploy. Nothing about co-residency. Nothing about production tenancy or barriers beyond the measured isolation cost. Nothing about multi-region, scale beyond the measured corpus, or training.

## Risks

Day 1 evening is the overloaded slot: seventeen cells across two models, plus a correctness control and agreement scoring. The sub-matrix split and the fixed cell order are the mitigation. The kill switch is not, because it belongs to day 2.

The browser render is deterministic only under a pinned digest and a fixed viewport, and it sits outside every gate. That is stated rather than solved. The rasteriser is inside a gate.

The aligner is a new surface, and loose alignment would inflate agreement silently. Its controls are the mitigation, and they bound what the aligner is shown to do to the hand-verified set.

Prefix caching over multimodal inputs keys blocks by an image hash, and there is at least one public report of incorrect outputs under concurrency on a related model. The correctness control is mandatory for that reason, and is justified on principle regardless of that report's current status. It is defined at max_num_seqs 1 because batched kernels are not invariant: a token flip at 8 is not evidence of a cache defect and would read as one.

XBRL and the rendered statement can disagree because the filer made them disagree. The agreement rate reports that as what it is.

The recompute-floor framing of the handoff is honest only because the row says the small model's cache was not tried for transfer. The research program's finding is the reason; it is cited, not restated as this repository's result.

Staging under the fair-access limit is slow and belongs to day 0, not to any timed run. Quota latency and vLLM image pull time remain the two items most likely to consume day 2, and both are outside the author's control.

## Open items

The seven decisions marked *(pending review)*, each introduced by the build plan on 2026-09-15:
1. correctness identity at max_num_seqs 1 only;
2. gold as-of equal to asof_date, with the boundary in America/New_York;
3. the hit rate as the overall counter delta, named as an upper bound on the document portion;
4. the aligner and its controls as a build task;
5. floors declared before any run, never set from one;
6. the pack surface's fourth twin;
7. the handoff gate's lower bound only.

Name the target posting. Until it is named, the Purpose paragraph defines the reader by function; the sentence is revised in place with a date when the posting is chosen.

Whether the extended matrix survives day 1, decided by the clock and recorded either way.

Whether to read VANTAGE gold through the PARALLAX reader contract instead of a pinned local export. Not taken now: a code dependency across repositories is outside three days.

Provenance for the g5.xlarge fetch floor beyond the declared fraction.

Whether to add a second VM run on local NVMe to show the classification flip.

Whether the retained-bucket alternative is preferable to force_destroy for readers who want to inspect raw manifests after teardown.

## Changes

This is a governing text for the repository, so it is revised in the body; this section names what changed and why.

2026-09-18, repository created fresh. The repository is new as hossainpazooki/vlm-filings-serving; the gameplay-era repository was deleted, and its documents are archived outside this repository. This design is now standalone. It previously revised the gameplay-era design in place, and it folds in the sections it had inherited: the driver and manifest-boundary paragraphs of Shape, the verdict row's field table, the twin and status-vocabulary paragraphs of Gates, Ledger and status, and Infrastructure. The design was reconciled with the build plan it drives in three places:
- serve-sweep-complete carries one check per declared sub-matrix and goes RED on a hole, with the dependent gates UNEVALUABLE; this replaces "a missing core cell makes the serve surface UNEVALUABLE";
- serve-handoff-economics checks the lower bound only;
- agreement across batch sizes is compared on the page, not gated.

2026-09-15, re-themed from gameplay video to rendered SEC filings, with a second model added as the adjudicator of a handoff sub-matrix. Purpose, Decisions taken, the four stage paragraphs of Shape, Verdict rows (surfaces, params and metrics), Gates, Floors, Schedule, Claim ceiling, Risks and Open items revised. serve-regression re-denominated per visual token. serve-cache-correctness, serve-cache-economics, serve-agreement, serve-handoff-economics and admission-asof added. pack-shape and serve-sweep-complete extended. The discipline, the twin rules, Ledger and status, and Infrastructure other than the tag value are unchanged from the gameplay-era design. That design's history (2026-09-05 to 2026-09-14) is kept with its archived record: its alignment with the governing text's first and second revisions, per-check crediting, and the decision to vendor the shared conformance checker.
