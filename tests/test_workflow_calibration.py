"""Offline release/reader checks using real saved records in disposable copies."""
from pathlib import Path
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "results/workflow_calibration"


class WorkflowCalibrationTests(unittest.TestCase):
    def invoke(self, artifact, cwd):
        return subprocess.run(
            [sys.executable, "-B", str(artifact / "scripts/recalculate.py"), "--json"],
            cwd=cwd, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=60,
        )

    def copy_fixture(self, directory):
        repo = Path(directory) / "repo"
        artifact = repo / "results/workflow_calibration"
        shutil.copytree(ARTIFACT, artifact)
        profile = repo / "results/processed/real_protocol_costs.csv"
        profile.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "results/processed/real_protocol_costs.csv", profile)
        return artifact, profile

    def test_complete_saved_release_recalculates_from_foreign_directory_without_writes(self):
        before = {p.relative_to(ARTIFACT): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in ARTIFACT.rglob("*") if p.is_file()}
        with tempfile.TemporaryDirectory() as directory:
            result = self.invoke(ARTIFACT, directory)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["counts"]["measured_workflows"], 120)
        self.assertEqual(data["counts"]["measured_workflow_rpcs"], 480)
        serial, parallel = data["paired_effects"]
        self.assertAlmostEqual(serial["mean_delta_ms"], .8279372333333335, places=10)
        self.assertAlmostEqual(serial["predicted_dag_delta_ms"], -.1564973, places=10)
        self.assertEqual(parallel["predicted_dag_delta_ms"], 0)
        self.assertGreater(parallel["AB_mean_ms"], 0)
        self.assertLess(parallel["BA_mean_ms"], 0)
        after = {p.relative_to(ARTIFACT): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in ARTIFACT.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_raw_observations_fail_even_when_stored_summaries_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact, _ = self.copy_fixture(directory)
            (artifact / "raw/workflow_runs.csv").unlink()
            self.assertTrue((artifact / "processed/summary.json").exists())
            result = self.invoke(artifact, directory)
        self.assertEqual(result.returncode, 2)
        self.assertIn("workflow_runs.csv", result.stderr)
        self.assertNotIn('"status": "passed"', result.stdout)

    def test_missing_historical_profile_has_no_summary_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact, profile = self.copy_fixture(directory)
            profile.unlink()
            result = self.invoke(artifact, directory)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Missing frozen historical profile", result.stderr)

    def test_semantic_timestamp_check_rejects_corruption_even_after_rehash(self):
        # Tamper with one value only in a disposable test copy; no replacement
        # measurements are produced, and this copy is never a publication input.
        with tempfile.TemporaryDirectory() as directory:
            artifact, _ = self.copy_fixture(directory)
            path = artifact / "raw/rpc_events.csv"
            with path.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                fields, rows = reader.fieldnames, list(reader)
            rows[0]["latency_ms"] = str(float(rows[0]["latency_ms"]) + .01)
            buffer = io.StringIO(newline="")
            writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
            path.write_bytes(buffer.getvalue().encode("utf-8"))
            manifest_path = artifact / "release_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            entry = manifest["files"]["raw/rpc_events.csv"]
            entry["publication_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            entry["copied_unchanged"] = False
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = self.invoke(artifact, directory)
        self.assertEqual(result.returncode, 2)
        self.assertIn("RPC timing", result.stderr)


if __name__ == "__main__":
    unittest.main()
