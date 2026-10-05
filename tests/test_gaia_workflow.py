import sys
sys.dont_write_bytecode = True
import copy
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.gaia_workflow import instantiate_workflow, load_official_patterns
from src.gaia_workflow_experiment import (
    load_verified_real_latencies, run_candidate_oracle, workflow_sweep)
from src.io_utils import BASE, PROTOCOLS, fingerprint, load_config
from src.local_router_adapter import baseline_assignment
from src.objective import manual_margin_losses


class GaiaWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=load_config(BASE / "configs/topology_cases.yaml")
        cls.agents=cls.config["agents"]
        cls.patterns=load_official_patterns()
        cls.baseline,_=baseline_assignment(cls.config["task_analysis"],cls.agents,
            BASE / "results/raw/local_router_output.json")
        cls.costs,_=load_verified_real_latencies()
        cls.losses=manual_margin_losses(cls.baseline,cls.config["manual_local_margin"])

    def graph(self,name,scale=1,normalize=False):
        return instantiate_workflow(self.patterns[name],self.agents,name,scale,
            self.config["payload_size_bytes"],normalize)

    def test_parse_exact_official_named_templates(self):
        self.assertEqual([(r["from"],r["to"]) for r in self.patterns["analysis_task"]],
                         [(0,[1]),(1,[2]),(2,"final")])
        self.assertEqual([(r["from"],r["to"]) for r in self.patterns["collaborative_task"]],
                         [(0,"all"),("all",0)])

    def test_analysis_final_preserved_without_invented_agent_or_edge(self):
        graph=self.graph("analysis_task")
        self.assertEqual([(e["src"],e["dst"]) for e in graph["edges"]],[("0","1"),("1","2")])
        self.assertEqual([(e["src"],e["dst"]) for e in graph["terminal_events"]],[("2","final")])
        self.assertFalse(graph["terminal_events"][0]["included_in_communication_objective"])
        self.assertEqual(graph["nodes"],self.agents)
        self.assertNotIn("3",{e["dst"] for e in graph["edges"]})
        self.assertEqual(graph["official_pattern"],self.patterns["analysis_task"])

    def test_collaboration_expands_only_declared_peer_flows(self):
        graph=self.graph("collaborative_task")
        pairs={(e["src"],e["dst"]) for e in graph["edges"]}
        expected={(a,b) for i in ("1","2","3") for a,b in [("0",i),(i,"0")]}
        self.assertEqual(pairs,expected)
        self.assertEqual(len(graph["edges"]),6)
        self.assertFalse(graph["terminal_events"])
        self.assertTrue(all(e["src"]!=e["dst"] for e in graph["edges"]))

    def test_traffic_scaling_and_equal_total_preserve_edges(self):
        for name in self.patterns:
            low,high=self.graph(name),self.graph(name,100)
            self.assertEqual([(e["src"],e["dst"]) for e in low["edges"]],
                             [(e["src"],e["dst"]) for e in high["edges"]])
            self.assertAlmostEqual(high["total_agent_messages"],100*low["total_agent_messages"])
            self.assertAlmostEqual(self.graph(name,10,True)["total_agent_messages"],10)

    def test_protocol_preferences_are_only_metadata(self):
        graph=self.graph("analysis_task",100)
        pattern=copy.deepcopy(self.patterns["analysis_task"])
        for step in pattern:
            step["protocol_preference"]="ACP"
            step["reason"]="metadata-only sensitivity control"
        changed=instantiate_workflow(pattern,self.agents,"analysis_task",100,10240)
        before=run_candidate_oracle(self.baseline,graph,self.costs,self.losses,.1,PROTOCOLS)
        after=run_candidate_oracle(self.baseline,changed,self.costs,self.losses,.1,PROTOCOLS)
        before.pop("runtime_seconds")
        after.pop("runtime_seconds")
        self.assertEqual(before,after)
        self.assertEqual(changed["edges"][0]["metadata"]["protocol_preference"],"ACP")

    def test_unknown_endpoints_rejected_without_extra_edges(self):
        for pattern in ([{"from":7,"to":[1]}],[{"from":0,"to":[7]}]):
            with self.assertRaises(ValueError):
                instantiate_workflow(pattern,self.agents,"unknown",1,10240)

    def test_global_agora_removal_forced_change_is_not_preference_reversal(self):
        original=copy.deepcopy(self.baseline)
        losses=copy.deepcopy(self.losses)
        result=run_candidate_oracle(self.baseline,self.graph("collaborative_task"),self.costs,
                                   self.losses,0,("A2A","ACP","ANP"))
        self.assertFalse(result["baseline_feasible"])
        self.assertEqual(result["forced_removal_nodes"],["0"])
        self.assertEqual(result["oracle_feasible_seed"]["0"],"A2A")
        self.assertTrue(all(p!="Agora" for p in result["graph_assignment"].values()))
        self.assertEqual(result["graph_local_loss"],1)
        self.assertEqual(result["objective_delta"],1)
        self.assertFalse(result["strict_reversal"])
        self.assertFalse(result["strict_eligible_preference_reversal"])
        self.assertEqual(self.baseline,original)
        self.assertEqual(self.losses,losses)

    def test_analysis_without_agora_retains_real_a2a_preference_reversal(self):
        result=run_candidate_oracle(self.baseline,self.graph("analysis_task",100),self.costs,
                                   self.losses,.1,("A2A","ACP","ANP"))
        self.assertEqual(result["forced_removal_nodes"],["0"])
        self.assertEqual(result["eligible_preference_reversal_nodes"],["1"])
        self.assertEqual(result["a2a_acp_anp_preference_reversal_nodes"],["1"])
        self.assertEqual(result["graph_assignment"]["1"],"ANP")
        self.assertEqual(result["graph_assignment"]["3"],"A2A")
        self.assertGreater(result["objective_delta"],0)
        self.assertLess(result["objective_delta_vs_feasible_seed"],0)
        self.assertFalse(result["strict_reversal"])
        self.assertTrue(result["strict_eligible_preference_reversal"])

    def test_collaboration_without_agora_eligible_leaf_reversals(self):
        result=run_candidate_oracle(self.baseline,self.graph("collaborative_task",100),self.costs,
                                   self.losses,.1,("A2A","ACP","ANP"))
        self.assertEqual(result["eligible_preference_reversal_nodes"],["1","3"])
        self.assertTrue(result["strict_reversal"])
        self.assertEqual(result["graph_assignment"],{"0":"ANP","1":"ANP","2":"ACP","3":"ANP"})
        self.assertEqual(result["assignments_enumerated"],81)

    def test_full_candidates_zero_lambda_or_zero_traffic_keep_baseline(self):
        for name in self.patterns:
            for lam,scale in [(0,100),(.1,0)]:
                result=run_candidate_oracle(self.baseline,self.graph(name,scale),self.costs,
                                           self.losses,lam,PROTOCOLS)
                self.assertEqual(result["graph_assignment"],self.baseline)
                self.assertFalse(result["strict_reversal"])
                self.assertEqual(result["assignments_enumerated"],256)

    def test_determinism_and_unchanged_control_inputs(self):
        original=fingerprint({"config":self.config,"patterns":self.patterns,"baseline":self.baseline})
        first=workflow_sweep(self.config,self.patterns,self.baseline,self.costs)
        second=workflow_sweep(self.config,self.patterns,self.baseline,self.costs)
        for result in (first,second):
            for row in result[0]:
                row.pop("runtime_seconds")
        self.assertEqual(first,second)
        self.assertEqual(len(first[0]),144)
        self.assertEqual(original,fingerprint({"config":self.config,"patterns":self.patterns,"baseline":self.baseline}))


if __name__ == "__main__":
    unittest.main()
