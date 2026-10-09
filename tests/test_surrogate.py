import torch

from oai_math_study.surrogate import TinyAdditionTransformer, make_tokens


def test_surrogate_shapes():
    tokens, targets = make_tokens()
    model = TinyAdditionTransformer()
    logits, states = model(tokens[:3], capture=True)
    assert tokens.shape == (100, 4)
    assert targets.shape == (100,)
    assert logits.shape == (3, 10)
    assert len(states) == 2
