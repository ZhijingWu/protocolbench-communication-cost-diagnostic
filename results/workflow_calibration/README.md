# Workflow-latency calibration — October 2026

This package contains existing-record evidence from one controlled local no-op session on **2026-10-09**. It is an independent extension of [ProtocolBench / AgentProtocols](https://github.com/ulab-uiuc/AgentProtocols), without affiliation with the original authors. It is a calibration diagnostic, not an algorithmic improvement or a new protocol-ranking claim.

## Research question

Can previously measured request-level communication costs predict end-to-end workflow makespan under controlled execution?

## Experimental design

Every application RPC carries 10,240 ASCII bytes (10 KiB) through real local client/server paths with deterministic no-op responders and no LLM inference. The receiver's assigned protocol determines transport. The fixed plans are:

| Receiver node | Baseline A | Treatment B |
|---|---|---|
| 0 | Agora | Agora |
| 1 | A2A | ANP |
| 2 | ACP | ACP |
| 3 | A2A | A2A |

`analysis_task` is serial: `0→1`, await completion, then `1→2`. The `2→final` marker is local termination, with no extra RPC. `collaborative_task` has two barrier-separated fork/join phases: concurrent `0→{1,2,3}`, wait for all, then three new concurrent `{1,2,3}→0` application RPCs. HTTP responses belong to their respective RPCs and are counted once.

Whole workflows execute sequentially. Each topology/plan cell has **5 excluded warmups and 30 measured executions**. Matched baseline/treatment runs are adjacent, indexed by topology and pair index. The schedule deterministically alternates AB/BA, **15 pairs of each order per topology**; workflow-priority order also alternates. This is balanced, not randomized.

| Dataset / cell | Measured workflows | Measured RPCs | Excluded warmup workflows / RPCs |
|---|---:|---:|---:|
| Serial / baseline | 30 | 60 | 5 / 10 |
| Serial / treatment | 30 | 60 | 5 / 10 |
| Fork/join / baseline | 30 | 180 | 5 / 30 |
| Fork/join / treatment | 30 | 180 | 5 / 30 |
| **Workflow total** | **120** | **480** | **20 / 80** |

The historical standalone dataset contains a **separate 480 measured requests and 80 warmup requests**, across A2A, ACP, ANP and Agora at 1–100 KiB. These are predictor inputs, not another 480 workflow RPCs. Its existing [cost table](../processed/real_protocol_costs.csv) is reused without duplication or refitting.

RPC latency brackets `BaseAgent.send`, including conversion, transport, server, no-op receipt and decoding. Workflow makespan brackets both scheduled phases and includes dispatch/observer/scheduling overhead. Payload preparation, endpoint setup and warmup samples are outside measured workflow summaries. Timestamps are monotonic `perf_counter_ns`, not Unix-epoch dates.

## Prediction and main results

The frozen historical 10 KiB mean RTTs (ms) are A2A 1.4698952333, ACP 1.3135204333, ANP 1.3133979333 and Agora 23.3858817333. The predictor sums edge means for communication work, and sums each stage's maximum edge mean for nominal DAG completion. It assumes zero agent compute and ideal within-stage overlap. A maximum of means is not an expected maximum of noisy simultaneous requests.

All differences below are **treatment minus baseline**; negative favors treatment.

| Workflow | Predicted aggregate work delta (ms) | Predicted DAG delta (ms) | Observed paired mean makespan delta (ms) | AB mean (ms) | BA mean (ms) |
|---|---:|---:|---:|---:|---:|
| Serial | −0.1564973 | −0.1564973 | **+0.8279372** | +0.982541 | +0.673334 |
| Fork/join | −0.1564973 | **0** | +2.299122 | +4.667984 | −0.069741 |

Serial observed mean makespans are 3.895017 ms (baseline) and 4.722954 ms (treatment), opposite to frozen predictions of 2.783416 and 2.626918 ms. This is a **single-session paired-mean ranking reversal**, not a predictor trained during that session, a speedup or a universal ordering. Of 30 pairs, 19 favor baseline and 11 treatment.

The parallel work saving does **not** predict a completion-time saving: an unchanged A2A branch determines the first-stage maximum and all return branches target Agora. Actual mean makespans are 47.296948 / 49.596069 ms. AB/BA mean signs disagree, with BA close to zero. Most of the pooled stage difference lies in the **unchanged Agora return stage** (mean stage completion spans 41.330970 / 43.511821 ms); it cannot be attributed entirely to the changed protocol. Client-send overlap does not establish parallel server CPU execution.

## Statistical interpretation and limitations

The 30 pair differences per topology are matched repeated executions, not simultaneous observations of both plans. The serial mean bootstrap interval is [0.293340, 1.333663] ms, while its paired median is +0.081879 ms with interval **[−0.028424, 1.897671] ms, including zero**. Mean and median results are distinct. Fork/join mean/median intervals are [1.210105, 3.387302] / [0.081927, 2.2107955] ms.

Intervals are descriptive 10,000-resample AB/BA-stratified percentile bootstraps of existing complete pairs, with fixed recorded seeds. They do not supply independent-session generalization, a causal order effect or a preregistered confirmatory test. Deterministic pair parity, workflow order and session progress are linked; drift, scheduling, queueing and observation overhead are possible explanations that this study did not isolate.

Scope: one local server session; deterministic no-op agents; frozen historical request profiles; nonrandomized order; no real GAIA task execution, task-quality outcome, production network evidence, general protocol ranking or independently demonstrated speedup. The original machine state, complete environment and original workflow YAML are not included, so this package does **not** claim full original-environment rerun reproducibility.

## Offline recalculation

From the repository root, with **Python 3.10+ and only its standard library**:

```sh
python results/workflow_calibration/scripts/recalculate.py
# Optional complete machine-readable calculations:
python results/workflow_calibration/scripts/recalculate.py --json
```

Paths are resolved relative to the script, so the command also works when invoked by absolute path from another directory. No installation, original remote server, SDK, network, model/API call or experimental-runner import is needed. No files are written. Missing or inconsistent inputs produce `FAIL` and exit 2, without falling back to saved summaries.

The script checks publication hashes, all raw workflow/RPC/stage/receipt identities, warmups, topology, complete adjacent AB/BA pairs, frozen predictions, means/medians/p95s, descriptive bootstrap intervals and consistency with retained derived tables. Six raw files and three original derived files are included. Their bytes are unchanged. The one historical dependency is the repository-relative cost table, verified against its frozen Git-blob SHA-256; Windows LF/CRLF checkout conversion is handled only for that declared dependency. This package's `.gitattributes` disables conversion to keep its own publication hashes exact.

## Provenance, excluded attempts and attribution

[experiment.json](config/experiment.json) is a **descriptive export of recorded manifest data**, not the missing original workflow YAML. It preserves fixed plans, instantiated stages, payloads, pairing and profile provenance. [source_hashes.json](provenance/source_hashes.json) retains the original manifest/source hashes without internal paths. [release_manifest.json](release_manifest.json) maps original files to publication files and records their hashes; it excludes itself from its own hash map to avoid self-reference. A checksum is evidence consistency, not an external signature/timestamp.

The recorded first smoke/preflight failed before business RPCs. A separately accepted smoke contains 4 workflows / 16 RPCs and is excluded from the full-run budget. The full session has zero recorded failed/retried/skipped business RPCs. Two post-results framework shutdown cancellation tracebacks are disclosed but are not failed measurement samples. Original console/runtime logs, full manifests, upstream code snapshots and the historical archive are retained privately rather than blindly published. [release_audit.md](provenance/release_audit.md) records selection, omissions, sanitation and validation.

This work uses [AgentProtocols at audited revision 6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f](https://github.com/ulab-uiuc/AgentProtocols/tree/6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f). Original authors retain attribution for code/design. See the preserved repository [MIT license](../../LICENSE) and [upstream attribution](../../UPSTREAM.md). The new offline calculator does not vendor/import the original runner or upstream source. It recalculates already recorded evidence and produces no new measurements.
