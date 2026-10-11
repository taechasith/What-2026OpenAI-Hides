# Novelty and literature audit for Version 2

**Reviewed:** 2026-10-12 (Asia/Bangkok)  
**Scope:** public-document structure, formal-counterfactual construction, and
causal interventions in separately specified open-weight models.

## Bottom line

Version 1 is a public-artifact audit plus a toy-model intervention
demonstration. It is not a mechanistic analysis of an OpenAI model. Version 2
is only novel if it executes a family-held-out, pre-registered comparison in
which corpus-derived proof-structure features predict causal intervention
effects in an inspectable model better than matched baselines. A proof graph,
a model rationale, or activation-patching visualizations alone would not
establish that result.

## Reviewed work

| Work | Verified contribution | Relevance and distinction |
| --- | --- | --- |
| Saha et al., *KisMATH* (TACL 2026), DOI 10.1162/tacl.a.729 | Releases causal-CoT graphs for 1,671 mathematical problems and evaluates graph-aligned interventions across 15 open-weight models. | Closest threat: Version 2 cannot claim the first graph-based mathematical-reasoning intervention study. Its distinct claim would need public research-manuscript provenance, explicit/inferred graph separation, family-disjoint evaluation, and a direct proof-structure-to-intervention prediction test. |
| Mueller et al., *MIB* (ICML 2025) | Defines evaluation tracks for circuit and causal-variable localization across tasks and models. | Requires Version 2 to compare against equal-information baselines and report causal-localization quality rather than illustrative sites. |
| Geiger et al., *Causal Abstraction* (JMLR 2025) | Formalizes causal abstraction and relates patching, causal scrubbing, and related methods. | Prevents language that treats a single patch as a complete or unique circuit explanation. |
| Zhang and Nanda, *Towards Best Practices of Activation Patching* (2023) | Shows corruption and metric choices can change patching conclusions. | Requires fixed corruption/metric choices and secondary sensitivity analyses. |
| Marks et al., *Sparse Feature Circuits* (2024) | Introduces feature-level causal graph discovery and editing. | A feature/circuit baseline is relevant only if a selected model and compute budget make it feasible; absence must be reported. |
| LeanDojo-v2 (2025 project) | Provides Lean 4 tooling for theorem-proving training and evaluation. | It does not itself validate the semantic fidelity of a corpus-derived informal transformation. |
| Ammanamanchi, Bhat, and Biderman, *Faults in Our Formal Benchmarking* (ICML 2026; arXiv:2606.29493) | Documents formal-benchmark defects; kernel checks alone do not establish informal semantic fidelity. | Requires verification tiers, failure logs, hidden-axiom/vacuity checks, and no collapsed "verified" count. |
| Khan et al., *Can Language Model Agents be Helpful Circuit Explainers?* (2026 preprint) | Evaluates agents that explain already localized circuits; validation remains a limiting step. | AI-assisted extraction cannot be called independent human validation. |
| Tan et al., *SAEScientist-Bench* (2026 preprint) | Evaluates autonomous SAE research agents and reports substantial gaps to expert performance. | The present autonomous pipeline must retain executable outputs and failure modes, not assert scientific validation from agent-generated descriptions. |

## Comparison matrix

| Question | Existing study / prior work | Version 2 proposal | New result threshold | Still unproven without execution |
| --- | --- | --- | --- | --- |
| Public corpus coverage | Version 1 audits a pinned release. | Add source-line provenance and a two-tier graph. | Deterministic artifacts and measured extraction checks. | Mathematical correctness or hidden OpenAI reasoning. |
| Mathematical reasoning graphs | KisMATH extracts graph structure from task rationales. | Extract explicit and rule-inferred structure from public research sources. | Family-aware evidence surviving template/length controls. | That inferred motifs are intended proof dependencies. |
| Formal counterfactuals | Lean benchmarks offer machine-checked statements. | Map corpus-supported transformations to tiered cases. | Checker logs plus semantic-audit records and rejection log. | Informal-faithful mathematical meaning from kernel checks alone. |
| Causal prediction | MIB and patching studies evaluate localization. | Predict held-out intervention effect from proof structure. | Pre-specified held-out superiority over text, metadata, shuffled baselines. | A general circuit theory or an OpenAI-model mechanism. |

## Principal risks and mitigation

1. **Novelty overlap:** KisMATH already joins mathematical structure and
   interventions. Version 2 must use restrained comparative language.
2. **Template confounding:** report family-stratified and source-length-aware
   descriptive analyses; do not interpret lexical motifs as neural signatures.
3. **Formalization fallacy:** retain verification tiers and distinguish a
   kernel proof from semantic adequacy.
4. **Leakage:** assign source families before model development; keep related
   variants together.
5. **Patching fragility:** fix the primary method before outcome scans and
   publish corruption/metric sensitivities.
6. **Autonomous-analysis overclaim:** no model-produced motif or audit label is
   human validation.

## Source records

- Saha et al. (2026), https://aclanthology.org/2026.tacl-1.59/
- Mueller et al. (2025), https://proceedings.mlr.press/v267/mueller25a.html
- Geiger et al. (2025), https://www.jmlr.org/beta/papers/v26/23-0058.html
- Zhang and Nanda (2023), https://arxiv.org/abs/2309.16042
- Marks et al. (2024), https://arxiv.org/abs/2403.19647
- LeanDojo-v2, https://github.com/lean-dojo/LeanDojo-v2
- Ammanamanchi et al. (2026), https://arxiv.org/abs/2606.29493
- Khan et al. (2026), https://arxiv.org/abs/2606.24026
- Tan et al. (2026), https://arxiv.org/abs/2609.09113

This is a documented, targeted review rather than an exhaustive systematic
review. It supports no claim of priority.
