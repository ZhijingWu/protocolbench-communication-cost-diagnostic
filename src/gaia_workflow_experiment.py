"""Workflow sensitivity using the existing exhaustive oracle, without runtime GAIA."""
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from .cost_schema import canonical_real_rows, read_rows, sha256
from .gaia_workflow import OFFICIAL_CONFIG, WORKFLOWS, instantiate_workflow, load_official_patterns
from .graph_aware_oracle import exhaustive_oracle, reversal_thresholds
from .io_utils import BASE, PROTOCOLS, fingerprint, load_config, output_path, write_csv, write_json
from .local_router_adapter import baseline_assignment
from .objective import evaluate_objective, manual_margin_losses

FIELDS = ["workflow", "candidate_set", "protocols", "traffic_label", "traffic_scale",
          "traffic_normalization", "lambda", "payload_size_bytes", "agent_edges", "terminal_events",
          "baseline_assignment", "graph_assignment", "baseline_feasible", "oracle_feasible_seed",
          "forced_removal_nodes", "changed_nodes", "changed_protocols", "eligible_changed_nodes",
          "eligible_preference_reversal_nodes", "a2a_acp_anp_preference_reversal_nodes",
          "baseline_local_loss", "graph_local_loss", "baseline_comm_cost", "graph_comm_cost",
          "baseline_objective", "graph_objective", "objective_delta", "weighted_comm_saving",
          "strict_reversal", "strict_eligible_preference_reversal", "feasible_seed_objective",
          "objective_delta_vs_feasible_seed", "assignments_enumerated", "runtime_seconds",
          "protocol_preference_handling", "result_kind"]


def load_verified_real_latencies(base=BASE):
    base = Path(base)
    source = base / "results/processed/real_protocol_costs.csv"
    raw = base / "results/raw/real_protocol_profile.csv"
    manifest_path = base / "results/raw/real_protocol_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("mode") != "real_local":
        raise ValueError("Need verified real_local communication provenance")
    for path in (source, raw):
        if manifest.get("output_sha256", {}).get(str(path.relative_to(base))) != sha256(path):
            raise ValueError(f"Measured source hash mismatch: {path.name}")
    source_rows, _ = read_rows(source)
    canonical = canonical_real_rows(source_rows)  # pure string mapping, no file writes/reaggregation
    return {(r["protocol"], int(r["payload_size_bytes"])): float(r["mean_latency_ms"]) for r in canonical}, {
        "cost_metric": "mean_latency_ms", "measurement_kind": "end_to_end_local_request",
        "input_sha256": {str(p.relative_to(base)):sha256(p) for p in (source,raw,manifest_path)},
        "latency_boundary": manifest["latency_boundary"], "measurements_recomputed": False}


