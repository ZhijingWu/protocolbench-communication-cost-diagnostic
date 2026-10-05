# Topology-aware protocol diagnostic

> Historical source-study record, made public-safe during packaging. Use the root README for current standalone commands. Source-time hashes and execution statements retain their original meaning; see PUBLICATION.md. Superseded outreach previews/v1 documents described here remain in the original study checkout; they are omitted from this artifact.


All files and outputs are isolated under experiments/topology_aware_protocol.
Original router, GAIA runner, adapters, conversion, metrics, datasets and configs
are unchanged. No commits, pushes, stashes or resets are part of this experiment.
Source audit: notes/experiment_design.md. Results/limitations: notes/findings.md.

## Canonical cost interface and current real-latency oracle run

The verified real_protocol_costs.csv is translated into the existing canonical
schema automatically when run_joint_assignment.py uses --profile-mode real
without an explicit --costs override. This only copies saved measurements; it
does not rerun the profiler or reaggregate raw requests. The canonical
protocol_costs.csv now contains mode=conversion-only and mode=real rows; the
unchanged load_measured_costs function filters modes. Real-only canonical rows
also live in protocol_costs_real.csv, with measurement_kind=end_to_end_local_request.
Mean/median/p95 latency strings and mean request-body bytes are copied exactly;
conversion runtime fields are empty for real rows. failure_rate is only the
requested metadata ratio failures/attempted_requests.

The superseded blocked protocol_costs_real.csv and prior canonical file are saved
under results/raw/cost_interface_archive/<sha256>/. Old failed raw profiles and
profile_manifest_real.json remain unchanged. cost_interface_manifest.json links
raw profile and verified summary SHA256 hashes to canonical output hashes.
Prior conversion-based oracle outputs/findings are archived under
results/raw/joint_output_archive/ before replacement by a different mode/metric.

Run from the repository root:

```bash
python \
  scripts/run_joint_assignment.py \
  --profile-mode real --cost-metric mean_latency_ms
python -m pytest -q -p no:cacheprovider tests
```

Current counts/witnesses are in results/processed/reversal_summary.json; the
full 144-case table is decision_reversal.csv. Topology/traffic counts are cases,
protocol node-event counts count each changed node, and protocol case counts can
overlap. The stored real costs are empirical local requests, while topology,
traffic and local preference margins remain controlled/synthetic sensitivity
inputs. This is not a GAIA end-to-end improvement result. The objective, margins,
cases and baseline are unchanged. Neither the old environment nor an LLM/GAIA
run is needed for this data-interface translation or oracle evaluation.

## Repository-defined GAIA workflow structures

The additional workflow experiment parses analysis_task and collaborative_task
from the official scenarios/gaia/config/meta_protocol.yaml without changing that
file, the baseline, manual margins or the existing oracle/objective. It uses the
already measured real_protocol_costs.csv latency values and the existing traffic,
lambda and normalization controls. protocol_preference stays metadata only.

```bash
python \
  scripts/run_gaia_workflow_assignment.py
python -m pytest -q -p no:cacheprovider tests
```

Outputs: results/processed/gaia_workflow_reversal.csv and gaia_workflow_summary.json;
the findings section describes literal templates, instantiated edges and provenance.
analysis_task keeps 2->final as a terminal output event, following
MeshNetwork.execute_workflow's final_result/break handling; it does not invent
an assigned final agent or a 2->3 edge. collaborative_task expands all as peers
in the unchanged four-agent roster, with no hub self-message. The named config
patterns are not captured runtime traces, and no GAIA task or LLM is run.

Global exclusion of Agora (selected by the user) makes the original agent-0
assignment infeasible. The saved original baseline is always retained as the
reference. The unchanged oracle receives a separately labeled feasible enumeration
seed and unchanged allowed entries of the original local-loss table. Forced
removals, strict objective benefits versus the original baseline, and non-forced
preference reversals are separate fields. A forced candidate-removal change or
tie is not counted as an eligible preference reversal. Whole-assignment benefit
can differ from a genuine eligible-node preference reversal because the forced
change adds its existing manual penalty. JSON witnesses record both comparisons.
Locally measured protocol costs, repository-defined workflow structure, controlled
traffic and synthetic local margins remain separate evidence categories; this
is not an end-to-end GAIA task-quality result. Prior topology-only outputs remain
historical evidence rather than being overwritten.

## Reproduce from the repository root

