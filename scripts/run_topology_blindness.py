#!/usr/bin/env python3
"""Reinvoke original fallback or replay saved outputs with fixed local inputs."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import json
from src.io_utils import BASE, fingerprint, load_config, provenance, write_csv, write_json
from src.local_router_adapter import baseline_assignment, prompt_digest
from src.topology_generator import generate_cases

FIELDS = ["topology", "traffic_label", "traffic_scale", "traffic_normalization", "edge_count",
          "total_messages", "local_inputs_sha256", "prompt_sha256", "graph_sha256",
          "assignment", "assignment_changed", "baseline_source", "test_kind"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=BASE / "configs/topology_cases.yaml")
    parser.add_argument("--routing-output", type=Path)
    args = parser.parse_args()
    config = load_config(args.config)
    baseline, info = baseline_assignment(config["task_analysis"], config["agents"], args.routing_output)
    prompt = prompt_digest(config["task_analysis"], config["agents"])
    graphs, rows = [], []
    for graph in generate_cases(config):
        observed, audit = baseline_assignment(config["task_analysis"], graph["nodes"], args.routing_output)
        digest = prompt_digest(config["task_analysis"], graph["nodes"])
        assert audit["local_inputs_sha256"] == info["local_inputs_sha256"] and digest == prompt
        graph["local_preferences"] = baseline.copy()
        rows.append({"topology": graph["topology"], "traffic_label": graph["traffic_label"],
                     "traffic_scale": graph["traffic_scale"], "traffic_normalization": graph["traffic_normalization"],
                     "edge_count": len(graph["edges"]), "total_messages": graph["total_messages"],
                     "local_inputs_sha256": audit["local_inputs_sha256"], "prompt_sha256": digest,
                     "graph_sha256": fingerprint(graph), "assignment": json.dumps(observed, sort_keys=True),
                     "assignment_changed": observed != baseline, "baseline_source": audit["source"],
                     "test_kind": "saved_output_replay" if args.routing_output else "original_fallback_reinvocation"})
        graphs.append(graph)
    write_json(BASE / "results/raw/local_router_output.json", info)
    write_json(BASE / "results/raw/topology_cases.json", graphs)
    write_csv(BASE / "results/processed/topology_blindness.csv", rows, FIELDS)
    write_json(BASE / "results/raw/topology_manifest.json", provenance(config, {
        "baseline_assignment": baseline, "baseline_source": info["source"], "case_count": len(rows),
        "assignment_changes": sum(r["assignment_changed"] for r in rows), "prompt_sha256": prompt,
        "saved_output": str(args.routing_output) if args.routing_output else None}))
    print(f"{len(rows)} graph/traffic cases; assignment changes={sum(r['assignment_changed'] for r in rows)}; source={info['source']}")
    if any(r["assignment_changed"] for r in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
