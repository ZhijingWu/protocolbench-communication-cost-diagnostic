#!/usr/bin/env python3
"""Measured-cost oracle with declared manual local margins: sensitivity only."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import hashlib
import json
from collections import Counter
from src.io_utils import BASE, fingerprint, load_config, provenance, write_csv, write_json, output_path
from src.cost_schema import ensure_canonical_real_costs, archive_joint_outputs
from src.local_router_adapter import baseline_assignment
from src.topology_generator import generate_cases
from src.objective import load_measured_costs, manual_margin_losses
from src.graph_aware_oracle import exhaustive_oracle, reversal_thresholds

FIELDS = ["topology", "traffic_scale", "lambda", "baseline_assignment", "graph_assignment",
          "changed_nodes", "baseline_comm_cost", "graph_comm_cost", "objective_delta",
          "traffic_label", "traffic_normalization", "total_messages", "baseline_local_loss",
          "graph_local_loss", "baseline_objective", "graph_objective", "weighted_comm_saving",
          "strict_reversal", "cost_metric", "profile_mode", "local_loss_source", "result_kind",
          "graph_sha256", "assignments_enumerated", "runtime_seconds"]
THRESHOLD_FIELDS = ["topology", "traffic_scale", "traffic_normalization", "node",
                    "baseline_protocol", "alternative_protocol", "local_margin",
                    "incoming_comm_saving", "lambda_threshold", "traffic_threshold_at_lambda",
                    "strict_reversal", "first_reversal_candidate"]


def resolve_cost_file(mode, explicit=None):
    if explicit is not None:
        return Path(explicit)
    if mode == "real":
        return ensure_canonical_real_costs(BASE)
    if mode == "conversion-only":
        return BASE / "results/processed/protocol_costs.csv"
    raise ValueError("Choose real or conversion-only profile mode")


def summarize_reversals(rows):
    strict = [r for r in rows if r["strict_reversal"]]
    protocols = ("A2A", "ACP", "ANP", "Agora")
    changed_from, changed_to = Counter(), Counter()
    case_from, case_to = Counter(), Counter()
    non_agora, agora_related = [], []
    for row in strict:
        before = json.loads(row["baseline_assignment"])
        after = json.loads(row["graph_assignment"])
        changed = json.loads(row["changed_nodes"])
        assert changed
        sources, targets = set(), set()
        touches_agora = False
        for node in changed:
            source, target = before[node], after[node]
            changed_from[source] += 1
            changed_to[target] += 1
            sources.add(source)
            targets.add(target)
            touches_agora |= "Agora" in (source, target)
        case_from.update(sources)
        case_to.update(targets)
        (agora_related if touches_agora else non_agora).append(row)
    def counts(field, key=lambda v: v):
        observed = Counter(key(r[field]) for r in strict)
        return {str(value): observed[value] for value in sorted({key(r[field]) for r in rows})}
    def witness(row):
        return {k: (json.loads(row[k]) if k in ("baseline_assignment", "graph_assignment", "changed_nodes") else row[k])
                for k in ("topology", "traffic_scale", "lambda", "traffic_normalization", "baseline_assignment",
                          "graph_assignment", "changed_nodes", "objective_delta")}
    min_scale = min((r["traffic_scale"] for r in strict), default=None)
    min_lambda = min((r["lambda"] for r in strict), default=None)
    return {
        "total_cases": len(rows), "strict_reversal_cases": len(strict),
        "by_topology_cases": counts("topology"),
        "by_traffic_scale_cases": counts("traffic_scale", lambda v: format(float(v), "g")),
        "by_traffic_normalization_cases": counts("traffic_normalization"),
        "changed_node_count": sum(changed_from.values()),
        "changed_from_protocol_node_events": {p: changed_from[p] for p in protocols},
        "changed_to_protocol_node_events": {p: changed_to[p] for p in protocols},
        "changed_from_protocol_case_counts": {p: case_from[p] for p in protocols},
        "changed_to_protocol_case_counts": {p: case_to[p] for p in protocols},
        "cases_with_agora_changes": len(agora_related), "cases_without_agora_changes": len(non_agora),
        "all_reversals_involve_agora": bool(strict) and len(agora_related) == len(strict),
        "any_reversal_to_agora": changed_to["Agora"] > 0,
        "a2a_acp_anp_only_reversal_exists": bool(non_agora),
        "a2a_acp_anp_only_reversal_cases": len(non_agora),
        "a2a_acp_anp_only_witness": witness(non_agora[0]) if non_agora else None,
        "minimum_traffic_scale": min_scale, "minimum_lambda": min_lambda,
        "minimum_lambda_at_minimum_traffic_scale": min((r["lambda"] for r in strict if r["traffic_scale"] == min_scale), default=None),
        "minimum_traffic_scale_at_minimum_lambda": min((r["traffic_scale"] for r in strict if r["lambda"] == min_lambda), default=None),
        "minimum_traffic_scale_witness": witness(min((r for r in strict if r["traffic_scale"] == min_scale), key=lambda r: r["lambda"])) if strict else None,
        "minimum_lambda_witness": witness(min((r for r in strict if r["lambda"] == min_lambda), key=lambda r: r["traffic_scale"])) if strict else None,
        "counting_definition": "topology/traffic counts are cases; protocol node-events count each changed node; protocol case counts can overlap",
        "non_agora_definition": "Every changed-from and changed-to protocol is A2A/ACP/ANP; an unchanged baseline Agora node is allowed",
    }


def write_findings(config, mode, metric, cost_file, info, rows, summary, archives):
    real = mode == "real"
    source_note = ("Real latency values are measured end-to-end LOCAL request costs from the verified real profiler. "
                   "No profiling was rerun and no means, medians, p95 values or byte values were recomputed." if real else
                   "Conversion-only values measure the original converter/JSON boundary and are not network latency.")
    kinds = ("end_to_end_local_request; ANP and Agora are the existing repository HTTP paths" if real else
             "conversion_serialization")
    table = "\n".join(f"| {r['topology']} | {r['traffic_normalization']} | {r['traffic_scale']} | {r['lambda']} | {r['changed_nodes']} | {r['objective_delta']:.6g} |"
                      for r in [r for r in rows if r["strict_reversal"]][:5])
    archive_note = "\n".join(f"- {a['original_path']} -> {a['archive_path']} (SHA256 {a['sha256']})" for a in archives)
    note = f"""# Findings: topology-aware protocol diagnostic