The remote environment used here is python (3.11.13).
Set PYTHONDONTWRITEBYTECODE=1 to avoid writing __pycache__ in original source,
and PYTHONHASHSEED=0 for reproducible original fallback metadata ordering.
The scripts also disable bytecode writing before original-module imports.
Python >=3.10 and PyYAML suffice for conversion, routing replay, oracle and tests.
The designated protocolbench environment has pytest. Existing tests remain
unittest-compatible. Communication dependencies are recorded in
notes/real_environment_freeze.txt and the local real-run manifest.

```bash
cd <UPSTREAM_ROOT>
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
PY=python

# Real local benchmark: starts original repository servers and deterministic
# no-op executors. Exit 2 means some protocols failed/blocked; see tracebacks.
$PY scripts/run_protocol_profile.py --mode real

# Separate empirical conversion/JSON-size measurements (NEVER network latency).
$PY scripts/run_protocol_profile.py --mode conversion-only

# Invoke the original router with the same local inputs for all 24 demand cases.
$PY scripts/run_topology_blindness.py

# Enumerate all 4^4 assignments per case using measured bytes and manual margins.
$PY scripts/run_joint_assignment.py --profile-mode conversion-only

$PY -m unittest discover -s tests -v
# When pytest is available:
# $PY -m pytest -q -p no:cacheprovider tests
```

The real profiler saves genuine communication costs in real_protocol_costs.csv.
The current joint-assignment run consumes their canonical schema translation.
Earlier conversion-based sensitivity outputs are preserved in the raw archives.
Missing real conditions are never assigned conversion-only numbers.
Rerunning the profiler overwrites its own latest real_protocol_* outputs; archived
diagnostic tracebacks remain separate. The complete current dependency freeze is
saved in notes/real_environment_freeze.txt.

## What is measured, what is controlled

Payload buckets mean 1024,10240,51200,102400 bytes of ASCII text in a business
payload. Each protocol/bucket has 5 warmups and 30 measured attempts. Raw CSV/JSON
include warmups, errors, stage and mode. Means/medians/p95 use successful measured
samples only; failure rates include setup-blocked requested attempts. A blocked
setup is explicitly not a transmitted request. Failed conditions keep numeric
fields empty rather than zero. p95 uses linear interpolation at (n-1)*0.95.

conversion-only loads the ORIGINAL UTE and converter source under an isolated
experiment package namespace because src/core/__init__.py eagerly imports SDKs.
It does not copy/rewrite converters, mock dependencies or run network code.
conversion_runtime_ms measures converter plus json.dumps/UTF-8 encoding;
latency_ms and all latency summary fields stay empty in conversion-only mode.
encoded_bytes uses the EXACT existing BaseAgent metric definition:
len(json.dumps(protocol_payload).encode('utf-8')). It is not actual wire bytes;
adapters can further wrap, serialize or encrypt this intermediate payload.

Real mode now automatically starts each protocol's ORIGINAL local server in an
isolated worker process using the same Python executable. No GAIA or LLM runs.
Each bucket has 5 warmups and 30 measured sends. Setup latency includes imports,
server startup/readiness and adapter initialization, recorded separately.
latency_ms is perf_counter_ns wall-clock time immediately around awaiting
BaseAgent.send, including UTE/encode/real send/server/response/decode. It is not
conversion runtime or the internal Prometheus histogram value. The latter is
recorded separately and checked against wall-clock elapsed time.

A successful sample requires one real server POST, one deterministic executor
receipt, acknowledgement of the exact payload byte count/SHA256, and a timing
sanity check. Server-side observers count the actual received HTTP body without
altering protocol messages or handlers. encoded_request_bytes means those actual
HTTP body bytes, excluding HTTP headers; ute_encoded_bytes retains the original
MSG_BYTES converter-boundary metric for successful adapter returns.
ANP is the repository's HTTP /anp/message path, not a WebSocket/E2E measurement.
Agora uses its existing toolformer=None client and original AgoraServerWrapper
/message handler with a deterministic answer callback. The callback's historical
QA/LLM name does not imply model use. No dummy toolformer, fake protocol server,
mock wire format or fabricated response is supplied. Non-loopback socket connects
are rejected in benchmark workers; API keys/DID services are not required.

Latest local real outputs are SEPARATE from the historical conversion/endpoint
attempt files and do not replace the conversion-based routing experiment:

