# Research definition, Version 3

**Frozen:** 2026-10-12 (Asia/Bangkok), before Version 3 outcome files were generated.

## Target and boundary

The target is a bounded reconstruction of *observable source-structure signals*
in the pinned public `openai/math` release. It is not an attempt to identify
the producer model, its hidden reasoning, prompts, training data, weights, or
neural circuitry.

| Level | Operational criterion | Version 3 status rule |
| --- | --- | --- |
| A, artifact reconstruction | provenance-complete source records and deterministic extraction checks | pass only for records meeting the extractor schema |
| B, strategy reconstruction | an independently adjudicated or formal strategy label with reported reliability | not met by lexical motif labels |
| C, functional reconstruction | family-disjoint held-out prediction exceeds all frozen matched baselines with uncertainty | evaluated only for extraction labels, not mathematical strategies |
| D, causal computational validation | preregistered effects in an inspectable model that passes behavioral competence checks | blocked without an eligible model and task set |
| E, producer-model mechanism | authorized target-specific internal intervention evidence | out of scope and unavailable |

## Questions and competing hypotheses

The primary exploratory question is whether explicit-reference graph features
predict a withheld lexical motif indicator better than matched non-graph
metadata. H1 attributes recurrence to reusable strategies; H2 attributes it to
mathematical conventions; H3 to source/retrieval overlap; H4 to publication
pipeline regularities; and H5 to mixtures. The public corpus cannot generally
distinguish H1--H5. A predictive gain, if observed, is evidence only about
association in the released source structure.

## Frozen functional experiment

- Unit: extracted node, with family-disjoint groups; `unlinked` documents form
  their own groups.
- Primary label: the fixed lexical `induction` indicator already emitted by the
  Version 2 extractor.
- Features: node kind, within-document relative line position, document node
  count, and literal-reference in/out degrees. No source text, label terms, or
  document identifiers enter a model.
- Models: logistic regression with a metadata-only baseline and a
  degree-permuted structural control. No hyperparameter search.
- Split: deterministic group split, seed 20261012; 20% held-out groups.
- Outcomes: AUROC, average precision, and Brier score; 1,000 group bootstrap
  draws for AUROC differences.
- Failure: no positive held-out AUROC difference against both controls means
  no claim that graph features add predictive value.

## Gate ledger

G1 is inherited as PASS for source pinning. G2 is PARTIAL because literal
syntax is checked but motifs lack semantic adjudication. G3 is PARTIAL only
for finite, exact integer-arithmetic counterfactuals. G4--G6 are BLOCKED:
there is no eligible open-weight mathematical model, competence result, or
causal intervention. G7 is PARTIAL when alternative controls and the model
organism test have run. G8 is PARTIAL until an independent external rerun.
