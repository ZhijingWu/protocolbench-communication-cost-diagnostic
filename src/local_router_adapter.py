"""Thin consumption of ORIGINAL RoutingDecision; no duplicate routing heuristics."""
import asyncio
import copy
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from .io_utils import REPO, fingerprint, protocol_name, source_module


def assignment_from_output(output, agents):
    output = asdict(output) if is_dataclass(output) else output
    if not isinstance(output, dict):
        raise ValueError("Expected RoutingDecision mapping")
    values = output.get("agent_assignments", output.get("protocol_assignments", output))
    if not isinstance(values, dict):
        raise ValueError("Assignment must be a mapping")
    values = {str(k): protocol_name(v) for k, v in values.items()}
    ids = {str(a["id"]) for a in agents}
    if set(values) != ids:
        raise ValueError(f"Assignment IDs must exactly match agents: {ids}")
    return values


def load_original_router():
    return source_module("_topology_original_gaia_router",
                         REPO / "scenarios/gaia/protocol_backends/meta_protocol/llm_router.py").GAIALLMRouter


def baseline_assignment(task_analysis, agents, saved_output=None):
    fixed = {"task_analysis": copy.deepcopy(task_analysis), "agents_config": copy.deepcopy(agents)}
    before = fingerprint(fixed)
    if saved_output:
        output = json.loads(Path(saved_output).read_text(encoding="utf-8"))
        source = "saved_routing_output_replay"
        # Require provenance with saved output so unrelated features cannot slip in.
        if output.get("local_inputs_sha256") != before:
            raise ValueError("Saved output needs matching local_inputs_sha256")
        decision = output.get("routing_decision", output)
    else:
        router = load_original_router()()  # matches actual GAIA caller: no LLM client
        decision = asdict(asyncio.run(router.route_gaia_task(
            fixed["task_analysis"], fixed["agents_config"])))
        source = decision["strategy"]
        # Original fallback builds this list from a set; canonicalize metadata only.
        decision["selected_protocols"] = sorted(decision["selected_protocols"])
    if fingerprint(fixed) != before:
        raise AssertionError("Original router mutated local inputs")
    return assignment_from_output(decision, agents), {
        "source": source, "local_inputs_sha256": before, "routing_decision": decision,
        "local_inputs": fixed}


def prompt_digest(task_analysis, agents):
    router = load_original_router()()
    return fingerprint({"system": router._create_gaia_system_prompt(),
                        "user": router._create_gaia_user_prompt(task_analysis, agents)})
