# Confirmatory analysis plan, Version 2

**Registered:** 2026-10-12 (Asia/Bangkok)  
**Status:** inactive until Gates G1--G4 pass

## Primary hypothesis

**H1.** On held-out result families, a pre-registered proof-structure-informed
predictor ranks causal intervention effects more accurately than matched
text-only, metadata-only, and shuffled-structure predictors.

H1 is falsified if its primary held-out estimate is not larger than every
matched baseline under the pre-specified hierarchical uncertainty analysis.
A null result remains a valid Version 2 outcome.

## Preconditions

Before activation-patching outcomes are inspected, the repository must contain:

1. A G1/G2-passing corpus manifest and extraction audit.
2. A G3-passing counterfactual set with a source identifier, answer, formal or
   computational checker record, verification tier, and rejection log.
3. A pinned open-weight model revision, license record, prompt/tokenization
   manifest, hardware manifest, and a G4 behavioral-competence report.
4. A task-family-disjoint development/held-out partition created before model
   intervention scanning.

Without all four, this plan remains inactive and neither H1 nor a causal model
comparison may be reported as executed.

## Locked primary analysis once activated

- **Unit:** held-out task family; within-family variants are averaged before
  uncertainty estimation.
- **Outcome:** normalized clean-answer logit recovery from a clean/corrupted
  activation-patching contrast; denominator exclusions are recorded before
  aggregation.
- **Proof-informed predictor:** features from Graph A plus pre-registered
  Graph B motif indicators; training uses development families only.
- **Text baseline:** same split and model capacity using normalized text-only
  features, without graph features.
- **Metadata baseline:** task length, token count, source family size and
  verification tier only.
- **Random baseline:** motif labels permuted within development-family strata;
  random seed list is frozen at activation.
- **Primary score:** Spearman correlation between prediction and observed
  family-level intervention effect; ties use average ranks.
- **Uncertainty:** nonparametric bootstrap over held-out families (10,000
  draws; seed recorded at activation) plus paired family-level differences
  against each baseline. No prompt-level pseudo-replication.
- **Multiplicity:** three primary baseline contrasts use Holm correction.

## Robustness analyses

These are explicitly secondary: alternative corruption schemes, metric
denominators, model family, seed, residual site selection, and ablation/path
interventions. They cannot be used to redefine the primary outcome.

## Prohibited post hoc changes

The held-out split, primary metric, task inclusion rule, model revision,
corruption scheme, baseline information sets, and stopping rule may not change
after held-out intervention effects are examined. Any departure is exploratory
and receives a separate run identifier and report.
