#!/usr/bin/env python3
"""Run the existing oracle on official workflow demand templates; no GAIA/LLM."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import json
from src.gaia_workflow import OFFICIAL_CONFIG
from src.gaia_workflow_experiment import run_workflow_experiment


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-config",type=Path,default=OFFICIAL_CONFIG)
    args=parser.parse_args()
    summary=run_workflow_experiment(official_config=args.official_config)
    print(json.dumps({"baseline_assignment":summary["baseline_assignment"],"total_cases":summary["total_cases"],
        "workflows":summary["workflows"]},indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
