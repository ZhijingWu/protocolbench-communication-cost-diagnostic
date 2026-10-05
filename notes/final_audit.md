# Final research audit: topology-aware protocol assignment

> Historical source-study record, made public-safe during packaging. Use the root README for current standalone commands. Source-time hashes and execution statements retain their original meaning; see PUBLICATION.md. Superseded outreach previews/v1 documents described here remain in the original study checkout; they are omitted from this artifact.


Audit date: 2026-10-05, Asia/Shanghai.
Repository: <UPSTREAM_ROOT>.
Experiment: this standalone artifact.
Baseline/current HEAD: 6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f.
Branch: exp/topology-aware-protocol-routing.

This audit inspected saved data and source, independently checked arithmetic and
provenance, and ran the full existing tests once. It did not rerun profiling or
add experiments. No scientific value, graph, margin, baseline, objective, candidate
set or result was changed. Only this note and notes/final_audit_tests.txt are new
audit deliverables. Source references below are relative to the repository root;
E/ denotes this artifact root; other source paths denote the compatible upstream checkout.

## A. Source-code claim audit

| Statement | Classification | Exact evidence and scope |
|---|---|---|
| 1. Audited GAIA assignment uses task/agent-local inputs without directly conditioning on graph/edge traffic. | VERIFIED | scenarios/gaia/protocol_backends/meta_protocol/network.py:456, MetaProtocolNetwork._assign_protocols_with_llm_router: creates GAIALLMRouter at 463; calls route_gaia_task(task_analysis, agents_config) at 489–492. llm_router.py:312–331, GAIALLMRouter._create_gaia_user_prompt: extracts task_type, complexity, required_tools, domain_areas and agent id/name/tool/role/port. No explicit graph, edge counts, payload sizes or measured costs are supplied. |
| 2. Runtime communication/network structure is maintained separately. | PARTIALLY VERIFIED | src/core/network.py:21–25, AgentNetwork.__init__, owns _graph; connect_agents at 55–67 manages topology separately from adapters; route_message at 140–154 enforces edges. GAIA instead extends MeshNetwork, with connections=[] at scenarios/gaia/core/network.py:57 and workflow.message_flow read at 225. MetaProtocolNetwork.deliver calls BaseAgent.send directly at network.py:376. Separate structure exists, but active AgentNetwork graph enforcement in this GAIA delivery path is not established. |
| 3. Destination assigned_protocol affects incoming communication path. | VERIFIED | MetaProtocolNetwork._install_outbound_adapters at scenarios/gaia/protocol_backends/meta_protocol/network.py:603–676 reads dst_protocol at 618, selects the corresponding client adapter, then installs it under the destination BaseAgent ID. src/core/base_agent.py:872, add_outbound_adapter, and send at 889–952 use that adapter and its codec. Conditional on successful initialization; failures can leave an adapter unavailable. |
| 4. Request-level latency/message-size metrics already exist. | VERIFIED | src/core/metrics.py:23–39 defines REQUEST_LATENCY, MSG_BYTES and REQUEST_FAILURES; MetricsTimer uses perf_counter. BaseAgent.send at src/core/base_agent.py:941–956 times adapter/byte-accounting/decode, increments encoded JSON bytes and records exceptions. Original MSG_BYTES is not complete wire size. |
| 5. Official config includes analysis_task and collaborative_task patterns. | VERIFIED | scenarios/gaia/config/meta_protocol.yaml:109–117, workflow.message_flow_patterns. Literal records are checked in section D. |

Decisive original caller:

~~~python
llm_router = GAIALLMRouter()
routing_decision = await llm_router.route_gaia_task(
    task_analysis=task_analysis, agents_config=agents_config)
~~~

GAIALLMRouter.route_gaia_task uses _fallback_routing when no client is present
(llm_router.py:165–166). This caller supplies none. _fallback_routing at 356–389
maps tool types and reports heuristic_fallback. Thus the experimental baseline
is the original released heuristic output, not a fresh LLM routing trial.

The scope is a direct structured-input omission. Free-text roles/task descriptions
could indirectly mention topology. RouterBench has a different module-level
interface: routerbench/prompt_template.py:325, format_scenario_prompt, forwards
descriptions/tasks/issues. Absence of all possible topology information across
every ProtocolRouter interface is not demonstrated.

