"""Destination-protocol objective with explicit units and separate local loss."""
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from .io_utils import PROTOCOLS, nonnegative, protocol_name


@dataclass(frozen=True)
class ObjectiveValue:
    local_loss: float
    communication_cost: float
    total_objective: float


def manual_margin_losses(baseline, margin):
    """Controlled sensitivity input; NOT measured router confidence or accuracy."""
    losses = {}
    for node, preferred in baseline.items():
        amount = nonnegative(margin[node] if isinstance(margin, dict) else margin, "manual_margin")
        losses[node] = {p: 0.0 if p == preferred else amount for p in PROTOCOLS}
    return losses


def validate_problem(nodes, edges, costs, local_losses, protocols=PROTOCOLS):
    nodes = tuple(nodes)
    if not nodes or len(set(nodes)) != len(nodes):
        raise ValueError("Nodes must be nonempty and unique")
    if set(local_losses) != set(nodes):
        raise ValueError("Local losses must cover exactly all nodes")
    for node in nodes:
        if set(local_losses[node]) != set(protocols):
            raise ValueError("Each node needs every candidate local loss")
        for loss in local_losses[node].values():
            nonnegative(loss, "local_loss")
    for edge in edges:
        if edge["src"] not in nodes or edge["dst"] not in nodes:
            raise ValueError("Edge references unknown node")
        nonnegative(edge["weight"], "edge weight")
        size = edge["payload_size_bytes"]
        if not isinstance(size, int) or size <= 0:
            raise ValueError("Edge size must be a positive integer")
        for p in protocols:
            if (p, size) not in costs:
                raise ValueError(f"Missing measured cost: {(p, size)}")
            nonnegative(costs[p, size], "communication cost")


def evaluate_objective(assignment, edges, costs, local_losses, lambda_cost):
    lam = nonnegative(lambda_cost, "lambda_cost")
    if set(assignment) != set(local_losses):
        raise ValueError("Assignment and local loss IDs differ")
    local = math.fsum(float(local_losses[node][p]) for node, p in assignment.items())
    comm = math.fsum(float(edge["weight"]) * costs[assignment[edge["dst"]], edge["payload_size_bytes"]]
                     for edge in edges)
    return ObjectiveValue(local, comm, local + lam * comm)


def load_measured_costs(path, mode, metric="mean_encoded_bytes", allow_failures=False):
    if mode not in ("real", "conversion-only"):
        raise ValueError("Choose an explicit profile mode")
    if metric not in ("mean_encoded_bytes", "mean_latency_ms", "mean_conversion_runtime_ms"):
        raise ValueError("Unsupported cost metric")
    if mode == "conversion-only" and metric == "mean_latency_ms":
        raise ValueError("Conversion-only cannot supply network latency")
    if mode == "real" and metric == "mean_conversion_runtime_ms":
        raise ValueError("Real mode does not measure isolated conversion runtime")
    costs = {}
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["mode"] != mode:
                continue
            key = (protocol_name(row["protocol"]), int(row["payload_size_bytes"]))
            if key in costs:
                raise ValueError(f"Duplicate condition: {key}")
            if int(row["success_count"]) == 0 or not row[metric]:
                raise ValueError(f"No measured successful cost for {key}")
            if float(row["failure_rate"]) > 0 and not allow_failures:
                raise ValueError(f"Failures for {key}; no implicit reliability penalty or imputation")
            costs[key] = nonnegative(row[metric], metric)
    if not costs:
        raise ValueError(f"No measured costs for mode {mode}")
    return costs
