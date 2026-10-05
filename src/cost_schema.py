"""Canonical cost-schema translation; measurements are copied, never rerun."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from .io_utils import BASE, PROTOCOLS, output_path, protocol_name, write_json
from .protocol_cost_profiler import STAT_FIELDS


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), reader.fieldnames


def canonical_real_rows(rows):
    """Copy existing real summary numeric strings without rounding/reaggregation."""
    result, keys = [], set()
    required = {"protocol", "payload_size_bytes", "status", "attempted_requests",
                "successful_requests", "failures", "mean_latency_ms", "median_latency_ms",
                "p95_latency_ms", "mean_encoded_request_bytes"}
    for row in rows:
        if not required.issubset(row):
            raise ValueError("Real summary is missing required schema columns")
        protocol = protocol_name(row["protocol"])
        size, attempted = int(row["payload_size_bytes"]), int(row["attempted_requests"])
        successes, failures = int(row["successful_requests"]), int(row["failures"])
        key = (protocol, size)
        if key in keys:
            raise ValueError(f"Duplicate real condition: {key}")
        keys.add(key)
        if (size <= 0 or attempted <= 0 or successes < 0 or failures < 0 or
                attempted != successes + failures):
            raise ValueError(f"Invalid real request counts for {key}")
        if row["status"] != "ok" or successes != attempted or failures:
            raise ValueError(f"Real condition is not fully successful: {key}")
        if int(row.get("skipped_requests", "0")) or int(row.get("requested_repetitions", attempted)) != attempted:
            raise ValueError(f"Incomplete real condition: {key}")
        for field in ("mean_latency_ms", "median_latency_ms", "p95_latency_ms", "mean_encoded_request_bytes"):
            if not row[field] or not math.isfinite(float(row[field])) or float(row[field]) < 0:
                raise ValueError(f"Missing/invalid measured {field} for {key}")
        record = dict.fromkeys(STAT_FIELDS, "")
        record.update(mode="real", protocol=protocol, payload_size_bytes=row["payload_size_bytes"],
                      measurement_kind="end_to_end_local_request", measured_attempts=row["attempted_requests"],
                      success_count=row["successful_requests"], failure_rate=str(failures / attempted),
                      mean_latency_ms=row["mean_latency_ms"], median_latency_ms=row["median_latency_ms"],
                      p95_latency_ms=row["p95_latency_ms"], mean_encoded_bytes=row["mean_encoded_request_bytes"])
        result.append(record)
    if not result:
        raise ValueError("No real conditions to canonicalize")
    return result


def csv_bytes(rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=STAT_FIELDS, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def archive_file(path, base=BASE, category="cost_interface_archive"):
    """Preserve exact prior bytes under a content-addressed experiment archive."""
    path, base = Path(path), Path(base)
    digest = sha256(path)
    destination = output_path(base / "results/raw" / category / digest / path.name)
    if destination.exists() and destination.read_bytes() != path.read_bytes():
        raise ValueError("Archive hash collision or corrupted archive")
    if not destination.exists():
        destination.write_bytes(path.read_bytes())
    return {"original_path": str(path.relative_to(base)),
            "archive_path": str(destination.relative_to(base)), "sha256": digest}


def ensure_canonical_real_costs(base=BASE):
    """Validate source provenance, archive stale costs, merge real + unchanged conversion rows."""
    base = Path(base)
    summary = base / "results/processed/real_protocol_costs.csv"
    raw = base / "results/raw/real_protocol_profile.csv"
    profile_manifest = base / "results/raw/real_protocol_manifest.json"
    manifest = json.loads(profile_manifest.read_text(encoding="utf-8"))
    if manifest.get("mode") != "real_local":
        raise ValueError("Expected verified real_local profile provenance")
    for source in (summary, raw):
        expected = manifest.get("output_sha256", {}).get(str(source.relative_to(base)))
        if not expected or expected != sha256(source):
            raise ValueError(f"Real profile source hash mismatch/missing: {source.name}")
    real, _ = read_rows(summary)
    canonical = canonical_real_rows(real)
    expected_keys = {(p, int(size)) for p in PROTOCOLS for size in manifest["config"]["payload_size_bytes"]}
    if {(r["protocol"], int(r["payload_size_bytes"])) for r in canonical} != expected_keys:
        raise ValueError("Real profile does not cover all recorded protocol/size conditions")
    if any(int(r["measured_attempts"]) != int(manifest["config"]["measured_repetitions"]) for r in canonical):
        raise ValueError("Real attempted counts differ from profile manifest")
    canonical_path = base / "results/processed/protocol_costs.csv"
    real_path = base / "results/processed/protocol_costs_real.csv"
    previous, fields = read_rows(canonical_path) if canonical_path.exists() else ([], STAT_FIELDS)
    if fields != STAT_FIELDS:
        raise ValueError("Existing canonical schema must remain unchanged")
    if any(r["mode"] not in ("real", "conversion-only") for r in previous):
        raise ValueError("Unknown mode in existing canonical costs")
    # Preserve every conversion row/value exactly, including its timing strings.
    conversion = [r for r in previous if r["mode"] == "conversion-only"]
    if not conversion:
        conversion, conversion_fields = read_rows(base / "results/processed/protocol_costs_conversion-only.csv")
        if conversion_fields != STAT_FIELDS or any(r["mode"] != "conversion-only" for r in conversion):
            raise ValueError("Invalid conversion-only canonical source")
    manifest_path = base / "results/raw/cost_interface_manifest.json"
    prior_manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    archives = list(prior_manifest.get("archives", []))
    for destination, rows in ((canonical_path, conversion + canonical), (real_path, canonical)):
        content = csv_bytes(rows)
        if destination.exists() and destination.read_bytes() != content:
            entry = archive_file(destination, base)
            if entry not in archives:
                archives.append(entry)
        if not destination.exists() or destination.read_bytes() != content:
            output_path(destination).write_bytes(content)
    # Earlier failed-run raw data/manifests retain their original names and hashes.
    historical = [base / f"results/raw/{name}" for name in
                  ("profile_manifest_real.json", "protocol_profile_real.csv", "protocol_profile_real.json")]
    inputs = [summary, raw, profile_manifest]
    interface = {
        "operation": "schema translation only; no measurements recomputed or rerun",
        "mode": "real", "measurement_kind": "end_to_end_local_request",
        "input_sha256": {str(p.relative_to(base)): sha256(p) for p in inputs},
        "output_sha256": {str(p.relative_to(base)): sha256(p) for p in (canonical_path, real_path)},
        "mapping": {"attempted_requests": "measured_attempts", "successful_requests": "success_count",
                    "failures / attempted_requests": "failure_rate",
                    "mean_encoded_request_bytes": "mean_encoded_bytes",
                    "mean/median/p95_latency_ms": "identical measured strings",
                    "conversion runtime columns": "empty for real rows"},
        "encoded_bytes_definition": manifest["encoded_request_bytes"],
        "latency_boundary": manifest["latency_boundary"],
        "real_conditions": len(canonical), "conversion_conditions_preserved": len(conversion),
        "archives": archives,
        "historical_failed_inputs_unchanged": {str(p.relative_to(base)): sha256(p) for p in historical if p.exists()},
    }
    write_json(manifest_path, interface)
    return canonical_path


def archive_joint_outputs(base=BASE):
    base = Path(base)
    paths = [base / "results/processed/decision_reversal.csv", base / "results/processed/reversal_thresholds.csv",
             base / "results/raw/joint_manifest.json", base / "notes/findings.md"]
    return [archive_file(p, base, "joint_output_archive") for p in paths if p.exists()]