## B. Measurement audit

**VERIFIED for the saved local implementation microbenchmark.**

Each of A2A, ACP, ANP and Agora has exactly four buckets: 1024, 10240, 51200 and
102400 ASCII text bytes. Here KB is a 1024-based label. Each condition has measured
indices 0–29 and warmup indices 0–4. Counts are:

- 4 × 4 × 30 = **480 measured requests, 480 successes**.
- 4 × 4 × 5 = **80 warmups**, also successful.
- **560 unique raw records**, with warmups excluded from summaries.
- No final setup, request or cleanup failure record.

Independent saved-data calculations reproduced all means, medians, linearly
interpolated p95 values, sample standard deviations (ddof=1) and mean received
HTTP-body byte counts. This arithmetic check did not rewrite or rerun measurements.

### Exact mean latency table, ms

All 16 values match the supplied table exactly as saved strings; no discrepancy.

| Protocol | 1 KB | 10 KB | 50 KB | 100 KB |
|---|---:|---:|---:|---:|
| A2A | 1.3585756 | 1.4698952333333333 | 1.9828458666666666 | 2.707684433333333 |
| ACP | 1.2176304666666666 | 1.3135204333333332 | 1.8806641333333334 | 2.608613 |
| ANP | 1.3194534 | 1.3133979333333334 | 1.7973076 | 6.2451045 |
| Agora | 23.70959746666667 | 23.38588173333333 | 26.200420033333334 | 26.8474713 |

### Timing and path validation

E/src/local_protocol_microbench.py:277, LocalSession.sample, prepares its input
before starting perf_counter_ns at 291, awaits the original BaseAgent.send via
asyncio.wait_for at 293, and ends the timer at 297. All 560 saved latencies equal
(end_ns-start_ns)/1e6 exactly. They include scheduling plus UTE creation, encoding,
real adapter/server/no-op processing/response and decoding; they are not
serialization-only timings. The original request histogram is separately retained
and fits within the outer interval. All timing sanity flags pass.

profile_one_protocol at lines 343–374 awaits LocalSession.open before entering
warmup/measured loops. Setup includes imports, server readiness and adapter
initialization, outside sample's timer. Setup ms:
A2A 1907.941015; ACP 2002.874017; ANP 2395.489563; Agora 1927.650991.

EchoReceipts.acknowledge at lines 66–71 hashes the full input text and returns its
byte count/SHA256. SDKNoopExecutor.execute, ACPNoopExecutor.__call__,
ANPNoopExecutor.answer and the Agora answer callback invoke that deterministic
responder. ServerBodyObserver at 117–135 forwards original ASGI events unchanged;
the Flask observer at 219–222 reads the original HTTP body. Success checks at
305–313 require one server POST, one responder call and the correct count/digest
in the decoded response, plus the timing guard. All raw rows record those checks.

Source inspection shows observers attached to the actual local servers and
original adapters addressed to those servers. This supports the intended
controlled local round trip, rather than accepting a fabricated fallback string.
It is not independent packet-capture, standard-compliance or adversarial identity
verification evidence.

### Implementation and measurement limits

A2A uses original A2AAdapter/A2AStarletteApplication /message with its SDK executor;
ACP uses ACPAdapter/ACPStarletteApplication /acp/message with an async generator.

ANPAdapter.send_message in src/agent_adapters/anp_adapter.py:1026–1132 directly
POSTs /anp/message. ANPSimpleNodeWrapper._create_http_app at
src/server_adapters/anp_adapter.py:385–422 invokes its supplied answer callback.
These are HTTP request costs, not measured WebSocket/E2E costs.

AgoraClientAdapter._simple_send in src/agent_adapters/agora_adapter.py:75–115
creates a new HTTP client/event loop/thread; AgoraServerWrapper's original
/message handler at src/server_adapters/agora_adapter.py:470–495 invokes the
deterministic answer callback. No model negotiation or generated routine is used.
This different connection/thread behavior is part of the measured implementation
cost; the table does not establish intrinsic protocol-standard rankings.

