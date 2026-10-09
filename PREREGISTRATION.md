# Preregistration

**Registered in repository:** 2026-10-09 (Asia/Bangkok)

## Questions

**RQ1.** What public artifact coverage is present in the pinned OpenAI
mathematics release?
**RQ2.** Is Lean-document availability associated with the number of
catalogue-linked manuscripts per result family?
**RQ3.** What can the released abridged reasoning summaries support as
descriptive evidence, and what do they not identify?

## Confirmatory estimands and tests

The RQ1 estimands are counts and proportions for families, manuscripts, PDFs,
source directories, Lean documents, and released summaries. For RQ2, the
estimand is the difference in average ranks of family manuscript count between
the Lean-document-available and unavailable groups. We report group medians,
Mann-Whitney U, rank-biserial correlation, and a two-sided exact-label
permutation p-value using 10,000 seed-20261009 permutations. The sole RQ2 test
uses alpha = .05 and is explicitly descriptive/associational.

## Exclusions and deviations

No family/manuscript is excluded for surprising content. Parser failures are
reported in `data/derived/parse_warnings.csv`. Any new analysis after this file
is committed is exploratory and must be labelled as such.

## Registered post-analysis extension

The corpus estimands above remain frozen. Before executing the added
multi-seed surrogate simulation, its design, seeds, uncertainty unit,
corruption, controls, formula, stopping rule, and claim boundary were fixed in
`SIMULATION_PROTOCOL.md`. This extension is exploratory relative to the
original corpus preregistration, but confirmatory within its separately
registered surrogate protocol. It does not alter RQ1--RQ3 or turn public
OpenAI outputs into evidence about model internals.

## Stopping rule

Run once against the pinned release. Re-runs must reproduce the same manifest
and deterministic results. A new upstream commit is a new corpus version, not
a silent refresh.
