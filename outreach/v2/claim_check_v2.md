# Claim check v2: visual redesign of the outreach note

> Historical source-study record, made public-safe during packaging. Use the root README for current standalone commands. Source-time hashes and execution statements retain their original meaning; see PUBLICATION.md. Superseded outreach previews/v1 documents described here remain in the original study checkout; they are omitted from this artifact.


**PASS: all 55 entries are SAFE.** Checked on 2026-10-05.
Coverage: every factual/methodological sentence, witness field, mathematical
definition, supported/not-established item and quantitative hero/plot element.
The title, section labels, personal interest sentence and conditional question
introduce no new empirical conclusion. Author details are supplied by the user.

Source commit: `6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f`.
Repository: `<UPSTREAM_ROOT>`.
E = the artifact root; other source paths refer to the upstream checkout.
A = `E/notes/final_audit.md`; P = `E/notes/local_preference_signal_audit.md`.
R = `E/results/processed/real_protocol_costs.csv`.
W = `E/results/processed/gaia_workflow_reversal.csv` and `gaia_workflow_summary.json`.
G = `E/results/processed/decision_reversal.csv` and `reversal_summary.json`.
V1 = `E/outreach/claim_check.md` and the preserved first-version note.

## Sentence and object checks

| ID | Final v2 statement/object | Supporting evidence and boundary | Status |
|---|---|---|---|
| V01 | “At commit 6349eb97, I noticed that the audited released GAIA assignment call receives task/agent inputs without explicit graph or edge-demand input.” | A §A; P §D; `scenarios/gaia/protocol_backends/meta_protocol/network.py:456–492`, `llm_router.py:311–331`. This specific structured call, not every router/interface or indirect prose input. | SAFE |
| V02 | “Its caller uses the original heuristic fallback.” | A §A; P §D; caller creates `GAIALLMRouter()` without a client; `llm_router.py:165–166,356–390`. No fresh LLM routing claim. | SAFE |
| V03 | “Runtime communication follows destination-specific protocol paths and records request metrics.” | A §A; adapter selection at `network.py:603–676`, delivery at 376; `src/core/base_agent.py:889–956`; `src/core/metrics.py:23–39`. No enforced generic graph is claimed for GAIA. | SAFE |
| V04 | “I asked whether measured local communication cost and controlled demand can change the minimizer of a declared assignment objective, with the saved baseline and synthetic margins held fixed.” | A §§C–F; G/W; unchanged saved routing-output replay and manual unit loss. This reports the existing diagnostic, not a rerun for v2. | SAFE |
| V05 | “The official analysis_task configuration template is instantiated under disclosed conventions.” | A §D; `scenarios/gaia/config/meta_protocol.yaml:109–117`; `E/src/gaia_workflow.py:10–73`. Not a captured execution graph. | SAFE |
| V06 | “Final is terminal output, not another agent.” | A §D; `scenarios/gaia/core/network.py:257–260`; W terminal event is excluded from communication cost. No invented final protocol or 2→3 edge. | SAFE |
| V07 | “Agent 3 remains A2A outside this template's edges.” | A §D; original baseline and all-four analysis witness in W. Only edges 0→1 and 1→2 are cost-bearing; agent 3 stays A2A. | SAFE |
| V08 | “480/480 measured requests succeeded across all four protocols.” | A §B; R has 16 conditions, each 30/30 successful measured requests; 80 warmups excluded. Original paths, no conversion-only substitute. | SAFE |
| V09 | “37/144 configurations strictly changed the declared minimizer.” | A §C; G records 144 controlled cases and 37 strict objective improvements/reversals. This combines per-edge and equal-total controlled cases; it is not a GAIA result or deployment success rate. | SAFE |
| V10 | “An eligible A2A→ANP reversal persists without Agora, with forced changes separated.” | A §D; W analysis_task/without_agora/per_edge/100/0.1 has eligible node 1 and forced-removal node 0. Global exclusion, not selective fixing of agent 0. | SAFE |
| V11 | “Local no-op request latency through released repository client/server paths.” | A §B; `E/notes/real_microbench.md`; R and audited raw profile. Original adapters/servers/responders/UTE codecs, not conversion-only measurements. | SAFE |
| V12 | “30 measured repetitions per protocol/size after 5 warmups.” | A §B; R all 16 conditions; raw phases independently checked in the audit. Warmups are excluded from means. | SAFE |
| V13 | “Setup excluded.” | A §B; `E/src/local_protocol_microbench.py:277–316,343–374`: session opens before sampling loops. | SAFE |
| V14 | “HTTP/runtime-specific measurements; not intrinsic protocol rankings.” | A §B implementation limits: original ANP HTTP path and Agora no-model/direct HTTP path, different connection/thread behavior. Not universal standard, WebSocket/E2E or model-negotiation costs. | SAFE |
| V15 | “Timing encloses BaseAgent.send, including encode/server/no-op/decode; no LLM.” | A §B; profiler's perf_counter_ns wraps the original send; original encoder/adapter/server/deterministic responder/decoder path; no task/model/API experiment. | SAFE |
| V16 | “ANP's 100 KB outlier is retained.” | A §B; raw maximum 107.861652 ms; saved mean 6.2451045 ms and SD 19.216113718930764 ms in R, unfiltered. | SAFE |
| V17 | “Close ACP/ANP mean differences do not establish statistical superiority.” | A §B: 10 KB gap ~0.0001225 ms vs observed SDs ~0.04 ms. V2 displays stored point estimates; no significance claim, uncertainty interval or winner annotation. | SAFE |
| V18 | Chart label: “1 KB = 1024 bytes”. | A §B; R's actual sizes 1024, 10240, 51200, 102400 bytes. No SI/binary unit substitution. | SAFE |
| V19 | J(p) = Σj Lj(pj) + λ Σ(i,j) in E wij C(pj,sij). | A §E; `E/src/objective.py:49–56`. Exactly the same destination-only additive objective; “in E” is typographic spelling of membership, not a changed edge set/model. | SAFE |
| V20 | “Lj: synthetic local preference loss”. | A §§C/E; P §§D/E/H; original unit margin is zero at baseline, one per replacement. No calibration or empirical utility meaning claimed. | SAFE |
| V21 | “C: measured latency, ms/request”. | A §§B/E; R; destination protocol argument pj in the equation. This is local request-service cost, not task makespan. | SAFE |
| V22 | “wij: controlled request demand”. | A §E; W has per-edge weight 100 for the witness. Not measured GAIA traffic. | SAFE |
| V23 | “λ: preference-loss units per accumulated ms”. | A §E; dimensionful conversion from weighted accumulated ms into synthetic loss units. Not a dimensionless coefficient. | SAFE |
| V24 | Witness: “Workflow analysis_task”. | A §D; corresponding W row and literal YAML template. | SAFE |
| V25 | Witness: “Payload 10 KB”. | W row has payload_size_bytes=10240; R's 10240-byte means are used. | SAFE |
| V26 | Witness: “Demand 100 requests/edge”. | W row has traffic_normalization=per_edge, scale=100, two cost-bearing edges each of weight 100. Not a measured runtime load. | SAFE |
| V27 | Witness: “λ 0.1”. | W corresponding saved witness; unchanged coefficient. | SAFE |
| V28 | Witness: “Margin synthetic unit loss”. | A §E; original margin=1.0, `manual_margin_losses` at `E/src/objective.py:16–22`. No derivation from fixed router confidence 0.3. | SAFE |
| V29 | Witness: “Change Agent 1: A2A→ANP”. | A §D; W all_four/per_edge/100/0.1: baseline agent 1=A2A; minimizer agent 1=ANP. | SAFE |
| V30 | Witness: “Agora unchanged”. | W original baseline `{0:Agora,1:A2A,2:ACP,3:A2A}` and all-four minimizer `{0:Agora,1:ANP,2:ACP,3:A2A}`. This refers to the all-four witness, separate from global-exclusion ablation. | SAFE |
| V31 | “The exhaustive oracle finds a changed minimizer of the declared objective; this is not a GAIA task-quality claim.” | A §§D/F; W all-four witness enumerates 256 assignments, objective_delta=−0.5649729999999984 synthetic loss units. Optimality is only within the declared model/candidates. | SAFE |
| V32 | “Global Agora exclusion preserves this eligible reversal.” | A §D; W restricted witness eligible node 1 and forced node 0. No Agora remains in the candidate set; forced replacement is not counted as preference reversal. | SAFE |
| V33 | “Forced agent-0 replacement leaves no whole-assignment gain versus the original baseline in this analysis ablation.” | A §D; W original-reference delta=+0.4350270000000016, feasible-seed delta=−0.5649729999999984. Original baseline is now infeasible; eligible saving does not cover both local replacement penalties. | SAFE |
| V34 | Supported: “Audited call: no explicit graph/edge-demand input.” | Same scope/evidence as V01; does not say ProtocolRouter is topology-blind. | SAFE |
| V35 | Supported: “Non-identical measured local runtime costs.” | A §B; all 16 exact means in R; specific local implementation paths and one profiling campaign only. No statistical universal ordering. | SAFE |
| V36 | Supported: “Declared objective admits reversals.” | A §§C/D/E; G/W; no new routing method or task-performance gain asserted. | SAFE |
| V37 | Supported: “Eligible A2A→ANP reversal without Agora.” | Same restricted witness and qualifications as V10/V32/V33; not a whole-assignment no-Agora improvement. | SAFE |
| V38 | Not established: “GAIA task-quality improvement”. | A §§B/F/H; no full GAIA/LLM task-quality trial in this study. | SAFE |
| V39 | Not established: “Makespan improvement”. | A §E: summing request-service times does not establish concurrent task elapsed time; no makespan measurement. | SAFE |
| V40 | Not established: “Calibrated local utility or preference margins”. | A §E; P §§D/E/H. Unit margins are controlled sensitivity inputs; no faithful released GAIA graded alternative-strength signal recovered. | SAFE |
| V41 | Not established: “Measured GAIA traffic traces”. | A §D; official named config templates and controlled traffic, not observed execution traces. | SAFE |
| V42 | Not established: “Universal protocol rankings”. | A §B measurement/uncertainty limits; specific local HTTP/runtime paths, retained outlier and close ACP/ANP means. | SAFE |
| V43 | Not established: “New routing-method superiority”. | A §§F/H; no novel learned routing method or comparable routing-quality trial. | SAFE |
| V44 | “The public release does not expose graded agent×protocol preferences or validated feasible-alternative masks for this GAIA path.” | P §§B/D/G/H; A §E. Strictly this GAIA path. Numeric scores in other SDK/security routers exist and are not denied. | SAFE |
| V45 | Conditional question about jointly studying demand under a constraint-preserving formulation, if such signals become available. | P §G describes the missing validated current-agent feasible sets; P §H recommends outreach. V2 asks about possible future work and does not claim constraints have been recovered or preserved in the current sensitivity test. | SAFE |
| V46 | Footer citation: “Hongyi Du et al. ProtocolBench. ICML 2026. OpenReview.” | V1 C34 and its primary citation verification: official ICML 2026 Downloads listing plus indexed camera-ready metadata. Full conference title is retained in README_v2.md. | SAFE |
| V47 | Source link: AgentProtocols @ 6349eb97; author GitHub. | HEAD verified read-only against full baseline; sanitized remote origin identifies `https://github.com/ulab-uiuc/AgentProtocols.git`. Author link is user-supplied. | SAFE |
| V48 | Hero (a): task_analysis/agents_config feed the GAIA assignment call; baseline agent circles 0=Agora,1=A2A,2=ACP,3=A2A. | A §A/D; saved baseline in W and `notes/findings.md`. Arrows represent argument flow, not empirically graded task influence; heuristic fallback remains disclosed. | SAFE |
| V49 | Hero dashed annotation: “graph / edge demand not explicit inputs to the audited assignment call”. | A §A; same as V01. Dashed leader points toward graph demand information; it is an explanatory leader, not an additional message edge. | SAFE |
| V50 | Hero (b): 0→1→2→final, edge-demand labels w01/w12, destination adapter/request metrics. | A §§A/D; official template. Two inter-agent edges, one dashed terminal event; no 2→3/final-agent cost. Edge width qualitatively indicates controlled demand, not measured packet count. | SAFE |
| V51 | Hero (c): four cost-bank dots, “10 KB means (ms; log)”, native axis 1/10/30, 480/480 requests succeeded. | A §B; exact R 10 KB means A2A 1.4698952333333333, ACP 1.3135204333333332, ANP 1.3133979333333334, Agora 23.38588173333333. Dot coordinates are logarithmic display transforms only. No ranking precision or fabricated mini-bar data. | SAFE |
| V52 | Hero arrow from cost bank to “measured C + controlled demand + synthetic margin”. | A §E; exact objective and declared sensitivity inputs. No additional loss term, empirical local suitability proxy or conversion-only cost introduced. | SAFE |
| V53 | Hero (d): the same analysis graph before/after, agent 1 alone highlighted; Agent 1 A2A→ANP, Agora unchanged. | Same all-four witness as V24–V30. Agent 3 is omitted from this graph because it has no edge and remains A2A, explicitly captioned. No before/after traffic or workflow mutation. | SAFE |
| V54 | Hero controls: 10 KB, 100 controlled requests/edge, λ=0.1, synthetic unit margin; footer “Diagnostic sensitivity analysis — not an end-to-end GAIA performance claim.” | W saved witness; A §§D–F. No task success, latency/makespan improvement, security preservation or deployment recommendation. | SAFE |
| V55 | Full latency figure: all four protocol curves and all 16 saved means, actual 1/10/50/100 KB positions, explicit log y-axis, direct end labels. | A §B; R exact strings below. Means were not recalculated, smoothed, replaced, rounded in source, or outlier-filtered. Lines are guides between measured buckets; separated end labels are connected to the correct endpoint and do not assert significance. | SAFE |