- results/raw/real_protocol_profile.csv: actual request attempts (warmups labeled).
- results/raw/real_protocol_profile_failures.json: setup and full request tracebacks.
- results/raw/real_protocol_setup.csv: per-protocol setup status and latency.
- results/processed/real_protocol_costs.csv: 16 protocol/bucket conditions with
  successful_requests, failures, skipped_requests, mean/median/p95/sample-std
  request latency and mean actual request-body bytes. Setup-blocked protocols
  have no invented request rows; skipped counts explain missing samples.
- results/raw/real_protocol_manifest.json: environment, dependencies and boundaries.
- results/raw/real_workers/: original worker logs/results for exact diagnosis.

Setup failures do not count as failed sent requests. Failed request durations are
kept in raw data; latency statistics use successful measured requests only.
No conversion-only costs substitute for missing real conditions. The older
protocol_profile_real.*, protocol_costs_real.csv and profile_manifest_real.json
are historical endpoint-attempt artifacts, not the latest local benchmark.

## Router baseline and topology controls

The original GAIA caller constructs GAIALLMRouter without an LLM client. This
experiment therefore invokes its unmodified heuristic fallback and records that
source. It does not claim a fresh LLM routing test. The adapter can also consume
saved original output via --routing-output with a matching local_inputs_sha256;
results label this as replay. Missing/extra IDs and unsupported protocols are
rejected. RouterBench module_selections need an explicit module-to-agent mapping
and cannot be silently mistaken for GAIA agent_assignments.

Chain has directed successor edges; star is bidirectional; full mesh has every
directed non-self pair; hotspot is seeded mesh with elevated incoming hub demand.
Node identities, roles, tools, task inputs and local protocol preferences stay
fixed. Traffic means expected message counts. Per-edge and equal-total traffic
controls are both generated; equal-total removes density/volume confounding.
The original runtime has graph support, but GAIA deliver bypasses the core graph
permission check. These demand graphs are not executed by a modified GAIA runner.

## Objective, thresholds and limitations

J(p) = sum_j local_loss_j(p_j) + lambda * sum_(i,j) w_ij C(p_j, payload_size_ij).
C comes from explicit measured protocol buckets; no mismatch penalty is used.
RoutingDecision.confidence is one uncalibrated scalar, not candidate probabilities.
Config manual_local_margin=1 is a TRANSPARENT controlled preference margin for
leaving each original assignment, not a measured probability or task-quality loss.
All joint results are labeled controlled_sensitivity_analysis. Synthetic demand
and manual local margins remain synthetic even when communication costs are real.
No accuracy-preserving or end-to-end superiority claim follows from this oracle.

Cost units are bytes (default) or ms; lambda has local-loss units per cost unit.
objective_delta = graph objective minus baseline objective (negative favors oracle).
A strict reversal needs lambda * communication saving > additional local loss.
Pairwise break-even lambda and traffic thresholds at lambda=1 are in
reversal_thresholds.csv. first_reversal_candidate marks the earliest alternative;
other rows may be dominated and are not asserted to be globally selected. Equality retains baseline. The model is separable by
weighted incoming demand, so different graphs with the same incoming bucket mix
have the same objective. It models no contention, queueing, concurrency or load.
The exhaustive oracle enumerates 4^N with a default 1,048,576-assignment guard.

## Outputs

- results/raw/protocol_profile_{mode}.csv and .json: every requested attempt.
- results/raw/profile_manifest_{mode}.json: config, environment, SDK versions,
  original-source hashes and blockers; these are not embedded secrets.
- results/processed/protocol_costs.csv and mode-specific summaries: 16 conditions.
- results/processed/topology_blindness.csv: 24 graph/traffic checks.
- results/processed/decision_reversal.csv: 144 topology/traffic/lambda checks,
  including unchanged assignments to show the transition rather than cherry-pick.
- results/processed/reversal_thresholds.csv: exact alternative-switch thresholds.
- results/raw/local_router_output.json, topology_cases.json and experiment manifests.
- notes/validation.txt: exact tests and verification; findings.md separates evidence.
- results/figures/.gitkeep: reserved; no polished figure is generated.

Repeatability tests fix configs/seeds and measured cost tables. Measured timing
and oracle runtime are naturally variable and excluded from equality checks.
An experiment-local .gitignore includes results in the review inventory despite
its root ignore rule; no root .gitignore edit is needed.
Untracked files do not appear in ordinary git diff --stat; review the untracked
inventory and per-file no-index diff stats/check as well. Nothing is staged.
