# Implementation and validation report

> Historical source-study record, made public-safe during packaging. Use the root README for current standalone commands. Source-time hashes and execution statements retain their original meaning; see PUBLICATION.md. Superseded outreach previews/v1 documents described here remain in the original study checkout; they are omitted from this artifact.


Repository: <UPSTREAM_ROOT>, branch
exp/topology-aware-protocol-routing, HEAD
6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f (unchanged).

All work is new and confined to experiments/topology_aware_protocol.
Original tracked files modified: 0. Staged files: 0. No commits, pushes, stashes
or resets. The experiment-local .gitignore exposes its results for review.

## Results and limits
- Real attempt: 560 requested rows (80 warmup, 480 measured), all setup-blocked
  by missing uvicorn. No requests sent, no measured network latency, no fake zeros.
- Conversion-only: 480/480 measured successes, 16 conditions, original converter
  and JSON metric sizes measured. Successful conversion timings are not latency.
- Original GAIA heuristic fallback reinvoked for 24 graph/traffic cases: 0 changes.
  Joint optimization consumes its saved assignment; no fresh LLM call is asserted.
- Exhaustive 256-assignment oracle at each of 144 sweep cases: 60 strict reversals
  using measured encoded-byte costs with explicitly manual local margin=1.
  These are controlled sensitivity results, not empirical end-to-end improvements.
- Unit per-edge chain: A2A->Agora threshold 1/150 and ACP->Agora 1/145 loss/byte.
  lambda=0.001 unchanged; lambda=0.01 changes nodes 1,2,3, objective_delta=-1.45.
- 27 unittest tests passed: exact log in notes/validation.txt (27 tests in 0.128s,
  OK). pytest was unavailable; no installation was performed.
- Independent audit checked raw/processed statistics, source hashes and arithmetic
  for all 144 results. End-to-end reruns yielded identical assignments/objective
  values and byte-identical topology table, excluding runtime_seconds.
  Details in notes/integrity_checks.json.

## Reproduce
From the repository root:

```bash
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
PY=<UNUSED_PYTHON_ENV>/bin/python
$PY scripts/run_protocol_profile.py --mode real
# Expected current blocker exit is 2; do not let it suppress the separate run.
$PY scripts/run_protocol_profile.py --mode conversion-only
$PY scripts/run_topology_blindness.py
$PY scripts/run_joint_assignment.py --profile-mode conversion-only
$PY -m unittest discover -s tests -v
```

Full SDK/server execution additionally needs missing runtime packages (uvicorn,
a2a-sdk, acp-sdk, agora-protocol, agent-connect, pynvml; consult profile manifest)
and actual running original protocol servers configured in microbench.yaml.
Servers must echo the unique request probe token, and ANP needs a valid target DID.
The supplied real profiler is endpoint-driven and does not fabricate a server or
response. Security, task quality, concurrent load and GAIA graph execution remain
unverified; no unsupported mismatch penalty is used.

## Git verification
`git diff --stat`: exit 0, empty because every experiment file is untracked.
`git diff --check`: exit 0, no output.
`git diff HEAD --name-only`: empty; confirms all original tracked files unchanged.
All new files also pass `git diff --no-index --check /dev/null FILE`.
Supplemental no-index inventory below accounts for files omitted by ordinary diff.

## New-file inventory

| Path below experiment directory | New lines | Bytes |
|---|---:|---:|
| .gitignore | 3 | 99 |
| README.md | 148 | 8970 |
| configs/microbench.yaml | 14 | 517 |
| configs/topology_cases.yaml | 20 | 926 |
| notes/change_report.md | 60 | 3349 |
| notes/experiment_design.md | 155 | 9427 |
| notes/findings.md | 93 | 5704 |
| notes/integrity_checks.json | 21 | 549 |
| notes/validation.txt | 32 | 3124 |
| results/figures/.gitkeep | 0 | 0 |
| results/processed/decision_reversal.csv | 145 | 65995 |
| results/processed/protocol_costs.csv | 17 | 2164 |
| results/processed/protocol_costs_conversion-only.csv | 17 | 2164 |
| results/processed/protocol_costs_real.csv | 17 | 973 |
| results/processed/reversal_thresholds.csv | 121 | 14805 |
| results/processed/topology_blindness.csv | 25 | 8794 |
| results/raw/joint_manifest.json | 140 | 4543 |
| results/raw/local_router_output.json | 65 | 1448 |
| results/raw/profile_manifest_conversion-only.json | 66 | 3197 |
| results/raw/profile_manifest_real.json | 87 | 3650 |
| results/raw/protocol_profile_conversion-only.csv | 561 | 62137 |
| results/raw/protocol_profile_conversion-only.json | 8402 | 220467 |
| results/raw/protocol_profile_real.csv | 561 | 66673 |
| results/raw/protocol_profile_real.json | 8402 | 229483 |
| results/raw/topology_cases.json | 2294 | 47564 |
| results/raw/topology_manifest.json | 108 | 3695 |
| scripts/run_joint_assignment.py | 182 | 12512 |
| scripts/run_protocol_profile.py | 46 | 2549 |
| scripts/run_topology_blindness.py | 53 | 3301 |
| src/graph_aware_oracle.py | 63 | 3628 |
| src/io_utils.py | 112 | 4074 |
| src/local_router_adapter.py | 56 | 2653 |
| src/objective.py | 83 | 3869 |
| src/protocol_cost_profiler.py | 249 | 12513 |
| src/topology_generator.py | 48 | 2307 |
| tests/test_graph_aware_oracle.py | 95 | 5157 |
| tests/test_objective.py | 130 | 6375 |
| tests/test_topology_generator.py | 74 | 3684 |

38 new files. Inventory counts for this report are from immediately before inserting this table.