def run_candidate_oracle(baseline, graph, costs, full_losses, lam, protocols):
    """Original baseline remains the reference even if exclusion makes it infeasible.

    The existing oracle requires a feasible baseline parameter. Its seed is only
    enumeration bookkeeping; forbidden baseline values are replaced by the first
    minimum-loss allowed candidate. Scores are copied from the ORIGINAL margin
    table. Report this seed separately and never overwrite the saved baseline.
    """
    protocols = tuple(protocols)
    if not protocols or len(set(protocols)) != len(protocols) or any(p not in PROTOCOLS for p in protocols):
        raise ValueError("Invalid candidate set")
    restricted_losses = {n:{p:full_losses[n][p] for p in protocols} for n in baseline}
    seed = {n:(p if p in protocols else min(protocols, key=lambda q: full_losses[n][q]))
            for n,p in baseline.items()}
    forced = [n for n,p in sorted(baseline.items()) if p not in protocols]
    result = exhaustive_oracle(seed, graph["edges"], costs, restricted_losses, lam, protocols=protocols)
    assignment = result["best_assignment"]
    original = evaluate_objective(baseline, graph["edges"], costs, full_losses, lam)
    best = evaluate_objective(assignment, graph["edges"], costs, full_losses, lam)
    assert math.isclose(best.total_objective, result["best"]["total_objective"], rel_tol=1e-12)
    seed_value = evaluate_objective(seed, graph["edges"], costs, full_losses, lam)
    changed = [n for n in sorted(baseline) if baseline[n] != assignment[n]]
    eligible = [n for n in changed if n not in forced]
    preference_nodes, node_evidence = [], []
    for node in eligible:
        saving = math.fsum(e["weight"]*(costs[baseline[node],e["payload_size_bytes"]] -
                                      costs[assignment[node],e["payload_size_bytes"]])
                           for e in graph["edges"] if e["dst"] == node)
        margin = full_losses[node][assignment[node]] - full_losses[node][baseline[node]]
        advantage = lam*saving - margin
        strict = advantage > 0 and not math.isclose(advantage, 0, abs_tol=1e-12)
        node_evidence.append({"node":node, "from":baseline[node], "to":assignment[node],
                              "communication_saving_ms":saving, "local_margin":margin,
                              "weighted_saving":lam*saving, "strict_preference_reversal":strict})
        if strict:
            preference_nodes.append(node)
    delta = best.total_objective-original.total_objective
    strict_original = bool(changed) and delta < 0 and not math.isclose(delta,0,abs_tol=1e-12)
    return {"baseline_assignment":dict(baseline), "graph_assignment":assignment,
            "baseline_feasible":not forced, "oracle_feasible_seed":seed,
            "forced_removal_nodes":forced, "changed_nodes":changed,
            "changed_protocols":[{"node":n,"from":baseline[n],"to":assignment[n],"forced":n in forced} for n in changed],
            "eligible_changed_nodes":eligible, "eligible_preference_reversal_nodes":preference_nodes,
            "a2a_acp_anp_preference_reversal_nodes":[n for n in preference_nodes
                if baseline[n] != "Agora" and assignment[n] != "Agora"],
            "node_reversal_evidence":node_evidence,
            "baseline_local_loss":original.local_loss, "graph_local_loss":best.local_loss,
            "baseline_comm_cost":original.communication_cost, "graph_comm_cost":best.communication_cost,
            "baseline_objective":original.total_objective, "graph_objective":best.total_objective,
            "objective_delta":delta, "weighted_comm_saving":lam*(original.communication_cost-best.communication_cost),
            "strict_reversal":strict_original, "strict_eligible_preference_reversal":bool(preference_nodes),
            "feasible_seed_objective":seed_value.total_objective,
            "objective_delta_vs_feasible_seed":best.total_objective-seed_value.total_objective,
            "assignments_enumerated":result["assignments_enumerated"], "runtime_seconds":result["runtime_seconds"]}


def grid_minima(rows, field):
    matches = [r for r in rows if r[field]]
    if not matches:
        return {"minimum_traffic_scale":None, "minimum_lambda":None,
                "minimum_lambda_at_minimum_traffic_scale":None, "minimum_traffic_scale_at_minimum_lambda":None}
    scale = min(r["traffic_scale"] for r in matches)
    lam = min(r["lambda"] for r in matches)
    return {"minimum_traffic_scale":scale, "minimum_lambda":lam,
            "minimum_lambda_at_minimum_traffic_scale":min(r["lambda"] for r in matches if r["traffic_scale"]==scale),
            "minimum_traffic_scale_at_minimum_lambda":min(r["traffic_scale"] for r in matches if r["lambda"]==lam)}


def summarize_variant(rows):
    strict = [r for r in rows if r["strict_reversal"]]
    eligible = [r for r in rows if r["strict_eligible_preference_reversal"]]
    non_agora = [r for r in rows if r["a2a_acp_anp_preference_reversal_nodes"]]
    purely_non_agora = [r for r in strict if not r["forced_removal_nodes"] and
        all(c["from"] != "Agora" and c["to"] != "Agora" for c in r["changed_protocols"])]
    transitions = Counter(f"{c['from']} -> {c['to']}" for r in strict for c in r["changed_protocols"])
    eligible_transitions = Counter(f"{c['from']} -> {c['to']}" for r in rows for c in r["node_reversal_evidence"]
                                  if c["strict_preference_reversal"])
    def example(row):
        return {k:row[k] for k in ("workflow","traffic_scale","traffic_normalization","lambda","baseline_assignment",
            "graph_assignment","forced_removal_nodes","eligible_preference_reversal_nodes",
            "a2a_acp_anp_preference_reversal_nodes","objective_delta","objective_delta_vs_feasible_seed")}
    return {"total_cases":len(rows), "strict_reversals_vs_original_baseline":len(strict),
            "strict_eligible_preference_reversal_cases":len(eligible),
            "a2a_acp_anp_preference_reversal_cases":len(non_agora),
            "pure_a2a_acp_anp_strict_assignment_reversal_cases":len(purely_non_agora),
            "cases_with_forced_removal":sum(bool(r["forced_removal_nodes"]) for r in rows),
            "strict_original_baseline_grid_minima":grid_minima(rows,"strict_reversal"),
            "eligible_preference_grid_minima":grid_minima(rows,"strict_eligible_preference_reversal"),
            "strict_changed_node_transitions":dict(transitions),
            "eligible_preference_node_transitions":dict(eligible_transitions),
            "distinct_graph_assignments":[json.loads(s) for s in sorted({json.dumps(r["graph_assignment"],sort_keys=True) for r in rows})],
            "strict_reversal_examples":[example(r) for r in strict[:3]],
            "non_agora_preference_reversal_examples":[example(r) for r in non_agora],
            "strict_by_traffic_scale":{str(s):sum(r["traffic_scale"]==s for r in strict) for s in sorted({r["traffic_scale"] for r in rows})},
            "strict_by_normalization":{s:sum(r["traffic_normalization"]==s for r in strict) for s in sorted({r["traffic_normalization"] for r in rows})}}


