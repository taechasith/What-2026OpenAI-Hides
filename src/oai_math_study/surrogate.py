"""Inspectable surrogate experiment: causal residual-stream patching.

This experiment is deliberately separate from the OpenAI corpus analysis. It
trains four independently initialized tiny Transformers from scratch on
addition modulo ten, then measures causal recovery after replacing a
residual-stream state from a clean prompt into a corrupted prompt. It is a
pedagogical mechanistic intervention, not evidence about any OpenAI model.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import Tensor, nn


SEEDS = (20261009, 20261010, 20261011, 20261012)
VOCAB_SIZE = 12  # digits 0-9, plus, equals
PLUS, EQUALS = 10, 11
POSITIONS = ("left addend", "operator", "right addend", "equals")
T_975_DF_3 = 3.182446305


class Block(nn.Module):
    def __init__(self, width: int, heads: int):
        super().__init__()
        self.norm_1 = nn.LayerNorm(width)
        self.attention = nn.MultiheadAttention(width, heads, batch_first=True)
        self.norm_2 = nn.LayerNorm(width)
        self.mlp = nn.Sequential(
            nn.Linear(width, width * 2),
            nn.GELU(),
            nn.Linear(width * 2, width),
        )

    def forward(self, value: Tensor) -> Tensor:
        normalized = self.norm_1(value)
        attended, _ = self.attention(normalized, normalized, normalized, need_weights=False)
        value = value + attended
        return value + self.mlp(self.norm_2(value))


class TinyAdditionTransformer(nn.Module):
    def __init__(self, width: int = 48, layers: int = 2, heads: int = 3):
        super().__init__()
        self.token = nn.Embedding(VOCAB_SIZE, width)
        self.position = nn.Embedding(4, width)
        self.blocks = nn.ModuleList([Block(width, heads) for _ in range(layers)])
        self.final_norm = nn.LayerNorm(width)
        self.unembed = nn.Linear(width, 10, bias=False)

    def forward(
        self,
        tokens: Tensor,
        capture: bool = False,
        patch: tuple[int, int, Tensor] | None = None,
    ) -> tuple[Tensor, list[Tensor]]:
        positions = torch.arange(tokens.shape[1], device=tokens.device)
        value = self.token(tokens) + self.position(positions)[None, :, :]
        states: list[Tensor] = []
        for layer_index, block in enumerate(self.blocks):
            value = block(value)
            states.append(value.detach())
            if patch is not None and layer_index == patch[0]:
                _, position, donor = patch
                value = value.clone()
                value[:, position, :] = donor[:, position, :]
        return self.unembed(self.final_norm(value[:, -1, :])), states


def make_tokens() -> tuple[Tensor, Tensor]:
    pairs = [(left, right) for left in range(10) for right in range(10)]
    tokens = torch.tensor([[left, PLUS, right, EQUALS] for left, right in pairs], dtype=torch.long)
    targets = torch.tensor([(left + right) % 10 for left, right in pairs], dtype=torch.long)
    return tokens, targets


def train_model(model: TinyAdditionTransformer, tokens: Tensor, targets: Tensor) -> list[dict[str, float]]:
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.01, weight_decay=0.001)
    records: list[dict[str, float]] = []
    for step in range(1, 2001):
        logits, _ = model(tokens)
        loss = nn.functional.cross_entropy(logits, targets)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if step % 100 == 0 or step == 1:
            accuracy = (logits.argmax(dim=-1) == targets).float().mean().item()
            records.append({"step": step, "loss": float(loss.item()), "accuracy": float(accuracy)})
        if step >= 300 and (logits.argmax(dim=-1) == targets).all():
            break
    return records


def patching_rows(
    model: TinyAdditionTransformer, clean: Tensor, targets: Tensor, seed: int
) -> list[dict[str, object]]:
    model.eval()
    with torch.no_grad():
        clean_logits, clean_states = model(clean, capture=True)
        corrupted = clean.clone()
        corrupted[:, 0] = (corrupted[:, 0] + 1) % 10
        corrupt_logits, _ = model(corrupted)
        index = torch.arange(len(targets))
        clean_score = clean_logits[index, targets]
        corrupt_score = corrupt_logits[index, targets]
        rows: list[dict[str, object]] = []
        for layer in range(len(model.blocks)):
            for position, label in enumerate(POSITIONS):
                patched_logits, _ = model(corrupted, patch=(layer, position, clean_states[layer]))
                patched_score = patched_logits[index, targets]
                denominator = clean_score - corrupt_score
                valid = denominator.abs() > 1e-5
                recovery = torch.where(
                    valid,
                    (patched_score - corrupt_score) / denominator,
                    torch.full_like(denominator, float("nan")),
                )
                rows.append(
                    {
                        "seed": seed,
                        "layer": layer,
                        "position": position,
                        "position_label": label,
                        "mean_logit_recovery": float(torch.nanmean(recovery).item()),
                        "median_logit_recovery": float(torch.nanmedian(recovery).item()),
                        "valid_examples": int(valid.sum().item()),
                    }
                )
    return rows


def _summary(values: list[float]) -> dict[str, float | int]:
    if not values:
        raise ValueError("cannot summarize an empty sequence")
    mean = float(np.mean(values))
    if len(values) == 1:
        return {"n_models": 1, "mean": mean, "sample_sd": 0.0, "ci95_low": mean, "ci95_high": mean}
    sample_sd = float(np.std(values, ddof=1))
    half_width = T_975_DF_3 * sample_sd / math.sqrt(len(values)) if len(values) == 4 else float("nan")
    return {
        "n_models": len(values),
        "mean": mean,
        "sample_sd": sample_sd,
        "ci95_low": mean - half_width,
        "ci95_high": mean + half_width,
    }


def summarize_patches(seed_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Summarize seed-level patching effects; seeds are the uncertainty unit."""
    summaries: list[dict[str, object]] = []
    for layer in range(2):
        for position, label in enumerate(POSITIONS):
            matching = [
                row for row in seed_rows if int(row["layer"]) == layer and int(row["position"]) == position
            ]
            values = [float(row["mean_logit_recovery"]) for row in matching]
            uncertainty = _summary(values)
            summaries.append(
                {
                    "layer": layer,
                    "position": position,
                    "position_label": label,
                    "valid_examples_per_model": ";".join(str(row["valid_examples"]) for row in matching),
                    "median_of_seed_medians": float(np.median([float(row["median_logit_recovery"]) for row in matching])),
                    "mean_logit_recovery": uncertainty["mean"],
                    "sample_sd": uncertainty["sample_sd"],
                    "ci95_low": uncertainty["ci95_low"],
                    "ci95_high": uncertainty["ci95_high"],
                    "n_models": uncertainty["n_models"],
                }
            )
    return summaries


