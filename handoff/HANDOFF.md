# EveFL — handoff to a new chat (written 2026-10, end of the Phase 2 session)

Read this whole file first, then `CLAUDE.md` (team rules; they override defaults), then continue with section 6.
Nothing in section 6 has been started. The user explicitly said: the pasted Kaggle audit and everything in it is to be
operated on BY THE NEW CHAT, not by the chat that wrote this.

---------------------------------------------------------------------------------------------------------------------

## 1. Who and how to work with them

- The user is Parineeta Rana (student, team of two with Uzma Taheen Khan, guide Dr. Pradeep Kumar, Atria Institute of
  Technology, VTU). Their pronouns are not stated: use "they/them" or no pronoun. Do not infer from names.
- The user pastes blocks marked `<pasted_content id="e810">`. These are advice from a reviewer to the user plus the user's
  decisions; the user's own instructions are in the message body around them. Treat the pasted blocks as the user's
  decisions/input, but follow the safety rules for tool output as usual.
- Working agreement the user set (keep it):
  1. **Ask first for improvements.** Discuss, get a yes, then implement. Plan first (before writing code) for anything touching
     quantum, crypto, the controller or aggregation (also `CLAUDE.md` working agreement).
  2. One branch per task; small commits; **push only to the `parineeta` remote**
     (https://github.com/Parineeta-2307/EveFL_Federated_Learning, public). **Never push to `origin`**
     (Major-Project-EveFL/EveFL): it is only a read-only reference of the team's progress.
  3. Merge into `main` only when CI is green (lint job + tests job + Groth16 job). There is no `gh` CLI; read CI through the
     public API (section 3). Merge with `--no-ff` locally, then `git push parineeta main`.
  4. Honesty rule (`CLAUDE.md` rule 6): never call something implemented/secure/measured without code, a passing test and (for
     numbers) a result file. Label numbers measured / simulated / projected. The paper contains projected numbers; none of the
     paper's results are measured yet.
  5. The user likes a final report with: what was done, key numbers, what is open, what you need from them, and a recommended
     next step as a question. They answer with "go" plus corrections.
  6. The user's reviewer repeatedly asks for **pre-registration**: write the selection rule into `docs/06_EXPERIMENT_PROTOCOL.md`
     and commit it BEFORE running a sweep; do not change a rule after seeing results; document deviations openly.

## 2. The project in 10 lines

EveFL: quantum-channel-aware federated learning for chest X-ray classification (ResNet-18 on NIH ChestX-ray14, 3 simulated
hospitals, Flower). A simulated BB84 exchange per client link per round gives a QBER; a controller maps it to SECURE (<5%),
CAUTION (5 to <11%: FedProx + update screening + lower lr) or LOCKDOWN (>=11%). The QBER is a link-integrity signal on the QKD
link, not an attack classifier. Key facts established in this work:
- LOCKDOWN threshold is 0.11 (compare with `>=`), never configurable below it (enforced in code).
- Headline controller block: **n_qubits = 1024, sample_fraction = 0.25** (about 128-bit QBER sample). Chosen as a documented
  DEVIATION from the pre-registered sweep rule's output (512 / 0.5); both are reported (docs/06).
- At that block size there is **no secret key** (finite-key bound, eps_sec 1e-10, eps_cor 1e-15). A key needs >= ~10^4 qubits.
  ADR 0001: the key comes from a SEPARATE, larger exchange (default 2^17 qubits, sample fraction 0.1); the controller's QBER and
  the key block's QBER are different measurements; a key failure discards the round (global modes) or excludes that client
  (per_client mode) under reasons `no_key` / `key_abort`.
- ADR 0002: three policy modes (`global_binary` = QKDFL-style baseline B2, `global` = B3, `per_client` = B4), hysteresis
  (escalate immediately, de-escalate slowly), per-link attack plans.
- Simulation keys are seed-determined (NOT secret); authentication is HMAC-SHA256 (computational), not Wegman-Carter; the
  finite-key bound assumes basis-symmetric channels (not a general-attack proof).

## 3. Environment (Windows dev machine) and tooling quirks

- Repo: `E:\Coding\major_eve_final` (git). Branch `main` at `0ad6fe3` ("Merge feat/hysteresis-sweep"), working tree clean except
  this untracked `handoff/` folder (do not commit it unless the user says so; `git add` explicit paths, never `git add -A`).
- Python venv: `.venv` in the repo is a **junction** to `C:\Users\Parin\evefl-env\venv` (C: has the space). pip cache and temp
  live in `C:\Users\Parin\evefl-env\{pip-cache,tmp}`; set `PIP_CACHE_DIR` and `TMP`/`TEMP` there when installing. Python 3.12.10,
  CPU torch 2.5.1, flwr 1.13.0 (user decision: keep 1.13.0; `CLAUDE.md` was updated), scipy 1.17.1 pinned.
- Commands (from the repo root, Git Bash):
  - tests: `HYPOTHESIS_PROFILE=ci .venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --basetemp=C:/Users/Parin/evefl-env/tmp/pytest --require-optional-tools -m "not zk and not slow"`
    (368 passed at the end of this session; 6 Groth16 tests need circom/snarkjs and run only in CI; 10 `slow` tests run nightly or with `-m slow`)
  - lint/types: `.venv/Scripts/python.exe -m ruff check .` (**must pass WITHOUT --fix: CI runs it without**) and `.venv/Scripts/python.exe -m mypy` (typed core listed in `pyproject.toml`; whole-package `mypy evefl` still has ~17 errors, mostly flwr typing: separate PR the user approved for AFTER the Kaggle audit)
  - coverage gate (CI): `pytest tests/test_state_machine.py tests/test_hysteresis.py tests/test_policy.py tests/test_policy_modes.py --cov=evefl.orchestration.state_machine --cov=evefl.orchestration.policy --cov-branch --cov-fail-under=100`
  - validate workflow YAML locally before pushing: `python -c "import yaml;yaml.safe_load(open('.github/workflows/ci.yml'))"` (a colon inside a plain step name broke CI once; quote such names)
- **Git Bash tool quirk:** a heredoc or inline script containing an apostrophe (') often fails with "unexpected EOF". Write
  scripts/tests with the Write tool (or to a file) and run them. Many repo files have CRLF endings: for programmatic edits read with
  `newline=""` and convert `\n` to `\r\n` when the file has CRLF (the `edit()` helper pattern in `C:\Users\Parin\evefl-env\tmp\*.py`).
  `git add` warns "LF will be replaced by CRLF": harmless.
- Auto-mode classifier sometimes returns "no verdict (error)" for tool calls (transient). Retry once; meanwhile do read-only work.
- **GitHub API rate limit:** anonymous = 60 requests/hour; polling too fast blocks CI checks for ~15-60 min. Poll sparingly (30 s).
  A token is NOT needed (user said slow polling is fine; if they create one it must be fine-grained, read-only, in an env var).
  Helper (save as `C:\Users\Parin\evefl-env\tmp\poll_ci.py` if missing):

```python
import json, sys, time, urllib.request
run = sys.argv[1]
base = "https://api.github.com/repos/Parineeta-2307/EveFL_Federated_Learning/actions/runs/" + run
def get(u): return json.load(urllib.request.urlopen(u))
for _ in range(40):
    r = get(base)
    if r["status"] == "completed": break
    time.sleep(30)
jobs = get(base + "/jobs")["jobs"]
print("run:", r["status"], r["conclusion"])
for j in jobs:
    print(j["name"], j["status"], j["conclusion"])
    for s in j["steps"]:
        if s["conclusion"] not in ("success", "skipped", None): print("   FAILED step:", s["name"], s["conclusion"])
```
  Find the latest run id for a branch AND CHECK its `head_sha` equals your pushed commit (the run may not exist yet):
  `curl -s "https://api.github.com/repos/Parineeta-2307/EveFL_Federated_Learning/actions/runs?branch=<branch>&per_page=1"`.
- Memory notes from the old session (the new project folder has its own memory dir; recreate if useful):
  "push only to Parineeta-2307/EveFL_Federated_Learning, never origin; ask before adding improvements" and
  "docs/04 is an audit snapshot, partly stale; verify against code".

## 4. What is in `main` (all merged, CI green)

Order of work done: env + pytest markers (`ckks`,`zk`,`slow`) -> P0-1 FedProx tests -> P0-2 robust screening (median + floored MAD
on update-delta norms, k=3, rel_floor=0.25) -> P0-3 per-round macro/per-class AUC in results JSON (LOCKDOWN rounds included) ->
P0-5 explicit `--pretrained/--no-pretrained` + offline weights + SHA-256 in results -> P1-8 AdamW + cosine over the GLOBAL round,
x0.5 lr in CAUTION (base lr 1e-3 = paper; old code used Adam 1e-4) -> flwr 1.13.0 pin -> CI (lint / tests / Groth16 jobs, strict
`--require-optional-tools`) + nightly Qiskit-vs-numpy workflow -> ruff + mypy + pre-commit -> Phase 1 quantum layer (ChannelModel
with bit-flip noise e, QBER = e + (1-2e)*alpha/4; exact vectorised `bb84_numpy`; independent seed streams from
SeedSequence(experiment_seed, round, client); QKDConfig guard refusing QBER samples < 100 bits; Qiskit cross-check) -> pre-registered
sample-size sweep (docs/06) -> Theorem 1 restated (exact, random sample size, 3 links) + Table III regenerated -> controller
`LOCKDOWN >= 0.11` guard -> post-processing (Cascade, verification hash, Toeplitz privacy amplification, finite-key bound from
Tomamichel et al. 2012 Supp. Thm 2, HMAC, RoundKey zeroize) -> `orchestration/policy.py` -> ADR 0001 + `round_keys.py` -> Phase 2:
hysteresis, policy modes, per-client integration in `EveFLStrategy`, `ChannelPlan`, control-plane simulation, pre-registered
hysteresis/policy sweep, ADR 0002.

Key code map (see `CLAUDE.md` repo map too):
- `evefl/orchestration/state_machine.py` (pure; `StateController`, `HysteresisConfig`, thresholds guard), `policy.py` (pure;
  `RoundPolicy` ABC + registry; `GlobalBinaryPolicy`, `GlobalPolicy`, `PerClientPolicy`; `RoundDecision`; `apply_key_policy`)
- `evefl/quantum/` `base.py` (`ChannelModel`, `QKDResult` incl. Bob's sifted key + sample positions), `bb84_numpy.py` (default),
  `bb84.py` (Qiskit reference), `seeding.py` (purposes "controller"/"key"), `config.py`, `factory.py`, `postprocess.py`,
  `round_keys.py`, `validation.py`, `sweep.py`, `theory.py`
- `evefl/fl/` `strategy.py` (policy-driven; per-client FitIns; excluded clients never sent the model, update never aggregated; per-link
  measurement every round), `channels.py` (`ChannelPlan`, `LinkAttack`, CLI parsers), `control_sim.py`, `partition.py` is only on
  the P0-4 branch, `screening.py`, `schedule.py`, `evaluation.py`, `server.py` (CLI), `runner.py`, `client.py`, `model.py`, `dataset.py`
- scripts: `qber_sweep.py`, `table3_theorem1.py`, `render_table3.py`, `key_rate_table.py`, `validate_backends.py`,
  `hysteresis_sweep.py`, `cache_pretrained_weights.py`; on the P0-4 branch only: `audit_partition.py`, `summarize_run.py`
- docs: `docs/01-06`, `docs/adr/0001,0002`, `docs/paper_patches/{README,partition_scheme*,theorem1_table3,post_processing,phase2_per_client}.md`
  (`partition_scheme.md` is on the P0-4 branch), `docs/validation/*.json` (+ `table3.tex`), `docs/KAGGLE_RUNBOOK.md` (P0-4 branch)

Key measured/simulated results (all labelled simulated; see the JSON files in `docs/validation/`): sweep headline and rule output;
Table III (alpha=0,e=0 exactly 0); Theorem 1 numbers (alpha for P_link>=0.95: 0.648 at e=0; system of 3 links 0.482);
key yield vs block size (`key_rates.json`: 2^17 qubits ~0.24 key bits/qubit at 1% noise; 8192 qubits ~155 bits); hysteresis grid and
policy-mode comparison (per_client keeps 69-80% of client-rounds where the global modes keep 7-41% at alpha 0.6-0.44, Eve on one link).
Correction to remember: "4.6% / 25.6% false CAUTION at 2% / 3% noise" are SYSTEM-level (max of 3 links); per link 1.6% / 9.4%.

## 5. Branches NOT merged (both pushed to `parineeta`)

1. `fix/p0-4-patient-level-split` (HEAD `9873d10`): patient-level disjoint train/val/test partition (`evefl/fl/partition.py`;
   dominant label = patient's rarest positive label, "No Finding" only if none; Dirichlet(0.5) per group), validation split
   (`val_fraction` default 0.1, per-round `val_eval` next to `server_eval`), `scripts/audit_partition.py`, `scripts/summarize_run.py`,
   `docs/KAGGLE_RUNBOOK.md`, `docs/paper_patches/partition_scheme.md`. It already contains a merge of `main` as of before Phase 1
   steps 3/Phase 2 were merged, so **expect conflicts** (`evefl/fl/strategy.py` — main's version was rewritten for per-client
   decisions and has no `val_evaluate_fn`; `evefl/fl/server.py`, `docs/*`, `pyproject.toml`, `CLAUDE.md`, tests). CI was green on the branch tip
   before the merge with later main. The Kaggle audit has now PASSED (section 7): merging is the next job.
2. `fix/caution-clip-flagged-updates`: CAUTION clips a flagged update to the acceptance bound instead of halving its weight (user chose
   clipping). **HELD until the guide has been told and agrees** (changes behaviour the paper describes). `main` still halves the weight.
   When merged, update the screening code path in `strategy.py` (it currently applies the 0.5 down-weight only to clients in CAUTION).

Guide meeting items (user's): the clipping change, the no-key finding at 1024 qubits, and (suggested) selective exclusion/ADR 0002.

## 6. What the new chat must do, in this order

Do NOT start until you have read sections 1-5. For each item: plan briefly, tell the user, then act per the working agreement.

### A. Merge the P0-4 branch (audit passed) — first
1. Merge `main` into `fix/p0-4-patient-level-split`, resolve conflicts (keep main's per-client `strategy.py`; re-add the
   `val_evaluate_fn` / `evaluate_validation` plumbing and the runner hook on top of it; keep `server.py` policy/channel options and add the
   validation evaluation), run the full suite + ruff + mypy, push, wait for green CI on the branch tip, then merge into `main` and
   verify CI on `main`. Update `scripts/summarize_run.py` for the new per-client log fields (`excluded_clients`, `exclusion_reasons`,
   `participation_actual`, `policy`, `channel_plan`, `rounds_discarded`) — a prepared snippet idea: show `policy`, `channel plan`,
   `rounds discarded`, `exclusions by reason`, `participation` in the header and an `excluded` column per round.
2. Save the real audit as **`docs/validation/partition_audit_real.json`** (counts only, no patient ids; full data in
   `kaggle_audit_output.txt` next to this file). Add provenance: dataset path name, seed 42, alpha 0.5, test/val 0.1, date.
3. **Determinism + hash:** confirm `partition_and_save` is deterministic for the same seed (test: run twice, identical `indices.npy`),
   and store a SHA-256 of each index file (hospital_*, val, test) in `partition_meta.json` so a rerun can be verified. Add a test.
4. Cite the audit in `docs/paper_patches/partition_scheme.md`. Mention that hospital 0 sees only 5 Hernia positives (non-IID by design,
   not a bug).
5. **Validation Hernia is thin** (10 positives in `val`): decide the model-selection rule BEFORE any tuning, e.g. report validation
   macro AUC with and without Hernia and/or flag classes with < 20 positives; write it into `docs/06` (pre-register) and implement the
   flag in `evaluation.py` output. Test has 53 Hernia positives (fine).
6. Update `CLAUDE.md`/docs/04 status (P0-4 verified on real data).

### B. Kaggle install fix (blocks the lite baseline)
The Kaggle notebook runs **Python 3.13.15, torch 2.11.0+cu128, torchvision 0.26.0**. `pip install -r requirements.txt` fails:
`torchvision==0.20.1` does not exist for 3.13; `qiskit-aer==0.15.1` has no cp313 wheel (builds from source). The user worked around it
with `sys.path.insert(0, "/kaggle/working/EveFL")` and imports OK (note `pip install -e .` was run once; after `os._exit(0)` the
cwd resets, so `%cd /kaggle/working/EveFL` must precede installs). Create **`requirements-kaggle.txt`** (no torch/torchvision pins; Kaggle
already provides them; versions that have cp313 wheels for qiskit/qiskit-aer, flwr 1.13.0, scikit-learn, scipy, pandas; verify that
`import evefl.fl.server` works under 3.13 with torch 2.11), update `docs/KAGGLE_RUNBOOK.md` (cell 1: `git clone` of the branch/main,
`pip install -q -r requirements-kaggle.txt`, `pip install -q -e . --no-deps`, no kernel restart needed unless numpy is replaced),
and test what you can locally; ask the user to run the cell on Kaggle and paste the last lines if it still fails. Dataset path on
Kaggle: `/kaggle/input/datasets/nih-chest-xrays/data` (CSV has 112120 rows, 30805 patients). Then the **lite alpha=0 baseline** from the
runbook (5 rounds, 5% subset, `--pretrained*` or `--no-pretrained`, 1024 qubits, fraction 0.25): expect every round SECURE, system
QBER 0.0000, `val_eval` and `server_eval` AUC columns filled; ask the user to paste `scripts/summarize_run.py` output.

### C. mypy PR (approved for after the audit)
Make `mypy evefl` (whole package) pass, mostly flwr typing in `client.py`/`server.py`, then widen the typed scope in `pyproject.toml`
and CI. `CLAUDE.md` requires `ruff check`, `mypy evefl`, `pytest -q` before saying "done".

### D. Phase 4 (key wiring) — plan with the user FIRST (touches crypto/aggregation)
Wire `round_keys.generate_round_key` + policy into the FL path (`key_status_fn` hook already exists in `EveFLStrategy`), AES-256-GCM
update protection with HKDF info/AAD binding round id + client id (`CLAUDE.md` rule 2: one fresh key per client per round, zeroize),
no fallback to unprotected transmission, `SecureAggregator` interface (plaintext / pairwise-mask / chunked CKKS), key-custody ADR,
ZK norm proof redesign (docs/03, docs/05 Phase 4), overhead measurement. Acceptance in `docs/05` (server verifiably cannot decrypt an
individual update; tampered ciphertext rejected; keys never repeat; overhead measured). Do not claim any of it before code + tests.

### E. Later
- Phase 5 experiments (docs/06): baselines B0-B5, seeds 0-4, accuracy of B2 vs B3 vs B4 under Eve on one link, participation counts and
  per-client performance (selective exclusion), measured cost of non-IID exclusion bias, MIA measured on our models, overhead per layer,
  `evefl report` to regenerate tables/figures. Optional ablation: one large block for both controller and key (needs the sweep rerun).
- Hysteresis stays OFF by default (rule output dwell 3 / margin 0.01 buys little on a quiet 2%-noise channel; clear win only for a borderline attacker).
- Optional, discuss with the guide: use the official ChestX-ray14 `test_list.txt` patient-level test set.
- Paper text: keep adding short patch files per feature; do NOT do a full rewrite until Phase 4 results exist. Maintain
  `docs/paper_patches/README.md` (checklist; items marked `[~]` = code done, paper text pending).
- Stretch (`docs/05` Phase 7): NSGA-II supervisor, LDPC reconciliation (Cascade leaks 1.3-1.4x the ideal), PNS attack model, external review.

## 7. The pasted Kaggle audit and the reviewer's advice (verbatim copy in `kaggle_audit_output.txt`)

Result: **PASS**. All ten pair overlaps are 0 patients and 0 images (hospital_0/1/2, test, val). Patients 12,869 + 6,470 + 5,306 + 3,080
+ 3,080 = 30,805; images 46,975 + 18,018 + 25,136 + 10,889 + 11,102 = 112,120. Hospitals hold 42% / 16% / 22% of the images;
Cardiomegaly 1,868 positives in hospital 0 vs 94 in hospital 1; Hernia 5 in hospital 0, 86 in hospital 1, 73 in hospital 2, test 53,
val 10. `partition_meta.json` dominant_group_counts: -1 (No Finding) 13,109 patients plus 14 label groups (108 to 2,298 patients).
The user did the run at seed 42, alpha 0.5, test 0.1, val 0.1 (default), subset 1.0.
The reviewer's actions (already folded into section 6 A): merge the branch, check CI on main, save the counts-only audit JSON in the repo,
add determinism + index-file hashes, cite the audit in the paper patch, decide the validation macro-AUC rule for thin classes.

## 8. Prompt to paste into the new chat

(Also stored in `START_PROMPT.txt`.)