encoded_request_bytes is received HTTP body size excluding headers.
ute_encoded_bytes retains the original converted-envelope MSG_BYTES boundary.
The canonical real mean_encoded_bytes copies mean_encoded_request_bytes;
conversion-only rows retain a different documented boundary. Modes must stay explicit.

The ANP 100 KB maximum is 107.861652 ms, median 2.3997365 ms,
and sample SD 19.216113718930764 ms. The outlier was retained. The 10 KB ACP–ANP
mean gap is approximately 0.0001225 ms, compared with sample SDs
0.04210521539542819 and 0.04010519661567075 ms. ANP is the stored point-estimate
winner, not statistically established as faster than ACP. This is one local,
sequential profiling campaign, with no demonstrated cross-host/load robustness.
No-op task processing is explicit; real GAIA LLM/tool processing is excluded.

## C. Controlled graph experiment audit

Classification: **CONTROLLED SENSITIVITY ANALYSIS**, not GAIA improvement.

Audited decision_reversal.csv, reversal_summary.json and reversal_thresholds.csv:

| Check | Verified value |
|---|---|
| Total cases / strict reversals | 144 / 37 |
| Topology case counts | chain 1; star 12; full_mesh 9; hotspot 15 |
| Traffic-scale case counts | 1: 6; 10: 12; 100: 19 |
| Changed-from nodes | A2A 8; Agora 36; ACP 0; ANP 0 |
| Changed-from cases | A2A 4; Agora 36; ACP 0; ANP 0; counts overlap |
| Changed-to nodes | ANP for all 44 |
| A2A-only witness | chain, per_edge, scale 100, lambda 0.1 |

The witness assignment is {0: Agora, 1: ANP, 2: ACP, 3: ANP}.
Agora remains unchanged. Weighted saving is 3.129946 loss units versus local
replacement loss 2; objective_delta is −1.1299459999999897.

For all 144 rows, reconstructing the saved controlled graph/config and using
stored means reproduced costs, losses and objective deltas. An independent
separable per-node lower bound agrees with recorded optimal objectives.
All **174 threshold rows** reproduce margin/incoming-cost-saving and the
declared traffic threshold at lambda=1.

Counts combine per-edge and equal-total controls, whose traffic-scale meanings
differ. Neither is a measured GAIA trace. This destination-only additive model
depends on per-node weighted incoming demand/bucket mix and is separable. It
does not establish the need for a learned graph method or arbitrary relational
coupling; equal incoming-demand vectors give equal modeled costs.

## D. Repository-defined GAIA workflow audit

### Literal structures: VERIFIED

The original YAML has exactly:

~~~text
analysis_task:       0 -> [1]; 1 -> [2]; 2 -> final
collaborative_task:  0 -> all; all -> 0
~~~

E/src/gaia_workflow.py:10–15, load_official_patterns, parses these original records.
Protocol preference/reason metadata is retained and never added to local losses.

The final output convention is grounded in
scenarios/gaia/core/network.py:MeshNetwork.execute_workflow, lines 257–260:
assign final_result and break. instantiate_workflow retains 2->final as a terminal
event outside the inter-agent objective, with no final-agent protocol/cost or
invented 2->3 edge.

The all expansion to peers 1/2/3 in the unchanged four-agent roster, excluding hub
self-messages, is **a disclosed experiment convention**. It is consistent with
AgentNetwork.setup_star_topology self-exclusion, but is not a verified executed
GAIA wildcard expansion. MeshNetwork.execute_workflow reads workflow.message_flow
at line 225, not the named templates, and does not implement equivalent all
broadcast/aggregation in that loop. Literal templates are VERIFIED; actual
executed GAIA communication graphs are NOT VERIFIED. Say “official configuration
templates instantiated under disclosed conventions,” not “observed GAIA traces.”

### Four-protocol results: VERIFIED

| Workflow | Strict reversals | Changes | Grid minima |
|---|---:|---|---|
| analysis_task | 1/36 | Agent 1: A2A→ANP | per_edge scale 100, lambda 0.1 |
| collaborative_task | 12/36 | Agent 0: Agora→ANP; agents 1 and 3 also change at per_edge scale 100/lambda 0.1 | Scale 1 at lambda 0.1; minimum lambda 0.001 at scale 100 |

