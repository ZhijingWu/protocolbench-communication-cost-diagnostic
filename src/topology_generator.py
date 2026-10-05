"""Deterministic directed demand graphs; node features are held fixed."""
import copy
import random
from .io_utils import nonnegative

TOPOLOGIES = ("chain", "star", "full_mesh", "hotspot")


def generate_topology(agents, topology, traffic_scale=1, payload_size_bytes=10240,
                      seed=6349, normalize_total=False):
    scale = nonnegative(traffic_scale, "traffic_scale")
    if not isinstance(payload_size_bytes, int) or payload_size_bytes <= 0:
        raise ValueError("payload_size_bytes must be a positive integer")
    nodes = copy.deepcopy(agents)
    ids = [str(agent["id"]) for agent in nodes]
    if len(ids) < 2 or len(ids) != len(set(ids)):
        raise ValueError("Require at least two uniquely identified nodes")
    pairs = []
    hub = ids[0]
    if topology == "chain":
        pairs = [(ids[i], ids[i+1], 1.0) for i in range(len(ids)-1)]
    elif topology == "star":
        pairs = [(a, b, 1.0) for leaf in ids[1:] for a, b in [(hub, leaf), (leaf, hub)]]
    elif topology == "full_mesh":
        pairs = [(a, b, 1.0) for a in ids for b in ids if a != b]
    elif topology == "hotspot":
        rng = random.Random(seed)
        pairs = [(a, b, float(rng.randint(8, 12)) if b == hub else 1.0)
                 for a in ids for b in ids if a != b]
    else:
        raise ValueError(f"Unknown topology: {topology}")
    total = sum(w for _, _, w in pairs)
    edges = [{"src": a, "dst": b, "weight": scale * w / (total if normalize_total else 1),
              "payload_size_bytes": payload_size_bytes} for a, b, w in pairs]
    return {"nodes": nodes, "edges": edges, "topology": topology,
            "traffic_scale": scale, "seed": seed,
            "traffic_normalization": "equal_total" if normalize_total else "per_edge",
            "total_messages": sum(edge["weight"] for edge in edges)}


def generate_cases(config):
    for normalize in config.get("normalizations", [False, True]):
        for topology in config["topologies"]:
            for traffic_label, scale in config["traffic_scales"].items():
                graph = generate_topology(config["agents"], topology, scale,
                                          config["payload_size_bytes"], config["seed"], normalize)
                graph["traffic_label"] = traffic_label
                yield graph
