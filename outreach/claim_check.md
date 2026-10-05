# Claim check: final outreach technical note

> Historical source-study record, made public-safe during packaging. Use the root README for current standalone commands. Source-time hashes and execution statements retain their original meaning; see PUBLICATION.md. Superseded outreach previews/v1 documents described here remain in the original study checkout; they are omitted from this artifact.


Status: **PASS. All 34 factual/methodological claim entries below are SAFE.**
Checked on 2026-10-05 against the two authoritative audits, all nine requested
saved evidence files, and the source snippets cited below. This document covers
the prose, equation, plot and embedded pipeline. Questions and titles assert no
additional empirical result. Author/contact details are supplied by the user.

Repository: `<UPSTREAM_ROOT>`.
Source commit: `6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f`.
All paths below are repository-relative; E = the artifact root; other source paths refer to the upstream checkout.
A = `E/notes/final_audit.md`; P = `E/notes/local_preference_signal_audit.md`.

| ID | Final sentence or figure/equation statement | Supporting audit/result/source | Status |
|---|---|---|---|
| C01 | “ProtocolBench [1] shows that protocol choice affects system behavior.” | ProtocolBench primary paper abstract; official ICML 2026 listing and indexed OpenReview camera-ready paper. See citation verification below. No new quantitative claim about that paper is added. | SAFE |
| C02 | “At commit 6349eb97, I noticed that the audited released GAIA assignment call receives task/agent inputs without an explicit graph or edge-demand input; its caller uses the original heuristic fallback.” | A §A; P §D. `scenarios/gaia/protocol_backends/meta_protocol/network.py:456–492`; `llm_router.py:165–166,311–331,356–390`. Caller constructs `GAIALLMRouter()` with no client. Scope is this structured call, not all ProtocolRouter interfaces or free-text information. | SAFE |
| C03 | “Runtime delivery nevertheless selects destination-specific adapters and records request metrics.” | A §A. Same `network.py:603–676`, especially destination protocol at 618; delivery calls source BaseAgent.send at 376. `src/core/base_agent.py:889–956`; `src/core/metrics.py:23–39`. No active enforcement of the generic AgentNetwork graph is claimed. | SAFE |
| C04 | “I tested a narrow question: when can measured implementation costs change the minimizer of a declared local protocol-assignment objective under controlled communication demand?” | A §§C–F; `E/src/objective.py:49–56`; saved decision/workflow CSVs and summaries. “I” reports the existing completed diagnostic; no fresh measurement or inference is implied. | SAFE |
| C05 | “Measured local no-op request latency through released repository client/server paths; 30 measured repetitions per protocol/size after 5 warmups.” | A §B; `E/notes/real_microbench.md`; all 16 rows in `E/results/processed/real_protocol_costs.csv`; A's independently checked raw records in `E/results/raw/real_protocol_profile.csv`. Actual adapters, servers and deterministic responders, not conversion-only costs. | SAFE |
| C06 | “Setup time excluded.” | A §B timing audit; `E/src/local_protocol_microbench.py:277–316,343–374`; session opens before warmup/measured loops. | SAFE |
| C07 | “Timing wraps BaseAgent.send, including encode/server/no-op/decode; no LLM.” | A §B; `E/notes/real_microbench.md`; `sample` starts perf_counter_ns before awaiting the original send and stops after response/decode. Original BaseAgent encode/adapter/decode inspected directly. | SAFE |
| C08 | “HTTP/runtime-specific costs, not universal rankings.” | A §B implementation limits: ANP HTTP path; Agora direct HTTP without toolformer/model negotiation. Connection/thread behavior remains part of these specific costs. | SAFE |
| C09 | “ANP's 100 KB outlier is retained; small ACP/ANP mean gaps do not establish statistical superiority.” | A §B: ANP max 107.861652 ms retained, mean 6.2451045 ms; 10 KB ACP–ANP gap ~0.0001225 ms vs SD ~0.04 ms. Exact mean/SD CSV. The note makes no statistical test or superiority claim. | SAFE |
| C10 | “Official analysis_task configuration template: 0→1→2→final.” | A §D literal structures; `scenarios/gaia/config/meta_protocol.yaml:109–117`, inspected directly. Template instantiation is expressly disclosed as such. | SAFE |
| C11 | “Cost-bearing edges are 0→1 and 1→2; final is terminal.” | A §D; `scenarios/gaia/core/network.py:257–260`; `E/src/gaia_workflow.py:26–73`; saved `agent_edges` and `terminal_events`. No final protocol/cost or invented 2→3 edge. | SAFE |
| C12 | “Agent 1: A2A→ANP.” | A §D four-protocol witness; `E/results/processed/gaia_workflow_reversal.csv`, analysis_task/all_four/per_edge/100/0.1 row; summary's corresponding witness. | SAFE |
| C13 | “10 KB costs · 100 controlled requests/edge.” | That saved witness has `payload_size_bytes=10240`, `traffic_scale=100.0`, `traffic_normalization=per_edge`, with weight 100 on each of its two cost-bearing edges. KB uses 1024 bytes. | SAFE |
| C14 | “λ=0.1 · synthetic unit preference margin.” | A §§D/E; saved witness and original local loss entries; `E/src/objective.py:16–22`. Neither λ nor the margin is empirically calibrated. | SAFE |
| C15 | “Agora remains unchanged.” | Full all-four witness: baseline `{0:Agora,1:A2A,2:ACP,3:A2A}`; modeled `{0:Agora,1:ANP,2:ACP,3:A2A}`. Both CSV and summary; A §D. This statement precedes and is separate from global-exclusion ablation. | SAFE |
| C16 | “The exhaustive oracle finds a changed minimizer of the declared sensitivity objective.” | A §D; all-four witness enumerates 256 assignments, objective_delta = −0.5649729999999984. Optimality is within the stated additive model and candidate set; no new routing method or task-performance optimum is asserted. | SAFE |
| C17 | “The same eligible A2A→ANP preference reversal persists when Agora is globally excluded and forced feasibility changes are accounted for.” | A §D global no-Agora audit; restricted witness has eligible reversal node 1 and forced_removal node 0, candidates exactly A2A/ACP/ANP. `E/src/gaia_workflow_experiment.py:45–98`. Forced replacement is not counted as an eligible reversal. | SAFE |
| C18 | “The forced agent-0 replacement leaves no whole-assignment gain versus the original baseline in this analysis ablation.” | A §D: eligible saving 1.564973 units vs its margin 1, plus forced margin 1; original-reference objective_delta +0.4350270000000016. Restricted analysis has 0/36 strict whole-assignment benefits vs original, though the original is infeasible. Feasible-seed delta is −0.5649729999999984. | SAFE |
| C19 | Equation: J(p) = Σj Lj(pj) + λ Σ(i,j)∈E wij C(pj,sij). | A §E; exact code in `E/src/objective.py:49–56`, inspected directly. Destination-only cost; no mismatch penalty or extra edges introduced. | SAFE |
| C20 | “Lj: explicit synthetic local preference loss (0 at baseline; 1 per replacement).” | A §E; P §§D/E/H; `manual_margin_losses`, unchanged original margin 1. It is not task accuracy, empirical utility, or derived from fixed confidence 0.3. | SAFE |
| C21 | “C: measured local request latency for the destination protocol, in ms/request.” | A §§A/B/E; stored means used by the oracle. These are accumulated request-service costs, not task makespan. | SAFE |
| C22 | “wij: controlled request count.” | A §E; saved per_edge witness: each edge has weight 100. Request counts are controlled demand, not measured GAIA traffic. | SAFE |
| C23 | “λ: preference-loss units per accumulated millisecond.” | A §E explicit dimensionful conversion coefficient; multiplying accumulated ms yields synthetic loss units. Not dimensionless. | SAFE |
| C24 | “This destination-only additive objective is separable by incoming demand.” | A §§C/E; grouping objective terms by destination yields independent per-node local-loss plus incoming-cost terms. No necessity for learned graph coupling is claimed. | SAFE |
| C25 | “No GAIA task-quality or makespan improvement is demonstrated.” | A §§B/E/F/H; existing no-op requests and modeled assignment objective measure neither full task quality nor completion time. | SAFE |
| C26 | “Local preference margins and traffic demand are controlled, not empirically calibrated.” | A §§C/E/H; P §§D/E/H. No released drop-in local margin found for this GAIA path; confidence 0.3 is not a candidate margin. | SAFE |
| C27 | “Workflow structures are official configuration templates instantiated under disclosed conventions, not observed execution traces.” | A §D. Named templates are not consumed as observed runtime traces; all expands to peers excluding hub self-loops, and final remains terminal. | SAFE |
| C28 | “The public release does not expose graded agent×protocol preferences or validated feasible-alternative masks for this GAIA path.” | P §§B/D/G/H, A §E. Explicitly scoped to current GAIA assignment. Numeric scores in separate SDK/security routers do exist and are not denied. | SAFE |
| C29 | Pipeline stage 1: task_analysis and agents_config → fixed protocol assignment; annotation “graph / edge demand not an explicit input to the audited assignment call”. | Same evidence as C02; unchanged saved routing-output replay; A §§A/D. “Fixed” means the diagnostic baseline, not that modeled oracle assignments cannot change. | SAFE |
| C30 | Pipeline stage 2: workflow/communication edges, destination-specific adapters, request metrics. | Same evidence as C03/C10/C11. The diagram does not claim the generic graph is actively enforced by GAIA or that config templates are observed execution traces. | SAFE |
| C31 | Pipeline stage 3: A2A/ACP/ANP/Agora, four payload sizes, 480/480 measured successes. | A §B; exact CSV: four protocols × four sizes × 30 successful measured requests = 480; 80 warmups excluded. Sizes: 1024/10240/51200/102400 bytes. | SAFE |
| C32 | Pipeline stage 4: measured C(p,size) + controlled edge demand + explicit synthetic preference margin → assignment reversal? Footer: “Diagnostic only — not an end-to-end GAIA performance claim”. | A §§C–F, P §H; C04/C19–C27. Question is about the stated model, not a claim of a superior router. | SAFE |
| C33 | All 16 plotted means, units, payload labels, and four curves. | Exact saved strings from `E/results/processed/real_protocol_costs.csv`, listed below and matched by the plot input. No interpolation-derived estimate, smoothing, error bar, significance label or outlier removal. Y axis explicitly log-scaled, X uses actual 1/10/50/100 KB spacing. | SAFE |
| C34 | Formal reference: “Hongyi Du et al., ProtocolBench: Which LLM MultiAgent Protocol to Choose?, ICML 2026.” | Official ICML 2026 Downloads listing plus indexed OpenReview camera-ready title, authors and first-page proceedings metadata; primary URLs below. | SAFE |

