import numpy as np

from oai_math_study.v3_experiments import _metrics


def test_metrics_perfect_ranking_is_bounded() -> None:
    result = _metrics(np.array([0, 0, 1, 1]), np.array([0.1, 0.2, 0.8, 0.9]))
    assert result["auroc"] == 1.0
    assert result["average_precision"] == 1.0
    assert 0.0 <= result["brier"] <= 1.0
