import sys
sys.dont_write_bytecode = True
import csv
import asyncio
import tempfile
from types import SimpleNamespace
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.io_utils import BASE, PROTOCOLS, output_path
from src.objective import (
    evaluate_objective, load_measured_costs, manual_margin_losses, validate_problem)
from src.protocol_cost_profiler import (
    _contains_token, _has_failure, conversion_sample, empty_row, summarize, RealSession)


class ObjectiveTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {"a": "A2A", "b": "ACP"}
        self.losses = manual_margin_losses(self.baseline, 3)
        self.costs = {(p, 1024): c for p, c in zip(PROTOCOLS, [5, 1, 3, 4])}
        self.edges = [{"src": "a", "dst": "b", "weight": 2, "payload_size_bytes": 1024}]

    def test_destination_protocol_only(self):
        first = evaluate_objective(self.baseline, self.edges, self.costs, self.losses, 1)
        changed_sender = evaluate_objective({"a": "ANP", "b": "ACP"}, self.edges, self.costs, self.losses, 1)
        self.assertEqual(first.communication_cost, 2)
        self.assertEqual(changed_sender.communication_cost, 2)
        self.assertEqual(changed_sender.local_loss, 3)

    def test_id_permutation_value(self):
        first = evaluate_objective(self.baseline, self.edges, self.costs, self.losses, .5)
        second = evaluate_objective({"z": "A2A", "x": "ACP"},
                                    [{"src": "z", "dst": "x", "weight": 2, "payload_size_bytes": 1024}],
                                    self.costs, {"z": self.losses["a"], "x": self.losses["b"]}, .5)
        self.assertEqual(first, second)

    def test_invalid_inputs_rejected(self):
        for value in [-1, float("inf"), float("nan")]:
            with self.assertRaises(ValueError):
                evaluate_objective(self.baseline, self.edges, self.costs, self.losses, value)
        broken = self.costs.copy()
        del broken["ANP", 1024]
        with self.assertRaises(ValueError):
            validate_problem(self.baseline, self.edges, broken, self.losses)
        with self.assertRaises(ValueError):
            manual_margin_losses(self.baseline, -1)

    def test_output_scope_guard(self):
        with self.assertRaises(ValueError):
            output_path(BASE.parents[1] / "README.md")

    def test_conversion_latency_not_network(self):
        with self.assertRaises(ValueError):
            load_measured_costs("nonexistent.csv", "conversion-only", "mean_latency_ms")

    def test_warmups_excluded_and_failures_retained(self):
        rows = []
        for phase, success, latency in [("warmup", True, 999), ("measured", True, 5), ("measured", False, None)]:
            row = empty_row("real", "A2A", 1024, phase, 0)
            row.update(success=success, latency_ms=latency, encoded_bytes=1200 if success else None)
            rows.append(row)
        stats = summarize(rows)[0]
        self.assertEqual(stats["mean_latency_ms"], 5)
        self.assertEqual(stats["failure_rate"], .5)
        self.assertEqual(stats["measured_attempts"], 2)
        self.assertIsNone(stats["mean_conversion_runtime_ms"])

    def test_setup_blocked_not_zero_cost(self):
        row = empty_row("real", "ANP", 1024, "measured", 0)
        row["stage"] = "setup_blocked_not_sent"
        stats = summarize([row])[0]
        self.assertIsNone(stats["mean_latency_ms"])
        self.assertIsNone(stats["mean_encoded_bytes"])
        self.assertEqual(stats["failure_rate"], 1)

    def test_original_conversion_measured_repeatable_sizes(self):
        for p in PROTOCOLS:
            time_ms, first = conversion_sample(p, 1024)
            _, second = conversion_sample(p, 1024)
            self.assertEqual(first, second)
            self.assertGreater(time_ms, 0)
            self.assertGreater(first, 1024)

    def test_missing_original_metric_rejects_success(self):
        async def send(dst, content):
            return content
        session = RealSession("A2A", {"url": "http://unused"}, 1)
        session.agent = SimpleNamespace(send=send)
        session.latency_metric = SimpleNamespace(collect=lambda: [])
        session.bytes_metric = SimpleNamespace(collect=lambda: [])
        latency, size, error = asyncio.run(session.sample(1024))
        self.assertIsNone(latency)
        self.assertIsNone(size)
        self.assertIsInstance(error, RuntimeError)

    def test_failed_cost_and_duplicate_cost_rejected(self):
        with tempfile.TemporaryDirectory(dir=BASE / "results/raw") as directory:
            path = Path(directory) / "costs.csv"
            fields = ["mode", "protocol", "payload_size_bytes", "success_count", "failure_rate", "mean_encoded_bytes"]
            def save(rows):
                with path.open("w", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(rows)
            row = dict(mode="conversion-only", protocol="A2A", payload_size_bytes=1024,
                       success_count=0, failure_rate=1, mean_encoded_bytes="")
            save([row])
            with self.assertRaises(ValueError):
                load_measured_costs(path, "conversion-only")
            row.update(success_count=29, failure_rate=1/30, mean_encoded_bytes=1200)
            save([row])
            with self.assertRaises(ValueError):
                load_measured_costs(path, "conversion-only")
            row.update(success_count=30, failure_rate=0)
            save([row, row])
            with self.assertRaises(ValueError):
                load_measured_costs(path, "conversion-only")

    def test_fallback_and_error_rejection(self):
        self.assertTrue(_has_failure({"text": "[Agora Fallback] Processed: token"}))
        self.assertTrue(_has_failure({"result": {"error": "failed"}}))
        self.assertFalse(_has_failure({"text": "ack token"}))
        self.assertTrue(_contains_token({"events": [{"data": "ack token"}]}, "token"))
        self.assertFalse(_contains_token(None, "token"))
        self.assertFalse(_contains_token({"text": "some unrelated response"}, "token"))


if __name__ == "__main__":
    unittest.main()
