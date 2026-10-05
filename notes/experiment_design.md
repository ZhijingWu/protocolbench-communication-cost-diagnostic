# Topology-aware protocol diagnostic: source audit and design

> Historical source-study record, made public-safe during packaging. Use the root README for current standalone commands. Source-time hashes and execution statements retain their original meaning; see PUBLICATION.md. Superseded outreach previews/v1 documents described here remain in the original study checkout; they are omitted from this artifact.


Audit: 2026-10-05; repository baseline 6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f;
branch exp/topology-aware-protocol-routing. No original source changes are allowed.

## A. Routing input path
`routerbench/run_benchmark.py:main` loads scenarios, calls
`ProtoRouterBenchmark.process_scenario` in `routerbench/proto_router.py`.
That function uses `routerbench/prompt_template.py:format_scenario_prompt`,
which reads description and module names, agents, tasks, potential_issues and
protocol_selection. It actually selects the WITH_RESULT template, which includes
historical examples; its protocol_selection tool returns module_selections.
`routerbench/evaluator.py:RouterBenchmarkEvaluator.evaluate_scenario` compares
selected_protocol against module_protocol ground-truth labels; these accuracy
metrics are not communication measurements. This is a MODULE-level benchmark,
not the same interface as the GAIA AGENT-level router.

## B. GAIA protocol assignment path
`scenarios/gaia/runners/run_meta_protocol.py:MetaProtocolRunner.create_network`
constructs MetaProtocolNetwork, then register_agents_from_config saves the agent
list. `MetaProtocolNetwork.start` calls `_create_agents_with_llm_routing`, then
`_assign_protocols_with_llm_router` (both in
`scenarios/gaia/protocol_backends/meta_protocol/network.py`). Key source:

```python
llm_router = GAIALLMRouter()
task_analysis = self.config.get("task_analysis", {})
routing_decision = await llm_router.route_gaia_task(
    task_analysis=task_analysis, agents_config=agents_config)
```

`scenarios/gaia/protocol_backends/meta_protocol/llm_router.py:GAIALLMRouter.route_gaia_task`
returns RoutingDecision(agent_assignments, selected_protocols, reasoning,
confidence, strategy). It immediately calls `_fallback_routing` without an LLM
client. The audited network caller does not inject one. The direct fallback
maps browser_use to agora, python_execute and str_replace_editor to a2a,
create_chat_completion to acp. The experiment calls this ORIGINAL implementation,
labels it heuristic_fallback, and can instead consume a saved RoutingDecision.
It does not describe fallback replay as a fresh LLM experiment.
The network normalizes IDs, may round-robin missing IDs and ultimately defaults
to a2a; the experiment rejects incomplete saved assignments rather than hiding
missing output. `_create_agents_with_llm_routing` persists protocol_assignments
and injects assigned_protocol into each agent config.

## C. Topology representation and enforcement limits
`src/core/network.py:AgentNetwork.__init__` declares
`self._graph: Dict[str, Set[str]] = defaultdict(set)`. connect_agents updates it;
get_topology exposes adjacency; route_message rejects an absent edge then calls
src_agent.send. setup_star_topology is bidirectional and setup_mesh_topology is
all directed non-self pairs. connect_agents does not install adapters.
GAIA instead extends `scenarios/gaia/core/network.py:MeshNetwork`, which keeps
`self.connections = []`. The audited MetaProtocolNetwork.deliver calls
BaseAgent.send directly, not AgentNetwork.route_message. Its adapter installer
covers all destinations including self; it does not filter by graph.
Therefore explicit graph support exists in the core, but enforcement of an
experiment graph by the GAIA runner is NOT established. Generated graphs here
represent expected communication demand, not a modified GAIA execution graph.
`scenarios/gaia/config/meta_protocol.yaml` contains workflow message_flow_patterns
and network timeouts, not weighted edges passed into the assignment call.

## D. Adapter installation
`MetaProtocolNetwork._install_outbound_adapters` reads:

```python
dst_protocol = getattr(dst_agent, 'config', {}).get('assigned_protocol', 'a2a')
# ... creates A2AAdapter, ACPAdapter, AgoraClientAdapter or ANPAdapter ...
await adapter.initialize()
src_base_agent.add_outbound_adapter(dst_id, adapter)
```

It uses the destination BaseAgent.agent_id. Source protocol is not used to pick
this adapter. The GAIA ANP branch supplies a dummy private key; valid ANP execution
must be verified rather than presumed. Adapter initialization errors are logged
and skipped by that installer.

## E. Message sending
`src/core/base_agent.py:BaseAgent.send` looks up `_outbound[dst_id]` (with protocol
name/default compatibility fallbacks), creates UTE.new, then:

