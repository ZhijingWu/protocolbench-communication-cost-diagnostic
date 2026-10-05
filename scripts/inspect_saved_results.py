#!/usr/bin/env python3
"""Inspect and independently check saved evidence, without imports or experiment runs."""
from pathlib import Path
from collections import Counter
import csv
import json
import math
import statistics

BASE = Path(__file__).resolve().parents[1]

def rows(relative):
    with (BASE / relative).open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))

def truth(value):
    return str(value).lower() in {'true', '1'}

def main():
    raw = rows('results/raw/real_protocol_profile.csv')
    measured = [r for r in raw if r['phase'] == 'measured']
    warmups = [r for r in raw if r['phase'] == 'warmup']
    assert len(raw) == 560 and len(measured) == 480 and len(warmups) == 80
    assert all(truth(r['success']) for r in raw)
    conditions = Counter((r['protocol'], int(r['payload_size_bytes'])) for r in measured)
    assert len(conditions) == 16 and set(conditions.values()) == {30}
    warmup_conditions = Counter((r['protocol'], int(r['payload_size_bytes'])) for r in warmups)
    assert set(warmup_conditions) == set(conditions) and set(warmup_conditions.values()) == {5}
    assert {p for p,s in conditions} == {'A2A','ACP','ANP','Agora'}
    assert {s for p,s in conditions} == {1024,10240,51200,102400}
    for r in raw:
        duration = (int(r['wall_clock_end_ns']) - int(r['wall_clock_start_ns'])) / 1e6
        assert duration == float(r['latency_ms'])
        assert truth(r['timing_sanity_passed'])
        assert int(r['server_requests']) == int(r['executor_calls']) == 1
        assert 0 <= float(r['original_request_metric_ms']) <= duration
    costs = rows('results/processed/real_protocol_costs.csv')
    assert len(costs) == 16
    for summary in costs:
        key = (summary['protocol'], int(summary['payload_size_bytes']))
        samples = [r for r in measured if (r['protocol'],int(r['payload_size_bytes'])) == key]
        values = [float(r['latency_ms']) for r in samples]
        ordered = sorted(values)
        q = (len(ordered)-1)*.95
        lo,hi = math.floor(q),math.ceil(q)
        p95 = ordered[lo] + (ordered[hi]-ordered[lo])*(q-lo)
        expected = {
            'mean_latency_ms': statistics.mean(values),
            'median_latency_ms': statistics.median(values),
            'p95_latency_ms': p95,
            'std_latency_ms': statistics.stdev(values),
            'mean_encoded_request_bytes': statistics.mean(int(r['encoded_request_bytes']) for r in samples),
        }
        assert int(summary['successful_requests']) == int(summary['attempted_requests']) == 30
        assert int(summary['failures']) == 0 and summary['status'] == 'ok'
        for field,value in expected.items():
            assert math.isclose(float(summary[field]),value,rel_tol=1e-12,abs_tol=1e-12), (key,field)
    controlled = rows('results/processed/decision_reversal.csv')
    result = json.loads((BASE/'results/processed/reversal_summary.json').read_text())
    reversals = sum(truth(r['strict_reversal']) for r in controlled)
    assert len(controlled) == result['total_cases'] == 144
    assert reversals == result['strict_reversal_cases'] == 37
    workflows = rows('results/processed/gaia_workflow_reversal.csv')
    workflow_summary = json.loads((BASE/'results/processed/gaia_workflow_summary.json').read_text())
    assert len(workflows) == workflow_summary['total_cases'] == 144
    witness = {}
    for candidate in ['all_four','without_agora']:
        matches = [r for r in workflows if r['workflow']=='analysis_task' and r['candidate_set']==candidate
                   and r['traffic_normalization']=='per_edge' and float(r['traffic_scale'])==100
                   and float(r['lambda'])==.1 and int(r['payload_size_bytes'])==10240]
        assert len(matches) == 1
        r = matches[0]
        baseline,assignment = json.loads(r['baseline_assignment']),json.loads(r['graph_assignment'])
        assert baseline['1']=='A2A' and assignment['1']=='ANP'
        assert '1' in json.loads(r['eligible_preference_reversal_nodes'])
        assert truth(r['strict_eligible_preference_reversal'])
        forced = json.loads(r['forced_removal_nodes'])
        if candidate == 'without_agora':
            assert forced == ['0'] and float(r['objective_delta']) > 0
            assert float(r['objective_delta_vs_feasible_seed']) < 0
        else:
            assert not forced and assignment['0'] == 'Agora' and float(r['objective_delta']) < 0
        witness[candidate] = {k:r[k] for k in ['graph_assignment','forced_removal_nodes','eligible_preference_reversal_nodes','objective_delta','objective_delta_vs_feasible_seed']}
    print(json.dumps({'measured_successes':480,'measured_attempts':480,'excluded_warmups':80,
        'conditions':16,'saved_request_statistics':'PASS','controlled_graph_reversals':37,
        'controlled_graph_cases':144,'workflow_cases':144,'analysis_task_witness':witness,
        'interpretation':'Measured local costs; controlled demand; synthetic margins; no task-quality claim'},indent=2))

if __name__ == '__main__':
    main()
