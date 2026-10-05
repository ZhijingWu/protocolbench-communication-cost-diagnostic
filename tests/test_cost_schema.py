import sys
sys.dont_write_bytecode = True
import contextlib
import copy
import csv
import io
import json
import math
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import cost_schema
from src.cost_schema import canonical_real_rows, ensure_canonical_real_costs, read_rows
from src.io_utils import BASE, source_module
from src.objective import load_measured_costs
from src.protocol_cost_profiler import STAT_FIELDS


class CostSchemaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=BASE / "results/raw")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        for relative in ("results/processed/real_protocol_costs.csv", "results/raw/real_protocol_profile.csv",
                         "results/raw/real_protocol_manifest.json", "results/processed/protocol_costs_conversion-only.csv",
                         "results/raw/local_router_output.json", "configs/topology_cases.yaml"):
            destination = self.base / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(BASE / relative, destination)
        self.source_rows, _ = read_rows(self.base / "results/processed/real_protocol_costs.csv")
        self.conversion_rows, _ = read_rows(self.base / "results/processed/protocol_costs_conversion-only.csv")
        shutil.copyfile(self.base / "results/processed/protocol_costs_conversion-only.csv",
                        self.base / "results/processed/protocol_costs.csv")
        # Explicit synthetic stale-run fixture, isolated in a disposable test directory.
        blocked = canonical_real_rows(self.source_rows)
        for row in blocked:
            row.update(success_count="0", failure_rate="1.0", measurement_kind="request_timer")
            for field in ("mean_latency_ms", "median_latency_ms", "p95_latency_ms", "mean_encoded_bytes"):
                row[field] = ""
        stale = self.base / "results/processed/protocol_costs_real.csv"
        stale.write_bytes(cost_schema.csv_bytes(blocked))
        self.stale_bytes = stale.read_bytes()

    def test_real_mapping_preserves_exact_numeric_strings(self):
        canonical = canonical_real_rows(self.source_rows)
        for original, mapped in zip(self.source_rows, canonical):
            self.assertEqual(mapped["mode"], "real")
            self.assertEqual(mapped["measurement_kind"], "end_to_end_local_request")
            self.assertEqual(mapped["measured_attempts"], original["attempted_requests"])
            self.assertEqual(mapped["success_count"], original["successful_requests"])
            self.assertEqual(float(mapped["failure_rate"]), int(original["failures"])/int(original["attempted_requests"]))
            for field in ("mean_latency_ms", "median_latency_ms", "p95_latency_ms"):
                self.assertEqual(mapped[field], original[field])
            self.assertEqual(mapped["mean_encoded_bytes"], original["mean_encoded_request_bytes"])
            for field in ("mean_conversion_runtime_ms", "median_conversion_runtime_ms", "p95_conversion_runtime_ms"):
                self.assertEqual(mapped[field], "")

    def test_both_canonical_modes_load_without_mixing_measurements(self):
        path = ensure_canonical_real_costs(self.base)
        rows, fields = read_rows(path)
        self.assertEqual(fields, STAT_FIELDS)
        self.assertEqual(len(rows), 32)
        self.assertEqual([r for r in rows if r["mode"] == "conversion-only"], self.conversion_rows)
        actual_real = load_measured_costs(path, "real", "mean_latency_ms")
        actual_conversion = load_measured_costs(path, "conversion-only", "mean_encoded_bytes")
        self.assertEqual(actual_real, {(r["protocol"], int(r["payload_size_bytes"])):float(r["mean_latency_ms"]) for r in self.source_rows})
        self.assertEqual(actual_conversion, {(r["protocol"], int(r["payload_size_bytes"])):float(r["mean_encoded_bytes"]) for r in self.conversion_rows})
        with self.assertRaises(ValueError):
            load_measured_costs(path, "conversion-only", "mean_latency_ms")

    def test_stale_failed_run_archived_with_hash_and_source_provenance(self):
        ensure_canonical_real_costs(self.base)
        manifest = json.loads((self.base / "results/raw/cost_interface_manifest.json").read_text())
        archived = next(r for r in manifest["archives"] if r["original_path"] == "results/processed/protocol_costs_real.csv")
        self.assertEqual((self.base / archived["archive_path"]).read_bytes(), self.stale_bytes)
        for source, sha in manifest["input_sha256"].items():
            self.assertEqual(cost_schema.sha256(self.base / source), sha)
        for output, sha in manifest["output_sha256"].items():
            self.assertEqual(cost_schema.sha256(self.base / output), sha)

    def test_translation_is_idempotent(self):
        path = ensure_canonical_real_costs(self.base)
        original = path.read_bytes()
        manifest_path = self.base / "results/raw/cost_interface_manifest.json"
        provenance = manifest_path.read_bytes()
        ensure_canonical_real_costs(self.base)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(manifest_path.read_bytes(), provenance)

    def test_changed_verified_source_rejected_before_outputs_mutate(self):
        path = self.base / "results/processed/real_protocol_costs.csv"
        old_canonical = (self.base / "results/processed/protocol_costs.csv").read_bytes()
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            ensure_canonical_real_costs(self.base)
        self.assertEqual((self.base / "results/processed/protocol_costs.csv").read_bytes(), old_canonical)

    def test_incomplete_failed_duplicate_and_nonfinite_rows_rejected(self):
        original = self.source_rows[0]
        changes = [dict(status="blocked"), dict(successful_requests="29", failures="1", status="partial"),
                   dict(attempted_requests="29"), dict(skipped_requests="1"), dict(mean_latency_ms="nan")]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                canonical_real_rows([{**original, **change}])
        with self.assertRaises(ValueError):
            canonical_real_rows([original, original])

    def run_cli(self, mode, metric):
        script = source_module("_cost_schema_joint_cli_regression", BASE / "scripts/run_joint_assignment.py")
        argv = ["run_joint_assignment.py", "--profile-mode", mode, "--cost-metric", metric]
        with patch.object(script, "BASE", self.base), patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            script.main()
        result, _ = read_rows(self.base / "results/processed/decision_reversal.csv")
        return result

    def test_cli_profile_mode_conversion_only_regression(self):
        # Most important regression: conversion mode after real rows were merged.
        ensure_canonical_real_costs(self.base)
        manifest_path = self.base / "results/raw/cost_interface_manifest.json"
        prior_manifest = manifest_path.read_bytes()
        result = self.run_cli("conversion-only", "mean_encoded_bytes")
        self.assertEqual(len(result), 144)
        self.assertTrue(all(r["profile_mode"] == "conversion-only" for r in result))
        chain = result[0]
        expected = math.fsum(float(next(r["mean_encoded_bytes"] for r in self.conversion_rows
                                  if r["protocol"] == p and r["payload_size_bytes"] == "10240"))
                             for p in ("A2A", "ACP", "A2A"))
        self.assertEqual(float(chain["baseline_comm_cost"]), expected)
        self.assertEqual(manifest_path.read_bytes(), prior_manifest)

    def test_cli_profile_mode_real_default_prepares_verified_sources(self):
        result = self.run_cli("real", "mean_latency_ms")
        self.assertEqual(len(result), 144)
        self.assertTrue(all(r["profile_mode"] == "real" and r["cost_metric"] == "mean_latency_ms" for r in result))
        expected = math.fsum(float(next(r["mean_latency_ms"] for r in self.source_rows
                                  if r["protocol"] == p and r["payload_size_bytes"] == "10240"))
                             for p in ("A2A", "ACP", "A2A"))
        self.assertEqual(float(result[0]["baseline_comm_cost"]), expected)
        self.assertTrue((self.base / "results/raw/cost_interface_manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
