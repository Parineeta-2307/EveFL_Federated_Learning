"""
Audit a saved patient-level partition against the real ChestX-ray14 metadata.

Run this on Kaggle right after `partition_and_save()` (the real dataset is not
available locally). It prints:
  * overlap counts (patients and images) for every pair of hospitals / test,
    which must ALL be zero,
  * per-hospital patient/image counts and "No Finding" share,
  * per-class positive counts per hospital (to eyeball the Dirichlet skew).

Exit code is 1 if any overlap is found.

    python scripts/audit_partition.py --data-root /kaggle/input/data \
        --partition-root /kaggle/working/partitions
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from evefl.fl.dataset import audit_saved_partition  # noqa: E402
from evefl.fl.model import CHESTXRAY_LABELS  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a patient-level ChestX-ray14 partition")
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--partition-root", type=Path, required=True)
    args = parser.parse_args()

    audit = audit_saved_partition(args.data_root, args.partition_root)

    print("\n=== Overlap counts (must all be 0) ===")
    for pair, counts in audit["overlaps"].items():
        print(f"  {pair:<24} patients={counts['patients']:<6} images={counts['images']}")

    print("\n=== Per-split size ===")
    for name, s in audit["stats"].items():
        print(f"  {name:<11} images={s['images']:<7} patients={s['patients']:<6} "
              f"no_finding_share={s['no_finding_share']:.3f}")

    print("\n=== Positive images per class ===")
    names = list(audit["stats"])
    print("  " + f"{'class':<20}" + "".join(f"{n:>12}" for n in names))
    for c, label in enumerate(CHESTXRAY_LABELS):
        print("  " + f"{label:<20}" + "".join(f"{audit['stats'][n]['positives_per_class'][c]:>12}" for n in names))

    print("\nRESULT:", "OK - disjoint at patient and image level" if audit["ok"] else "FAIL - overlap found")
    return 0 if audit["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
