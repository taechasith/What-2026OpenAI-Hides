# Optional instrumentation evaluation: Jacobian and REA

**Evaluation date:** 2026-10-12 (Asia/Bangkok)  
**Decision:** Do not integrate either tool into the current experimental
pipeline. Re-evaluate Jacobian on its supported Linux/Python platform before a
future verified-counterfactual phase; consider REA only for a separately
authorized, accessible software target.

## Scope and provenance

| Tool | Inspected revision | License | Intended use here |
| --- | --- | --- | --- |
| [Jacobian](https://github.com/morluto/jacobian) | `9dc2aaf6efe8803f1c501e2972f741dd94962c32` | MIT | exact typed operations, graph operations, bounded SAT/SMT, and counterexample-oriented validation |
| [REA](https://github.com/morluto/rea) | `c22111eca2c4bc84a084f12711f405b3e7422a40` | MIT, with separate third-party/provider terms | static or runtime inspection of an authorized accessible deployment |

The two shallow source checkouts are under ignored `external/` and are not
release inputs. No MCP registration, agent configuration change, global package
installation, model download, API call, or inspection of proprietary software
was performed.

## Capability and compatibility assessment

Jacobian 0.23.0 exposes an executable vocabulary through Python, CLI, and MCP:
exact linear algebra, graph/isomorphism operations, bounded SAT/SMT through
Z3, and optional Singular/QEPCAD-backed operations. This is potentially useful
for replacing some finite-arithmetic checks with typed, bounded operation
records and for graph counterfactuals. It is not a general proof assistant,
and its result contract must be recorded per operation. Its declared runtime is
Python >=3.12,<3.14; the tested binary-install contract is CPython 3.12/3.13 on
glibc Linux x86-64. This host is Windows with project Python 3.10.

REA is a reverse-engineering MCP/CLI for binaries, applications, JavaScript,
and runtime behavior. It requires Node 22.19+ (or later listed releases) and
target-specific providers for native work. The host has Node 22.14.0, below
that stated requirement. More importantly, there is no authorized accessible
open-weight deployment, binary, or inference runtime whose implementation is
needed to answer the current proof-structure questions. REA cannot reveal a
model's learned circuits merely by inspecting an inference engine, and it has
no evidential bearing on OpenAI's unreleased model.

## Security and cost review

Jacobian's mandatory stack includes native/binary dependencies such as
CyPari, PPLPy, Python-FLINT, and Z3; optional Singular/QEPCAD operations launch
external executables. Its source has bounded backend diagnostics, but a
successful installation is not a proof of mathematical correctness. The
Windows pilot encountered a mandatory `pplpy` build rather than a ready wheel.

REA setup can write agent configuration and register an MCP server. Runtime
capture executes or interacts with the selected target under the user's
permissions; its security policy explicitly says this is not a sandbox. Native
analysis additionally depends on locally authorized Ghidra, Hopper, or IDA.
Those effects are disproportionate to the current project need, so no setup or
runtime pilot was appropriate.

## Reproducible pilot

Pinned source checkouts and host facts:

```powershell
git clone --depth 1 https://github.com/morluto/jacobian.git external/jacobian
git -C external/jacobian rev-parse HEAD
uv run --directory external\jacobian --python 3.12 jacobian inspect integer.compute.extended_gcd
```

The last command was attempted twice in an isolated `external/jacobian/.venv`.
It selected CPython 3.12.10, then stalled building mandatory `pplpy==0.9.0` on
Windows; the first attempt also emitted repeated `uv` cache rename
access-denied warnings. Neither bounded 30-second attempt reached the
`jacobian inspect` result, so no Jacobian mathematical result is reported.
This is a compatibility failure, not negative evidence about Jacobian's
operation semantics.

Existing instruments completed the comparable small checks without additional
installation: Python's `math.gcd(84,30)` returned 6 with a Bézout check of 6,
and NetworkX returned 4 nodes, 3 edges, and shortest-path length 3 for `P4`.
The existing counterfactual pipeline's 480 concrete integer cases already has
100% agreement with its declared exact-integer checker. Jacobian therefore
showed no measurable execution, validity, or reproducibility improvement on
this host.

## Adoption decision and future gate

**Jacobian: deferred, not integrated.** It is the preferred candidate if a
future Linux x86-64/Python 3.12+ environment can execute a pinned release and
demonstrate a gain on a preregistered graph or SMT counterfactual suite over
the existing checker. Adoption requires operation IDs, inputs, version/lock
hash, typed outputs, independent verifier agreement, resource limits, and a
failure log. Even then, Jacobian's exact result is operation-scoped; it does
not establish informal mathematical meaning or a neural mechanism.

**REA: rejected for the current phase.** Reconsider only when an authorized
open-weight deployment's compiled/runtime behavior is itself an experimental
object and static/runtime inspection can discriminate preregistered competing
implementation hypotheses. Any such study must pin the artifact, obtain
authorization, record target side effects and provider version, and retain
separate causal interventions for claims about learned computation.
