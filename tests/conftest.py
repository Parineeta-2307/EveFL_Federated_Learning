"""
Optional-tool gating for the test suite.

Some tests need tooling that is not available everywhere (TenSEAL on some
platforms, circom + snarkjs which need Node). Rather than failing local runs,
those tests are marked and skipped automatically when the tool is missing, so
plain `pytest` stays green locally while Kaggle / WSL / CI run the full suite.

    ckks  -> needs the `tenseal` package
    zk    -> needs `circom` and `snarkjs` on PATH

Select or exclude explicitly with e.g. `pytest -m "not zk"`.
"""

from __future__ import annotations

import importlib.util
import shutil

import pytest

# Test modules that are tagged automatically (so the tests themselves stay untouched).
_MODULE_MARKERS = {
    "test_ckks": "ckks",
    "test_groth16": "zk",
}


def _missing_reason(marker: str) -> str | None:
    if marker == "ckks":
        if importlib.util.find_spec("tenseal") is None:
            return "tenseal is not installed"
    elif marker == "zk":
        missing = [tool for tool in ("circom", "snarkjs") if shutil.which(tool) is None]
        if missing:
            return f"{' and '.join(missing)} not found on PATH"
    return None


def pytest_collection_modifyitems(config, items):
    for item in items:
        marker = _MODULE_MARKERS.get(item.module.__name__.rsplit(".", 1)[-1])
        if marker is None:
            continue
        item.add_marker(getattr(pytest.mark, marker))
        reason = _missing_reason(marker)
        if reason:
            item.add_marker(pytest.mark.skip(reason=reason))
