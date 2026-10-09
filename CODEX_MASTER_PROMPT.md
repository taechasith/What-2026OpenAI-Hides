# Execution record and operating contract

## Objective

Produce a transparent, reproducible empirical study of the publicly released
OpenAI mathematics collection and an arXiv-ready manuscript titled
*Reverse-Engineering Mathematical Reasoning from OpenAI's 2026 Mathematics
Corpus: Implications for Mechanistic Interpretability*.

## Scope correction made before analysis

The task checkout was initialized with only a README. No prior `AGENTS.md`,
`RESEARCH_PROTOCOL.md`, or `PREREGISTRATION.md` existed. This document and the
three companion documents are therefore the version-controlled study contract
created before the analysis scripts and outputs.

The corpus is the public `openai/math` repository, acquired at a pinned commit
recorded in `data/provenance/corpus_manifest.json`. It consists of public
manuscripts, source artifacts, selected abridged reasoning summaries, and Lean
artifacts. It is not a release of model weights, activations, prompts in full,
training data, or complete hidden chain-of-thought.

## Non-negotiable claim boundary

No result in this repository may claim to identify a circuit, feature,
activation, attention head, latent state, or causal internal mechanism of an
OpenAI model. The empirical component is a public-artifact and provenance
analysis. The paper separates this from proposed or optional experiments on
open-weight surrogate models.

## Deliverables

- Frozen acquisition record and corpus integrity checks.
- Deterministic analysis code, tests, derived tables, and figures.
- A complete LaTeX manuscript and locally built PDF.
- `release/arxiv_submission.zip`, excluding third-party corpus files.
- `reports/FINAL_AUDIT.md` stating passing checks and residual limitations.

## Completion rule

The study can be called *artifact-analysis ready* only if the pinned corpus
passes acquisition checks, scripts rerun from a clean output directory, tests
pass, the PDF renders cleanly, citations resolve to real sources, and the
arXiv archive contains compilable source. It must not be called a completed
mechanistic-interpretability experiment without access to an inspectable model
and causal-intervention results.
