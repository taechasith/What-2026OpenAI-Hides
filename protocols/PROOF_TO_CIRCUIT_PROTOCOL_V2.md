# Proof-to-Circuit protocol, Version 2

**Registered:** 2026-10-12 (Asia/Bangkok)  
**Status:** frozen before any Version 2 derived-data run  
**Branch:** `research/v2-proof-to-circuit`

## Scope and evidence boundary

Version 2 tests whether reproducibly extracted public proof structure can
generate *pre-registered predictions* for causal interventions in separately
specified inspectable open-weight models. The public `openai/math` corpus is
evidence about released documents only. It supplies neither model weights nor
internal activations and cannot identify a mechanism in an unreleased OpenAI
model.

The corpus snapshot is the immutable upstream commit
`fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`. Original Version 1 outputs remain
historical baselines and are not overwritten.

## Research questions

- **RQ1:** Which explicit proof references and cautiously inferred proof motifs
  recur across the corpus after family-aware accounting?
- **RQ2:** Which source-derived transformations can be placed in a formal
  counterfactual benchmark with an explicit verification tier?
- **RQ3:** Do pre-specified proof-structure features predict held-out causal
  intervention effects better than equal-information text, metadata, and
  shuffled-structure baselines in an inspectable model?
- **RQ4:** Are any such effects stable to corruption, seed, and intervention
  choices?
- **RQ5:** Which limits prevent any attribution from public artifacts to an
  unreleased OpenAI model?

## Analytical units and splits

The extraction unit is a source statement or proof-like segment with immutable
blob provenance. Corpus summaries use result family as the independent unit.
Counterfactual and intervention analyses, if admitted, split by result family
before feature development. Near-duplicate variants, source paths from the
same family, and all tasks based on one theorem remain in the same partition.

The first Version 2 run is **exploratory extraction only**. It cannot be
relabeled confirmatory. A later confirmatory run is permitted only after the
confirmatory analysis plan below is frozen and Gates G1--G4 have passed.

## Extraction design

`src/oai_math_study/v2_proof_extraction.py` will read immutable Git blobs,
not an incomplete Windows checkout. It will emit one record for each source
file and deterministic candidate statement/proof segment.

Graph A contains only explicit edges: TeX cross-references and formal
declaration/reference syntax. Such edges are labelled `explicit_source_ref`,
are not mathematical entailment claims, and retain source path, blob id and
line span.

Graph B contains deterministic, lexically inferred candidate motifs (for
example `contradiction`, `induction`, `case_split`, `construction`,
`reduction`, `invariant`, and `limit`). They are labelled inferred, carry the
matching rule and confidence `rule_based_unvalidated`, and must never be
reported as verified dependency edges.

## Gates and stopping rules

- **G1 corpus integrity:** upstream commit and Git object database verify; all
  output rows retain immutable provenance.
- **G2 structural validity:** output schema passes, explicit and inferred
  edges remain separated, and a documented audit reports duplicate/path,
  parsing, and denominator checks.
- **G3 benchmark validity:** each case has a verified truth condition and a
  verification tier. Cases without this are excluded from causal evaluation.
- **G4 behavioral competence:** an open-weight model reaches the pre-set task
  accuracy threshold on held-out clean tasks. The threshold, selected model,
  revision, prompt template and scorer must be written to the confirmatory
  plan before measuring intervention outcomes.
- **G5--G7:** predictive value, causal evaluation, and robustness are not
  entered unless G1--G4 pass.

Failure of a gate is a reported result. It is not repaired by changing the
model, test set, metric, or inclusion criteria after seeing the failed outcome.

## Infrastructure status at registration

The registered execution environment has CPU-only PyTorch and no local model
cache. Lean/Lake were not detected. Therefore no task is labelled
kernel-checked unless an actual checker run and log are produced. No paid API,
cloud endpoint, or model download requiring credentials is authorized by this
protocol.

## Claim constraints

Activation patching, if run, establishes an intervention effect for the named
inspectable model and task under the recorded implementation. A single-site
effect alone does not establish necessity, sufficiency, uniqueness, a complete
circuit, or a mechanism in an OpenAI model.
