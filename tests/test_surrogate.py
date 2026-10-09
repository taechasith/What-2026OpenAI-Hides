import pytest
import torch

from oai_math_study.surrogate import TinyAdditionTransformer, make_tokens, summarize_patches


def test_surrogate_shapes():
    tokens, targets = make_tokens()
    model = TinyAdditionTransformer()
    logits, states = model(tokens[:3], capture=True)
    assert tokens.shape == (100, 4)
    assert targets.shape == (100,)
    assert logits.shape == (3, 10)
    assert len(states) == 2


def test_seed_level_summary_uses_sample_uncertainty():
    rows = [
        {
            "seed": seed,
            "layer": 0,
            "position": 0,
            "position_label": "left addend",
            "mean_logit_recovery": value,
            "median_logit_recovery": value,
            "valid_examples": 100,
        }
        for seed, value in zip((20261009, 20261010, 20261011, 20261012), (0.0, 1.0, 2.0, 3.0))
    ]
    for layer in range(2):
        for position, label in enumerate(("left addend", "operator", "right addend", "equals")):
            if layer != 0 or position != 0:
                rows.extend(
                    {
                        "seed": seed,
                        "layer": layer,
                        "position": position,
                        "position_label": label,
                        "mean_logit_recovery": 0.0,
                        "median_logit_recovery": 0.0,
                        "valid_examples": 100,
                    }
                    for seed in (20261009, 20261010, 20261011, 20261012)
                )
    first = summarize_patches(rows)[0]
    assert first["n_models"] == 4
    assert first["mean_logit_recovery"] == pytest.approx(1.5)
    assert first["sample_sd"] == pytest.approx(1.2909944487)
    assert first["ci95_low"] < 0 < first["ci95_high"]
