# Functional reconstruction execution protocol

This protocol is frozen before `python -m oai_math_study.v3_experiments`.
It implements the Version 3 experiment defined in `RESEARCH_DEFINITION.md`.

The test set is not a future OpenAI output. It is a family-disjoint subset of
already public documents. Because motif labels are lexical rules over the same
documents, the experiment tests prediction of reproducible extraction labels,
not mathematical validity or latent reasoning strategy. No text feature is
used: a text model would directly expose the words used by the label rules and
would be a leakage-prone comparison rather than a semantic baseline.

All seed values, split logic, models, metrics, bootstrap procedure, and
stopping rule are implemented as constants in
`src/oai_math_study/v3_experiments.py`. The process is one-shot; changing them
after inspecting results requires a new exploratory run identifier.