def primary_contrast(seed_rows: list[dict[str, object]]) -> dict[str, object]:
    by_seed = {
        seed: {
            (int(row["layer"]), int(row["position"])): float(row["mean_logit_recovery"])
            for row in seed_rows
            if int(row["seed"]) == seed
        }
        for seed in SEEDS
    }
    effects = [by_seed[seed][(0, 0)] - by_seed[seed][(0, 1)] for seed in SEEDS]
    return {
        "contrast": "Layer 1 left-addend recovery minus Layer 1 operator recovery",
        "per_seed_effects": [{"seed": seed, "effect": effect} for seed, effect in zip(SEEDS, effects)],
        **_summary(effects),
    }


def _write_csv(destination: Path, rows: list[dict[str, object]]) -> None:
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _display(value: float) -> str:
    """Avoid an uninformative signed zero in rounded manuscript values."""
    return f"{0.0 if abs(value) < 0.005 else value:.2f}"


def run(root: Path) -> dict[str, object]:
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    tokens, targets = make_tokens()
    trajectories: list[dict[str, object]] = []
    seed_rows: list[dict[str, object]] = []
    accuracies: dict[str, float] = {}
    parameter_count: int | None = None
    for seed in SEEDS:
        torch.manual_seed(seed)
        np.random.seed(seed)
        model = TinyAdditionTransformer()
        parameter_count = sum(parameter.numel() for parameter in model.parameters())
        trajectory = train_model(model, tokens, targets)
        with torch.no_grad():
            logits, _ = model(tokens)
            accuracy = float((logits.argmax(dim=-1) == targets).float().mean().item())
        if accuracy != 1.0:
            raise RuntimeError(f"surrogate seed {seed} did not fit its frozen task (accuracy={accuracy:.3f})")
        accuracies[str(seed)] = accuracy
        trajectories.extend({"seed": seed, **record} for record in trajectory)
        seed_rows.extend(patching_rows(model, tokens, targets, seed))
    summaries = summarize_patches(seed_rows)
    contrast = primary_contrast(seed_rows)
    data = root / "data" / "derived"
    data.mkdir(parents=True, exist_ok=True)
    _write_csv(data / "surrogate_training.csv", trajectories)
    _write_csv(data / "surrogate_patching_seed.csv", seed_rows)
    _write_csv(data / "surrogate_patching_summary.csv", summaries)
    _write_csv(data / "surrogate_patching.csv", summaries)
    (data / "surrogate_primary_contrast.json").write_text(
        json.dumps(contrast, indent=2) + "\n", encoding="utf-8"
    )
    result = {
        "experiment": "four-seed tiny Transformer causal residual-stream patching on addition modulo 10",
        "simulation_protocol": "SIMULATION_PROTOCOL.md",
        "seeds": list(SEEDS),
        "n_models": len(SEEDS),
        "architecture": {"layers": 2, "heads": 3, "width": 48, "parameters": parameter_count},
        "training_pairs": 100,
        "training_accuracy_by_seed": accuracies,
        "intervention": "replace post-block residual state from clean into left-addend-corrupted prompt",
        "uncertainty_unit": "independent random initialization seed",
        "claim_boundary": "This is a surrogate-only causal result and says nothing about OpenAI model internals.",
    }
    (data / "surrogate_experiment.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    generated = root / "paper" / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    recovery = {(int(row["layer"]), int(row["position"])): row for row in summaries}
    left = recovery[(0, 0)]
    operator = recovery[(0, 1)]
    final_equals = recovery[(1, 3)]
    (generated / "surrogate_macros.tex").write_text(
        "\n".join(
            [
                r"\newcommand{\SurrogateAccuracy}{100\%}",
                rf"\newcommand{{\SurrogateParameters}}{{{parameter_count:,}}}",
                rf"\newcommand{{\SurrogateSeedCount}}{{{len(SEEDS)}}}",
                rf"\newcommand{{\LayerOneLeftRecovery}}{{{_display(float(left['mean_logit_recovery']))}}}",
                rf"\newcommand{{\LayerOneLeftCI}}{{[{_display(float(left['ci95_low']))}, {_display(float(left['ci95_high']))}]}}",
                rf"\newcommand{{\LayerOneOperatorRecovery}}{{{_display(float(operator['mean_logit_recovery']))}}}",
                rf"\newcommand{{\LayerOneOperatorCI}}{{[{_display(float(operator['ci95_low']))}, {_display(float(operator['ci95_high']))}]}}",
                rf"\newcommand{{\LayerOnePrimaryDifference}}{{{_display(float(contrast['mean']))}}}",
                rf"\newcommand{{\LayerOnePrimaryDifferenceCI}}{{[{_display(float(contrast['ci95_low']))}, {_display(float(contrast['ci95_high']))}]}}",
                rf"\newcommand{{\LayerTwoEqualsRecovery}}{{{_display(float(final_equals['mean_logit_recovery']))}}}",
                rf"\newcommand{{\LayerTwoEqualsCI}}{{[{_display(float(final_equals['ci95_low']))}, {_display(float(final_equals['ci95_high']))}]}}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _plot(root / "figures" / "surrogate_patching", summaries)
    return result


def _plot(destination: Path, rows: list[dict[str, object]]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    matrix = np.array(
        [[next(float(row["mean_logit_recovery"]) for row in rows if row["layer"] == layer and row["position"] == pos) for pos in range(4)] for layer in range(2)]
    )
    fig, (ax, uncertainty_ax) = plt.subplots(1, 2, figsize=(10.2, 3.6), gridspec_kw={"width_ratios": [1.12, 1]})
    image = ax.imshow(matrix, cmap="PuOr", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(4), ["left addend", "operator", "right addend", "equals"])
    ax.set_yticks(range(2), ["Layer 1", "Layer 2"])
    ax.set_title("Mean recovery across four seeds")
    for layer in range(2):
        for position in range(4):
            ax.text(position, layer, f"{matrix[layer, position]:.2f}", ha="center", va="center", fontsize=9)
    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Recovery fraction")
    labels = [f"L{int(row['layer']) + 1} {str(row['position_label'])}" for row in rows]
    means = [float(row["mean_logit_recovery"]) for row in rows]
    lower = [mean - float(row["ci95_low"]) for mean, row in zip(means, rows)]
    upper = [float(row["ci95_high"]) - mean for mean, row in zip(means, rows)]
    uncertainty_ax.errorbar(
        means,
        range(len(rows)),
        xerr=np.array([lower, upper]),
        fmt="o",
        color="#4c2a85",
        capsize=3,
    )
    uncertainty_ax.axvline(0, color="0.65", linewidth=0.8)
    uncertainty_ax.set_yticks(range(len(rows)), labels, fontsize=8)
    uncertainty_ax.invert_yaxis()
    uncertainty_ax.set_xlabel("Mean recovery; 95% t interval")
    uncertainty_ax.set_title("Seed-level uncertainty ($n=4$)")
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        fig.savefig(destination.with_suffix(f".{suffix}"), dpi=240, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(run(args.root.resolve()), indent=2))


if __name__ == "__main__":
    main()