Baseline: {0: Agora, 1: A2A, 2: ACP, 3: A2A}.
Analysis reversal: {0: Agora, 1: ANP, 2: ACP, 3: A2A}.
Collaborative reversal assignments are {0: ANP, 1: A2A, 2: ACP, 3: A2A} and,
at the high-load witness, {0: ANP, 1: ANP, 2: ACP, 3: ANP}.
Each minimum was independently checked against CSV rows. These are finite-grid
observations; minimum scale and minimum lambda need not occur together.

### Global no-Agora ablation: VERIFIED with feasibility qualification

All 72 restricted cases allow exactly A2A/ACP/ANP and contain no Agora assignment.
Agent 0's original protocol is forbidden, so its replacement is mandatory.

E/src/gaia_workflow_experiment.py:45–98, run_candidate_oracle, preserves the original
baseline reference, labels forced_removal_nodes, passes a separately named feasible
enumeration seed to the unchanged oracle and copies original allowed loss values.
The seed has agent 0=A2A, the first tied minimum-loss allowed candidate; it is
bookkeeping, not a regenerated empirical baseline. Forced agent 0 is excluded
from eligible preference-reversal checks at lines 67–80.

At per_edge scale 100/lambda 0.1, non-forced A2A→ANP reversals remain:
agent 1 in analysis_task; agents 1 and 3 in collaborative_task. Each satisfies
weighted incoming saving > its unchanged margin. They are not counted merely
because Agora is forbidden.

In restricted analysis, the eligible node saves about 1.564973 weighted-loss units
against its own margin 1. Forced agent 0 also incurs its existing replacement
margin 1, despite having no incoming cost-bearing edge. Total added local loss is
2, yielding original-reference objective_delta **+0.4350270000000016**.
Whole-assignment benefit versus the original, now-infeasible baseline is absent;
delta versus the feasible seed is about −0.564973.

| Restricted workflow | Strict whole-assignment benefits vs original | Eligible preference-reversal cases |
|---|---:|---:|
| analysis_task | 0/36 | 1/36 |
| collaborative_task | 12/36 | 1/36, with two A2A nodes |

Do not call the twelve beneficial forced Agora changes twelve independent
non-Agora preference reversals. All workflow objective values, candidate-constrained
per-node optimal values, forced exclusions and eligibility flags were independently
verified.

## E. Objective / unit audit

Exact code: E/src/objective.py:49–56, evaluate_objective; manual_margin_losses:16–22.

~~~text
L(p) = sum_j local_losses[j][p_j]
Q(p) = sum_(i,j) w_ij * C(p_j, payload_size_ij)
J(p) = L(p) + lambda * Q(p)
~~~

| Explicit question | Answer |
|---|---|
| Units of communication_cost? | Weighted accumulated request-service ms when w is expected message count and C is ms/request. Not measured task makespan; concurrent latencies cannot generally be added to predict elapsed time. |
| Units of local_loss? | Arbitrary manual preference-loss units/points: zero for baseline, one per replacement. No empirical task-quality or calibrated probability meaning. |
| Is lambda dimensionful? | Yes: manual-loss units per accumulated ms for this latency objective; inverse-ms if points are considered dimensionless. It acts as a tradeoff/conversion coefficient. |
| Are margins empirical? | No. They are synthetic sensitivity inputs; scalar router confidence is not used to estimate alternative losses. |
| Are traffic weights measured from GAIA? | No. Controlled generated/instantiated demand. Per-edge weight equals scale; equal-total controls divide scale over agent edges. |
| Historical byte objectives? | Require a different coefficient, loss units/byte. A byte-objective lambda is not physically interchangeable with a latency-objective lambda. |

There is no algebraic unit mismatch **if lambda is explicitly interpreted as this
conversion coefficient**. Floats in the implementation do not enforce units.
Treating lambda as dimensionless while adding preference scores to ms would be
a mismatch and must not be the note's interpretation.

