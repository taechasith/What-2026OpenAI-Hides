# Repository operating rules

1. Keep all third-party source material under `external/` and do not include it
   in commits or the arXiv source package. Record its provenance and license.
2. Treat the public OpenAI release as an evolving source. Every analysis run
   requires a pinned Git commit and emits a manifest.
3. Do not infer correctness of an unformalized manuscript from its presence,
   prose, apparent confidence, or a reported model result.
4. Never identify output text with internal model computation. Terms such as
   "mechanism", "circuit", "feature", and "causal" require direct,
   intervention-based evidence from an inspectable model.
5. Derived outputs must be reproducible through `python -m
   oai_math_study.run_analysis` and may not be hand-edited.
6. A substantive source or output change requires rerunning tests, analysis,
   manuscript build, PDF inspection, and the final audit.
