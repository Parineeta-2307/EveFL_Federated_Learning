# 01 Project Context

## Problem
Hospitals cannot pool chest X-rays (HIPAA, GDPR), so they use federated learning (FL) and send
model updates instead. Updates leak: gradients can be inverted to reconstruct images, and
membership inference reveals who was in the training set. Transport is normally classical TLS,
which hides content but gives no live signal that a channel is being attacked. "Harvest now,
decrypt later" adds a quantum-era risk for recorded traffic.

## Solution: EveFL (authoritative, crypto-first framing)
A mid-project pivot moved the design from "QBER detection is the whole idea" to "cryptography
first, QBER orchestrates". Older documents that pitch only the three-state controller are
outdated. Layers:
1. Key layer. BB84 QKD (simulated) produces per-client, per-round key material and a QBER
   reading. CRYSTALS-Kyber (ML-KEM-768) is a hybrid fallback. Keys are combined with HKDF-SHA256
   into an AES-256-GCM session key.
2. Orchestration layer. A three-state machine on max-over-clients QBER.
   SECURE (<5%) runs FedAvg. CAUTION (5% to <11%) runs FedProx (mu=0.01) plus update screening.
   LOCKDOWN (>=11%) discards the round, keeps the last good model and forces fresh keys.
3. Privacy layer. CKKS homomorphic aggregation so the server never sees individual updates.
4. Integrity layer. Groth16 proof that a client's update has bounded L2 norm (Byzantine defence).
5. Supervisor. NSGA-II retunes thresholds and mu offline, trading AUC against crypto overhead.

## Positioning
- Closest prior work as cited: QKDFL (Wang, Zhang, Li, IEEE IoT J. 2024). Binary pause/resume at a
  static 11% QBER. FedSec (Lyu et al., ACM CSUR 2024) is cited as naming channel-state-aware
  orchestration an open gap. VERIFY BOTH by DOI before relying on them. The novelty claim rests
  on them and they could not be confirmed.
- Claimed contributions, with honest status.
  (a) QBER as a live orchestration signal. Implemented, simulated.
  (b) Graduated three-state response vs binary. Implemented. The advantage over binary only
      exists in the CAUTION band and needs per-client or intermittent-Eve experiments to show.
  (c) Accuracy-security Pareto curve. Not yet measured. Nothing in the paper is measured yet.
  (d) Integrated hybrid QKD + PQC + CKKS + Groth16 pipeline. Modules exist, not integrated.
- Lit review file has 5 clusters. Its header says 43 papers but the tables hold 46. The paper's
  reference list is a different corpus with partial overlap. Reconcile and verify every entry.

## Threat model in one paragraph
QBER measures disturbance on the quantum key-exchange link. It is a disturbance detector, not an
attack classifier, and it does not observe interception of classical ciphertext. Frame it as
"link-integrity signal for the QKD link that feeds keys to FL clients", not "detects gradient
sniffing". Full detail in docs/03.

## Dataset
NIH ChestX-ray14. 112,120 images, 30,805 patients, 14 pathology labels plus "No Finding".
It has NO COVID-19 label. Remove COVID claims. Three simulated hospitals via Dirichlet(0.5).
Held-out IID test split (10%). Split by patient ID.

## Implementation status (from code audit)
| Component | Exists | Tested | Wired into FL | Notes |
|---|---|---|---|---|
| BB84 sim (Qiskit Aer) | yes | yes | yes (QBER only) | noiseless, slow, key not used |
| AES-256-GCM + HKDF | yes | yes | NO | README and dashboard imply otherwise |
| State machine | yes | yes | yes | no hysteresis |
| Strategy (FedAvg/CAUTION/LOCKDOWN) | yes | smoke only | yes | anomaly rule ineffective |
| Client (FedProx) | yes | no | yes | FedProx crashes (P0-1) |
| Dataset + Dirichlet | yes | no | yes | overlap, image-level split |
| Server / experiment runner | yes | smoke | yes | Ray deadlock on Kaggle |
| CKKS (TenSEAL) | yes | yes | NO | no chunking, key custody unresolved |
| Groth16 (n=8) | yes | yes | NO | soundness gaps, insecure setup |
| Kyber, NSGA-II | no | no | no | |
| Global AUC-ROC evaluation | no | no | no | evaluate_fn=None |
| Dashboard | yes (4 pages) | no | n/a | CKKS/Groth16 pages are honest stubs |
| CI, Docker, W&B, Prometheus | no | | | |

## Team and venue
Two-person team, guide Dr. Pradeep Kumar (an older brief named a different guide, confirm).
Paper is LaTeX IEEEtran, currently targeting a VTU-aligned venue, with IEEE S&P workshop, ACM
CCS or a medical-AI journal as stretch targets. Compute is Kaggle (primary) and Colab (demos).

## What "production-grade" can honestly mean here
Achievable: clean interfaces, typed and tested code, CI, pinned and audited dependencies,
reproducible experiments, real gRPC/TLS deployment mode, containers, telemetry, audit logging,
a written threat model and an independent-review-ready security doc.
Not achievable by software alone: real QKD security (needs hardware, so the quantum layer must
consume keys through the ETSI GS QKD 014 key-delivery interface so sim and hardware are
swappable), formal certification, or clinical validation.

## Plain-English glossary
- QBER: fraction of key bits Alice and Bob disagree on. Eavesdropping on BB84 raises it.
- Intercept-resend with probability alpha: Eve measures a fraction alpha of photons and resends.
  Expected QBER = alpha/4 (max 25%).
- FedAvg: server averages client models. FedProx: adds a pull-toward-global term to local loss.
- CKKS: encryption that allows adding and scaling encrypted vectors, approximately.
- Groth16: compact zero-knowledge proof system needing a trusted setup.
- NSGA-II: multi-objective evolutionary optimiser that returns a Pareto front.