"""
Urja-X: Factor Sensitivity Tournament Engine (Stage 1)
Evaluates all 9 empirical factors individually across 250 real-world corridor test cases
using the unbiased Triad Network Health Index (Geometric Mean of Service, Demand, Readiness).
Derives objective, research-backed weights from empirical data variance.
"""

import os
import sys
import json
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = "data"
TEST_CASES_PATH = os.path.join(DATA_DIR, "corridor_test_cases.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "factor_tournament_results.json")

print("=" * 80)
print("⚔️ URJA-X: STAGE 1 - FACTOR SENSITIVITY TOURNAMENT ENGINE")
print("Evaluating all 9 empirical factors on Triad Network Health Index (NHI)")
print("=" * 80)

if not os.path.exists(TEST_CASES_PATH):
    print(f"Error: {TEST_CASES_PATH} not found. Run empirical_test_generator.py first.")
    sys.exit(1)

with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
    test_cases = json.load(f)

print(f"Loaded {len(test_cases)} empirical corridor test cases.")

# The 9 factors under test
FACTORS = [
    {
        'id': 'f1_distance',
        'name': 'Inter-Charger Distance (<100 km)',
        'sort_key': lambda n: n['factors']['f1_charger_dist_km'], # Higher distance deficit = higher priority
        'reverse': True
    },
    {
        'id': 'f2_ev_fleet',
        'name': 'EV Fleet Density (VAHAN Registrations)',
        'sort_key': lambda n: n['factors']['f2_ev_fleet_norm'],
        'reverse': True
    },
    {
        'id': 'f3_traffic_flow',
        'name': 'Highway Traffic Flow (IHMCL PCU)',
        'sort_key': lambda n: n['factors']['f3_traffic_pcu'],
        'reverse': True
    },
    {
        'id': 'f4_population',
        'name': 'Human Population Density',
        'sort_key': lambda n: n['factors']['f4_pop_density_norm'],
        'reverse': True
    },
    {
        'id': 'f5_economic',
        'name': 'Economic / Night-Lights Radiance',
        'sort_key': lambda n: n['factors']['f5_economic_ntl_norm'],
        'reverse': True
    },
    {
        'id': 'f6_tourism',
        'name': 'Tourism & Waypoint Pull',
        'sort_key': lambda n: n['factors']['f6_tourism_pull_norm'],
        'reverse': True
    },
    {
        'id': 'f7_substation',
        'name': 'Electricity Grid Substation Proximity',
        'sort_key': lambda n: n['factors']['f7_substation_dist_km'], # Closer distance = higher priority
        'reverse': False
    },
    {
        'id': 'f8_fuel_station',
        'name': 'Fuel Stations / Brownfield Points',
        'sort_key': lambda n: (1 if n['factors']['f8_has_fuel'] else 0, -n['factors']['f8_fuel_dist_km']),
        'reverse': True
    },
    {
        'id': 'f9_dhaba_amenity',
        'name': 'Commercial Amenities & Dhabas',
        'sort_key': lambda n: (1 if n['factors']['f9_has_dhaba'] else 0, -n['factors']['f9_dhaba_dist_km']),
        'reverse': True
    }
]

def evaluate_chosen_network(chosen_nodes, all_nodes, total_corridor_len_km):
    """
    Evaluates a proposed set of K stations across the Triad Dimensions:
    1. M_service: Coverage % satisfying <= 25km MoP spacing
    2. M_demand: Captured traffic and EV fleet pressure
    3. M_readiness: Proximity to 11kV substation (within 5 km CEA norm) and brownfield match
    """
    if not chosen_nodes:
        return 0.0, 0.0, 0.0, 0.0
        
    k = len(chosen_nodes)
    chosen_kms = sorted([n['km_mark'] for n in chosen_nodes])
    
    # 1. SERVICE EFFECTIVENESS (M_service)
    # Check inter-station intervals along the corridor
    intervals = []
    # Start of corridor to first charger
    intervals.append(chosen_kms[0])
    # Between chargers
    for i in range(len(chosen_kms) - 1):
        intervals.append(chosen_kms[i+1] - chosen_kms[i])
    # Last charger to end of corridor
    intervals.append(total_corridor_len_km - chosen_kms[-1])
    
    # Statutory MoP Benchmark: <= 25 km
    compliant_intervals = sum(1 for d in intervals if d <= 25.0)
    service_coverage_ratio = compliant_intervals / float(len(intervals))
    
    # Penalty for severe deserts (> 75 km)
    severe_deserts = sum(1 for d in intervals if d > 75.0)
    severe_penalty = max(0.0, 1.0 - (severe_deserts * 0.25))
    m_service = round(service_coverage_ratio * severe_penalty, 4)
    
    # 2. DEMAND ALIGNMENT (M_demand)
    # Average traffic PCU captured + VAHAN EV fleet
    traffic_vals = [n['factors']['f3_traffic_pcu'] for n in chosen_nodes]
    ev_vals = [n['factors']['f2_ev_fleet_norm'] for n in chosen_nodes]
    
    # Normalizing traffic against max observable ~ 60,000 PCU
    norm_traffic = np.mean(traffic_vals) / 45000.0
    norm_traffic = min(1.0, max(0.1, norm_traffic))
    norm_ev = min(1.0, max(0.1, np.mean(ev_vals)))
    m_demand = round(0.55 * norm_traffic + 0.45 * norm_ev, 4)
    
    # 3. INFRASTRUCTURE & GRID READINESS (M_readiness)
    # Substation proximity (CEA 5 km limit)
    sub_dists = [n['factors']['f7_substation_dist_km'] for n in chosen_nodes]
    # Score 1.0 if <= 1.5 km, drops to 0.0 at 10 km
    sub_scores = [max(0.0, 1.0 - (d / 10.0)) if d <= 10.0 else 0.0 for d in sub_dists]
    avg_sub_score = np.mean(sub_scores)
    
    # Brownfield match (has petrol pump or commercial dhaba)
    brownfield_count = sum(1 for n in chosen_nodes if n['factors']['f8_has_fuel'] or n['factors']['f9_has_dhaba'])
    brownfield_ratio = brownfield_count / float(k)
    m_readiness = round(0.60 * avg_sub_score + 0.40 * brownfield_ratio, 4)
    
    # TRIAD GEOMETRIC MEAN: S_i = (M_service * M_demand * M_readiness)^(1/3)
    # Using small epsilon to prevent zero collapse
    eps = 0.001
    s_i = round(float((max(eps, m_service) * max(eps, m_demand) * max(eps, m_readiness)) ** (1.0 / 3.0)), 4)
    
    return s_i, m_service, m_demand, m_readiness

print("\nRunning Factor Sensitivity Tournament across 250 corridor test cases...")

results = {}
for factor in FACTORS:
    f_id = factor['id']
    f_name = factor['name']
    
    scores = []
    m_services = []
    m_demands = []
    m_readinesses = []
    
    for tc in test_cases:
        k = tc['target_station_quota_k']
        nodes = tc['candidate_nodes']
        total_len = tc['total_corridor_len_km']
        
        # Factor sorts nodes strictly by its own metric
        sorted_nodes = sorted(nodes, key=factor['sort_key'], reverse=factor['reverse'])
        chosen_nodes = sorted_nodes[:k]
        
        # Evaluate on unbiased Triad Metric
        s_i, m_s, m_d, m_r = evaluate_chosen_network(chosen_nodes, nodes, total_len)
        scores.append(s_i)
        m_services.append(m_s)
        m_demands.append(m_d)
        m_readinesses.append(m_r)
        
    avg_s = float(np.mean(scores))
    std_s = float(np.std(scores))
    avg_ms = float(np.mean(m_services))
    avg_md = float(np.mean(m_demands))
    avg_mr = float(np.mean(m_readinesses))
    
    results[f_id] = {
        'factor_id': f_id,
        'factor_name': f_name,
        'mean_triad_score': round(avg_s, 4),
        'score_std': round(std_s, 4),
        'mean_service_ms': round(avg_ms, 4),
        'mean_demand_md': round(avg_md, 4),
        'mean_readiness_mr': round(avg_mr, 4)
    }

# Compute Normalized Objective Weights
total_score_sum = sum(v['mean_triad_score'] for v in results.values())
for f_id in results:
    w_i = results[f_id]['mean_triad_score'] / total_score_sum
    results[f_id]['derived_weight'] = round(w_i, 4)
    results[f_id]['derived_weight_pct'] = f"{round(w_i * 100, 1)}%"

# Sort by derived weight descending
sorted_factors = sorted(results.values(), key=lambda x: x['derived_weight'], reverse=True)

print("\n" + "=" * 90)
print(f"{'RANK':<5} | {'FACTOR NAME':<38} | {'SERVICE':<8} | {'DEMAND':<8} | {'GRID/READY':<10} | {'WEIGHT':<8}")
print("-" * 90)
for rank, f_data in enumerate(sorted_factors, 1):
    print(f"#{rank:<4} | {f_data['factor_name']:<38} | {f_data['mean_service_ms']*100:>6.1f}% | {f_data['mean_demand_md']*100:>6.1f}% | {f_data['mean_readiness_mr']*100:>8.1f}% | {f_data['derived_weight_pct']:>7}")
print("=" * 90)

# Save Tournament Results
tournament_output = {
    'total_test_cases_evaluated': len(test_cases),
    'evaluation_metric': 'Triad Network Health Index (Geometric Mean: M_service * M_demand * M_readiness)^(1/3)',
    'ranked_factors': sorted_factors,
    'raw_factor_data': results
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(tournament_output, f, indent=2)

print(f"\n✓ Saved Stage 1 Factor Tournament Results to: {OUTPUT_PATH}")
print("=" * 80)