The major limitation is calibration: neither the unit margin nor lambda is mapped
to observed utility, task accuracy or an acceptable latency/quality tradeoff.
Traffic and lambda jointly scale a linear term; sufficiently large products can
make the cheaper protocol win by construction. Thresholds locate a change in the
declared counterfactual objective, not a demonstrated deployment recommendation.
No capability/security/quality-preserving feasibility constraint was validated
beyond the reported candidates. The destination-protocol implementation supports
this initial cost model, not queueing, congestion or invented mismatch penalties.

## F. Novelty-claim safety audit

| Proposed exact statement | Classification | Defensible replacement/scope |
|---|---|---|
| 1. “ProtocolRouter is topology-blind.” | TOO STRONG | Restrict to the audited GAIA assignment call and commit, without ruling out other interfaces or indirect textual input. |
| 2. “The audited released GAIA routing path does not directly condition protocol assignment on graph/edge traffic.” | SAFE | Name the path/commit and disclose the caller's heuristic fallback. |
| 3. “Measured protocol runtime costs can change the system-level optimal assignment under controlled communication loads.” | TOO STRONG as unqualified | “The minimizer of the specified additive destination-cost objective can differ from the fixed baseline under stored local costs, controlled demand and synthetic margins.” Optimality is within that model/candidate set, not actual task performance. |
| 4. “We improve GAIA performance.” | UNSUPPORTED | No full GAIA/task-quality/completion-time experiment. |
| 5. “We outperform ProtocolRouter.” | UNSUPPORTED | No comparable fresh LLM routing or RouterBench quality/accuracy benchmark. |
| 6. “We propose the first topology-aware protocol router.” | UNSUPPORTED | No prior-art novelty search establishes first; no new learned router was evaluated. |
| 7. “Repository-defined GAIA workflow structures admit A2A->ANP assignment reversals under measured protocol costs and controlled traffic.” | SAFE | Explicitly identify config-template conventions, local latency point estimates, synthetic unit margins and eligible rather than forced changes. |
| 8. “The result demonstrates a representation-execution mismatch.” | TOO STRONG | Describe the observed distinction between assignment inputs and runtime communication information. A defect, causal mismatch or author-intended optimization objective is not proved. |
| 9. “Topology-aware protocol assignment is universally better.” | TOO STRONG | Selected points improve this objective; zero demand/lambda-zero stays unchanged and task quality is unmeasured. |

### Safest technical-note wording

“At commit 6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f, the audited released GAIA
assignment call receives task/agent inputs without an explicit graph/edge-demand
input; its caller uses the original heuristic fallback. We measured 480 successful
local no-op requests through repository client/server paths. Using the stored
latency means in a specified additive destination-protocol cost objective, with
controlled demand and a synthetic unit preference margin, the exhaustive oracle
finds assignment reversals. An A2A->ANP reversal occurs in the analysis configuration
template without changing Agora; eligible A2A->ANP reversals persist under global
Agora exclusion when forced feasibility changes are separated. This does not
establish GAIA task-quality gains, statistical ANP superiority over ACP, or novelty.”

### Safest outreach-email wording

“I inspected the released GAIA assignment call at the cited commit and noticed
that it does not receive explicit graph/edge-demand inputs, although destination
adapters and request metrics are available in the runtime. I have a small
reproducible local microbenchmark and controlled sensitivity diagnostic: using
measured local request means and an explicitly synthetic preference margin, the
modeled optimum can change for the published workflow configuration templates,
including eligible A2A->ANP changes after forced Agora removal is accounted for.
I have not demonstrated GAIA task-quality gains or a novel routing method.
Would a short note about this narrowly scoped cost-awareness question be useful?”

No outreach message was sent.

## G. Reproducibility / integrity audit

