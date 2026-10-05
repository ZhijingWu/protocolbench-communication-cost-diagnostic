import sys
sys.dont_write_bytecode = True
import copy
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.io_utils import BASE, fingerprint, load_config
from src.topology_generator import generate_cases, generate_topology
from src.local_router_adapter import (
    assignment_from_output, baseline_assignment, prompt_digest)


class TopologyTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(BASE / "configs/topology_cases.yaml")
        self.agents = self.config["agents"]

    def test_structures_and_fixed_features(self):
        before = copy.deepcopy(self.agents)
        for topology, count in [("chain", 3), ("star", 6), ("full_mesh", 12), ("hotspot", 12)]:
            graph = generate_topology(self.agents, topology)
            self.assertEqual(len(graph["edges"]), count)
            self.assertEqual(graph["nodes"], before)
            self.assertTrue(all(e["src"] != e["dst"] and e["weight"] > 0 for e in graph["edges"]))
        self.assertEqual(self.agents, before)

    def test_seed_repeatability(self):
        first = generate_topology(self.agents, "hotspot", seed=17)
        second = generate_topology(self.agents, "hotspot", seed=17)
        self.assertEqual(first, second)
        third = generate_topology(self.agents, "hotspot", seed=18)
        self.assertNotEqual(first["edges"], third["edges"])

    def test_explicit_traffic_scaling(self):
        low = generate_topology(self.agents, "star", 1)
        high = generate_topology(self.agents, "star", 100)
        self.assertEqual(high["total_messages"], 100 * low["total_messages"])
        self.assertEqual(low["nodes"], high["nodes"])

    def test_equal_total_control(self):
        for topology in self.config["topologies"]:
            self.assertAlmostEqual(generate_topology(self.agents, topology, 10,
                                                    normalize_total=True)["total_messages"], 10)

    def test_zero_traffic_and_invalid_nodes(self):
        graph = generate_topology(self.agents, "hotspot", 0)
        self.assertEqual(graph["total_messages"], 0)
        with self.assertRaises(ValueError):
            generate_topology(self.agents, "invalid")
        with self.assertRaises(ValueError):
            generate_topology([self.agents[0], self.agents[0]], "chain")

    def test_original_router_inputs_prompt_and_assignment_fixed(self):
        first, info = baseline_assignment(self.config["task_analysis"], self.agents)
        self.assertEqual(info["source"], "heuristic_fallback")
        digest = prompt_digest(self.config["task_analysis"], self.agents)
        cases = list(generate_cases(self.config))
        self.assertEqual(len(cases), 24)
        self.assertGreater(len({fingerprint(g["edges"]) for g in cases}), 4)
        for graph in cases:
            observed, audit = baseline_assignment(self.config["task_analysis"], graph["nodes"])
            self.assertEqual(first, observed)
            self.assertEqual(audit["local_inputs_sha256"], info["local_inputs_sha256"])
            self.assertEqual(prompt_digest(self.config["task_analysis"], graph["nodes"]), digest)

    def test_saved_assignment_validation(self):
        output = {"agent_assignments": {str(a["id"]): "a2a" for a in self.agents}}
        self.assertEqual(set(assignment_from_output(output, self.agents).values()), {"A2A"})
        with self.assertRaises(ValueError):
            assignment_from_output({"agent_assignments": {"0": "a2a"}}, self.agents)


if __name__ == "__main__":
    unittest.main()