def workflow_sweep(config, patterns, baseline, costs):
    if config.get("local_loss_source") != "controlled_manual_margin":
        raise ValueError("Preserve the existing controlled manual margin declaration")
    losses = manual_margin_losses(baseline, config["manual_local_margin"])
    rows, graphs, summaries = [], [], {}
    variants = {"all_four":PROTOCOLS, "without_agora":tuple(p for p in PROTOCOLS if p != "Agora")}
    for name in WORKFLOWS:
        for normalize in config.get("normalizations", [False]):
            for traffic_label, scale in config["traffic_scales"].items():
                graph = instantiate_workflow(patterns[name],config["agents"],name,scale,
                    config["payload_size_bytes"],normalize)
                graphs.append(graph)
                for label, protocols in variants.items():
                    for lam in config["lambdas"]:
                        result = run_candidate_oracle(baseline,graph,costs,losses,lam,protocols)
                        rows.append({"workflow":name,"candidate_set":label,"protocols":list(protocols),
                            "traffic_label":traffic_label,"traffic_scale":graph["traffic_scale"],
                            "traffic_normalization":graph["traffic_normalization"],"lambda":lam,
                            "payload_size_bytes":config["payload_size_bytes"],
                            "agent_edges":[{"src":e["src"],"dst":e["dst"],"weight":e["weight"]} for e in graph["edges"]],
                            "terminal_events":graph["terminal_events"],**result,
                            "protocol_preference_handling":"metadata only",
                            "result_kind":"repository_workflow_controlled_sensitivity"})
        summaries[name] = {"official_pattern":patterns[name],
            "variants":{label:summarize_variant([r for r in rows if r["workflow"]==name and r["candidate_set"]==label]) for label in variants}}
    return rows, graphs, summaries, losses


def append_workflow_findings(base, summary):
    lines = ["## Repository-defined GAIA workflow structures", "",
        "Protocol latencies are measured locally. The workflow structure comes from the",
        "official scenarios/gaia/config/meta_protocol.yaml message_flow_patterns, parsed",
        "directly without editing it. Traffic scaling remains controlled, and local",
        "preference margins remain synthetic (unchanged margin=1). This is still not an",
        "end-to-end GAIA task-quality result. No LLM, GAIA task or new routing method ran.", "",
        "The fixed baseline is 0=Agora, 1=A2A, 2=ACP, 3=A2A. Payload size stays 10 KB;",
        "traffic scales 1/10/100, lambda grid and per-edge/equal-total controls are reused.",
        "protocol_preference and reason remain metadata and never enter local losses.", "",
        "analysis_task retains the exact 0->1, 1->2, 2->final structure. final is a",
        "terminal output marker: MeshNetwork.execute_workflow assigns final_result and",
        "breaks; it is not another assigned agent. Thus only 0->1 and 1->2 enter the",
        "agent-communication objective. The final event is retained in output metadata;",
        "no agent 3 edge or unmeasured final-output cost is invented.", "",
        "collaborative_task retains 0->all and all->0, instantiated as 0<->1/2/3 over",
        "the unchanged four-agent roster, excluding hub self-messages. This explicit",
        "peer broadcast/aggregation convention mirrors core star topology handling;",
        "the literal official steps and expansion are preserved in the graph manifest.",
        "MeshNetwork executes workflow.message_flow, not these named templates directly:",
        "these are config-grounded demand structures, not captured GAIA runtime traffic.", "",
        "Global removal of Agora makes original agent 0's baseline infeasible. Its",
        "mandatory replacement is labeled forced_removal, never a preference reversal.",
        "The existing exhaustive oracle uses a separately reported feasible enumeration",
        "seed (agent 0=A2A, first tied minimum-loss allowed protocol); the ORIGINAL",
        "baseline remains the comparison reference, and no saved assignment or local",
        "margin changes. Allowed losses copy the original entries exactly. Relative",
        "scores to both original baseline and feasible seed are reported separately.", "",
        "A strict assignment reversal means the constrained assignment beats the",
        "original baseline objective. An eligible preference reversal means an agent",
        "whose baseline protocol was still allowed changes only when weighted incoming",
        "communication saving exceeds its original margin. The latter avoids counting",
        "forced removal or tie selection as evidence. Eligible A2A/ACP/ANP changes",
        "can persist even if the forced removal penalty prevents beating the original,",
        "now-infeasible baseline for the whole assignment.", "",
        "| Workflow | Candidates | Cases | Strict vs original | Eligible preference cases | A2A/ACP/ANP preference cases |",
        "|---|---|---:|---:|---:|---:|"]
    for name, workflow in summary["workflows"].items():
        for label, result in workflow["variants"].items():
            lines.append(f"| {name} | {label} | {result['total_cases']} | {result['strict_reversals_vs_original_baseline']} | {result['strict_eligible_preference_reversal_cases']} | {result['a2a_acp_anp_preference_reversal_cases']} |")
    lines.extend(["", "Grid minima and assignments (minimum scale and minimum lambda may occur in",
        "different cases; no continuous threshold is inferred from a finite grid):", ""])
    for name, workflow in summary["workflows"].items():
        for label, result in workflow["variants"].items():
            lines.append(f"- {name}, {label}: strict-original minima {result['strict_original_baseline_grid_minima']}; eligible preference minima {result['eligible_preference_grid_minima']}.")
            lines.append(f"  Assignments: {result['distinct_graph_assignments']}.")
    lines.extend(["", "Full changed-node/protocol evidence, forced changes, original baseline, feasible",
        "seed, objective values and witnesses are in results/processed/gaia_workflow_reversal.csv",
        "and gaia_workflow_summary.json. Official patterns, final/all handling, source",
        "hashes and controlled weighted graphs are retained. Stored mean latencies are",
        "point estimates; tiny ANP/ACP differences do not establish statistical superiority.",
        "Previous synthetic-topology diagnostics remain preserved as historical outputs.", ""])
    start = "<!-- gaia-workflow-section:start -->"
    end = "<!-- gaia-workflow-section:end -->"
    path = base / "notes/findings.md"
    current = path.read_text(encoding="utf-8")
    if start in current:
        if end not in current:
            raise ValueError("Incomplete prior workflow findings section")
        left, remainder = current.split(start,1)
        _, right = remainder.split(end,1)
        current = left.rstrip()+"\n"+right.lstrip()
    output_path(path).write_text(current.rstrip()+"\n\n"+start+"\n"+"\n".join(lines)+end+"\n",encoding="utf-8")


