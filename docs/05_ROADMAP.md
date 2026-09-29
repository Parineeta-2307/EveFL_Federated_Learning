# 05 Roadmap

Each task has acceptance criteria. Do not start a phase before the previous one is green.

## Phase 0 Stabilise (do first)
- Fix P0-1 to P0-8 with tests. Add `ruff`, `mypy`, pre-commit, GitHub Actions CI.
- Make the single-process runner first-class (`evefl/fl/runner.py`), CUDA seeded lazily.
- Fix P2-1, P2-2 and refresh README to match reality.
Acceptance: `pytest` green, smoke test passes at alpha 0.0, 0.3 and 1.0 with assertions on
`fedprox_active`, lockdown behaviour and unchanged global params, CI green.

## Phase 1 Quantum layer
- `ChannelModel` with Eve and depolarizing noise. Numpy backend cross-checked against Qiskit
  (KS test over QBER distributions). Full post-processing per docs/03. Numerical unit tests for
  alpha/4. `etsi014.py` client with a mock KME server for tests.
Acceptance: regenerated Table III from real runs with mean, std and seeds saved as JSON, and a
Theorem 1 restatement checked by simulation.

## Phase 2 Controller
- Hysteresis and minimum dwell, per-client Decision, global and per-client modes, property tests
  (hypothesis) on monotonicity and boundary behaviour.
Acceptance: controller has no forbidden imports (enforced by a test), 100% branch coverage.

## Phase 3 FL core
- Patient-level disjoint Dirichlet(0.5) partition, cached filename index, server-side AUC
  evaluation, robust screening, configurable epochs and optimiser, pretrained init.
Acceptance: measured baseline AUC (unsecured FedAvg, 3 seeds) recorded with config hash.

## Phase 4 Crypto integration
- KeyManager and AEAD wired into the FL path, Kyber via liboqs, SecureAggregator interface with
  plaintext, pairwise-mask and chunked CKKS implementations, ZK norm proof redesign, key-custody
  decision recorded as an ADR.
Acceptance: end-to-end round test where the server verifiably cannot decrypt an individual
update, a tampered ciphertext is rejected, keys never repeat across rounds, and overhead is
measured (time and bytes) for each layer.

## Phase 5 Experiments
- Run docs/06 protocol. Generate every table and figure from result files via `evefl report`.
Acceptance: paper numbers all trace to a results file and config hash.

## Phase 6 Productisation
- Flower gRPC with mutual TLS, Docker and compose, Prometheus and W&B, hash-chained audit log,
  Streamlit dashboard reading real results, mkdocs site, SECURITY.md, SBOM, release v0.1.0.
Acceptance: `docker compose up` runs a 3-client federation with a live dashboard, and a fresh
clone reproduces one scenario end to end from the README alone.

## Phase 7 Stretch
NSGA-II supervisor (pymoo) with the theta2 >= 0.11 constraint, LSTM or CUSUM QBER forecasting,
PNS attack model, external security review of docs/03.

## Kickoff prompts

Prompt 1 (orientation, no code):
"Read CLAUDE.md, docs/01, docs/04 and docs/05. Then inspect the repo and list any place where
the code contradicts the docs. Do not modify files. Propose a plan for Phase 0 as ordered
tasks with tests, and ask me any blocking questions."

Prompt 2 (first fix):
"Phase 0, task P0-1. In plan mode, reproduce the FedProx crash with a failing unit test, then
fix `calculate_fedprox_term`, then add the alpha=0.3 smoke assertion. Run ruff, mypy and pytest
and report results. Update docs/04 when done."

Prompt 3 (per task after that):
"Next item in docs/05 Phase 0. Same workflow. Stop after this item."