## Exact plot inputs (stored means, ms)

| Protocol | 1024 bytes | 10240 bytes | 51200 bytes | 102400 bytes |
|---|---|---|---|---|
| A2A | 1.3585756 | 1.4698952333333333 | 1.9828458666666666 | 2.707684433333333 |
| ACP | 1.2176304666666666 | 1.3135204333333332 | 1.8806641333333334 | 2.608613 |
| ANP | 1.3194534 | 1.3133979333333334 | 1.7973076 | 6.2451045 |
| Agora | 23.70959746666667 | 23.38588173333333 | 26.200420033333334 | 26.8474713 |

Plotting parses these stored strings as floats solely to position marks. It does
not recalculate means, filter samples, or alter the source CSV. Connecting lines
are visual guides, not new measurements between buckets.

## Primary citation verification

Access/check date: 2026-10-05. Discovery: the available web search tool, queries
for the exact title and `site:icml.cc`/`site:openreview.net`, followed by an official
ICML listing find.

- [Official ICML 2026 Downloads listing](https://icml.cc/Downloads/2026): exact title found at the paper entry.
- [OpenReview paper page](https://openreview.net/forum?id=GZRiXE2zBe).
- [Indexed camera-ready PDF](https://openreview.net/pdf/c6f32b78359b8bb7e2fae1153354b6cdc9e2aaf3.pdf): exact title, Hongyi Du as first author, and first-page “Proceedings of the 43rd International Conference on Machine Learning ... PMLR 306, 2026” metadata returned by search.
- [Primary arXiv record](https://arxiv.org/abs/2510.17149) corroborates authors; its earlier title is “Which LLM Multi-Agent Protocol to Choose?”. The note cites the conference title.

Coverage limitation: direct OpenReview opens returned browser verification; the
conference title/year is supported by the accessible official ICML listing and
indexed camera-ready metadata. No access control was bypassed. No third-party
figure or paper text was reproduced.

## Final claim boundary

Strongest claim used, verbatim:

> The same eligible A2A→ANP preference reversal persists when Agora is globally excluded and forced feasibility changes are accounted for.

This claim is attached to the disclosed analysis-template witness (10 KB,
100 requests/edge, λ=0.1, synthetic unit margin). It is not statistical ANP
superiority, a no-Agora whole-assignment improvement, a validated feasible
deployment recommendation, novelty, or GAIA task-performance evidence.

Exact disclosed limitation bullets:

- No GAIA task-quality or makespan improvement is demonstrated.
- Local preference margins and traffic demand are controlled, not empirically calibrated.
- Workflow structures are official configuration templates instantiated under disclosed conventions, not observed execution traces.

No unsupported entry remains. Original data, objective, baseline, candidate
semantics and scientific source files were not changed for this note.
