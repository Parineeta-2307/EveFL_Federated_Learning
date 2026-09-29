# 06 Experiment Protocol

Rule. Every number in the paper comes from a saved result file with a config hash and seeds.
Anything else is marked projected or removed.

## Setup
ResNet-18 (14 outputs, BCEWithLogits), NIH ChestX-ray14, 3 clients, Dirichlet(0.5), patient-level
disjoint splits, 10% IID test split, E local epochs (default 5, reduce for budget), B=32,
AdamW with cosine annealing, 50 rounds. Seeds 0 to 4 (minimum 3). Report mean and 95% CI.

## Compute budget (rough estimate, measure it)
Full data at 224px, 5 epochs, 50 rounds, 4+ scenarios is far beyond Kaggle session and weekly GPU
quotas. Provide a lite profile (data subset, 128 to 160px, 1 to 2 epochs) for sweeps and run the
full profile only for the headline scenarios. LOCKDOWN rounds are nearly free because clients
skip training.

## Baselines
B0 unsecured FedAvg. B1 FedAvg with AEAD only (same accuracy as B0, measure overhead).
B2 QKDFL-style global binary pause at 11%, reimplemented. B3 EveFL global states.
B4 EveFL per-client exclusion. B5 secure aggregation baseline (pairwise-mask) against CKKS.

## Attack settings
- Static Eve, alpha in {0, 0.1, ..., 1.0}, on all links.
- Single compromised link (Eve on 1 of 3), the setting where graduated response can win.
- Intermittent Eve (per-round activation probability) and step attack at round 20.
- Baseline noise sweep, depolarizing in {0, 1, 2, 3}%, to measure false CAUTION and false LOCKDOWN.
- Byzantine client (scaled or sign-flipped update) to test screening and the norm proof.

## Metrics
Macro AUC-ROC (and per-class), rounds to AUC 0.80 (if reached), detection latency in rounds,
false alarm rate, effective training rounds, MIA success measured with a shadow-model or
loss-threshold attack on our own trained models, bytes and seconds per round per layer, memory.

## Outputs
JSON per run (config, seeds, per-round log, metrics), aggregated tables, and three core figures.
FSM diagram, QBER validation curve (simulated vs alpha/4 with noise), accuracy-security Pareto
curve. `evefl report` regenerates all figures and LaTeX tables from results. Placeholders in the
paper stay commented until a result file replaces them.