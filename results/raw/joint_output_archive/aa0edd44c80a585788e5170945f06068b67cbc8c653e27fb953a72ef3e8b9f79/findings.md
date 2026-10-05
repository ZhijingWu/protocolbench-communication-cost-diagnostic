# Findings: topology-aware protocol diagnostic

> Historical source-study record, made public-safe during packaging. Use the root README for current standalone commands. Source-time hashes and execution statements retain their original meaning; see PUBLICATION.md. Superseded outreach previews/v1 documents described here remain in the original study checkout; they are omitted from this artifact.


> Communication update: the local real benchmark now succeeded for all four
> protocols (480/480 measured requests). See notes/real_microbench.md and
> results/processed/real_protocol_costs.csv. The sections below preserve the
> earlier conversion-based topology experiment and its then-current blockers.

## A. Directly observed in original code
See experiment_design.md for exact paths/functions and source snippets. GAIA
assignment exposes task_analysis and agents_config, without graph/edge traffic.
The audited network constructs GAIALLMRouter without a client, invoking the
original heuristic fallback. Destination assigned_protocol selects outbound
adapters; BaseAgent.send records existing request timing and encoded JSON size.
AgentNetwork has a directed graph but GAIA delivery bypasses its edge check.
No pairwise protocol mismatch penalty is supported by this audit.

## B. Measured experimentally
Topology baseline measured source: heuristic_fallback.
Joint oracle baseline consumption: saved_routing_output_replay. The same local feature hash and
prompt hash are checked for all 24 graph/traffic cases. The produced
results/processed/topology_blindness.csv reports actual original fallback
reinvocations (or explicitly labeled saved-output replay), not fresh LLM trials.

Cost source: protocol_costs.csv; mode=conversion-only; metric=mean_encoded_bytes.
Conversion-only profiles measure real original converter plus serialization
runtime and original boundary JSON bytes; network latency columns remain empty.
The standard profile uses 5 warmups plus 30 measured attempts at each of 4 sizes
for each of 4 protocols. Warmups are excluded; p95 is linear interpolation;
means are successful-attempt statistics. Consult raw CSV/JSON and manifests
for errors, counts, environment and source SHA256. These are measured costs of
a controlled ASCII payload, not GAIA task execution or packet capture.

Real network latency measured in attempted real run: False.
Observed real-mode blockers (setup-blocked rows were NOT sent):
- A2A: ModuleNotFoundError: No module named 'uvicorn'
- ACP: ModuleNotFoundError: No module named 'uvicorn'
- ANP: ModuleNotFoundError: No module named 'uvicorn'
- Agora: ModuleNotFoundError: No module named 'uvicorn'

## C. Synthetic / controlled sensitivity analysis
All oracle results use generated demand graphs and EXPLICIT manual local losses,
with margin=1.0 loss units for any alternative.
There are 144 sweep cases, 60 strict reversals.
Costs are measured from the stated mode; graph demand and preference margins
are controlled inputs. No empirical router quality loss, probability-derived
margin, task accuracy, or end-to-end performance advantage is asserted.

J = local loss + lambda * sum(edge weight * destination-protocol cost).
Cost units are bytes for mean_encoded_bytes, ms for latency/conversion metrics;
lambda is loss units per corresponding cost unit. objective_delta is graph minus
baseline, so negative values indicate improvement ONLY for this stated objective.
Every four-node case enumerates all 256 assignments, retaining baseline ties.
The separable destination-only model depends on weighted incoming demand; graphs
with the same per-node incoming demand and bucket mix have identical objectives.
Equal-total demand controls accompany per-edge traffic cases to expose density
confounding. Fractional traffic weights denote expected message counts.

| Topology | Scale | Lambda | Changed nodes | Objective delta |
|---|---:|---:|---|---:|
| chain | 1.0 | 0.01 | ["1", "2", "3"] | -1.45 |
| chain | 1.0 | 0.1 | ["1", "2", "3"] | -41.5 |
| chain | 10.0 | 0.001 | ["1", "2", "3"] | -1.45 |
| chain | 10.0 | 0.01 | ["1", "2", "3"] | -41.5 |
| chain | 10.0 | 0.1 | ["1", "2", "3"] | -442 |

Exact per-node pairwise break-even thresholds are in reversal_thresholds.csv.
first_reversal_candidate marks the earliest alternative that overtakes baseline;
other alternative rows are not necessarily selected globally because a cheaper
alternative may already dominate. At unit per-edge chain traffic, nodes 1 and 3
have an A2A-to-Agora threshold of 1/150 = 0.00666667 loss/byte; node 2 has an
ACP-to-Agora threshold of 1/145 = 0.00689655. The sweep brackets both between
lambda=0.001 (unchanged) and 0.01 (changed). At lambda=0.01 the corresponding
traffic thresholds are 2/3 and 20/29 expected messages. These are controlled
manual-margin examples using measured serialization costs, not network claims.

Threshold formula:
lambda_threshold = local_margin / incoming_comm_saving, with strict reversal
above the threshold and equality a tie. traffic_threshold_at_lambda is reported
at lambda=1; divide by another positive lambda to obtain its traffic threshold.
A faster/cheaper alternative is not always selected below the threshold.

## D. Unsupported / not yet verified
Fresh LLM routing behavior and calibrated candidate losses; real four-protocol
server round trips in the current environment; GAIA execution under each generated
graph; queueing/contention, concurrent workload, actual wire bytes, ANP security
properties and quality-preserving protocol changes. The real profiler additionally
requires running original servers that echo the unique request probe token;
endpoint settings are intentionally unset. It rejects missing acknowledgements
and known Agora fallback/error strings, which original counters can miss.
Even with installed dependencies, endpoint readiness and response semantics need
verification. No fabricated or imputed costs replace unavailable conditions.

## Validation and reproduction
See README.md for commands; tests use unittest (also pytest-compatible) because
pytest is missing in the remote environments inspected. Exact executed results
are recorded in notes/validation.txt. Timing is environment-dependent; repeatability
means identical assignments/objective outputs given identical cost/config files,
excluding observed timing fields. No polished figures are produced.
