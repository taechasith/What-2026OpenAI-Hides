# Version 2 counterfactual benchmark status

No counterfactual case is released as verified in this checkpoint.

The V2 protocol requires each case to contain source provenance, a reference
answer, a transformation type, a verification tier, and a checker record. The
current environment has no detected Lean/Lake toolchain, and no semantic audit
record has been produced. Extracted source motifs therefore cannot honestly be
transformed into a `verified_counterfactuals.jsonl` dataset.

This directory is reserved for a later gate-passing benchmark. It must not be
used as evidence that removing an assumption invalidates a theorem: an invalid
proof is not a counterexample.
