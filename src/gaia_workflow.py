"""Instantiate official GAIA workflow templates as controlled communication demand."""
import copy
from pathlib import Path
from .io_utils import REPO, load_config, nonnegative

OFFICIAL_CONFIG = REPO / "scenarios/gaia/config/meta_protocol.yaml"
WORKFLOWS = ("analysis_task", "collaborative_task")


def load_official_patterns(path=OFFICIAL_CONFIG):
    config = load_config(path)
    patterns = config.get("workflow", {}).get("message_flow_patterns", {})
    if not all(name in patterns for name in WORKFLOWS):
        raise ValueError("Official config needs analysis_task and collaborative_task patterns")
    return {name: copy.deepcopy(patterns[name]) for name in WORKFLOWS}


def instantiate_workflow(pattern, agents, name, traffic_scale, payload_size_bytes,
                         normalize_total=False):
    """Only expand explicitly declared flows; final stays a terminal event.

    all means peers in the fixed experiment roster: exclude the same source/dst
    from broadcast/aggregation, rather than inventing a hub self-message.
    This is an explicit template-instantiation convention, not an observed trace.
    """
    ids = [str(a["id"]) for a in agents]
    if len(ids) != len(set(ids)) or not ids:
        raise ValueError("Workflow roster needs unique agent IDs")
    if not isinstance(payload_size_bytes, int) or payload_size_bytes <= 0:
        raise ValueError("Payload size must be a positive integer")
    scale = nonnegative(traffic_scale, "traffic_scale")
    edges, terminal = [], []
    for index, step in enumerate(pattern):
        if not isinstance(step, dict) or "from" not in step or "to" not in step:
            raise ValueError("Every official flow needs from and to")
        source, target = step["from"], step["to"]
        destinations = target if isinstance(target, list) else [target]
        metadata = {k: copy.deepcopy(v) for k, v in step.items() if k not in ("from", "to")}
        sources = ids if source == "all" else [str(source)]
        if any(src not in ids for src in sources):
            raise ValueError(f"Unknown source in workflow: {source}")
        for dst_value in destinations:
            if dst_value == "final":
                if source == "all":
                    raise ValueError("Unsupported all->final template; do not infer extra terminal events")
                terminal.append({"src": str(source), "dst": "final", "step_index": index,
                                 "metadata": metadata, "weight": scale,
                                 "included_in_communication_objective": False})
                continue
            dsts = ids if dst_value == "all" else [str(dst_value)]
            if any(dst not in ids for dst in dsts):
                raise ValueError(f"Unknown destination in workflow: {dst_value}")
            for src in sources:
                for dst in dsts:
                    if src == dst and (source == "all" or dst_value == "all"):
                        continue
                    edges.append({"src": src, "dst": dst, "weight": scale,
                                  "payload_size_bytes": payload_size_bytes, "step_index": index,
                                  "metadata": copy.deepcopy(metadata)})
    if not edges:
        raise ValueError("Workflow has no inter-agent edges")
    if normalize_total:
        for edge in edges:
            edge["weight"] /= len(edges)
    return {"workflow": name, "nodes": copy.deepcopy(agents), "official_pattern": copy.deepcopy(pattern),
            "edges": edges, "terminal_events": terminal, "traffic_scale": scale,
            "traffic_normalization": "equal_total" if normalize_total else "per_edge",
            "total_agent_messages": sum(e["weight"] for e in edges),
            "all_expansion": "all other agents in the unchanged four-node experiment roster",
            "final_handling": "terminal output marker; no new agent, assigned protocol or invented network cost",
            "protocol_preference_handling": "metadata only; not used in local loss or objective"}
