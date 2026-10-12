# Literature review and novelty audit (updated 2026-10-12)

The review used primary publication pages or arXiv records. It does not claim
exhaustive coverage of all 2025--2026 work; it records the closest verified
work relevant to the study's claim boundary.

| Work | Status | Question and evidence | Limitation relevant here | Consequence for this study |
| --- | --- | --- | --- | --- |
| Geiger et al., *Causal Abstraction* (JMLR 2025) | peer reviewed | formalizes causal abstraction and intervention methods | requires access to low-level variables | public artifacts cannot establish causal abstraction of OpenAI |
| Saha et al., *KisMATH* (TACL 2026) | peer reviewed | graph-aligned interventions over 1,671 math problems and 15 open models | uses accessible models and extracted CoT graphs | no priority claim for graph-informed math interventions; our graph is source syntax only |
| Mueller et al., *MIB* (ICML 2025) | peer reviewed | evaluates causal pathway/variable recovery across tasks and models | benchmark targets inspectable neural models | causal claims require shared targets and controls, absent here |
| Ammanamanchi et al., *Faults in Our Formal Benchmarking* (ICML 2026) | peer reviewed | audits Lean benchmark defects | a kernel proof need not validate intended informal semantics | exact arithmetic is explicitly below formal-semantic assurance |
| Hsiang et al., *LeanDojo-v2* (2025) | workshop publication | traces Lean repositories into theorem/proof state data | requires Lean tooling and does not solve informal fidelity | future formal extension needs an actual Lean run and audit |
| Turpin et al., *Language Models Don't Always Say What They Think* (2023) | preprint | manipulates rationales to test faithfulness | rationale evidence remains model/task dependent | public summaries cannot be treated as hidden reasoning |
| Zhong et al., *Pando* (2026) | preprint | controlled model organisms separate elicitation from internal signal | concerns model mechanisms, not publication artifacts | motivates the equivalence-control organism experiment |
| Khan et al., *Can Language Model Agents be Helpful Circuit Explainers?* (2026) | preprint | evaluates agent explanations after circuit localization | explanation validation remains difficult | automated explanation cannot substitute for causal validation |
| Sjöberg et al., *Nonlinear Black-Box Modeling in System Identification* (1995) | peer reviewed review | surveys non-linear black-box model identification | observational equivalence remains a core issue | process labels need calibrated identifiability tests |

## Novelty conclusion

This work is not the first to use mathematical reasoning graphs or causal
interventions. Its bounded contribution is a provenance-preserving study of a
pinned public research release, coupled to family-disjoint prediction of an
extraction label and a controlled demonstration that output-only producer
identification can fail under observational equivalence. Those are not novel
claims about OpenAI's internal model.

Primary records: [JMLR causal abstraction](https://www.jmlr.org/beta/papers/v26/23-0058.html),
[KisMATH](https://aclanthology.org/2026.tacl-1.59/),
[MIB](https://proceedings.mlr.press/v267/mueller25a.html),
[formal benchmarking faults](https://proceedings.mlr.press/v306/ammanamanchi26a.html),
[LeanDojo-v2](https://leandojo.org/leandojo.html),
[faithfulness](https://arxiv.org/abs/2307.13702),
[Pando](https://arxiv.org/abs/2604.11061), and
[AgenticInterpBench](https://arxiv.org/abs/2606.24026).
