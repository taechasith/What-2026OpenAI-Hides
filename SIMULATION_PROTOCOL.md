# Registered extension: multi-seed causal surrogate simulation

**Version:** `2026-10-09-multiseed-v1`
**Status:** fixed before execution
**Scope:** inspectable surrogate only; no claim about OpenAI model internals

## Purpose and boundary

This extension turns the repository's single-run pedagogical intervention into
a repeated, causal simulation.  It tests the reproducibility of a residual
state-patching measurement in a tiny Transformer.  It is not an experiment on
the public OpenAI corpus, an OpenAI model, a generalization benchmark, or
evidence that the surrogate learned an arithmetic algorithm.

## Fixed design

Four independently initialized models use seeds `20261009`, `20261010`,
`20261011`, and `20261012`.  Each is a two-block, three-head Transformer with
residual width 48, a two-times-width MLP, and a 12-token vocabulary (digits,
plus, equals).  Each model trains from scratch with full-batch AdamW
(`lr=0.01`, `weight_decay=0.001`) on all 100 ordered modulo-10 addition
prompts.  Training stops only after 300 or more updates if the full table is
fit exactly, otherwise after 2,000 updates.  A seed that fails exact fit is
retained as a failure and stops the experiment; seeds are never replaced.

For every clean prompt `(a,+,b,=)`, the corrupted prompt replaces the left
addend by `(a+1) mod 10`.  At each post-block residual stream (two layers by
four token positions), the clean state replaces the corresponding corrupted
state.  The per-prompt outcome is normalized clean-answer-logit recovery,

`(patched_logit - corrupted_logit) / (clean_logit - corrupted_logit)`.

Examples whose denominator has absolute value at most `1e-5` are excluded and
their number is recorded.  Within each model and site, the reported effect is
the mean across valid prompts.  Across models, the reported estimate is the
mean, sample standard deviation, and two-sided 95% Student-t interval with
three degrees of freedom.  The four seeds, rather than the 100 prompts, are
the uncertainty unit.

## Planned comparisons and controls

The prespecified primary descriptive contrast is Layer 1 left-addend recovery
minus Layer 1 operator recovery, paired within seed.  The operator is a
contextual control: its input token is unchanged by the corruption but its
contextual residual state can still change, so it is not assumed to be exactly
zero.  Layer 2 at the equals position is an outcome-position positive control:
it is close to the readout and is not interpreted as evidence of a distributed
arithmetic circuit.  No null-hypothesis significance test is planned for four
seeds; all seed-level measurements, estimates, and intervals are released.

## Scientific interpretation

Activation patching is a causal intervention on a known model state, not a
correlational probe.  Nevertheless, single-site patching does not establish
that a site is necessary, sufficient, unique, or a faithful high-level
explanation.  The report therefore treats this simulation as a reproducible
methods demonstration and directs claims about circuits to future work with
held-out tasks, multi-site/path interventions, ablations, and hypothesis tests
such as causal scrubbing.
