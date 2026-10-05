# Focused audit: released local protocol-preference signals

> Historical source-study record, made public-safe during packaging. Use the root README for current standalone commands. Source-time hashes and execution statements retain their original meaning; see PUBLICATION.md. Superseded outreach previews/v1 documents described here remain in the original study checkout; they are omitted from this artifact.


Date: 2026-10-05 (Asia/Shanghai).
Repository: <UPSTREAM_ROOT>.
Commit: 6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f.
Study: this standalone artifact.

**Recommendation: STOP HERE AND WRITE OUTREACH.**

For the current released GAIA assignment path and unchanged four-agent baseline,
no released comparable candidate-preference-strength signal can faithfully replace
the synthetic manual margin. This is NOT a claim that the repository contains no
numeric scores: a different SDK load-balancer and security-specific code do.
Those quantities must not be transplanted into the current GAIA objective and
advertised as its original local suitability loss.

Audit only: source/text/AST and saved JSON inspection. No original module was
imported/executed, no inference/API call, score construction, router change, test
run or experiment occurred. This note is the only file created/changed. Source
references below are relative to the repository root.

## A. Routing-path coverage and repository search

Inspected all requested files:

- routerbench/proto_router.py: ProtoRouterBenchmark.process_scenario and _parse_llm_response.
- routerbench/prompt_template.py: both prompt constants, format_scenario_prompt and PROTOCOL_SELECTION_FUNCTION.
- routerbench/run_benchmark.py: load_config, load_dataset, main.
- routerbench/evaluator.py: RouterBenchmarkEvaluator.evaluate_scenario, calculate_overall_statistics and report/result paths.
- scenarios/gaia/protocol_backends/meta_protocol/llm_router.py: GAIALLMRouter initialization, route_gaia_task, prompts, fallback, metric update and statistics.
- scenarios/gaia/protocol_backends/meta_protocol/network.py: MetaProtocolNetwork assignment, ID normalization, adapter creation, configuration storage and runtime metrics; MetaProtocolCommBackend heuristics.
- scenarios/gaia/config/meta_protocol.yaml: router weights, protocol_characteristics, candidate list and workflow metadata.
- src/core/intelligent_router.py: LLMIntelligentRouter, ProtocolInfo, RoutingDecision, compatibility route_task, LLM parsing and round-robin fallback.
- src/core/intelligent_network_manager.py: IntelligentNetworkManager request construction, factory registration, routing, execution and metric updates.
- src/core/network.py: AgentNetwork graph/transport/metric management; no local candidate-utility calculation.

Also inspected discovered paths:

src/core/router_interface.py; src/core/llm_router.py;
src/core/load_balanced_router.py; src/core/intelligent_network.py;
src/utils/core.py; scenarios/gaia/core/llm.py;
scenarios/gaia/protocol_backends/meta_protocol/agent.py;
scenarios/gaia/core/llm_judge.py;
fail_storm_recovery and streaming_queue meta-protocol routers;
safety_tech S2 router/coordinator and ANP privacy analyzer;
RouterBench data/data.json and local_results/benchmark_results.json.

