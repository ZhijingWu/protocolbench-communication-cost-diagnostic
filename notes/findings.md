# Findings: topology-aware protocol diagnostic

> Historical source-study record, made public-safe during packaging. Use the root README for current standalone commands. Source-time hashes and execution statements retain their original meaning; see PUBLICATION.md. Superseded outreach previews/v1 documents described here remain in the original study checkout; they are omitted from this artifact.


## A. Directly observed in original code
See experiment_design.md for exact paths/functions and source snippets. The
GAIA assignment interface takes task_analysis and agents_config without explicit
graph or edge traffic. Its audited caller supplies no LLM client, so the existing
heuristic fallback is the measured baseline. Destination assigned_protocol selects
outbound adapters. No pairwise mismatch penalty is supported by this audit.
Core AgentNetwork has a graph; GAIA deliver bypasses its edge permission check.

Baseline consumption: saved_routing_output_replay; original fixed-feature assignment remains
0=Agora, 1=A2A, 2=ACP, 3=A2A. The saved local-input hash is
7feebac851b3efda55198539da729651b1fddf7b1fe6abc9ac2e97e44ac5b835. Topology/traffic variation did not change this
baseline in the existing 24-case diagnostic. No baseline was regenerated here.

## B. Measured communication evidence and data interface
Real latency values are measured end-to-end LOCAL request costs from the verified real profiler. No profiling was rerun and no means, medians, p95 values or byte values were recomputed.
Canonical oracle input: protocol_costs.csv; mode=real; metric=mean_latency_ms.
Measurement kind: end_to_end_local_request; ANP and Agora are the existing repository HTTP paths.

The verified real source remains results/processed/real_protocol_costs.csv,
traceable to results/raw/real_protocol_profile.csv and real_protocol_manifest.json.
The source has 30 successful measured requests per protocol/size, with 5 warmups
excluded. Request timing surrounds original BaseAgent.send; startup is separate.
Canonical real rows copy measured latency strings unchanged, map
successful_requests to success_count and mean_encoded_request_bytes to
mean_encoded_bytes, and derive only failure_rate = failures / attempted_requests.
Real conversion-runtime columns stay empty. Real bytes are actual HTTP body bytes,
excluding headers; historical conversion bytes are the converter-boundary JSON size.

results/raw/cost_interface_manifest.json records source/raw/manifest hashes,
canonical output hashes and archives. protocol_costs.csv retains unchanged
conversion-only rows alongside mode=real rows; the existing loader filters modes.
protocol_costs_real.csv now contains verified successful canonical real rows.
Its superseded zero-success table is archived under results/raw/cost_interface_archive/;
the earlier profile_manifest_real.json and failed raw profiles are preserved.
No conversion-only value substitutes for a missing real cost.

## C. Controlled sensitivity analysis
Topology and traffic are CONTROLLED inputs, and local routing margins remain
SYNTHETIC sensitivity inputs: margin=1.0 local-loss units
for leaving the baseline. Confidence=0.3 is not used as a calibrated candidate loss.
This is NOT a GAIA end-to-end improvement result. No task quality, task success,
quality-preserving protocol change or universal advantage is established.

The objective, margins, topology cases, baseline, enumeration and tie policy are
unchanged. J = local loss + lambda * sum(edge weight * destination protocol cost).
Every case enumerates all 256 assignments. For latency, cost units are ms and
lambda is local-loss units/ms. Traffic weights are expected message counts.
Per-edge and equal-total controls are both included; counts below combine them.
The destination-only model is separable by incoming demand, without queueing or
contention. It uses stored cost point estimates, not a significance test of close
latency rankings. objective_delta is graph minus baseline, negative for improvement
ONLY in this stated sensitivity objective.

Total cases: 144; strict reversal cases: 37.
By topology (case counts): {'chain': 1, 'full_mesh': 9, 'hotspot': 15, 'star': 12}.
By traffic scale (case counts): {'1': 6, '10': 12, '100': 19}.
By traffic normalization (case counts): {'equal_total': 15, 'per_edge': 22}.
Changed-from protocols (node events): {'A2A': 8, 'ACP': 0, 'ANP': 0, 'Agora': 36}.
Changed-to protocols (node events): {'A2A': 0, 'ACP': 0, 'ANP': 44, 'Agora': 0}.
There are 44 changed-node events. Per-protocol CASE counts
(which may overlap) and witness assignments are in reversal_summary.json.

Every reversal involves an Agora change: False.
Cases with Agora changes: 36; without: 1.
Any change TO Agora: False.
Any A2A/ACP/ANP-only reversal: True.
Here "only" describes changed protocols; an unchanged baseline Agora node is allowed.

