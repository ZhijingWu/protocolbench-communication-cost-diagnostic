# Communication-Cost Sensitivity in LLM Multi-Agent Protocol Assignment

An independent reproducible diagnostic built on the released ProtocolBench / AgentProtocols implementation.

**Research question.** Can measured local communication cost and controlled communication demand change the minimizer of a declared protocol-assignment objective when a saved local assignment and explicit synthetic preference margins are held fixed?

**Audited conclusion.** The audited released GAIA assignment path does not directly condition protocol assignment on explicit graph/edge-demand inputs. Using measured local request costs, controlled communication demand, and explicit synthetic local preference margins, the declared sensitivity objective can admit assignment reversals.

This is an independent experimental extension / diagnostic, with no affiliation with UIUC or the ProtocolBench authors. It does not introduce a new router or demonstrate GAIA, ProtocolRouter, task-quality, or makespan improvement, topology-aware routing superiority, ANP superiority, or “first” novelty.

## Evidence at a glance

The saved local microbenchmark measures **A2A, ACP, ANP, and Agora** at **1 KB, 10 KB, 50 KB, and 100 KB** (1 KB = 1024 bytes). Each protocol/size has **30 measured repetitions after 5 excluded warmups**: **480/480 measured requests succeeded**, with a further 80 successful warmups. Setup is recorded separately and excluded from request statistics.

Requests traverse the released client/server paths with deterministic no-op executors and no LLM calls. Latency encloses `BaseAgent.send`, including encode, transport, server, no-op execution, and decode. HTTP-body bytes are distinguished from converter-boundary bytes. These are **local implementation-specific latency measurements**, not intrinsic protocol rankings. ANP's 100 KB outlier is retained; close ACP/ANP point estimates do not establish statistical superiority.

The [controlled graph results](results/processed/reversal_summary.json) record **37 strict reversals among 144 declared configurations**. This finite sensitivity grid is not a deployment success rate or a GAIA evaluation.

The repository-defined workflow witness is **`analysis_task`: Agent 1 A2A → ANP**, under the declared controlled setting: 10 KB, 100 requests per edge, λ = 0.1 preference-loss units per accumulated ms, and a synthetic unit replacement loss. Agora stays unchanged in this all-four-protocol witness. Its stored objective delta is `-0.5649729999999984`.

An eligible A2A → ANP reversal persists in the **no-Agora ablation after forced feasibility changes are separated**. Removing Agora globally forces Agent 0 away from its original assignment. For the analysis witness, the delta against the original, now-infeasible baseline is `+0.4350270000000016`; the delta against the feasible enumeration seed is `-0.5649729999999984`. Thus the eligible node reversal does **not** establish a whole-assignment gain against the original baseline in that ablation. See the [workflow table](results/processed/gaia_workflow_reversal.csv) and [workflow summary](results/processed/gaia_workflow_summary.json).

## Model and interpretation boundary

The declared additive objective is

```text
J(p) = Σ_j L_j(p_j) + λ Σ_(i,j)∈E w_ij C(p_j, s_ij)
```

`L_j` is synthetic local preference loss: zero at the saved baseline and one per replacement. `C` is measured local mean latency in ms/request; `w_ij` is controlled request demand. λ converts accumulated communication milliseconds into preference-loss units. The cost is destination-protocol dependent. The exhaustive oracle is optimal only over the small declared objective and candidate sets; ties retain the baseline/first candidate.

The traffic is controlled, and the margins are synthetic rather than empirically calibrated local suitability, probability, or task-quality loss. The workflow structures instantiate released configuration templates under explicit conventions; they are not observed GAIA execution traces. `final` is terminal output, not an additional assigned agent; `all` expands over peers in the fixed roster without self-messages. Protocol-preference metadata does not become an empirical local margin. Validated task-preserving alternative feasibility masks have not been recovered.

The measurements do not establish concurrency/queueing behavior, end-to-end task quality, security preservation, intrinsic protocol rankings, or a deployment recommendation. ANP's measured path is its current HTTP implementation, not an E2E/WebSocket benchmark; Agora uses its direct HTTP path with `toolformer=None`, without negotiation or code generation.

## Repository structure

```text
configs/             Fixed microbenchmark and sensitivity controls
src/                 Isolated diagnostic, objective, oracle, and interfaces
scripts/             Read-only inspection, integrity checks, and optional reruns
tests/               Existing offline unit/regression tests
results/raw/         Current measurements, workers, manifests, and historical evidence
results/processed/   Saved summaries and sensitivity tables
notes/               Scientific audits, environment freeze, publication audit
outreach/v2/         Final two-page note, editable source, and final figures
LICENSE              Upstream MIT license with its copyright notice preserved
UPSTREAM.md          Attribution and exact upstream dependency
```

Historical observer failures, earlier blocked profiles, conversion-only measurements, and content-addressed archives are retained because they explain the numerical/provenance chain. They are not substituted into the current 480-request results. [PUBLICATION.md](PUBLICATION.md) explains public path redactions and the distinction between original historical hashes and public-file hashes.

## Reproduction

### 1. Read-only inspection of saved results

From this artifact root, with Python ≥ 3.10:

```bash
python scripts/inspect_saved_results.py
python scripts/verify_artifact.py
```

These commands use only the standard library and saved files, make no API calls, and write no results. Neither upstream nor rerunning the measurements is needed to inspect the evidence. The [raw request CSV](results/raw/real_protocol_profile.csv), [measured costs](results/processed/real_protocol_costs.csv), [final audit](notes/final_audit.md), and [local-preference audit](notes/local_preference_signal_audit.md) provide the detailed evidence.

### 2. Offline unit and integrity tests

Some existing tests load the upstream pure converters/router and official workflow YAML. Use a separate compatible checkout at the audited baseline; upstream modules are loaded in place rather than vendored:

```bash
git clone https://github.com/ulab-uiuc/AgentProtocols.git ../AgentProtocols
git -C ../AgentProtocols checkout --detach 6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f
export AGENTPROTOCOLS_ROOT="$(cd ../AgentProtocols && pwd)"
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-test.txt
python scripts/verify_artifact.py --upstream "$AGENTPROTOCOLS_ROOT"
python -m pytest -q -p no:cacheprovider tests
# Existing tests are also unittest-compatible:
python -m unittest discover -s tests -v
```

`AGENTPROTOCOLS_ROOT` is optional if the upstream checkout is a sibling named `AgentProtocols`. The original experiment Python was 3.11.13. [The saved environment freeze](notes/real_environment_freeze.txt) and [real measurement manifest](results/raw/real_protocol_manifest.json) record the actual package versions. These tests use temporary fixture directories and local mocks; they make no external API calls and do not rerun real profiling. Some regression tests exercise the oracle only on disposable fixtures. The SDK packages are unnecessary for the pure converter/router tests.

### 3. Optional protocol profiling

**This creates new measurements and is unnecessary for inspecting the published results.** Real profiling requires compatible upstream SDK dependencies, as recorded in the saved manifest/freeze, and local server ports. A rerun produces hardware/runtime-specific timings and should not be expected to reproduce exact latency values.

Make a disposable copy to keep the published evidence intact; use the configured compatible upstream checkout and your chosen Python environment:

```bash
# Run from the artifact root; choose a fresh destination that does not exist.
cp -a . ../protocolbench-diagnostic-rerun
cd ../protocolbench-diagnostic-rerun
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
python scripts/run_protocol_profile.py --mode real
# Optional, separate converter/JSON-size measurement; never network latency:
python scripts/run_protocol_profile.py --mode conversion-only
```

The scripts write only inside the copied artifact. The real worker starts the original protocol servers with deterministic no-op callbacks and blocks non-loopback socket connections. Exit 2 indicates failed/blocked requests; inspect the saved failure records. Latest profiling outputs are overwritten in the disposable copy.

### 4. Optional workflow sensitivity experiment

This uses the saved real costs, unchanged synthetic unit margins, and the released `scenarios/gaia/config/meta_protocol.yaml`. It does not run GAIA or an LLM, but it **writes sensitivity outputs**, so use the disposable copy above:

```bash
python scripts/run_gaia_workflow_assignment.py
# Optional controlled-graph sensitivity using the already saved measurements:
python scripts/run_joint_assignment.py --profile-mode real --cost-metric mean_latency_ms
# Optional replay of the original local fallback across controlled demand cases:
python scripts/run_topology_blindness.py
```

The experiment's formulas, enumeration, candidate policy, raw numeric strings, baseline, and controls are preserved. Standalone code changes only adapt imports and upstream-location discovery; the original source checkout is not changed. Historical records describe earlier source-time executions; current artifact instructions are the commands above.

## Attribution and further evidence

Built on [ProtocolBench / AgentProtocols](https://github.com/ulab-uiuc/AgentProtocols), audited at [commit 6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f](https://github.com/ulab-uiuc/AgentProtocols/tree/6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f). Original upstream authors retain attribution for their code and design. See [UPSTREAM.md](UPSTREAM.md) and the preserved [MIT license](LICENSE).

Read the [microbenchmark note](notes/real_microbench.md), [findings](notes/findings.md), [final technical note](outreach/v2/technical_note_v2.pdf), and [its claim audit](outreach/v2/claim_check_v2.md). This repository is an independent diagnostic, not an official ProtocolBench repository.

## Workflow-Latency Calibration (October 2026)

A separate controlled no-op session evaluated **120 measured serial/fork/join workflows containing 480 workflow RPCs**, excluding 20 warmup workflows / 80 warmup RPCs. These requests are separate from the historical 480-request profile and the synthetic-margin sensitivity study above.

For the serial comparison, frozen historical request costs predict treatment−baseline **−0.1564973 ms**, while the observed paired mean workflow makespan difference is **+0.8279372 ms**. This is a single-session mean calibration reversal, not a speedup or general protocol ranking. Fork/join predicted communication work decreases but predicted DAG completion ties; observed AB/BA means disagree in sign, without isolating a causal order effect.

See the [workflow calibration evidence and offline recalculation](results/workflow_calibration/README.md). The package contains original recorded timing/receipt/order data and a standard-library calculator; it does not claim full original-environment rerun reproducibility, real GAIA execution or task-quality gains.
