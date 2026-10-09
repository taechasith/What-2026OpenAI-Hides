"""Inspectable surrogate experiment: causal residual-stream patching.

This experiment is deliberately separate from the OpenAI corpus analysis. It
trains a tiny Transformer from scratch on addition modulo ten, then measures
causal recovery after replacing a residual-stream state from a clean prompt
into a corrupted prompt. It is a pedagogical mechanistic intervention, not
evidence about any OpenAI model.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import Tensor, nn


SEED = 20261009
VOCAB_SIZE = 12  # digits 0-9, plus, equals
PLUS, EQUALS = 10, 11


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


def patching_rows(model: TinyAdditionTransformer, clean: Tensor, targets: Tensor) -> list[dict[str, object]]:
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
            for position, label in enumerate(["left addend", "operator", "right addend", "equals"]):
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
                        "layer": layer,
                        "position": position,
                        "position_label": label,
                        "mean_logit_recovery": float(torch.nanmean(recovery).item()),
                        "median_logit_recovery": float(torch.nanmedian(recovery).item()),
                        "valid_examples": int(valid.sum().item()),
                    }
                )
    return rows


def run(root: Path) -> dict[str, object]:
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    torch.set_num_threads(1)
    tokens, targets = make_tokens()
    model = TinyAdditionTransformer()
    trajectory = train_model(model, tokens, targets)
    with torch.no_grad():
        logits, _ = model(tokens)
        accuracy = float((logits.argmax(dim=-1) == targets).float().mean().item())
    if accuracy != 1.0:
        raise RuntimeError(f"surrogate did not fit its frozen task (accuracy={accuracy:.3f})")
    patches = patching_rows(model, tokens, targets)
    data = root / "data" / "derived"
    data.mkdir(parents=True, exist_ok=True)
    with (data / "surrogate_training.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["step", "loss", "accuracy"])
        writer.writeheader()
        writer.writerows(trajectory)
    with (data / "surrogate_patching.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(patches[0]))
        writer.writeheader()
        writer.writerows(patches)
    result = {
        "experiment": "tiny transformer trained from scratch on addition modulo 10",
        "seed": SEED,
        "architecture": {"layers": 2, "heads": 3, "width": 48, "parameters": sum(p.numel() for p in model.parameters())},
        "training_pairs": 100,
        "training_accuracy": accuracy,
        "intervention": "replace post-block residual state from clean into left-addend-corrupted prompt",
        "claim_boundary": "This is a surrogate-only causal result and says nothing about OpenAI model internals.",
    }
    (data / "surrogate_experiment.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    generated = root / "paper" / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    recovery = {(int(row["layer"]), int(row["position"])): float(row["mean_logit_recovery"]) for row in patches}
    (generated / "surrogate_macros.tex").write_text(
        "\n".join(
            [
                r"\newcommand{\SurrogateAccuracy}{100\%}",
                r"\newcommand{\SurrogateParameters}{39,264}",
                rf"\newcommand{{\LayerOneLeftRecovery}}{{{recovery[(0, 0)]:.2f}}}",
                rf"\newcommand{{\LayerTwoEqualsRecovery}}{{{recovery[(1, 3)]:.2f}}}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _plot(root / "figures" / "surrogate_patching", patches)
    return result


def _plot(destination: Path, rows: list[dict[str, object]]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    matrix = np.array(
        [[next(float(row["mean_logit_recovery"]) for row in rows if row["layer"] == layer and row["position"] == pos) for pos in range(4)] for layer in range(2)]
    )
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    image = ax.imshow(matrix, cmap="PuOr", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(4), ["left addend", "operator", "right addend", "equals"])
    ax.set_yticks(range(2), ["Layer 1", "Layer 2"])
    ax.set_title("Toy surrogate: mean clean-logit recovery after residual patching")
    for layer in range(2):
        for position in range(4):
            ax.text(position, layer, f"{matrix[layer, position]:.2f}", ha="center", va="center", fontsize=9)
    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Recovery fraction")
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