| Check | Verified current status |
|---|---|
| Protected tracked source changes | 0; git diff HEAD --name-only empty; saved original-source hashes match. |
| Experiment placement | All non-ignored untracked files lie under ; experiment paths resolve inside it. |
| Full tests, run once for this audit | **50 passed in 3.10s**; notes/final_audit_tests.txt. |
| git diff --check | Exit 0, no output. Untracked contents are not checked by ordinary diff; earlier supplemental code/data checks and this audit note's no-index check cover that qualification. |
| Staged files | 0; git diff --cached --name-only empty. |
| Experiment commits | HEAD equals baseline; git rev-list baseline..HEAD gives 0; local HEAD reflog contains clone/checkouts, not experiment commits. |
| Pushed branch | git ls-remote --heads origin refs/heads/exp/topology-aware-protocol-routing returned no ref, exit 0. The branch is not currently published there; no push occurred in this work. This cannot prove a remote's entire historical state. |
| Scientific-result edits during audit | None; 77 result/config/code/test-file hashes checked unchanged after note creation. |
| Expensive/new experiment runs | None. Only source/saved-data/provenance checks and requested tests. |

Commands:

~~~bash
cd <UPSTREAM_ROOT>
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
python -m pytest -q -p no:cacheprovider tests
git diff --check
git diff --cached --name-only
git rev-list --count 6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f..HEAD
git ls-remote --heads origin refs/heads/exp/topology-aware-protocol-routing
~~~

Actual git status --short:

~~~text
?? experiments/
~~~

### Provenance sufficient for the declared numerical chains

Real profile manifest output/source hashes match raw data and processed costs;
it records config, environment/dependencies and timing/byte definitions. Worker
logs/results and the earlier corrected-observer diagnostic remain separate.

cost_interface_manifest.json links verified raw/summary/profile-manifest hashes
to both canonical files, preserving conversion rows. The stale failed table's
archive hash and unchanged historical failed-run raw files match.

joint_manifest.json matches canonical cost SHA256, fixed config, baseline and
losses; archived predecessor links match. Its controlled edges are reconstructable,
and all 174 threshold equations match saved inputs. Workflow summary matches
official-config/control-config/baseline/measured-source hashes; the workflow
verification note matches both output hashes and the protected-input snapshot.
Literal patterns and weighted graphs are embedded.

This is sufficient to reconstruct the declared result chains, with limits:
the main profiling manifest does not by itself sign/hash every experiment-code
file at measurement time; not every derived artifact has a self-contained
manifest. Current source, archived files, subsequent snapshots and independent
arithmetic support reconstruction, not a tamper-proof historical execution claim.

Older notes contain historical test counts or statements that routing was not yet
rerun. These describe prior rounds; latest manifests/results and this fresh test
log are authoritative. Chronological prose is not a numerical discrepancy.

## H. Final verdict

**READY WITH CAVEATS**

The evidence supports a narrowly scoped technical note and exploratory email
using section F's language. It does not support GAIA superiority, unqualified
system/task optimality, a causal design-defect claim or novelty.

### Top three strongest findings

1. Source-verifiable input-scope distinction: the audited GAIA assignment call has
   no explicit graph/edge-demand input, while destination adapters and request
   metrics are available elsewhere. This is specific to that path/commit.
2. Empirical local implementation costs: 480/480 measured successes, setup/warmups
   excluded, real server/responder/digest checks, exact matching means and traceable
   canonical mapping. No invented mismatch penalty supplied those costs.
3. Declared sensitivity reversals: 37/144 controlled-graph reversals include an
   A2A-only witness; official config-template instantiations retain eligible
   A2A->ANP reversals under globally excluded Agora with forced changes separated.

### Top three limitations

1. Synthetic utility/demand: unit margins, lambda's loss/ms conversion and edge
   weights are uncalibrated controlled inputs. Score reduction is not measured
   quality/makespan improvement; the model is separable and omits validated
   concurrency/capability loss.
2. Measurement scope/uncertainty: one local no-op campaign, specific HTTP/settings
   and connection behavior, no ANP WebSocket/E2E or Agora negotiation measurements,
   and an ANP–ACP mean gap much smaller than observed variability. Stored-point
   selection is not a statistically established universal recommendation.
3. Workflow/ablation interpretation: templates are not executed traces; final/all
   semantics are disclosed conventions. Agora exclusion makes the original
   baseline infeasible. Restricted analysis has an eligible node reversal but no
   whole-assignment gain against that original after the forced penalty. No
   defect, representation-execution mismatch or routing novelty is established.

Numerical discrepancies: **0**. Tests: **50 passed in 3.10s**.
Git integrity checks passed within the stated current-state scope.