## A. Directly observed in original code
See experiment_design.md for exact paths/functions and source snippets. The
GAIA assignment interface takes task_analysis and agents_config without explicit
graph or edge traffic. Its audited caller supplies no LLM client, so the existing
heuristic fallback is the measured baseline. Destination assigned_protocol selects
outbound adapters. No pairwise mismatch penalty is supported by this audit.
Core AgentNetwork has a graph; GAIA deliver bypasses its edge permission check.

Baseline consumption: {info['source']}; original fixed-feature assignment remains
0=Agora, 1=A2A, 2=ACP, 3=A2A. The saved local-input hash is
{info['local_inputs_sha256']}. Topology/traffic variation did not change this
baseline in the existing 24-case diagnostic. No baseline was regenerated here.

## B. Measured communication evidence and data interface
{source_note}
Canonical oracle input: {cost_file.name}; mode={mode}; metric={metric}.
Measurement kind: {kinds}.

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
SYNTHETIC sensitivity inputs: margin={config['manual_local_margin']} local-loss units
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

Total cases: {summary['total_cases']}; strict reversal cases: {summary['strict_reversal_cases']}.
By topology (case counts): {summary['by_topology_cases']}.
By traffic scale (case counts): {summary['by_traffic_scale_cases']}.
By traffic normalization (case counts): {summary['by_traffic_normalization_cases']}.
Changed-from protocols (node events): {summary['changed_from_protocol_node_events']}.
Changed-to protocols (node events): {summary['changed_to_protocol_node_events']}.
There are {summary['changed_node_count']} changed-node events. Per-protocol CASE counts
(which may overlap) and witness assignments are in reversal_summary.json.

Every reversal involves an Agora change: {summary['all_reversals_involve_agora']}.
Cases with Agora changes: {summary['cases_with_agora_changes']}; without: {summary['cases_without_agora_changes']}.
Any change TO Agora: {summary['any_reversal_to_agora']}.
Any A2A/ACP/ANP-only reversal: {summary['a2a_acp_anp_only_reversal_exists']}.
Here "only" describes changed protocols; an unchanged baseline Agora node is allowed.

Minimum traffic_scale with a strict reversal: {summary['minimum_traffic_scale']},
at lambda={summary['minimum_lambda_at_minimum_traffic_scale']}.
Minimum lambda with a strict reversal: {summary['minimum_lambda']},
at traffic_scale={summary['minimum_traffic_scale_at_minimum_lambda']}.
These are separate minima within the unchanged finite grid, not asserted continuous
thresholds or a single jointly attained minimum. Exact model break-even thresholds
remain in reversal_thresholds.csv; equality is a tie and baseline ties are retained.

