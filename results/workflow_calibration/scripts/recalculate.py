#!/usr/bin/env python3
"""Verify saved workflow-calibration evidence offline (Python 3.10+, stdlib only).

No network, experimental runner imports, measurements, or input-file writes.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import sys


class EvidenceError(ValueError):
    """A required record is missing, changed, or internally inconsistent."""


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def close(actual, expected, message):
    require(math.isfinite(actual) and math.isfinite(expected)
            and math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-10),
            f"{message}: actual={actual!r}, expected={expected!r}")


def required_file(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), f"Path outside artifact: {relative}")
    require(path.is_file(), f"Missing required input: {relative}")
    return path


def load_json(root, relative):
    return json.loads(required_file(root, relative).read_text(encoding="utf-8"))


def load_csv(root, relative):
    with required_file(root, relative).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(bool(rows), f"No observations in required input: {relative}")
    return rows


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verify_release_files(root):
    manifest = load_json(root, "release_manifest.json")
    require(manifest["schema_version"] == 1, "Unsupported release manifest version")
    expected = set(manifest["files"])
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    require(actual == expected | {"release_manifest.json"},
            f"Release file inventory mismatch: missing={sorted(expected-actual)}, "
            f"unexpected={sorted(actual-expected-{'release_manifest.json'})}")
    for relative, entry in manifest["files"].items():
        digest = sha256(required_file(root, relative).read_bytes())
        require(digest == entry["publication_sha256"], f"Publication hash mismatch: {relative}")
        if entry.get("copied_unchanged"):
            require(digest == entry["original_sha256"], f"Original/public hash mismatch: {relative}")
    return manifest


def percentile(values, fraction):
    ordered = sorted(values)
    position = (len(ordered)-1) * fraction
    index = int(position)
    return ordered[index] + (ordered[min(index+1, len(ordered)-1)]-ordered[index]) * (position-index)


def bootstrap(values, labels, seed, include_median=False):
    groups = [[v for v, label in zip(values, labels) if label == key]
              for key in sorted(set(labels))]
    generator = random.Random(seed)
    means, p95s, medians = [], [], []
    for _ in range(10000):
        sample = [generator.choice(group) for group in groups for _ in group]
        if include_median:
            medians.append(statistics.median(sample))
        else:
            means.append(sum(sample)/len(sample))
            p95s.append(percentile(sample, .95))
    interval = lambda x: [percentile(x, .025), percentile(x, .975)]
    if include_median:
        return {"median_ci95_ms": interval(medians)}
    return {"mean_ci95_ms": interval(means), "p95_ci95_ms": interval(p95s)}


def interval_metrics(intervals):
    require(bool(intervals), "An RPC/stage interval set is empty")
    edges = []
    for start, end in intervals:
        require(start < end, "Nonpositive observed interval")
        edges.extend([(start, 1), (end, -1)])
    edges.sort(key=lambda x: (x[0], x[1]))
    active = peak = union = overlap = 0
    previous = edges[0][0]
    for timestamp, change in edges:
        if active:
            union += timestamp-previous
        if active >= 2:
            overlap += timestamp-previous
        active += change
        peak = max(peak, active)
        previous = timestamp
    total = sum(end-start for start, end in intervals)
    return {"rpc_interval_sum_ms": total/1e6, "rpc_interval_union_ms": union/1e6,
            "parallel_overlap_ms": overlap/1e6, "overlap_credit_ms": (total-union)/1e6,
            "peak_concurrent_rpc": peak}


def frozen_profile(root, config):
    repository = root.parent.parent
    reference = config["historical_profile"]
    path = (repository / reference["repository_relative_path"]).resolve()
    require(path.is_relative_to(repository.resolve()), "Historical profile path escapes repository")
    require(path.is_file(), f"Missing frozen historical profile: {reference['repository_relative_path']}")
    raw = path.read_bytes()
    # The pre-existing repository permits Windows LF -> CRLF checkout conversion.
    # Only this declared dependency uses canonical LF hashing; package files are -text.
    digest = sha256(raw.replace(b"\r\n", b"\n"))
    require(digest == reference["git_blob_sha256"], "Frozen historical profile hash mismatch")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 16, "Historical cost table must contain 16 protocol/payload cells")
    require(len({(r["protocol"], int(r["payload_size_bytes"])) for r in rows}) == 16,
            "Duplicate historical cost cells")
    for row in rows:
        require(row["status"] == "ok" and int(row["successful_requests"]) == 30
                and int(row["failures"]) == int(row["skipped_requests"]) == 0,
                "Historical cost table contains an incomplete measured cell")
    means = {r["protocol"]: float(r["mean_latency_ms"]) for r in rows
             if int(r["payload_size_bytes"]) == config["payload_size_bytes"]}
    require(set(means) == {"A2A", "ACP", "ANP", "Agora"}, "Missing frozen 10 KiB means")
    require(all(math.isfinite(v) and v > 0 for v in means.values()), "Invalid frozen mean RTT")
    return means, digest


def predictions(config, means):
    result = {}
    for name, topology in config["topologies"].items():
        for plan, assignment in config["plans"].items():
            costs = [[means[assignment[e["dst"]]] for e in stage] for stage in topology["stages"]]
            result[name, plan] = {"work_ms": sum(sum(s) for s in costs),
                                  "dag_ms": sum(max(s) for s in costs)}
    return result


def verify_observations(root, config, predicted):
    runs = load_csv(root, "raw/workflow_runs.csv")
    rpcs = load_csv(root, "raw/rpc_events.csv")
    stages = load_csv(root, "raw/stage_events.csv")
    schedule = load_json(root, "raw/execution_order.json")
    require(load_json(root, "raw/failures.json") == [], "Recorded full-run failures are nonempty")
    require((len(runs), len(rpcs), len(stages), len(schedule)) == (140, 560, 280, 140),
            "Full-run raw counts must be 140 workflows / 560 RPCs / 280 stages")
    require(Counter(r["phase"] for r in runs) == {"warmup": 20, "measured": 120}, "Workflow phase counts")
    require(Counter(r["phase"] for r in rpcs) == {"warmup": 80, "measured": 480}, "RPC phase counts")
    require(all(str(r[k]) == str(v) for r, s in zip(runs, schedule) for k, v in s.items()),
            "Raw workflow rows differ from recorded schedule")
    require(all(int(r["execution_order"]) == i and r["run_id"] == f"r{i:04d}" for i, r in enumerate(runs)),
            "Workflow IDs/order are not contiguous")
    require(all(int(a["end_ns"]) <= int(b["start_ns"]) for a, b in zip(runs, runs[1:])),
            "Whole-workflow executions overlap")
    run_ids = {r["run_id"] for r in runs}
    require(len(run_ids) == 140 and all(r["run_id"] in run_ids for r in rpcs+stages), "Orphan or duplicate run IDs")
    require(len({r["rpc_id"] for r in rpcs}) == 560, "Duplicate RPC IDs")
    digest_map = {r["digest"]: r for r in rpcs}
    require(len(digest_map) == 560, "Duplicate RPC payload digests")
    events = [json.loads(line) for line in required_file(root, "raw/server_executor_events.jsonl")
              .read_text(encoding="utf-8").splitlines() if line.strip()]
    require(all(e["kind"] in {"http", "executor"} for e in events), "Unexpected observer event kind")
    posts = [e for e in events if e["kind"] == "http" and e["method"] == "POST"]
    calls = [e for e in events if e["kind"] == "executor"]
    require(len(posts) == len(calls) == 560, "POST/executor totals differ from application RPC totals")
    require(Counter(e["digest"] for e in posts) == Counter(digest_map.keys()), "POST digest accounting")
    require(Counter(e["digest"] for e in calls) == Counter(digest_map.keys()), "Executor digest accounting")
    post_map = {e["digest"]: e for e in posts}
    call_map = {e["digest"]: e for e in calls}
    by_run, by_stage = defaultdict(list), defaultdict(list)
    for row in rpcs:
        rid = row["rpc_id"]
        require(row["status"] == "ok" and row["receipt_verified"] == row["timing_sanity_passed"] == "True",
                f"Unsuccessful or unchecked RPC: {rid}")
        require(int(row["payload_size_bytes"]) == 10240 and int(row["harness_retries"]) == 0,
                f"Payload/retry mismatch: {rid}")
        require(int(row["server_post_count"]) == int(row["executor_count"]) == 1, f"RPC observation count: {rid}")
        start, end = int(row["start_ns"]), int(row["end_ns"])
        close(float(row["latency_ms"]), (end-start)/1e6, f"RPC timing: {rid}")
        post, call = post_map[row["digest"]], call_map[row["digest"]]
        require(post["status_code"] == 200 and post["endpoint"] == f"{row['dst']}-{row['protocol']}", f"RPC target/status: {rid}")
        require(post["body_bytes"] == int(row["encoded_request_bytes"]) and call["payload_bytes"] == 10240
                and call["status"] == "ok",
                f"RPC body/receipt: {rid}")
        require(start <= post["start_ns"] <= call["start_ns"] <= call["end_ns"] <= post["end_ns"] <= end,
                f"RPC/server/executor timestamps are not nested: {rid}")
        require(row["protocol"] == config["plans"][row["plan"]][row["dst"]], f"Destination protocol: {rid}")
        by_run[row["run_id"]].append(row)
    for stage in stages:
        by_stage[stage["run_id"]].append(stage)
    for run in runs:
        rid = run["run_id"]
        require(run["status"] == "ok", f"Failed workflow: {rid}")
        rows = by_run[rid]
        ss = sorted(by_stage[rid], key=lambda s: int(s["stage_id"]))
        expected = config["topologies"][run["workflow"]]["stages"]
        require(len(ss) == 2 and [int(s["stage_id"]) for s in ss] == [0, 1], f"Missing/duplicate stages: {rid}")
        require(len(rows) == sum(len(s) for s in expected), f"Workflow RPC count: {rid}")
        require(int(run["attempted_rpcs"]) == int(run["successful_rpcs"]) == len(rows)
                and int(run["failed_rpcs"]) == int(run["skipped_rpcs"]) == 0, f"Workflow counters: {rid}")
        start, end = int(run["start_ns"]), int(run["end_ns"])
        close(float(run["makespan_ms"]), (end-start)/1e6, f"Workflow timing: {rid}")
        require(start <= int(ss[0]["start_ns"]) < int(ss[0]["end_ns"])
                <= int(ss[1]["start_ns"]) < int(ss[1]["end_ns"]) <= end, f"Stage chronology: {rid}")
        require(int(ss[1]["first_rpc_start_ns"]) >= int(ss[0]["end_ns"]), f"Stage barrier: {rid}")
        require(all(start <= int(r["start_ns"]) < int(r["end_ns"]) <= end for r in rows), f"RPC outside workflow: {rid}")
        for field, value in interval_metrics([(int(r["start_ns"]), int(r["end_ns"])) for r in rows]).items():
            close(float(run[field]), value, f"Workflow {field}: {rid}")
        for field, key in [("predicted_work_ms", "work_ms"), ("predicted_dag_ms", "dag_ms")]:
            close(float(run[field]), predicted[run["workflow"], run["plan"]][key], f"Frozen prediction: {rid}")
        for index, stage in enumerate(ss):
            branch_rows = [r for r in rows if int(r["stage_id"]) == index]
            require([(r["src"], r["dst"]) for r in branch_rows] == [(e["src"], e["dst"]) for e in expected[index]],
                    f"Topology mismatch: {rid}, stage {index}")
            last = max(branch_rows, key=lambda r: int(r["end_ns"]))
            require(stage["critical_rpc_id"] == last["rpc_id"] and stage["critical_protocol"] == last["protocol"]
                    and int(stage["last_completion_ns"]) == int(last["end_ns"]), f"Last completion: {rid}")
            close(float(stage["critical_completion_span_ms"]),
                  (int(last["end_ns"])-int(stage["start_ns"]))/1e6, f"Critical span: {rid}")
            for row in branch_rows:
                close(float(row["join_wait_ms"]), (int(last["end_ns"])-int(row["end_ns"]))/1e6,
                      f"Join wait: {row['rpc_id']}")
            intervals = interval_metrics([(int(r["start_ns"]), int(r["end_ns"])) for r in branch_rows])
            for field, value in intervals.items():
                close(float(stage[field]), value, f"Stage {field}: {rid}")
            if run["workflow"] == "collaborative_task":
                require(intervals["peak_concurrent_rpc"] == 3 and intervals["parallel_overlap_ms"] > 0,
                        f"Missing three-way client-send overlap: {rid}")
    return runs, rpcs, stages


def recompute(root):
    root = root.resolve()
    release = verify_release_files(root)
    config = load_json(root, "config/experiment.json")
    require(config["configuration_kind"] == "descriptive_export_of_recorded_evidence",
            "Configuration must be labeled as a descriptive export")
    means, profile_hash = frozen_profile(root, config)
    predicted = predictions(config, means)
    runs, rpcs, stages = verify_observations(root, config, predicted)
    summary = load_json(root, "processed/summary.json")
    saved_pairs = load_csv(root, "processed/paired_differences.csv")
    saved_cells = load_csv(root, "processed/workflow_summary.csv")
    require(len(saved_pairs) == 60 and len(saved_cells) == 4, "Stored derived-table sizes are inconsistent")
    cells, pairs, effects = [], [], []
    for name in ("analysis_task", "collaborative_task"):
        for plan in ("baseline", "treatment"):
            rows = [r for r in runs if r["phase"] == "measured" and r["workflow"] == name and r["plan"] == plan]
            warm = [r for r in runs if r["phase"] == "warmup" and r["workflow"] == name and r["plan"] == plan]
            require(len(rows) == 30 and len(warm) == 5, f"Per-cell measured/warmup accounting: {name}/{plan}")
            values = [float(r["makespan_ms"]) for r in rows]
            cell = {"workflow": name, "plan": plan, "measured_workflows": len(rows),
                    "predicted_work_ms": predicted[name, plan]["work_ms"],
                    "predicted_dag_ms": predicted[name, plan]["dag_ms"],
                    "mean_makespan_ms": statistics.mean(values), "median_makespan_ms": statistics.median(values),
                    "p95_makespan_ms": percentile(values, .95), "std_makespan_ms": statistics.stdev(values),
                    "mean_rpc_interval_sum_ms": statistics.mean(float(r["rpc_interval_sum_ms"]) for r in rows),
                    **bootstrap(values, [r["pair_order"] for r in rows], 6349+len(cells))}
            saved = [x for x in summary["workflow_summary"] if x["workflow"] == name and x["plan"] == plan]
            require(len(saved) == 1, f"Missing/duplicate stored cell summary: {name}/{plan}")
            for field in ("mean_makespan_ms", "median_makespan_ms", "p95_makespan_ms", "std_makespan_ms", "mean_rpc_interval_sum_ms"):
                close(cell[field], saved[0][field], f"Stored cell {field}: {name}/{plan}")
            for field in ("mean_ci95_ms", "p95_ci95_ms"):
                for a, b in zip(cell[field], saved[0][field]):
                    close(a, b, f"Stored cell interval {field}: {name}/{plan}")
            csv_cell = [x for x in saved_cells if x["workflow"] == name and x["plan"] == plan]
            require(len(csv_cell) == 1, f"Missing/duplicate derived CSV cell: {name}/{plan}")
            for field in ("mean_makespan_ms", "median_makespan_ms", "p95_makespan_ms", "std_makespan_ms"):
                close(cell[field], float(csv_cell[0][field]), f"Derived CSV cell {field}: {name}/{plan}")
            cells.append(cell)
        for index in range(30):
            rows = [r for r in runs if r["phase"] == "measured" and r["workflow"] == name and int(r["pair_index"]) == index]
            require(len(rows) == 2 and {r["plan"] for r in rows} == {"baseline", "treatment"}, f"Incomplete pair: {name}/{index}")
            baseline = next(r for r in rows if r["plan"] == "baseline")
            treatment = next(r for r in rows if r["plan"] == "treatment")
            require(abs(int(baseline["execution_order"])-int(treatment["execution_order"])) == 1, f"Nonadjacent pair: {name}/{index}")
            order = "AB" if int(baseline["execution_order"]) < int(treatment["execution_order"]) else "BA"
            require(order == baseline["pair_order"] == treatment["pair_order"] == ("AB" if index%2 == 0 else "BA"),
                    f"Deterministic pair order: {name}/{index}")
            pair = {"workflow": name, "pair_index": index, "pair_order": order,
                    "delta_ms": float(treatment["makespan_ms"])-float(baseline["makespan_ms"]),
                    "delta_work_ms": float(treatment["rpc_interval_sum_ms"])-float(baseline["rpc_interval_sum_ms"]),
                    "delta_predicted_dag_ms": float(treatment["predicted_dag_ms"])-float(baseline["predicted_dag_ms"]),
                    "delta_predicted_work_ms": float(treatment["predicted_work_ms"])-float(baseline["predicted_work_ms"])}
            saved = [p for p in saved_pairs if p["workflow"] == name and int(p["pair_index"]) == index]
            require(len(saved) == 1, f"Missing/duplicate saved pair: {name}/{index}")
            for field in ("delta_ms", "delta_work_ms", "delta_predicted_dag_ms", "delta_predicted_work_ms"):
                close(pair[field], float(saved[0][field]), f"Saved pair {field}: {name}/{index}")
            pairs.append(pair)
        selected = [p for p in pairs if p["workflow"] == name]
        values, labels = [p["delta_ms"] for p in selected], [p["pair_order"] for p in selected]
        require(Counter(labels) == {"AB": 15, "BA": 15}, f"AB/BA imbalance: {name}")
        effect = {"workflow": name, "complete_pairs": len(selected),
                  "predicted_work_delta_ms": predicted[name, "treatment"]["work_ms"]-predicted[name, "baseline"]["work_ms"],
                  "predicted_dag_delta_ms": predicted[name, "treatment"]["dag_ms"]-predicted[name, "baseline"]["dag_ms"],
                  "mean_delta_ms": statistics.mean(values), "median_delta_ms": statistics.median(values),
                  "mean_delta_ci95_ms": bootstrap(values, labels, 96349+len(effects))["mean_ci95_ms"],
                  "median_delta_ci95_ms": bootstrap(values, labels, 96349, True)["median_ci95_ms"],
                  "AB_mean_ms": statistics.mean(p["delta_ms"] for p in selected if p["pair_order"] == "AB"),
                  "BA_mean_ms": statistics.mean(p["delta_ms"] for p in selected if p["pair_order"] == "BA"),
                  "treatment_faster_pairs": sum(v < 0 for v in values), "baseline_faster_pairs": sum(v > 0 for v in values)}
        saved = [e for e in summary["paired_effects"] if e["workflow"] == name]
        require(len(saved) == 1, f"Missing/duplicate stored effect: {name}")
        close(effect["mean_delta_ms"], saved[0]["mean_delta_ms"], f"Stored paired mean: {name}")
        close(effect["median_delta_ms"], saved[0]["median_delta_ms"], f"Stored paired median: {name}")
        for a, b in zip(effect["mean_delta_ci95_ms"], saved[0]["mean_delta_ci95_ms"]):
            close(a, b, f"Stored paired mean interval: {name}")
        for a, b in zip(effect["median_delta_ci95_ms"], config["recorded_review_median_ci95_ms"][name]):
            close(a, b, f"Recorded review median interval: {name}")
        effects.append(effect)
    stage_results = []
    for name in ("analysis_task", "collaborative_task"):
        for plan in ("baseline", "treatment"):
            for index in (0, 1):
                selected = [s for s in stages if s["phase"] == "measured" and s["workflow"] == name
                            and s["plan"] == plan and int(s["stage_id"]) == index]
                stage_results.append({"workflow": name, "plan": plan, "stage": index,
                                      "mean_completion_span_ms": statistics.mean(float(s["critical_completion_span_ms"]) for s in selected),
                                      "critical_protocol_counts": dict(Counter(s["critical_protocol"] for s in selected))})
    counts = {"measured_workflows": 120, "warmup_workflows": 20, "measured_workflow_rpcs": 480,
              "warmup_workflow_rpcs": 80, "complete_measured_pairs": len(pairs),
              "measured_rpcs_by_topology": dict(Counter(r["workflow"] for r in rpcs if r["phase"] == "measured"))}
    return {"status": "passed", "release_files_verified": len(release["files"]),
            "historical_profile_git_blob_sha256": profile_hash, "historical_10KiB_means_ms": means,
            "counts": counts, "workflow_summary": cells, "paired_effects": effects, "stage_results": stage_results,
            "interpretation": "Existing-record recalculation only; one-session calibration diagnostic. "
                              "Frozen predictions, descriptive stratified bootstrap, no causal order or general ranking claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Artifact directory (default: script-relative, independent of current directory)")
    parser.add_argument("--json", action="store_true", help="Print full recalculated results as JSON")
    args = parser.parse_args()
    try:
        result = recompute(args.artifact)
    except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, allow_nan=False))
    else:
        print(f"PASS: {result['release_files_verified']} publication file hashes; raw timing, receipts, topology and derived statistics.")
        print("Measured: 120 workflows / 480 workflow RPCs. Excluded warmups: 20 workflows / 80 RPCs.")
        print("Each topology: 30 complete pairs, 15 AB and 15 BA; 30 measured executions per topology/plan cell.")
        for effect in result["paired_effects"]:
            print(f"{effect['workflow']}: predicted work delta={effect['predicted_work_delta_ms']:+.7f} ms; "
                  f"predicted DAG delta={effect['predicted_dag_delta_ms']:+.7f} ms; "
                  f"observed paired mean delta={effect['mean_delta_ms']:+.7f} ms")
            print(f"  AB={effect['AB_mean_ms']:+.7f} ms; BA={effect['BA_mean_ms']:+.7f} ms; "
                  f"paired median={effect['median_delta_ms']:+.7f} ms; median CI={effect['median_delta_ci95_ms']}")
        print(result["interpretation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