Minimum traffic_scale with a strict reversal: 1.0,
at lambda=0.01.
Minimum lambda with a strict reversal: 0.0001,
at traffic_scale=100.0.
These are separate minima within the unchanged finite grid, not asserted continuous
thresholds or a single jointly attained minimum. Exact model break-even thresholds
remain in reversal_thresholds.csv; equality is a tie and baseline ties are retained.

| Topology | Normalization | Scale | Lambda | Changed nodes | Objective delta |
|---|---|---:|---:|---|---:|
| chain | per_edge | 100.0 | 0.1 | ["1", "3"] | -1.12995 |
| star | per_edge | 1.0 | 0.1 | ["0"] | -5.62175 |
| star | per_edge | 10.0 | 0.01 | ["0"] | -5.62175 |
| star | per_edge | 10.0 | 0.1 | ["0"] | -65.2175 |
| star | per_edge | 100.0 | 0.001 | ["0"] | -5.62175 |

## D. Unsupported / not yet verified
GAIA end-to-end task improvements, calibrated local accuracy losses, fresh LLM
routing, concurrency/queueing behavior and security properties. ANP costs are for
its current HTTP request implementation; Agora costs are for its direct HTTP/no
model path. They are not measured WebSocket/E2E or protocol-negotiation costs.
No figures, new routing methods or benchmark changes were introduced.

## Reproduction, validation and preserved history
Run the existing oracle with --profile-mode real --cost-metric mean_latency_ms
using python. Real mode prepares canonical rows
from the already verified sources; it does not call the profiler. All regression
tests, including both profile modes, are recorded in notes/cost_interface_validation.txt.
New source measurements and the prior baseline/config/objective hashes remain
unchanged; see cost_interface_before.json and final verification notes.
Prior oracle outputs replaced by this mode/metric change are preserved:
- results/processed/decision_reversal.csv -> results/raw/joint_output_archive/a2eefdc97afa4f569a4dda4eddeed51aab546aa5a4f00d08a9b3140ec05b04cc/decision_reversal.csv (SHA256 a2eefdc97afa4f569a4dda4eddeed51aab546aa5a4f00d08a9b3140ec05b04cc)
- results/processed/reversal_thresholds.csv -> results/raw/joint_output_archive/237a11fadb06fec17043f6c695605e3d07cd1a7db0f34f8748b6ccecc3e27dc3/reversal_thresholds.csv (SHA256 237a11fadb06fec17043f6c695605e3d07cd1a7db0f34f8748b6ccecc3e27dc3)
- results/raw/joint_manifest.json -> results/raw/joint_output_archive/1233150d85156166f5aaacac0221b3df99017840ad1eb41e66e5ebe1a66df523/joint_manifest.json (SHA256 1233150d85156166f5aaacac0221b3df99017840ad1eb41e66e5ebe1a66df523)
- notes/findings.md -> results/raw/joint_output_archive/aa0edd44c80a585788e5170945f06068b67cbc8c653e27fb953a72ef3e8b9f79/findings.md (SHA256 aa0edd44c80a585788e5170945f06068b67cbc8c653e27fb953a72ef3e8b9f79)

<!-- gaia-workflow-section:start -->
## Repository-defined GAIA workflow structures

Protocol latencies are measured locally. The workflow structure comes from the
official scenarios/gaia/config/meta_protocol.yaml message_flow_patterns, parsed
directly without editing it. Traffic scaling remains controlled, and local
preference margins remain synthetic (unchanged margin=1). This is still not an
end-to-end GAIA task-quality result. No LLM, GAIA task or new routing method ran.

The fixed baseline is 0=Agora, 1=A2A, 2=ACP, 3=A2A. Payload size stays 10 KB;
traffic scales 1/10/100, lambda grid and per-edge/equal-total controls are reused.
protocol_preference and reason remain metadata and never enter local losses.

analysis_task retains the exact 0->1, 1->2, 2->final structure. final is a
terminal output marker: MeshNetwork.execute_workflow assigns final_result and
breaks; it is not another assigned agent. Thus only 0->1 and 1->2 enter the
agent-communication objective. The final event is retained in output metadata;
no agent 3 edge or unmeasured final-output cost is invented.

collaborative_task retains 0->all and all->0, instantiated as 0<->1/2/3 over
the unchanged four-agent roster, excluding hub self-messages. This explicit
peer broadcast/aggregation convention mirrors core star topology handling;
the literal official steps and expansion are preserved in the graph manifest.
MeshNetwork executes workflow.message_flow, not these named templates directly:
these are config-grounded demand structures, not captured GAIA runtime traffic.

Global removal of Agora makes original agent 0's baseline infeasible. Its
mandatory replacement is labeled forced_removal, never a preference reversal.
The existing exhaustive oracle uses a separately reported feasible enumeration
seed (agent 0=A2A, first tied minimum-loss allowed protocol); the ORIGINAL
baseline remains the comparison reference, and no saved assignment or local
margin changes. Allowed losses copy the original entries exactly. Relative
scores to both original baseline and feasible seed are reported separately.