def run_workflow_experiment(base=BASE, official_config=OFFICIAL_CONFIG):
    base = Path(base)
    config_path = base / "configs/topology_cases.yaml"
    config = load_config(config_path)
    baseline_path = base / "results/raw/local_router_output.json"
    baseline, info = baseline_assignment(config["task_analysis"],config["agents"],baseline_path)
    costs, cost_info = load_verified_real_latencies(base)
    patterns = load_official_patterns(official_config)
    rows, graphs, workflows, losses = workflow_sweep(config,patterns,baseline,costs)
    summary = {"result_kind":"repository_workflow_controlled_sensitivity", "baseline_assignment":baseline,
        "baseline_source":info["source"],"local_inputs_sha256":info["local_inputs_sha256"],
        "manual_local_margin":config["manual_local_margin"],"local_losses":losses,
        "payload_size_bytes":config["payload_size_bytes"],"cost_provenance":cost_info,
        "official_config_path":str(official_config),"official_config_sha256":sha256(official_config),
        "control_config_sha256":sha256(config_path),"baseline_file_sha256":sha256(baseline_path),
        "controlled_traffic_scales":config["traffic_scales"],"controlled_lambdas":config["lambdas"],
        "normalizations":config["normalizations"],"total_cases":len(rows),"workflows":workflows,
        "candidate_set_totals":{label:summarize_variant([r for r in rows if r["candidate_set"]==label])
            for label in ("all_four","without_agora")},
        "no_agora_policy":"global exclusion; forced changes are not eligible preference reversals",
        "original_baseline_unchanged":True,"protocol_preferences":"metadata only", "graphs":graphs,
        "limitations":["measured local latency point estimates", "official config templates, not executed GAIA traces",
            "traffic scaling controlled", "local margins synthetic", "terminal output cost outside agent objective",
            "all instantiated as peers, no self-loop", "no end-to-end GAIA task-quality claim"]}
    serial = []
    for row in rows:
        serial.append({k:(json.dumps(row[k],sort_keys=True) if isinstance(row[k],(dict,list)) else row[k]) for k in FIELDS})
    write_csv(base / "results/processed/gaia_workflow_reversal.csv",serial,FIELDS)
    write_json(base / "results/processed/gaia_workflow_summary.json",summary)
    append_workflow_findings(base,summary)
    return summary
