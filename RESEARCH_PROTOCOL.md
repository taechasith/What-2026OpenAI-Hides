# Research protocol

## Design

This is a preregistered, cross-sectional audit of a public repository release.
The unit of analysis is a result family for catalogue and formalization
analyses, a manuscript for source/PDF availability analyses, and one of the
explicitly released abridged summaries for trace-text analyses. These units are
not independent model runs and are never treated as such.

## Corpus and inclusion

The inclusion set is every family and manuscript linked from `CONTENTS.md` at
the pinned public `openai/math` commit. The trace subset is exactly the ten
files named in that commit's README. Missing, unreadable, or malformed files
are retained as availability failures; they are not silently dropped.

## Measurements

- Family identifier, title, abstract, and manuscript links are parsed from the
  catalogue.
- Lean-document availability is determined from `lean/docs/<family>.md`; this
  is an availability marker, not a proof of theorem correctness.
- Manuscript source/PDF availability and byte size are measured from the local
  checkout.
- Trace page count and token-like word counts are extracted with `pypdf`.
  Transparent keyword counts (`attempt`, `verify`, `lemma`, `proof`, `error`,
  `fail`) are descriptive only.

## Primary analyses

1. Describe family, manuscript, source/PDF, Lean-document, and trace coverage.
2. Compare number of linked manuscripts between families with and without a
   Lean document using Mann-Whitney U, rank-biserial effect size, and an exact
   label-permutation p-value (10,000 deterministic permutations).
3. Describe, but do not infer from, the small, non-random trace subset.

## Exploratory exhaustive release-tree extension

The preregistered inclusion set and RQ1--RQ3 estimands above remain unchanged.
`FULL_TREE_INVENTORY_PROTOCOL.md` separately specifies an exploratory,
structural census of every versioned Git blob in the same pinned release. It
uses the exact resolved commit rather than a mutable branch name and records
path, Git object identifier, byte size, path/extension-based artifact role,
and catalogue/summary relation for every blob. This extension establishes
release-tree coverage and organization only; it does not semantically read or
validate every mathematical claim, compile Lean, or expand the corpus to all
OpenAI research outside `openai/math`.

## Interpretation and inferential limits

Coverage is an artifact property, not a validation rate. The observational
comparison is associational, not causal; its p-value is a label-assignment
reference calculation, not evidence of independent draws. No claim is made
about model intelligence, mathematical truth, hidden reasoning, or neural
mechanisms from text alone.

## Quality controls

The pipeline fails on an unpinned checkout, zero parsed families, zero parsed
manuscripts, duplicate family identifiers, or a mismatch between parsed trace
entries and physical trace PDFs. Tests use fixtures and never need the corpus.
