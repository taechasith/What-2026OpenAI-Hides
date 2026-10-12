# Discovery review

## Observable and unobservable material

The pinned release exposes versioned files, TeX syntax, literal references,
Lean source files, and selected public summaries. It does not expose a target
model's activations, weights, prompts, data, rejected attempts, or complete
internal reasoning. The existing Version 2 graph is therefore a source graph,
not an entailment graph or causal graph.

## Design weaknesses found

1. Lexical motifs were useful provenance-preserving candidates but were not
   semantic annotations.
2. No family-held-out prediction compared graph features with a matched
   non-graph baseline.
3. Output-only evidence cannot identify a production mechanism without an
   identifiability calibration.
4. No counterfactual benchmark had verified task status.
5. The existing four-seed addition simulation is a pedagogical intervention,
   not evidence about mathematical proof strategies or the producer model.

## Consequence

Version 3 adds only tests that this environment can execute honestly: a
nonlexical source-structure prediction study, controlled model organisms with
known hidden processes, and exact finite arithmetic counterfactual checks.
Formal Lean validation and open-weight causal testing remain separately
blocked rather than being replaced by claims from the toy simulation.