## Exact latency strings used (unchanged)

| Protocol | 1 KB | 10 KB | 50 KB | 100 KB |
|---|---|---|---|---|
| A2A | 1.3585756 | 1.4698952333333333 | 1.9828458666666666 | 2.707684433333333 |
| ACP | 1.2176304666666666 | 1.3135204333333332 | 1.8806641333333334 | 2.608613 |
| ANP | 1.3194534 | 1.3133979333333334 | 1.7973076 | 6.2451045 |
| Agora | 23.70959746666667 | 23.38588173333333 | 26.200420033333334 | 26.8474713 |

## Change from v1

No scientific claim was strengthened and no scientific result, source, measured
value, byte value, baseline, local margin, objective, workflow or candidate-set
semantics changed. The prose and claim ordering changed to serve two pages.
The previously audited 37/144 controlled statistic is now visible on page 1;
the new miniature cost bank reuses the same stored 10 KB means. Neither is a new
experiment/result. The final question explicitly conditions a future
constraint-preserving study on unavailable validated signals; it does not claim
the present diagnostic preserves task constraints. The citation display is
shortened, with full metadata in README_v2.md and the preserved V1 audit.

## Primary reference and interpretation boundary

Full reference: Hongyi Du et al., “ProtocolBench: Which LLM MultiAgent Protocol
to Choose?”, ICML 2026.
[Official ICML listing](https://icml.cc/Downloads/2026);
[OpenReview paper page](https://openreview.net/forum?id=GZRiXE2zBe).
The exact title/venue/year was verified in the previous authoring round against
the official listing and indexed camera-ready metadata. Direct OpenReview opens
returned browser verification; no access control was bypassed. No new external
scientific claim or third-party figure was added in the redesign.

All claims remain diagnostic: local measurements, official configuration-template
instantiations, controlled demand and synthetic margins. Eligible no-Agora
preference reversal and whole-assignment benefit are explicitly distinguished.
No defect, novelty, universal ranking, task-quality/makespan gain or router
superiority claim is made. No scientific experiment was rerun for v2.