| Topology | Normalization | Scale | Lambda | Changed nodes | Objective delta |
|---|---|---:|---:|---|---:|
{table}

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
{archive_note or '- No previous mode/metric outputs replaced in this run.'}
"""
    output_path(BASE / "notes/findings.md").write_text(note, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=BASE / "configs/topology_cases.yaml")
    parser.add_argument("--costs", type=Path, help="Canonical cost CSV; default preserves both modes and prepares verified real rows")
    parser.add_argument("--profile-mode", choices=["real", "conversion-only"], required=True)
    parser.add_argument("--cost-metric", choices=["mean_encoded_bytes", "mean_latency_ms", "mean_conversion_runtime_ms"])
    parser.add_argument("--routing-output", type=Path, default=BASE / "results/raw/local_router_output.json")
    args = parser.parse_args()
    args.costs = resolve_cost_file(args.profile_mode, args.costs)
    config = load_config(args.config)
    if config.get("local_loss_source") != "controlled_manual_margin":
        raise ValueError("This config must explicitly declare controlled_manual_margin")
    metric = args.cost_metric or config["cost_metric"]
    costs = load_measured_costs(args.costs, args.profile_mode, metric)
    baseline, info = baseline_assignment(config["task_analysis"], config["agents"], args.routing_output)
    losses = manual_margin_losses(baseline, config["manual_local_margin"])
    rows, thresholds = [], []
    for graph in generate_cases(config):
        for threshold in reversal_thresholds(baseline, graph["edges"], costs, losses, graph["traffic_scale"]):
            thresholds.append({"topology": graph["topology"], "traffic_scale": graph["traffic_scale"],
                               "traffic_normalization": graph["traffic_normalization"], **threshold})
        for lam in config["lambdas"]:
            result = exhaustive_oracle(baseline, graph["edges"], costs, losses, lam)
            before, after = result["baseline"], result["best"]
            saving = lam * (before["communication_cost"] - after["communication_cost"])
            delta = after["total_objective"] - before["total_objective"]  # negative favors oracle
            row = {"topology": graph["topology"], "traffic_scale": graph["traffic_scale"], "lambda": lam,
                   "baseline_assignment": json.dumps(baseline, sort_keys=True),
                   "graph_assignment": json.dumps(result["best_assignment"], sort_keys=True),
                   "changed_nodes": json.dumps(result["changed_nodes"]),
                   "baseline_comm_cost": before["communication_cost"], "graph_comm_cost": after["communication_cost"],
                   "objective_delta": delta, "traffic_label": graph["traffic_label"],
                   "traffic_normalization": graph["traffic_normalization"], "total_messages": graph["total_messages"],
                   "baseline_local_loss": before["local_loss"], "graph_local_loss": after["local_loss"],
                   "baseline_objective": before["total_objective"], "graph_objective": after["total_objective"],
                   "weighted_comm_saving": saving,
                   "strict_reversal": bool(result["changed_nodes"]) and saving > after["local_loss"] - before["local_loss"],
                   "cost_metric": metric, "profile_mode": args.profile_mode,
                   "local_loss_source": "controlled_manual_margin", "result_kind": "controlled_sensitivity_analysis",
                   "graph_sha256": fingerprint(graph), "assignments_enumerated": result["assignments_enumerated"],
                   "runtime_seconds": result["runtime_seconds"]}
            if result["changed_nodes"] and not row["strict_reversal"]:
                raise AssertionError("Changed assignment must have communication saving exceeding margin")
            rows.append(row)
    summary = summarize_reversals(rows)
    cost_hash = hashlib.sha256(args.costs.read_bytes()).hexdigest()
    old_manifest_path = BASE / "results/raw/joint_manifest.json"
    previous = json.loads(old_manifest_path.read_text()) if old_manifest_path.exists() else {}
    archives = []
    if previous and (previous.get("profile_mode"), previous.get("cost_metric"), previous.get("cost_file_sha256")) != (args.profile_mode, metric, cost_hash):
        archives = archive_joint_outputs(BASE)
    write_csv(BASE / "results/processed/decision_reversal.csv", rows, FIELDS)
    write_csv(BASE / "results/processed/reversal_thresholds.csv", thresholds, THRESHOLD_FIELDS)
    cost_hash = hashlib.sha256(args.costs.read_bytes()).hexdigest()
    write_json(BASE / "results/raw/joint_manifest.json", provenance(config, {
        "profile_mode": args.profile_mode, "cost_metric": metric, "cost_file": str(args.costs),
        "cost_file_sha256": cost_hash, "baseline": baseline, "local_losses": losses,
        "local_loss_source": "controlled_manual_margin", "result_kind": "controlled_sensitivity_analysis",
        "local_inputs_sha256": info["local_inputs_sha256"], "case_count": len(rows),
        "strict_reversal_cases": sum(r["strict_reversal"] for r in rows),
        "objective_delta_definition": "graph_objective - baseline_objective (negative = improvement)",
        "threshold_traffic_lambda": 1.0, "reversal_summary": summary,
        "previous_joint_outputs_archived": archives,
        "cost_interface_manifest": ("results/raw/cost_interface_manifest.json" if args.profile_mode == "real" and
            args.costs == BASE / "results/processed/protocol_costs.csv" else None)}))
    write_json(BASE / "results/processed/reversal_summary.json", summary)
    write_findings(config, args.profile_mode, metric, args.costs, info, rows, summary, archives)
    print(f"{len(rows)} exhaustive cases; strict reversals={summary['strict_reversal_cases']}; {metric}; {args.profile_mode}; controlled sensitivity only")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
