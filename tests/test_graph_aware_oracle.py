import sys
sys.dont_write_bytecode = True
import random
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.io_utils import PROTOCOLS
from src.objective import manual_margin_losses
from src.graph_aware_oracle import exhaustive_oracle, reversal_thresholds


class OracleTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {"a": "A2A", "b": "A2A"}
        self.losses = manual_margin_losses(self.baseline, 3)
        self.edges = [{"src": "a", "dst": "b", "weight": 2, "payload_size_bytes": 1024}]
        self.costs = {(p, 1024): c for p, c in zip(PROTOCOLS, [5, 1, 3, 4])}

    def run_oracle(self, lam=1, edges=None, costs=None, losses=None):
        return exhaustive_oracle(self.baseline, self.edges if edges is None else edges,
                                 self.costs if costs is None else costs,
                                 self.losses if losses is None else losses, lam)

    def test_hand_computed_two_node_case(self):
        # Baseline J=2*5=10; switch b to ACP: J=3+2*1=5; a has no incoming demand.
        result = self.run_oracle()
        self.assertEqual(result["best_assignment"], {"a": "A2A", "b": "ACP"})
        self.assertEqual(result["baseline"]["total_objective"], 10)
        self.assertEqual(result["best"]["total_objective"], 5)
        self.assertEqual(result["best"]["local_loss"], 3)
        self.assertEqual(result["best"]["communication_cost"], 2)
        self.assertEqual(result["assignments_enumerated"], 16)
        self.assertEqual(result["changed_nodes"], ["b"])

    def test_lambda_zero_is_local_optimum(self):
        result = self.run_oracle(lam=0)
        self.assertEqual(result["best_assignment"], self.baseline)
        self.assertEqual(result["best"]["local_loss"], 0)
        # Check true local optimum even when provided baseline is locally suboptimal.
        losses = {n: {p: (0 if p == "ANP" else 2) for p in PROTOCOLS} for n in self.baseline}
        self.assertEqual(self.run_oracle(lam=0, losses=losses)["best_assignment"], {"a": "ANP", "b": "ANP"})

    def test_zero_traffic(self):
        zero = [{**e, "weight": 0} for e in self.edges]
        self.assertEqual(self.run_oracle(lam=100, edges=zero)["best_assignment"], self.baseline)
        self.assertEqual(self.run_oracle(lam=100, edges=[])["best_assignment"], self.baseline)

    def test_equal_costs(self):
        equal = {(p, 1024): 5 for p in PROTOCOLS}
        self.assertEqual(self.run_oracle(lam=100, costs=equal)["best_assignment"], self.baseline)

    def test_threshold_tie_and_strict_reversal(self):
        threshold = next(t for t in reversal_thresholds(self.baseline, self.edges, self.costs, self.losses)
                         if t["node"] == "b" and t["alternative_protocol"] == "ACP")
        self.assertEqual(threshold["lambda_threshold"], .375)
        self.assertEqual(self.run_oracle(lam=.375)["best_assignment"], self.baseline)
        self.assertEqual(self.run_oracle(lam=.376)["changed_nodes"], ["b"])
        scaled = [{**e, "weight": e["weight"] * 10} for e in self.edges]
        threshold10 = next(t for t in reversal_thresholds(self.baseline, scaled, self.costs, self.losses, 10, 1)
                           if t["node"] == "b" and t["alternative_protocol"] == "ACP")
        self.assertEqual(threshold10["lambda_threshold"], .0375)
        self.assertEqual(threshold10["traffic_threshold_at_lambda"], .375)

    def test_permutation_invariance_oracle(self):
        first = self.run_oracle()
        second = exhaustive_oracle({"z": "A2A", "x": "A2A"},
                                   [{"src": "z", "dst": "x", "weight": 2, "payload_size_bytes": 1024}],
                                   self.costs, {"z": self.losses["a"], "x": self.losses["b"]}, 1)
        self.assertEqual(first["best"], second["best"])
        self.assertEqual(second["best_assignment"], {"z": "A2A", "x": "ACP"})

    def test_deterministic_assignment_and_objective(self):
        first, second = self.run_oracle(), self.run_oracle()
        for result in (first, second):
            result.pop("runtime_seconds")
        self.assertEqual(first, second)

    def test_size_guard(self):
        with self.assertRaises(ValueError):
            exhaustive_oracle(self.baseline, self.edges, self.costs, self.losses, 1, max_assignments=15)

    def test_exhaustive_matches_independent_separable_calculation(self):
        rng = random.Random(6349)
        for _ in range(12):
            lam = rng.random() * 2
            costs = {(p, 1024): rng.randint(1, 12) for p in PROTOCOLS}
            losses = {n: {p: rng.randint(0, 7) for p in PROTOCOLS} for n in self.baseline}
            result = self.run_oracle(lam=lam, costs=costs, losses=losses)
            expected = min(losses["a"].values()) + min(losses["b"][p] + lam * 2 * costs[p, 1024]
                                                       for p in PROTOCOLS)
            self.assertAlmostEqual(result["best"]["total_objective"], expected)


if __name__ == "__main__":
    unittest.main()
