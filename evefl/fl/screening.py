"""
Robust screening of client updates by the size of their change.

Why this exists (P0-2)
----------------------
The first CAUTION rule flagged a client when its norm exceeded
`mean + k*std` of the client norms. With N clients that can never fire for
small N: the largest possible z-score is (N-1)/sqrt(N), i.e. 1.155 for N=3, so
`k=2` is unreachable. It also measured the norm of the full parameter vector,
which is dominated by the (huge, shared) global weights, not by what the client
changed.

This module fixes both:

* it works on the norm of the update *delta* (client weights - global weights),
* it uses the median and a scaled MAD, which a single outlier cannot drag.

Small-N caveat and the MAD floor
--------------------------------
With only 3 clients, two honest updates can be almost identical, making the MAD
tiny. A healthy third client that is a few percent larger would then look like a
huge outlier. So the spread is never allowed to fall below `rel_floor * median`:

    scale     = max(1.4826 * MAD, rel_floor * median)
    threshold = median + k * scale          (flag if norm > threshold)

Only *large* updates are flagged (scaled / poisoned updates blow the norm up).
With fewer than 3 updates a median is not meaningful, so nothing is flagged.
"""

from __future__ import annotations

from typing import List, Sequence

import numpy as np

MAD_TO_SIGMA = 1.4826  # makes MAD consistent with std for normally distributed data
MIN_CLIENTS_FOR_SCREENING = 3


def update_delta_norm(client_ndarrays: Sequence[np.ndarray], global_ndarrays: Sequence[np.ndarray]) -> float:
    """L2 norm of (client - global), flattened over all floating-point tensors.

    Integer tensors (BatchNorm `num_batches_tracked`) are counters, not learned
    weights, so they are excluded.
    """
    if len(client_ndarrays) != len(global_ndarrays):
        raise ValueError(
            f"Tensor count mismatch: client has {len(client_ndarrays)}, global has {len(global_ndarrays)}."
        )
    total = 0.0
    for client, global_ in zip(client_ndarrays, global_ndarrays):
        if not np.issubdtype(client.dtype, np.floating):
            continue
        delta = client.astype(np.float64) - global_.astype(np.float64)
        total += float(np.sum(np.square(delta)))
    return float(np.sqrt(total))


def screening_threshold(norms: Sequence[float], *, k: float, rel_floor: float) -> float:
    """Norm above which an update is flagged (see module docstring)."""
    arr = np.asarray(norms, dtype=np.float64)
    median = float(np.median(arr))
    mad = float(np.median(np.abs(arr - median)))
    scale = max(MAD_TO_SIGMA * mad, rel_floor * median)
    return median + k * scale


def flag_anomalous_updates(norms: Sequence[float], *, k: float = 3.0, rel_floor: float = 0.25) -> List[bool]:
    """Boolean flag per update: True if its norm is anomalously large."""
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}.")
    if rel_floor < 0:
        raise ValueError(f"rel_floor must be non-negative, got {rel_floor}.")
    if len(norms) < MIN_CLIENTS_FOR_SCREENING:
        return [False] * len(norms)
    threshold = screening_threshold(norms, k=k, rel_floor=rel_floor)
    return [bool(n > threshold) for n in norms]
