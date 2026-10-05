#!/usr/bin/env python3
"""Run explicit real or conversion-only profile; never silently switch modes."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import asyncio
from src.io_utils import BASE, load_config, provenance, write_csv, write_json
from src.protocol_cost_profiler import (
    RAW_FIELDS, STAT_FIELDS, dependency_versions, profile)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["real", "conversion-only"], required=True)
    parser.add_argument("--config", type=Path, default=BASE / "configs/microbench.yaml")
    parser.add_argument("--worker-protocol", choices=["A2A", "ACP", "ANP", "Agora"], help=argparse.SUPPRESS)
    parser.add_argument("--worker-output", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.mode == "real":
        from src.local_protocol_microbench import profile_one_protocol, run_real_microbench
        if args.worker_protocol:
            if not args.worker_output:
                parser.error("Internal worker requires output path")
            result = asyncio.run(profile_one_protocol(config, args.worker_protocol))
            write_json(args.worker_output, result)
            return 0
        return asyncio.run(run_real_microbench(config))
    rows, stats, blockers = asyncio.run(profile(config, args.mode))
    raw_csv = BASE / f"results/raw/protocol_profile_{args.mode}.csv"
    raw_json = BASE / f"results/raw/protocol_profile_{args.mode}.json"
    write_csv(raw_csv, rows, RAW_FIELDS)
    write_json(raw_json, rows)
    # Each run retains its own summary. Canonical table contains only measured
    # successful conditions for the chosen explicit mode, never mixed units.
    write_csv(BASE / f"results/processed/protocol_costs_{args.mode}.csv", stats, STAT_FIELDS)
    if args.mode == "conversion-only" or (not blockers and all(
            r["success"] for r in rows if r["phase"] == "measured")):
        write_csv(BASE / "results/processed/protocol_costs.csv", stats, STAT_FIELDS)
    write_json(BASE / f"results/raw/profile_manifest_{args.mode}.json", provenance(config, {
        "mode": args.mode, "blockers": blockers, "dependencies": dependency_versions(),
        "network_latency_measured": args.mode == "real" and any(r["success"] for r in rows),
        "raw_csv": str(raw_csv.relative_to(BASE)), "statistics_success_only": True,
        "failure_rate_includes_setup_blocked_attempts": True,
        "p95_definition": "linear interpolation at (n-1)*0.95"}))
    successes = sum(r["success"] for r in rows if r["phase"] == "measured")
    measured = sum(r["phase"] == "measured" for r in rows)
    print(f"mode={args.mode}; measured successes={successes}/{measured}; setup/cleanup blockers={len(blockers)}")
    for blocker in blockers:
        print(f"{blocker['protocol']}: {blocker['error_type']}: {blocker['message']}")
    return 0 if successes == measured and not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
