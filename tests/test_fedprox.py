"""
P0-1 regression tests: the FedProx proximal term in CAUTION rounds.

The original bug zipped `model.parameters()` (62 tensors for ResNet-18) with a
list built from `state_dict()` (122 tensors, BatchNorm buffers included), which
raised in CAUTION and made CAUTION rounds silent no-ops.
"""

import pytest
import torch

from evefl.fl.client import _fedprox_term, _train_one_client
from evefl.fl.model import build_resnet18


@pytest.fixture(scope="module")
def model():
    torch.manual_seed(0)
    return build_resnet18(pretrained=False)


def test_resnet18_has_buffers_beyond_parameters(model):
    """Guards the premise of the bug: state_dict() has more tensors than parameters()."""
    assert len(model.state_dict()) > len(list(model.parameters()))


def test_fedprox_term_is_zero_at_the_global_model(model):
    global_params = [p.detach().clone() for p in model.parameters()]
    assert _fedprox_term(model, global_params, mu=0.01).item() == 0.0


def test_fedprox_term_matches_manual_formula(model):
    global_params = [p.detach().clone() + 0.1 for p in model.parameters()]
    expected = 0.5 * 0.01 * sum(((p.detach() - g) ** 2).sum() for p, g in zip(model.parameters(), global_params))
    assert _fedprox_term(model, global_params, mu=0.01).item() == pytest.approx(expected.item(), rel=1e-5)


def test_fedprox_term_has_gradient_toward_global(model):
    global_params = [p.detach().clone() + 0.1 for p in model.parameters()]
    model.zero_grad()
    _fedprox_term(model, global_params, mu=0.01).backward()
    first = next(model.parameters())
    # local < global everywhere, so the gradient of (mu/2)||w-g||^2 = mu*(w-g) is negative
    assert torch.all(first.grad < 0)


def _tiny_loader(n_batches=2, batch=2):
    torch.manual_seed(1)
    return [(torch.randn(batch, 3, 64, 64), torch.randint(0, 2, (batch, 14)).float()) for _ in range(n_batches)]


def test_train_one_client_runs_with_fedprox_on_resnet18():
    """The end-to-end shape of the original crash: local training with mu > 0."""
    model = build_resnet18(pretrained=False)
    metrics = _train_one_client(model, _tiny_loader(), device=torch.device("cpu"),
                                epochs=1, lr=1e-3, fedprox_mu=0.01)
    assert metrics["n_batches"] == 2
    assert metrics["train_loss"] == metrics["train_loss"]  # not NaN


def test_fedprox_keeps_local_model_closer_to_global():
    """A large mu must pull the trained model nearer to the starting (global) weights."""
    def distance_after_training(mu):
        torch.manual_seed(0)
        model = build_resnet18(pretrained=False)
        start = [p.detach().clone() for p in model.parameters()]
        _train_one_client(model, _tiny_loader(n_batches=3), device=torch.device("cpu"),
                          epochs=1, lr=1e-2, fedprox_mu=mu)
        return sum(((p.detach() - s) ** 2).sum() for p, s in zip(model.parameters(), start)).item()

    assert distance_after_training(mu=10.0) < distance_after_training(mu=0.0)