```python
proto_payload = ENCODE_TABLE[adapter.protocol_name](ute)
with MetricsTimer(REQUEST_LATENCY, (self.agent_id, dst_id, protocol_name)):
    response = await adapter.send_message(dst_id, proto_payload)
    msg_size = len(json.dumps(proto_payload).encode('utf-8'))
    MSG_BYTES.labels("out", self.agent_id).inc(msg_size)
    ute_response = DECODE_TABLE[adapter.protocol_name](response)
```

`src/core/protocol_converter.py` supplies ute_to_a2a/acp/anp/agora and decode
registries; all converters are pure, without network I/O. Some adapter classes
further wrap this payload. Thus encoded_bytes means the EXACT existing metric's
JSON size at the UTE conversion boundary, not complete HTTP/WebSocket wire bytes.
No measured/source-supported sender-destination protocol mismatch penalty is
established. AgoraClientAdapter._simple_send can return an `[Agora Fallback]`
string instead of raising on network failure; the real profiler must reject such
results and also require a receiver acknowledgement.

## F. Existing metrics and timing boundaries
`src/core/metrics.py`: REQUEST_LATENCY is agent_request_latency_seconds with
src,dst,protocol labels; MetricsTimer uses perf_counter and observes even when
its body raises. In BaseAgent.send the timer excludes UTE creation/encoding but
includes adapter execution, byte accounting and response decoding.
MSG_BYTES is agent_message_bytes_total with direction,agent_id labels; only
successful adapter returns are counted, before decoding. REQUEST_FAILURES is
agent_request_failures_total with src,dst labels, incremented within the send
try/except. Exceptions before the timer (e.g. encoding) are outside that counter.
RECOVERY_TIME is a histogram, unrelated to this microbenchmark.
The experiment reads per-request histogram sum/count deltas in an isolated
sequential profiler process, rather than redefining the repository metrics.
Semantic acknowledgement failures are separately labeled experimental failures;
original metrics can count adapter success despite a fallback/error response.

## G. Visibility and permitted claims
The GAIA assignment signature and its prompt builder expose no explicit graph,
edge weights, message counts, payload sizes or measured costs.
_create_gaia_user_prompt extracts task_type, complexity, required_tools,
domain_areas and agent id,name,tool,role,port. Arbitrary descriptions in routerbench
could mention topology in natural language, so do not generalize this GAIA audit
to every possible ProtocolRouter input.
RoutingDecision.confidence is a single self-reported scalar, with no calibrated
per-agent candidate probabilities/rankings. It cannot define local alternative
losses. Use explicitly configured manual margins and call optimization a
controlled sensitivity analysis, even when C is empirically measured.

## Experimental design
Fixed four-node controlled fixture; identical task/agent objects across chain,
bidirectional star, directed full mesh and seeded hotspot; low/medium/high
traffic explicitly means expected message counts (no rounding at fractional scales).
Also equal-total-message cases control for graph density versus total volume.
Profile A2A, ACP, ANP, Agora at text lengths 1024,10240,51200,102400 ASCII bytes;
5 warmups and 30 attempts per bucket. Payload_size_bytes is text length; JSON
business/envelope overhead is reported separately in encoded_bytes.
Two explicit modes: real (unaltered adapters, BaseAgent.send and existing
metrics, protocol servers where startup works); conversion-only (unaltered
converter loaded under an isolated package namespace to avoid eager SDK imports).
Conversion-only measures conversion plus JSON serialization runtime, never
network latency; use serialized bytes for the default sensitivity cost metric.
Setup failures produce rows with missing latency/bytes and error types, not zeros.
Warmups are kept in raw data, excluded from processed statistics. No missing
protocol is assigned a fabricated cost, no bucket interpolation is implicit.

J(p) = sum_j local_loss_j(p_j) + lambda * sum_(i,j) w_ij C(p_j,size_ij).
Local loss is a configured nonnegative margin for departing from the original
assignment. Units: objective loss units; lambda is loss units per byte (or per ms).
No mismatch term, contention, concurrency, queueing or task accuracy is modeled.
This destination-only additive objective is separable by weighted incoming demand;
exhaustive 4^N enumeration is an audit oracle, not needed for scalable optimization.
Baseline ties are retained; enumeration has a size guard. A per-node alternative
reverses when lambda * incoming_cost_saving > manual_margin. Equality is a tie,
not strict evidence of improvement. Report exact threshold and a sweep bracket.

Validation: lambda=0, zero demand, equal protocol costs, a hand-computed 2-node
case, ID permutation invariance and repeatability; add invalid/missing costs,
mode separation and input immutability checks. No learning, external optimizer,
figure, LLM API call, dependency installation or protected source edit.
