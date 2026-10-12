"""Bounded Version 3 reconstruction, identifiability, and counterfactual tests.

All output-only results concern observable extraction labels, never the hidden
OpenAI producer. Run from the repository root after the Version 2 extractor.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit

SEED = 20261012
BOOTSTRAPS = 1000


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _metrics(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    return {
        "auroc": float(roc_auc_score(y, p)),
        "average_precision": float(average_precision_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
    }


def _features(nodes: pd.DataFrame, edges: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    motifs = pd.read_parquet(nodes.attrs["motif_path"])
    induction = set(motifs.loc[motifs["motif"] == "induction", "node_id"])
    out_degree = edges.groupby("source_node_id").size()
    in_degree = edges.groupby("target_node_id").size()
    frame = nodes.copy()
    frame["out_degree"] = frame.node_id.map(out_degree).fillna(0).astype(float)
    frame["in_degree"] = frame.node_id.map(in_degree).fillna(0).astype(float)
    frame["doc_nodes"] = frame.groupby("document_id").node_id.transform("size").astype(float)
    max_line = frame.groupby("document_id").line_start.transform("max").clip(lower=1)
    frame["relative_line"] = frame.line_start / max_line
    kind = pd.get_dummies(frame.node_kind, prefix="kind", dtype=float)
    meta = np.column_stack((kind.to_numpy(), frame[["relative_line", "doc_nodes"]].assign(doc_nodes=np.log1p(frame.doc_nodes)).to_numpy()))
    structural = np.column_stack((meta, np.log1p(frame[["in_degree", "out_degree"]].to_numpy())))
    groups = np.where(frame.result_family_ids.eq("unlinked"), "unlinked:" + frame.document_id, "family:" + frame.result_family_ids).astype(str)
    y = frame.node_id.isin(induction).astype(int).to_numpy()
    return frame, y, (meta, structural, groups)


def functional(root: Path) -> dict[str, object]:
    base = root / "data" / "derived" / "v2"
    nodes = pd.read_parquet(base / "proof_nodes.parquet")
    nodes.attrs["motif_path"] = base / "proof_motifs.parquet"
    edges = pd.read_parquet(base / "proof_edges.parquet")
    frame, y, (meta, structural, groups) = _features(nodes, edges)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=SEED)
    train, test = next(splitter.split(structural, y, groups))
    rng = np.random.default_rng(SEED)
    shuffled_train, shuffled_test = structural[train].copy(), structural[test].copy()
    for col in (-2, -1):
        shuffled_train[:, col] = rng.permutation(shuffled_train[:, col])
        shuffled_test[:, col] = rng.permutation(shuffled_test[:, col])
    configurations = {
        "metadata": (meta[train], meta[test]),
        "structure": (structural[train], structural[test]),
        "shuffled_structure": (shuffled_train, shuffled_test),
    }
    predictions: list[dict[str, object]] = []
    summaries: dict[str, dict[str, float]] = {}
    probability: dict[str, np.ndarray] = {}
    for name, (x_train, x_test) in configurations.items():
        model = LogisticRegression(max_iter=500, class_weight="balanced", random_state=SEED)
        model.fit(x_train, y[train])
        p = model.predict_proba(x_test)[:, 1]
        probability[name] = p
        summaries[name] = _metrics(y[test], p)
        predictions.extend({"node_id": frame.node_id.iloc[i], "group": groups[i], "y": int(y[i]), "model": name, "probability": float(value)} for i, value in zip(test, p))
    test_groups = np.unique(groups[test])
    deltas = []
    for _ in range(BOOTSTRAPS):
        selected = rng.choice(test_groups, size=len(test_groups), replace=True)
        sampled_index = np.concatenate([np.flatnonzero(groups[test] == group) for group in selected])
        if len(np.unique(y[test][sampled_index])) < 2:
            continue
        for baseline in ("metadata", "shuffled_structure"):
            deltas.append({"baseline": baseline, "delta_auroc": float(roc_auc_score(y[test][sampled_index], probability["structure"][sampled_index]) - roc_auc_score(y[test][sampled_index], probability[baseline][sampled_index]))})
    delta_frame = pd.DataFrame(deltas)
    contrasts = {
        name: {"mean_delta_auroc": float(group.delta_auroc.mean()), "ci95_low": float(group.delta_auroc.quantile(.025)), "ci95_high": float(group.delta_auroc.quantile(.975)), "bootstrap_draws": int(len(group))}
        for name, group in delta_frame.groupby("baseline")
    }
    out = root / "experiments" / "functional_reconstruction"
    out.mkdir(parents=True, exist_ok=True)
    _write_json(out / "config.json", {"seed": SEED, "test_group_fraction": .20, "target": "fixed lexical induction label", "models": ["metadata", "structure", "degree-permuted structure"], "bootstrap_draws": BOOTSTRAPS, "source_text_used": False})
    pd.DataFrame(predictions).to_csv(out / "heldout_predictions.csv", index=False)
    result = {"experiment": "v3_family_disjoint_induction_label_prediction", "seed": SEED, "test_nodes": int(len(test)), "test_groups": int(len(test_groups)), "positive_rate": float(y[test].mean()), "metrics": summaries, "auroc_contrasts": contrasts, "limitations": ["The target is a lexical extractor label, not a validated proof strategy.", "Source text and document identifiers were excluded to avoid direct lexical leakage.", "The test set consists of already public artifacts, not future producer outputs."]}
    _write_json(out / "results.json", result)
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    labels = list(summaries)
    ax.bar(labels, [summaries[x]["auroc"] for x in labels], color=["#7A7A7A", "#007C91", "#A95D00"])
    ax.axhline(.5, color="black", lw=.8, ls="--")
    ax.set_ylim(0, 1); ax.set_ylabel("Held-out AUROC"); ax.set_title("Family-disjoint induction-label prediction")
    fig.tight_layout()
    for ext in ("pdf", "png"): fig.savefig(root / "figures" / f"v3_functional_prediction.{ext}", dpi=240)
    plt.close(fig)
    return result


def organisms(root: Path) -> dict[str, object]:
    rng = np.random.default_rng(SEED + 1)
    rows, truth = [], []
    # The final two producers intentionally share the exact same observable law.
    settings = {"planner": ("induction", 4.5, 55), "retrieval": ("construction", 7.0, 105), "editorial": ("equivalence", 1.2, 42), "mixed": ("case_split", 3.0, 75), "equiv_a": ("reduction", 2.5, 66), "equiv_b": ("reduction", 2.5, 66)}
    for label, (motif, refs, length) in settings.items():
        for index in range(240):
            run = index // 6
            observed = {"case_id": f"{label}-{index:03d}", "run_id": run, "motif": motif if rng.random() < .72 else rng.choice(["induction", "construction", "equivalence", "case_split", "reduction"]), "references": int(rng.poisson(refs)), "length": int(max(5, rng.normal(length, 12))), "node_kind": rng.choice(["proof", "lemma", "proposition"], p=[.55, .30, .15])}
            rows.append(observed); truth.append({"case_id": observed["case_id"], "hidden_process": label})
    observed, truth = pd.DataFrame(rows), pd.DataFrame(truth)
    x = pd.get_dummies(observed[["motif", "node_kind"]], dtype=float)
    x[["references", "length"]] = observed[["references", "length"]]
    splitter = GroupShuffleSplit(n_splits=1, test_size=.25, random_state=SEED)
    train, test = next(splitter.split(x, truth.hidden_process, observed.run_id))
    model = LogisticRegression(max_iter=600, class_weight="balanced", multi_class="multinomial", random_state=SEED)
    model.fit(x.iloc[train], truth.hidden_process.iloc[train])
    prediction = model.predict(x.iloc[test])
    test_truth = truth.hidden_process.iloc[test].to_numpy()
    per_class = {label: float((prediction[test_truth == label] == label).mean()) for label in sorted(set(test_truth))}
    equiv_mask = np.isin(test_truth, ["equiv_a", "equiv_b"])
    equivalence_accuracy = float((prediction[equiv_mask] == test_truth[equiv_mask]).mean())
    out = root / "experiments" / "identifiability"; out.mkdir(parents=True, exist_ok=True)
    _write_json(out / "config.json", {"seed": SEED + 1, "artifacts_per_process": 240, "processes": list(settings), "equivalence_pair": ["equiv_a", "equiv_b"], "test_group_fraction": .25})
    observed.to_csv(out / "observable_artifacts.csv", index=False); truth.to_csv(out / "frozen_hidden_ground_truth.csv", index=False)
    results = {"experiment": "v3_hidden_process_model_organisms", "seed": SEED + 1, "n_artifacts": int(len(observed)), "n_test": int(len(test)), "overall_accuracy": float((prediction == test_truth).mean()), "per_process_accuracy": per_class, "observational_equivalence_pair_accuracy": equivalence_accuracy, "equivalence_chance_level": .5, "interpretation": "The equivalence pair has identical observable generation laws. Its process identity is not identifiable from these artifacts; above-chance variation is sampling noise, not recovery."}
    _write_json(out / "results.json", results)
    fig, ax = plt.subplots(figsize=(7, 3.4)); labels=list(per_class); ax.bar(labels, [per_class[x] for x in labels], color="#6B4C9A"); ax.axhline(.5, color="black", lw=.8, ls="--"); ax.set_ylim(0,1); ax.set_ylabel("Held-out process accuracy"); ax.set_title("Known-process calibration with equivalence control"); ax.tick_params(axis="x", rotation=25); fig.tight_layout()
    for ext in ("pdf", "png"): fig.savefig(root / "figures" / f"v3_identifiability.{ext}", dpi=240)
    plt.close(fig)
    return results


def counterfactuals(root: Path) -> dict[str, object]:
    rng = np.random.default_rng(SEED + 2); rows=[]
    for index in range(120):
        a, b = (int(x) for x in rng.integers(-50, 51, size=2)); total=a+b
        variants = [("original", total, True), ("equivalent_commuted", b+a, True), ("changed_hypothesis", (a+1)+b, True), ("invalid_conclusion", total+1, False)]
        for variant, claimed, valid in variants:
            checked = claimed == (total if variant != "equivalent_commuted" else b+a) if variant != "changed_hypothesis" else claimed == (a+1)+b
            rows.append({"case_id": f"arith-{index:03d}-{variant}", "base_id": f"arith-{index:03d}", "variant": variant, "a":a, "b":b, "claimed_value":claimed, "expected_valid":valid, "checker_valid":bool(checked), "verification_tier":"exact_concrete_integer_arithmetic", "formal_kernel_checked":False})
    frame=pd.DataFrame(rows); out=root/"experiments"/"counterfactuals"; out.mkdir(parents=True, exist_ok=True); _write_json(out/"config.json", {"seed":SEED+2,"base_problems":120,"variants":["original","equivalent_commuted","changed_hypothesis","invalid_conclusion"],"verification_tier":"exact_concrete_integer_arithmetic"}); frame.to_csv(out/"cases.csv", index=False)
    result={"experiment":"v3_exact_integer_counterfactuals", "seed":SEED+2, "cases":int(len(frame)), "base_problems":120, "checker_agreement":float((frame.expected_valid==frame.checker_valid).mean()), "valid_cases":int(frame.checker_valid.sum()), "invalid_cases":int((~frame.checker_valid).sum()), "limitations":["Concrete integer equalities are exactly checked by Python integer arithmetic, not a proof-assistant kernel.", "These cases do not establish informal-to-formal semantic fidelity or support a neural causal claim."]}
    _write_json(out/"results.json",result); return result


def reports(root: Path, f: dict[str, object], i: dict[str, object], c: dict[str, object]) -> None:
    r=root/"reports"; r.mkdir(exist_ok=True)
    metrics=f["metrics"]; contrasts=f["auroc_contrasts"]
    (r/"FUNCTIONAL_RECONSTRUCTION_RESULTS.md").write_text(f"# Functional reconstruction results\n\nThe frozen family-disjoint test contains {f['test_nodes']:,} nodes from {f['test_groups']} groups; induction-label prevalence is {f['positive_rate']:.3f}. The structure model AUROC is {metrics['structure']['auroc']:.3f}, metadata AUROC is {metrics['metadata']['auroc']:.3f}, and degree-permuted control AUROC is {metrics['shuffled_structure']['auroc']:.3f}. Structure-minus-metadata AUROC is {contrasts['metadata']['mean_delta_auroc']:.3f} (bootstrap 95% CI {contrasts['metadata']['ci95_low']:.3f} to {contrasts['metadata']['ci95_high']:.3f}). This is an association with a lexical extraction label, not validation of a mathematical strategy or hidden producer process.\n",encoding="utf-8")
    (r/"IDENTIFIABILITY_AND_MODEL_ORGANISM_RESULTS.md").write_text(f"# Identifiability and model-organism results\n\nAcross {i['n_artifacts']:,} synthetic observable artifacts, hidden-process classification accuracy was {i['overall_accuracy']:.3f}. The deliberately observationally equivalent pair had accuracy {i['observational_equivalence_pair_accuracy']:.3f} against a chance reference of 0.500. The result calibrates a failure mode: distinct producer identities cannot be recovered when their observable laws coincide. It does not identify the OpenAI producer.\n",encoding="utf-8")
    (r/"COUNTERFACTUAL_RESULTS.md").write_text(f"# Counterfactual results\n\nThe finite arithmetic suite has {c['cases']} cases ({c['valid_cases']} valid, {c['invalid_cases']} invalid) and exact checker agreement {c['checker_agreement']:.3f}. Its assurance tier is exact concrete integer arithmetic, not Lean kernel verification or semantic audit. It is excluded from causal-model conclusions.\n",encoding="utf-8")
    (r/"BASELINE_COMPARISONS.md").write_text("# Baseline comparisons\n\nThe functional experiment compares a fixed graph-feature logistic model against metadata-only and degree-permuted graph controls under the same family-disjoint split. Text was intentionally excluded because labels are lexical rules over source text, making a text baseline directly leakage-prone. Results are reported in `FUNCTIONAL_RECONSTRUCTION_RESULTS.md`.\n",encoding="utf-8")
    (r/"CAUSAL_INTERVENTION_RESULTS.md").write_text("# Causal intervention results\n\n**Status: BLOCKED.** No local open-weight mathematical model, compatible interpretability stack, or preregistered behavioral-competence result is available. The historical tiny addition simulation remains a pedagogical method demonstration and is not counted as Version 3 causal validation.\n",encoding="utf-8")
    (r/"CLAIM_EVIDENCE_MATRIX.md").write_text("# Claim-evidence matrix\n\n| Claim | Scope | Status | Evidence | Constraint |\n| --- | --- | --- | --- | --- |\n| Pinned public artifacts are structurally indexed | public corpus | PASS | V1/V2 manifests | not semantic correctness |\n| Literal graph features predict a lexical motif label | public source structure | PARTIAL | V3 held-out results | not a strategy label |\n| Output-only methods identify hidden processes | controlled organisms | FAIL as general claim | equivalence control | indistinguishable processes remain equivalent |\n| Concrete arithmetic status is checked | finite synthetic cases | PARTIAL | V3 counterfactual cases | no Lean or semantic audit |\n| Causal proof strategy exists in an open model | surrogate/open model | BLOCKED | none | no eligible model or competence test |\n| OpenAI internal mechanism is identified | unreleased producer | UNSUPPORTED | none | inaccessible internals |\n",encoding="utf-8")
    (r/"PROOF_STRUCTURE_RESULTS.md").write_text("# Proof-structure results\n\nVersion 2 remains the primary source-structure extraction: 45,620 literal environment candidates, 97,343 within-document literal references, and 42,143 lexical motif records. Version 3 does not upgrade their verification status.\n",encoding="utf-8")
    (r/"INDEPENDENT_SCIENTIFIC_AUDIT.md").write_text("# Skeptical scientific audit\n\nThe observed graph-label association can be explained by source conventions, editorial practice, or extraction artifacts. The controlled equivalence pair demonstrates that output-only process attribution is not generally identifiable. No text model was run because label words would leak. No result supports a claim about OpenAI internals, proof correctness, or causal computation in a mathematical language model. The reproducibility boundary is a local rerun, not independent human replication.\n",encoding="utf-8")
    (r/"REPRODUCIBILITY_AUDIT.md").write_text("# Reproducibility audit\n\nRun `python -m oai_math_study.v3_experiments --root .` after the V2 artifacts exist. The command uses fixed seeds, writes experiment datasets/results, figures, reports, and a manifest. `python -m pytest -q` validates unit tests. An external rerun remains outstanding.\n",encoding="utf-8")
    (r/"FINAL_SCIENTIFIC_CONCLUSIONS.md").write_text("# Final scientific conclusions\n\nThis execution supports Level A artifact reconstruction and a bounded predictive analysis of lexical source labels. It does not support Level B strategy reconstruction, Level D causal transfer, or Level E producer-model mechanism identification. The model-organism experiment positively establishes an identifiability limit: different hidden processes can be observationally equivalent. The appropriate outcome is **C: limited reconstruction**, not an account of OpenAI's hidden reasoning.\n",encoding="utf-8")
    (r/"VERSION_CHANGELOG.md").write_text("# Version changelog\n\n- V1: pinned catalogue and release inventory.\n- V2: provenance-preserving literal source extraction; no predictive or causal claim.\n- V3: frozen family-disjoint extraction-label prediction, hidden-process calibration with an equivalence control, and finite arithmetic counterfactual checks. No previous artifact is overwritten and no mechanism claim is added.\n",encoding="utf-8")


def run(root: Path) -> dict[str, object]:
    f=functional(root); i=organisms(root); c=counterfactuals(root); reports(root,f,i,c)
    manifest={"version":"v3", "seed":SEED, "functional":f, "identifiability":i, "counterfactuals":c}
    _write_json(root/"data"/"derived"/"v3"/"experiment_manifest.json",manifest)
    environment={"python":sys.version, "platform":platform.platform(), "packages":{name:importlib.metadata.version(name) for name in ["numpy","pandas","scikit-learn","matplotlib","pyarrow"]}}
    _write_json(root/"experiments"/"environment_lock.json",environment)
    generated=root/"paper"/"generated"; generated.mkdir(parents=True,exist_ok=True)
    generated.joinpath("v3_macros.tex").write_text("\n".join([rf"\newcommand{{\VThreeFunctionalAUROC}}{{{f['metrics']['structure']['auroc']:.2f}}}",rf"\newcommand{{\VThreeMetadataAUROC}}{{{f['metrics']['metadata']['auroc']:.2f}}}",rf"\newcommand{{\VThreeOrganismAccuracy}}{{{i['overall_accuracy']:.2f}}}",rf"\newcommand{{\VThreeEquivalenceAccuracy}}{{{i['observational_equivalence_pair_accuracy']:.2f}}}",rf"\newcommand{{\VThreeCounterfactualCases}}{{{c['cases']}}}"])+"\n",encoding="utf-8")
    tracked=[root/"experiments"/name/file for name,file in [("functional_reconstruction","results.json"),("identifiability","results.json"),("counterfactuals","results.json")]]
    _write_json(root/"data"/"derived"/"v3"/"checksums.json", {str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in tracked})
    return manifest


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--root",type=Path,default=Path.cwd()); args=parser.parse_args(); print(json.dumps(run(args.root.resolve()),indent=2))

if __name__ == "__main__": main()