Case-insensitive git grep searched original tracked repository material, excluding
experiments/** so our own synthetic margins/results could not be mistaken for
released signals. Matching-file counts include prose/data matches:

| Term | All tracked matching files | Python/YAML matching files |
|---|---:|---:|
| confidence | 31 | 23 |
| score | 70 | 39 |
| probability | 13 | 4 |
| logprob | 0 | 0 |
| ranking | 14 | 2 |
| preference | 18 | 4 |
| candidate | 26 | 11 |
| constraint | 20 | 10 |
| utility | 18 | 14 |
| reward | 8 | 1 |
| performance_weight | 2 | 2 |
| reliability_weight | 1 | 1 |
| recovery_weight | 1 | 1 |

Utility often means helper functions. Probability matches in source refer to
entropy/attack/packet-reordering calculations, not protocol-selection posterior
probabilities. Reward matches include an ANP privacy-analyzer bonus description,
not a trained routing reward estimator. Ranking code matches are S2-specific;
the SDK load-balancer additionally uses a sorted local score list.

Reproducible search form (read-only):

~~~bash
git grep -l -i -- confidence . ':(exclude)experiments/**'
git grep -n -i -E 'confidence|score|probability|logprob|ranking|preference|candidate|constraint|utility|reward|performance_weight|reliability_weight|recovery_weight' -- '*.py' '*.yaml' ':(exclude)experiments/**'
~~~

All runtime-availability statements below are inferred from inspected source;
this audit did not instantiate the routers. In particular, S2LLMRouter.__init__
calls _initialize_llm, which makes a connection-test inference call
(s2_llm_router.py:86–122). It was deliberately not instantiated.

## B. Candidate-signal inventory

### Central ten-category answer

| Requested category | Released evidence |
|---|---|
| 1. Per-protocol scalar score | Yes elsewhere: SDK load-balancer internals; S2 security profiles/recommendation priors; conditional MetaProtocolAgent history heuristic. No such score in active GAIALLMRouter fallback or RouterBench selection output. |
| 2. Per-protocol probability | No protocol-choice distribution found. success_rate fields are operational/historical rates, not P(protocol selected or suitable given this module). |
| 3. Log-probability/token likelihood | No request/capture path found; no logprob keyword in original tracked material. |
| 4. Ranked candidate list | S2 exposes rankings; SDK load-balancer sorts an internal score list. Selected-protocol lists in GAIA/RouterBench are not ranked complete alternatives. |
| 5. Constraint-satisfaction score | No per-module, per-protocol satisfaction score or validated hard-requirement checker in the audited assignment paths. |
| 6. Utility/reward estimate | Performance/security heuristics and outcome grading exist, but no calibrated expected task-local routing utility/reward matrix. |
| 7. Calibrated confidence | Not found. Confidence values are fixed constants or an LLM-produced scalar, with no calibration procedure for alternative protocols. |
| 8. Deterministic rule score | LoadBalancedRouter has a numeric heuristic. Active GAIA uses an if/elif label mapping, not candidate scores. |
| 9. Performance-prior score | Raw priors and some separate performance/security composites exist; GAIA config weights do not generate a local score. |
| 10. Other quantitative preference quantity | RouterBench exact-match grading and post-execution quality/security metrics can serve their own evaluation purposes, but do not expose current GAIA agent-local preference strength. |

### Exact signals: variable, origin, runtime coverage

| ID | Exact source / class-function / field | Runtime existence and candidate coverage | Origin |
|---|---|---|---|
| S1 | routerbench/proto_router.py:26, ProtoRouterBenchmark.process_scenario; prompt_template.py:365, PROTOCOL_SELECTION_FUNCTION; module_selections[].selected_protocol and justification | Returned if inference/parsing succeeds; one chosen label and text per module. No vector, per-label confidence or alternative scores. success is call/parsing status, not suitability. | LLM-selected label and free text. |
| S2 | routerbench/evaluator.py:17–99, RouterBenchmarkEvaluator.evaluate_scenario; module_results[id].correct, correct_modules, individual_accuracy; data/data.json ground_truth[id].module_protocol | Exact-match Boolean for the supplied prediction; one gold label per module. Can define benchmark label correctness, not a released scored preference over all alternatives. | Annotated label plus deterministic evaluation, not empirical protocol-utility measurement. |
| S3 | scenarios/gaia/protocol_backends/meta_protocol/llm_router.py:29, RoutingDecision.confidence; route_gaia_task:226–231 and _fallback_routing:384–389 | One scalar for the whole joint decision. Current caller returns fixed 0.3. Client branch would use returned confidence or default 0.5. No per-agent/per-protocol vector. | Hard-coded in fallback; LLM self-report/default in client branch. |
| S4 | same file, GAIALLMRouter._fallback_routing:356–390; protocol and agent_assignments | Active released caller's tool-to-label mapping. No scores, alternative penalties or ranking. selected_protocols is built from a set. | Deterministic heuristic label rule. |
| S5 | same file, ProtocolInfo.avg_response_time/success_rate/current_load; _initialize_gaia_protocol_info:57–146, update_agent_metrics:392–403 | Fields for all four protocols exist on initialization. Time/rate constants are not combined into a score or used by this fallback. Metric update changes load only. | Embedded priors described as historical performance; their initialization is hard-coded, not an empirical module-specific estimate. |
| S6 | src/core/intelligent_router.py, LLMIntelligentRouter.route_task:184–212, route_task_with_llm, _parse_llm_response and _fallback_routing:419–449; confidence_score/confidence/selected_protocols | Compatibility route selects first available agent with 0.5 confidence; other branches return one joint scalar (LLM/default or constant 0.3). Round-robin lists are not suitability ranks. Generic src/core/llm_router.py:127–284 has equivalent scalar outputs/fallbacks. | LLM-produced scalar or hard-coded heuristics. |
| S7 | src/core/load_balanced_router.py:31–124, LoadBalancedRouter.route; protocol_scores, score, new_score | Internal score for every registered protocol, sorted and updated with assignment load. Not returned as a candidate-score vector; result metadata returns load_distribution. Task-local features/constraints are not scored. | Heuristic arithmetic over supplied/default/runtime performance and load. |
| S8 | scenarios/gaia/protocol_backends/meta_protocol/agent.py:335–356, MetaProtocolAgent._select_protocol_fallback; score, best_score, _protocol_performance | Conditional per-protocol scores only for recorded histories with installed adapters. Initially empty. Separate from network's agent assignment. Score vector is not returned. | Heuristic history composite; incomplete/stub timing and text-error-based success. |
| S9 | scenarios/safety_tech/protocol_backends/meta_protocol/s2_llm_router.py:42–63, S2SecurityProfile.__post_init__; s2_comprehensive_score and component fields; S2LLMRouter._initialize_s2_security_profiles:132–180, get_s2_security_summary:509–542 | All four profiles/ranks exist when the S2 path is instantiated. S2RoutingDecision.expected_s2_scores at 393–406/488–506 includes only selected doctor protocol(s), while summary exposes all four. Not GAIA's agent assignment. | Hard-coded security component priors and designer weights; rankings are genuinely coded. |
| S10 | scenarios/safety_tech/protocol_backends/meta_protocol/s2_meta_coordinator.py:758–786, _calculate_s2_score(analysis, protocol); s2_score and s2_analysis['s2_scores'] | Post-test score assigned to the chosen doctor protocols. Both calls use the same aggregate analysis; protocol parameter is not used in the calculation. Not an all-candidate local comparison. | Aggregate probe counters plus heuristic scoring weights. |
| S11 | same coordinator:1807–1909, _generate_protocol_recommendations; protocol_profiles[protocol]['score'], protocol_levels, gap | Four hard-coded scores when recommendation method runs: ANP 87.0, Agora 85.0, ACP 83.5, A2A 57.4. Recommendation text, not module-suitability output. ANPPrivacyAnalyzer._apply_anp_privacy_bonuses, scenarios/safety_tech/protocol_backends/anp/analyzer.py:311–351, adds protocol-specific bonuses. | Hard-coded recommendation priors; privacy scoring mixes response heuristics and built-in protocol bonuses. |
| S12 | scenarios/gaia/core/llm_judge.py:23, JudgmentOutput.quality_score; EnhancedLLMJudge.judge_answer:254 and _fallback_judgment:191–236; prompt partial_credit at 123–133 | Post-execution score for an actual answer/trace, not counterfactual candidate predictions. No released module×protocol suitability matrix for our fixed agents. | LLM judge or hard-coded fallback grading; not routing confidence. |
| S13 | src/core/intelligent_router.py, ProtocolInfo and _initialize_protocol_info/get_routing_statistics; src/core/router_interface.py:22, ProtocolCapability.performance_metrics, BaseRouter.update_metrics/get_statistics; intelligent_network_manager.py:247–259, _update_router_metrics | Available registry-wide fields for registered protocols; manager updates selected/ID-matching entries. No guarantee that all alternatives have task-matched outcomes. Generic initialization constants differ from GAIA priors. | Hard-coded priors and, where actually updated, operational measurements with heuristic aggregation. |

### Comparability and scientific local-margin judgment

The classification concerns the current GAIA study. “USABLE WITH STRONG CAVEATS”
does not license transferring an unrelated router/evaluation scale into this
baseline's local loss.

| ID | Comparable across candidate protocols? | Comparable across modules/tasks? | Difference as current local margin / classification |
|---|---|---|---|
| S1 | No candidate numeric values. | No numeric scale. | NOT USABLE; text extraction would create a new proxy. |
| S2 | Yes for exact gold-label correctness in the same RouterBench module; all non-gold labels share ungraded incorrectness. | Comparable as Boolean benchmark accuracy only, not task utility or difficulty. | USABLE WITH STRONG CAVEATS for a separate RouterBench label-misclassification objective; NOT a faithful replacement for current GAIA agent preference. |
| S3 | No, one joint scalar has no q value. | No calibration. | NOT USABLE; assigning it to the selected label and distributing remainder to alternatives would be invented. |
| S4 | Only intended winner known, alternatives unscored. | No strength/utility units. | NOT USABLE as a numeric margin. A one-hot score would just encode another unit-penalty assumption. |
| S5 | Raw metric units can be compared only under matched operational conditions, not as local task preferences. | Not module/role-conditioned; provenance/control mismatch. | NOT USABLE as local margin. Using the same latency as communication cost would double-count. |
| S6 | No complete score/rank vector. | Fixed/self-reported scalars are not calibrated. | NOT USABLE. |
| S7 | Yes as internal priorities at the SAME registered state and assignment step. | Not task-conditioned; values change with load and arbitrary metric scaling. | USABLE WITH STRONG CAVEATS only for studying that load-balancing heuristic itself. NOT a current GAIA preference margin. |
| S8 | Only observed/installed subset; time field not genuinely updated by the recorder. | Histories/roles/execution contexts differ. | NOT USABLE. |
| S9 | Comparable within the defined S2 heuristic index/ranking. | Fixed profiles, not per-module suitability; no validated cross-task utility scale. | USABLE WITH STRONG CAVEATS for that security heuristic's own objective; NOT the current GAIA margin. |
| S10 | Not protocol-specific: common aggregate supplied to both names. | No module/candidate counterfactuals. | NOT USABLE. |
| S11 | Hard-coded index or protocol-specific bonus systems; not demonstrated common empirical scale. | Not local requirements/task-conditioned. | NOT USABLE for current margins. |
| S12 | Would require matched counterfactual task/trace outcomes for all protocols, which this study lacks. | Grading/rubrics and tasks differ; scalar is outcome quality rather than calibrated preference. | NOT USABLE from the released current routing outputs. A new outcome study is outside this audit. |
| S13 | Raw rates/times can be compared only with compatible definitions and matched conditions. | No module/agent suitability calibration. | NOT USABLE for current local-loss margins. |

No signal is classified unconditionally USABLE for replacing this study's manual
margin. Weakly usable signals above retain a different objective, population or
hard-coded scale; the core caveat would remain after transplantation.

## C. RouterBench-specific findings

1. process_scenario receives the scenario dictionary, calls Core.function_call_execute
   and returns parsed function arguments under llm_response, plus status/error.
   Its _parse_llm_response at proto_router.py:77–108 extracts tool/function arguments.
   It does not return per-protocol scores, confidence or SDK choice likelihoods.
2. PROTOCOL_SELECTION_FUNCTION at prompt_template.py:365–399 requests one enum-like
   selected_protocol per module, with module_id and justification. No candidate
   ranking, distribution or confidence field is requested. The labels are A2A,
   ACP, Agora, ANP; multiple module decisions share one output.
3. Justification is a free-text string. “Metric-level reasoning” in the prompt
   is not a structured quantitative evidence vector or a validated score.
4. **Model logprobs are NOT requested.** src/utils/core.py:135, Core.function_call_execute,
   uses chat.completions.create with model/messages/tools/tool_choice/temperature/n
   (197–204, 235–250), without logprobs or top_logprobs. The parser subsequently
   keeps function arguments, not a probability record.
The parser does not explicitly reject every extra JSON argument key. An incidental,
unrequested number would still not constitute a released complete candidate-score
contract or a calibrated signal; no such extra score fields occur in the inspected
saved module outputs.

5. evaluator.py:17–99, evaluate_scenario, uses is_correct = gt_protocol == llm_protocol,
   counts exact matches, scenario correctness and A2A/ACP confusion. calculate_overall_statistics
   at 101 onward aggregates scenario/module accuracy. There is no chosen-versus-
   alternative margin, graded alternative ordering or calibrated correctness probability.
6. Static data audit: 60 scenarios, 180 modules, 180 ground-truth records.
   All 180 modules list the same four choices and select_exactly=1.
   Ground-truth keys include module_protocol, justification and behavioral_expectations.
   There is one gold protocol per module, with prose/list-of-string expectations,
   not four graded utilities. The formatter forwards module tasks/issues, not a
   per-candidate feasibility matrix; evaluator ignores behavioral_expectations
   when calculating correctness.
7. The saved local_results/benchmark_results.json contains 185 parsed module-output
   objects, all with only module_id, selected_protocol and justification. No hidden
   candidate scores occur in those objects. Do not assume those 185 predictions
   are a validated one-to-one mapping to the current 180 module records without
   checking identifiers/counts. This audit did not rerun or repair that artifact.

An official 0/1 label-error criterion could be scientifically described as
RouterBench classification loss. It is NOT a measure of the original router's
preference strength, severity between incorrect alternatives, or actual GAIA task
utility. The four experimental agents have no supplied mapping to those annotated
modules. Replacing their margins with gold-label errors would introduce a new
population/mapping and possibly a different lambda=0 local optimum. If a baseline
already matches gold, the Boolean criterion reproduces the same flat unit penalty,
without validating its interpretation as latency-versus-quality utility.

## D. Audited GAIA path and configuration activation

network.py:456, MetaProtocolNetwork._assign_protocols_with_llm_router, constructs:

~~~python
llm_router = GAIALLMRouter()
routing_decision = await llm_router.route_gaia_task(
    task_analysis=task_analysis, agents_config=agents_config)
~~~

No llm_client is provided or injected into this local router. The constructor
default is None (llm_router.py:49–55), and route_gaia_task immediately calls the
fallback at 165–166.

Fallback mapping at 356–390:

- browser_use -> agora
- python_execute -> a2a
- create_chat_completion -> acp
- str_replace_editor -> a2a
- otherwise -> agora

It computes no candidate scores/ranks and exposes no numeric alternative penalties.
The role variable is read but not used in this branch; task_analysis does not
affect the mapping. The decision-wide confidence is fixed 0.3.
selected_protocols is a list built from a set, so its order is not a preference rank.

meta_protocol.yaml:27–29 has performance_weight=0.4, reliability_weight=0.6,
recovery_weight=0.8. Lines 32–59 contain protocol_characteristics including
recovery_time, success_rate, answer_rate and avg_response_time.

These weights are **not used in the audited assignment calculation**.
Within GAIA source, search finds their names in YAML, while network.py:258 only
stores self._router_config. _assign_protocols_with_llm_router does not pass that
dict or protocol_characteristics into the router. MetaProtocolCommBackend creates
IntelligentNetworkManager(router_type=LLM_BASED) without that weighting dict.
The separate MetaProtocolAgent history formula uses literal 0.7/0.3, not these
YAML weights, and does not calculate the initial assignment.

GAIALLMRouter separately initializes numerically similar performance constants
in ProtocolInfo. Equality of a constant with YAML is not evidence of config
consumption. Its fallback ignores them; its LLM prompt explicitly asks for
capability reasoning, not numeric performance claims (303–307), and user-prompt
construction contains task/agent descriptions rather than a score table.

network.py:532–547 also has an exception fallback ordered list
['a2a','agora','anp','acp'] followed by round-robin. A comment calls it recovery-based,
but it is neither a computed graded margin nor a task-local ranked alternative
output; this is not the normal successful GAIALLMRouter fallback.

MetaProtocolCommBackend._select_communication_protocol at 156–173 is a separate
hard message-size/priority/type rule returning a label. No score/vector.
The current destination-adapter delivery/assignment path must not be conflated
with that alternative helper.

## E. Performance-prior possibility and double-counting

Numeric performance/security information does exist:

- RouterBench's USED PROTOCOL_SELECTION_PROMPT_WITH_RESULT includes literal
  quality_avg, success_avg, communication-time examples and recovery/answer-rate
  summaries (prompt_template.py:151–176, 212–259, 296–302). These are scenario/
  whole-pipeline illustrations in the prompt, not module-local returned scores.
- GAIA ProtocolInfo/YAML contain embedded historical-looking priors for all four.
- Generic LLMIntelligentRouter exposes avg_response_time/success_rate/current_load
  in its registry/statistics and forwards them to its LLM prompt. Its response-
  time updater uses EMA alpha=0.3; its success-rate update block does not calculate
  a new rate. These are not calibrated task-selection probabilities.
- SDK ProtocolCapability.performance_metrics can hold supplied/updated operational
  data. IntelligentNetworkManager._update_router_metrics at 247–259 assigns
  execution_time/len(agent_ids) and binary success to each selected ID. Its
  executor actually uses the first selected agent (211–238), so this update is
  not a clean per-agent causal outcome/quality estimate for all alternatives.
- Fail-storm factory registration (scenarios/fail_storm_recovery/protocol_backends/
  meta_protocol/runner.py:201–273) supplies hard-coded avg_response_time,
  success_rate, answer_discovery_rate and recovery_time constants with comments
  claiming performance origins. The load-balancer reads response_time, not
  avg_response_time, so those initial time priors are not automatically used
  without a correctly named update.
- Existing REQUEST_LATENCY, MSG_BYTES and RECOVERY_TIME in src/core/metrics.py,
  used by src/core/network.py/BaseAgent.send, are runtime communication metrics.
  They are the cost side of our study, not task suitability.
- EnhancedLLMJudge reports actual-run outcome/trace quality, but does not supply
  matched agent/module×candidate counterfactual outcomes here. Aggregated scenario
  scores cannot be distributed among Reader/Analyst/Synthesizer/Editor as local
  penalties without assumptions about role, task difficulty, tools, peers and
  protocol configuration.

Separate the quantities:

A. Runtime communication cost C(p,size): actual transport/request processing cost
   already used by the study.
B. Local suitability U_i(p): task/role/requirement value or validated quality
   of selecting p instead of q for the same module/agent.

Using the SAME latency matrix on both sides, calling one copy local preference
and the other communication cost, is **scientifically invalid for claiming an
independent router-derived suitability signal: it double-counts that evidence**.
A declared latency regularizer could be a different objective, but would not solve
the missing local-utility problem. End-to-end historical times may already contain
communication; they are not demonstrably disjoint local compute costs either.

Success/reliability/answer-rate summaries can be legitimate aggregate outcomes,
but are not automatically module-local suitability margins. Their provenance,
definitions, matched tasks, same agent features, alternative exposure and uncertainty
would need validation. This audit did not establish such a matrix for the current
baseline. Comments describing performance priors as empirical do not make them
an empirical per-agent margin.

### Important score implementations actually found

LoadBalancedRouter.route (src/core/load_balanced_router.py:51–92):

~~~text
score = current_load/max(1,max_capacity) + response_time/10.0 + (1-success_rate)
~~~

The scores cover registered protocols but mix arbitrary scaling and stateful load.
The router assigns by round-robin index through a sorted list, increments loads
and re-sorts. The selected agent protocol need not minimize a fixed independent
local score. Transplanting score differences can change the lambda=0 optimum,
baseline and policy. It is not GAIALLMRouter's tool-matching margin.

MetaProtocolAgent._select_protocol_fallback (agent.py:335–356):

~~~text
score = 0.7*success_rate + 0.3/max(avg_response_time,0.1)
~~~

_record_task_performance at 394–423 initializes avg_response_time and total_response_time
to zero but never accumulates timing; success means the word error is absent from
the result. The initial history is empty. _select_optimal_protocol calls the SDK
compatibility route_task without its required available_agents argument and expects
a dict while the implementation returns SimpleNamespace. Its send_msg computes
a selected label but delegates to the preinstalled destination adapter regardless.
The safe execute method at 236–309 bypasses this selection and sends through its
bound BaseAgent. These findings preclude treating this helper as a released,
populated four-candidate suitability scorer for the actual initial assignment.

The legacy src/core/intelligent_network.py benchmark_agents says “calibrate routing”
in a comment, but provides response-time/operational-success summaries. It imports
intelligent_router, TaskRequirement, ProtocolProfile and ProtocolCapability from
intelligent_router.py, which does not define those names at this commit. Static
inspection therefore does not establish a working confidence-calibration pipeline;
no attempt was made to execute or repair it.

S2SecurityProfile.__post_init__ uses fixed weighted components:
TLS 0.40, session 0.15, E2E 0.18, timing 0.12, metadata 0.15.
Its profile inputs are constants, not fitted module utilities. S2LLMRouter does
expose genuine all-profile rankings, but its returned confidence is fixed 0.8
or rule-based 0.7, not calibrated to that ranking.

S2MetaCoordinator._calculate_s2_score takes a protocol argument but ignores it,
using shared aggregate violation counts for both selected protocols. Those values
cannot support a protocol differential. Its separate recommendation table and
ANP-specific privacy bonuses are also not a common empirical GAIA suitability scale.

## F. LLM logprob option

**Classification: POSSIBLE BUT WEAK.** Not a clean extension of the existing
observable routing interface and not an empirical utility margin.

1. RouterBench and GAIA use function/tool calls with structured JSON arguments
   containing enum-like chosen labels and free-text explanations. Generic SDK
   fallback parsing also supports JSON extracted from prose. Routing is not an
   isolated four-label classification response.
2. No existing call requests/captures complete candidate-label sequence likelihoods.
   A conditional likelihood comparison at an identical chosen-label slot could
   in principle be investigated, but selected-response token likelihood alone
   does not give all alternatives at a common context.
3. A2A/ACP/ANP/Agora may tokenize into different sequences/lengths depending on
   the model. Quotes, casing, JSON spacing, tool-argument serialization, earlier
   module decisions and explanations change context. Whole-output likelihood
   mixes assignment, explanation and other modules; it is not a clean protocol
   preference. No tokenizer/model was run to manufacture comparisons here.
4. Inference instrumentation would have to change. Core.function_call_execute
   currently has no logprob flag; RouterBench parsing discards non-argument
   response metadata. GAIA LLM.ask_tool accepts **kwargs, so flags could be passed,
   but it returns only response['choices'][0]['message'] (core/llm.py:485),
   dropping choice-level likelihood metadata. Provider/model support for logprobs
   of TOOL ARGUMENTS is not established by this code; merely adding a flag may
   not be sufficient. A consistent sequence-scoring/capture method is required.
5. Such scores would be model confidence/propensity proxies, not calibrated
   empirical task utility. Calibration against matched suitability/quality outcomes
   would still be missing. Activating a client would also change the current
   released no-client fallback study into a different inference path.

No API, tokenizer, model call or redesigned output format was used.

## G. Hard-requirement / feasible-set alternative

**Classification: PARTIALLY FEASIBLE.**

In principle, explicit protocol feasibility F_i would permit minimizing
communication cost subject to preserving validated task requirements, avoiding
a synthetic soft local-loss margin. The release provides some requirement material,
but not enough for a faithful complete feasible set for the current GAIA agents.

What is explicit:

- RouterBench module.protocol_selection.choices and select_exactly: all 180
  inspected modules permit the four labels and require one selection.
- ground_truth.module_protocol, justification and behavioral_expectations contain
  a gold choice and module-specific textual expectations, including refusal of
  forged identities, authorized reads, replay protection and similar requirements.
- The prompt's canonical protocol-feature descriptions explain qualitative
  identity/E2E/UI/operation semantics.
- RoutingRequest.constraints in src/core/router_interface.py:34–39 can carry
  max_latency/requires_security-style caller data, and protocol registration/card
  fields express availability or descriptive capabilities.

What is missing/not enforced:

- No per-agent structured must-have requirement vector plus validated
  protocol×requirement satisfaction matrix for the current deployment variants.
- No generic hard-feasibility predicate: src/core/llm_router.py:100–124 passes
  constraints into prompt text; LoadBalancedRouter.route ignores them when scoring.
- GAIALLMRouter fallback neither validates hard requirements nor exports F_i.
  YAML available_protocols is not passed as a candidate mask into its assignment;
  its schema/fallback use the four standard protocol labels.
- RouterBench evaluator checks the gold label, not whether each alternative
  satisfies behavioral_expectations. A gold winner is not proof all other
  protocols are infeasible; prose preference is not a hard prohibition.
- The studied ANP HTTP and Agora no-model paths do not establish all deployment-
  dependent security/capability guarantees mentioned by the high-level prompt.
  Protocol-standard descriptions and separate security tests cannot automatically
  certify the exact microbenchmarked implementation/configuration for every module.

Thus syntactic/declared availability/cardinality restrictions can be preserved,
but “preserves ALL original hard protocol requirements” is not supportable from
this data alone. Choosing one gold protocol as the only feasible option would
freeze each module; treating the heuristic GAIA mapping as mandatory would freeze
the four-agent baseline. Either prevents protocol reassignment rather than
validating graded interchangeable alternatives.

Manually turning “prefer” or capability prose into exclusions, deriving masks
from ground-truth labels alone, or assuming unverified security capabilities would
introduce a new annotation/assumption. That would not remove the current core caveat.
A constraint-preserving study becomes justified after an author-provided/validated
requirement and implementation-satisfaction specification, not before.

## H. Recommendation

**STOP HERE AND WRITE OUTREACH.**

This recommendation is scoped to replacing the current GAIA local margin while
keeping the released baseline semantics. It does not deny that unrelated released
heuristics have real code-level scores or that RouterBench label accuracy is a
legitimate separate evaluation criterion.

Further experiments using confidence 0.3, scenario priors, security constants,
load-balancing scores, extracted explanations or post-hoc label losses would
mostly replace one assumption with another, change the baseline/population/policy,
or duplicate the runtime-cost signal. Logprob collection would require a different
inference/capture setup and would still be an uncalibrated confidence proxy.
There is no sufficiently defensible drop-in candidate-local signal here.

Recommended next action: use the existing audited controlled-sensitivity note,
retain explicit disclosure of synthetic margins, and ask a ProtocolBench author:

- Are there unreleased module/agent×protocol candidate scores or graded preferences?
- Do behavioral_expectations have validated feasible-alternative masks?
- Is the tool-to-protocol fallback intended as a mandatory capability constraint
  or simply a best-fit heuristic?
- Which deployment/transport variants are meant to satisfy the stated hard requirements?

Do not claim the manual margins have been removed, an empirical local utility
has been recovered, or the released confidence has been calibrated. No new
experiment is recommended before that missing requirement/preference information
is supplied. No outreach message was sent.

## I. Audit-only integrity and terminal conclusion

Only notes/local_preference_signal_audit.md was created/changed.
All other experiment-file contents and the inspected protected source/configuration
contents were hash-checked unchanged; HEAD remains the specified baseline.
No tests, benchmarks, LLM APIs, new scores, routers or result changes occurred.
No commit, push, stash or reset was performed.

Terminal conclusion:

- Verdict: STOP HERE AND WRITE OUTREACH.
- Best available local datum: RouterBench gold labels plus behavioral expectations;
  no comparable candidate-local preference strength for the current GAIA agents.
- Best existing numeric proxy: SDK load-balancing score, usable only for that
  separate heuristic's own context, not current GAIA suitability or empirical utility.
- Synthetic manual margins removable faithfully now: NO.
- Full hard-constraint formulation from released current data: not established;
  PARTIALLY FEASIBLE only for explicit choice/availability/cardinality restrictions.
- Next action: outreach asking for validated graded alternatives or feasible sets.