A strict assignment reversal means the constrained assignment beats the
original baseline objective. An eligible preference reversal means an agent
whose baseline protocol was still allowed changes only when weighted incoming
communication saving exceeds its original margin. The latter avoids counting
forced removal or tie selection as evidence. Eligible A2A/ACP/ANP changes
can persist even if the forced removal penalty prevents beating the original,
now-infeasible baseline for the whole assignment.

| Workflow | Candidates | Cases | Strict vs original | Eligible preference cases | A2A/ACP/ANP preference cases |
|---|---|---:|---:|---:|---:|
| analysis_task | all_four | 36 | 1 | 1 | 1 |
| analysis_task | without_agora | 36 | 0 | 1 | 1 |
| collaborative_task | all_four | 36 | 12 | 12 | 1 |
| collaborative_task | without_agora | 36 | 12 | 1 | 1 |

Grid minima and assignments (minimum scale and minimum lambda may occur in
different cases; no continuous threshold is inferred from a finite grid):

- analysis_task, all_four: strict-original minima {'minimum_traffic_scale': 100.0, 'minimum_lambda': 0.1, 'minimum_lambda_at_minimum_traffic_scale': 0.1, 'minimum_traffic_scale_at_minimum_lambda': 100.0}; eligible preference minima {'minimum_traffic_scale': 100.0, 'minimum_lambda': 0.1, 'minimum_lambda_at_minimum_traffic_scale': 0.1, 'minimum_traffic_scale_at_minimum_lambda': 100.0}.
  Assignments: [{'0': 'Agora', '1': 'A2A', '2': 'ACP', '3': 'A2A'}, {'0': 'Agora', '1': 'ANP', '2': 'ACP', '3': 'A2A'}].
- analysis_task, without_agora: strict-original minima {'minimum_traffic_scale': None, 'minimum_lambda': None, 'minimum_lambda_at_minimum_traffic_scale': None, 'minimum_traffic_scale_at_minimum_lambda': None}; eligible preference minima {'minimum_traffic_scale': 100.0, 'minimum_lambda': 0.1, 'minimum_lambda_at_minimum_traffic_scale': 0.1, 'minimum_traffic_scale_at_minimum_lambda': 100.0}.
  Assignments: [{'0': 'A2A', '1': 'A2A', '2': 'ACP', '3': 'A2A'}, {'0': 'A2A', '1': 'ANP', '2': 'ACP', '3': 'A2A'}].
- collaborative_task, all_four: strict-original minima {'minimum_traffic_scale': 1.0, 'minimum_lambda': 0.001, 'minimum_lambda_at_minimum_traffic_scale': 0.1, 'minimum_traffic_scale_at_minimum_lambda': 100.0}; eligible preference minima {'minimum_traffic_scale': 1.0, 'minimum_lambda': 0.001, 'minimum_lambda_at_minimum_traffic_scale': 0.1, 'minimum_traffic_scale_at_minimum_lambda': 100.0}.
  Assignments: [{'0': 'ANP', '1': 'A2A', '2': 'ACP', '3': 'A2A'}, {'0': 'ANP', '1': 'ANP', '2': 'ACP', '3': 'ANP'}, {'0': 'Agora', '1': 'A2A', '2': 'ACP', '3': 'A2A'}].
- collaborative_task, without_agora: strict-original minima {'minimum_traffic_scale': 1.0, 'minimum_lambda': 0.001, 'minimum_lambda_at_minimum_traffic_scale': 0.1, 'minimum_traffic_scale_at_minimum_lambda': 100.0}; eligible preference minima {'minimum_traffic_scale': 100.0, 'minimum_lambda': 0.1, 'minimum_lambda_at_minimum_traffic_scale': 0.1, 'minimum_traffic_scale_at_minimum_lambda': 100.0}.
  Assignments: [{'0': 'A2A', '1': 'A2A', '2': 'ACP', '3': 'A2A'}, {'0': 'ANP', '1': 'A2A', '2': 'ACP', '3': 'A2A'}, {'0': 'ANP', '1': 'ANP', '2': 'ACP', '3': 'ANP'}].

Full changed-node/protocol evidence, forced changes, original baseline, feasible
seed, objective values and witnesses are in results/processed/gaia_workflow_reversal.csv
and gaia_workflow_summary.json. Official patterns, final/all handling, source
hashes and controlled weighted graphs are retained. Stored mean latencies are
point estimates; tiny ANP/ACP differences do not establish statistical superiority.
Previous synthetic-topology diagnostics remain preserved as historical outputs.
<!-- gaia-workflow-section:end -->
