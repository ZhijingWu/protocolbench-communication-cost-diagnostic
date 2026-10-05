"""Exhaustive audit oracle for small graphs; no learning or external solver."""
import itertools
import math
import time
from dataclasses import asdict
from .io_utils import PROTOCOLS, nonnegative
from .objective import evaluate_objective, validate_problem


def exhaustive_oracle(baseline, edges, costs, local_losses, lambda_cost,
                      protocols=PROTOCOLS, max_assignments=1048576):
    lam = nonnegative(lambda_cost, "lambda_cost")
    nodes = tuple(sorted(baseline))
    validate_problem(nodes, edges, costs, local_losses, protocols)
    count = len(protocols) ** len(nodes)
    if count > max_assignments:
        raise ValueError(f"Exhaustive search needs {count} assignments, limit {max_assignments}")
    if any(p not in protocols for p in baseline.values()):
        raise ValueError("Invalid baseline protocol")
    started = time.perf_counter()
    baseline_value = evaluate_objective(baseline, edges, costs, local_losses, lam)
    best_assignment, best = dict(baseline), baseline_value
    choices = [(baseline[n],) + tuple(p for p in protocols if p != baseline[n]) for n in nodes]
    for candidate in itertools.product(*choices):
        assignment = dict(zip(nodes, candidate))
        value = evaluate_objective(assignment, edges, costs, local_losses, lam)
        # Stable tie policy: retain baseline/first candidate within floating precision.
        if value.total_objective < best.total_objective and not math.isclose(
                value.total_objective, best.total_objective, rel_tol=1e-12, abs_tol=1e-12):
            best, best_assignment = value, assignment
    return {"baseline_assignment": dict(baseline), "best_assignment": best_assignment,
            "baseline": asdict(baseline_value), "best": asdict(best),
            "changed_nodes": [n for n in nodes if baseline[n] != best_assignment[n]],
            "assignments_enumerated": count, "runtime_seconds": time.perf_counter() - started}


def reversal_thresholds(baseline, edges, costs, local_losses, traffic_scale=1, lambda_cost=1):
    scale = nonnegative(traffic_scale, "traffic_scale")
    lam = nonnegative(lambda_cost, "lambda_cost")
    result = []
    for node, preferred in sorted(baseline.items()):
        incoming = [e for e in edges if e["dst"] == node]
        for alternative in PROTOCOLS:
            if alternative == preferred:
                continue
            saving = math.fsum(e["weight"] * (costs[preferred, e["payload_size_bytes"]] -
                                               costs[alternative, e["payload_size_bytes"]])
                               for e in incoming)
            margin = local_losses[node][alternative] - local_losses[node][preferred]
            if saving <= 0 or margin < 0:
                continue
            threshold = margin / saving
            result.append({"node": node, "baseline_protocol": preferred,
                           "alternative_protocol": alternative, "local_margin": margin,
                           "incoming_comm_saving": saving, "lambda_threshold": threshold,
                           "traffic_threshold_at_lambda": (margin * scale / (lam * saving)
                                                           if lam > 0 and scale > 0 else None),
                           "strict_reversal": "lambda > threshold (equality is tie)"})
    for row in result:
        earliest = min(r["lambda_threshold"] for r in result if r["node"] == row["node"])
        row["first_reversal_candidate"] = math.isclose(row["lambda_threshold"], earliest,
                                                       rel_tol=1e-12, abs_tol=1e-12)
    return result
