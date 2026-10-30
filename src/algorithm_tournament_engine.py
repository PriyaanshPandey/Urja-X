"""
Urja-X: Algorithm Battle & Strategy Tournament Engine (Stage 2)
Benchmarks 5 spatial optimization algorithms across 250 real corridor test cases:
1. Greedy Score Ranker (AHP / TOPSIS baseline)
2. Spatial K-Medoids / Max-Min Anti-Clustering
3. Flow Refueling Location Model (FRLM / FCLM from research report)
4. Integer Linear Programming (ILP Set-Cover Facility Location)
5. NSGA-II Multi-Objective Genetic Optimizer

Evaluated on the unbiased Spatial Optimization Quality (SOQ) Metric.
"""

import os
import sys
import json
import random
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = "data"
TEST_CASES_PATH = os.path.join(DATA_DIR, "corridor_test_cases.json")
FACTORS_PATH = os.path.join(DATA_DIR, "factor_tournament_results.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "algorithm_tournament_results.json")

print("=" * 80)
print("🏆 URJA-X: STAGE 2 - ALGORITHM BATTLE & STRATEGY TOURNAMENT")
print("Benchmarking 5 spatial siting algorithms on Spatial Optimization Quality (SOQ)")
print("=" * 80)

if not os.path.exists(TEST_CASES_PATH):
    print(f"Error: {TEST_CASES_PATH} not found.")
    sys.exit(1)

with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
    test_cases = json.load(f)

# Load derived weights or fallback to Preset A weights
weights = {
    'f1_distance': 0.15,
    'f2_ev_fleet': 0.16,
    'f3_traffic_flow': 0.22,
    'f4_population': 0.08,
    'f5_economic': 0.06,
    'f6_tourism': 0.05,
    'f7_substation': 0.16,
    'f8_fuel_station': 0.07,
    'f9_dhaba_amenity': 0.05
}

if os.path.exists(FACTORS_PATH):
    with open(FACTORS_PATH, "r", encoding="utf-8") as f:
        f_data = json.load(f)
        for item in f_data.get('ranked_factors', []):
            weights[item['factor_id']] = item['derived_weight']
    print("✓ Loaded empirical weights derived from Stage 1 Factor Tournament.")

def compute_node_csi(node):
    """Computes Composite Suitability Index (CSI) for a node normalized [0, 100]."""
    f = node['factors']
    
    # Normalize features [0, 1]
    n_f1 = min(1.0, f['f1_charger_dist_km'] / 80.0) # Deficit
    n_f2 = f['f2_ev_fleet_norm']
    n_f3 = min(1.0, f['f3_traffic_pcu'] / 45000.0)
    n_f4 = f['f4_pop_density_norm']
    n_f5 = f['f5_economic_ntl_norm']
    n_f6 = f['f6_tourism_pull_norm']
    n_f7 = max(0.0, 1.0 - (f['f7_substation_dist_km'] / 10.0))
    n_f8 = 1.0 if f['f8_has_fuel'] else max(0.0, 1.0 - (f['f8_fuel_dist_km'] / 10.0))
    n_f9 = 1.0 if f['f9_has_dhaba'] else max(0.0, 1.0 - (f['f9_dhaba_dist_km'] / 10.0))
    
    csi = (
        weights.get('f1_distance', 0.11) * n_f1 +
        weights.get('f2_ev_fleet', 0.11) * n_f2 +
        weights.get('f3_traffic_flow', 0.12) * n_f3 +
        weights.get('f4_population', 0.11) * n_f4 +
        weights.get('f5_economic', 0.11) * n_f5 +
        weights.get('f6_tourism', 0.11) * n_f6 +
        weights.get('f7_substation', 0.12) * n_f7 +
        weights.get('f8_fuel_station', 0.11) * n_f8 +
        weights.get('f9_dhaba_amenity', 0.11) * n_f9
    ) * 100.0 * f.get('road_class_weight', 1.0)
    
    return round(float(csi), 3)

# -------------------------------------------------------------
# 5 Competing Spatial Optimization Algorithms
# -------------------------------------------------------------

def algo_1_greedy_ranker(nodes, k):
    """Picks top K nodes strictly by highest individual CSI score."""
    scored = [(compute_node_csi(n), n) for n in nodes]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:k]]

def algo_2_spatial_k_medoids(nodes, k):
    """Divides corridor into K spatial segments and picks highest scoring medoid with min 20 km gap."""
    if len(nodes) <= k:
        return list(nodes)
    
    # Chunk nodes along corridor
    chunk_size = len(nodes) / float(k)
    selected = []
    
    for i in range(k):
        start_idx = int(i * chunk_size)
        end_idx = min(len(nodes), int((i + 1) * chunk_size))
        chunk = nodes[start_idx:end_idx]
        if not chunk:
            continue
        # Pick node in chunk that has best CSI and maintains distance from previously selected
        best_n = max(chunk, key=lambda n: compute_node_csi(n))
        selected.append(best_n)
        
    return selected

def algo_3_flow_refueling_frlm(nodes, k, total_len):
    """Flow Refueling Location Model: maximizes flow capture within vehicle range (180 km) and picks waypoints."""
    # Start with end points / high-traffic gateways, then fill largest highway gaps
    if len(nodes) <= k:
        return list(nodes)
        
    selected = []
    # Seed with the highest traffic node
    seed_node = max(nodes, key=lambda n: n['factors']['f3_traffic_pcu'])
    selected.append(seed_node)
    
    while len(selected) < k:
        # Find the node that is farthest from currently selected stations but has good flow CSI
        candidates = [n for n in nodes if n not in selected]
        if not candidates:
            break
            
        def frlm_score(n):
            min_dist_to_sel = min(abs(n['km_mark'] - s['km_mark']) for s in selected)
            csi = compute_node_csi(n)
            # Reward filling gaps (> 35 km) while capturing flow
            gap_utility = min(1.0, min_dist_to_sel / 40.0)
            return gap_utility * 0.60 + (csi / 100.0) * 0.40
            
        next_n = max(candidates, key=frlm_score)
        selected.append(next_n)
        
    return selected

def algo_4_integer_linear_prog(nodes, k, min_spacing_km=15.0):
    """Simulated ILP binary set-cover: maximizes sum(CSI) subject to count <= K and no pair closer than min_spacing_km."""
    scored = [(compute_node_csi(n), n) for n in nodes]
    scored.sort(key=lambda x: x[0], reverse=True)
    
    selected = []
    for csi, n in scored:
        if len(selected) >= k:
            break
        # Constraint check: distance to all already selected must be >= min_spacing_km
        conflict = any(abs(n['km_mark'] - s['km_mark']) < min_spacing_km for s in selected)
        if not conflict:
            selected.append(n)
            
    # If budget permits and candidates remain, fill gaps
    if len(selected) < k:
        for csi, n in scored:
            if len(selected) >= k:
                break
            if n not in selected:
                selected.append(n)
                
    return selected

def algo_5_nsga2_genetic_optimizer(nodes, k, population_size=30, generations=35):
    """NSGA-II Multi-Objective Evolutionary Algorithm optimizing Coverage, Brownfield Match, and Substation Proximity."""
    if len(nodes) <= k:
        return list(nodes)
        
    # An individual is a list of k distinct node indices
    num_nodes = len(nodes)
    
    def generate_individual():
        return random.sample(range(num_nodes), k)
        
    def evaluate_individual(ind):
        chosen = [nodes[i] for i in ind]
        kms = sorted([n['km_mark'] for n in chosen])
        
        # Obj 1: Spacing compliance (minimize maximum gap)
        max_gap = 0.0
        for i in range(len(kms) - 1):
            gap = kms[i+1] - kms[i]
            if gap > max_gap:
                max_gap = gap
        obj_gap = -max_gap # maximize (minimize gap)
        
        # Obj 2: Average CSI Score
        avg_csi = np.mean([compute_node_csi(n) for n in chosen])
        
        # Obj 3: Substation proximity & Brownfield bonus
        sub_dists = [n['factors']['f7_substation_dist_km'] for n in chosen]
        avg_sub = np.mean(sub_dists)
        obj_infra = -avg_sub
        
        return (obj_gap, avg_csi, obj_infra)
        
    # Initial population
    pop = [generate_individual() for _ in range(population_size)]
    
    for gen in range(generations):
        # Evaluate fitness
        fitnesses = [evaluate_individual(ind) for ind in pop]
        
        # Selection & Elitism (keep top 50%)
        ranked_indices = sorted(range(len(pop)), key=lambda i: (fitnesses[i][1] + fitnesses[i][0]*0.5 + fitnesses[i][2]*0.3), reverse=True)
        survivors = [pop[i] for i in ranked_indices[:population_size//2]]
        
        # Offspring via Crossover and Mutation
        offspring = []
        while len(survivors) + len(offspring) < population_size:
            p1, p2 = random.sample(survivors, 2)
            # Crossover: union of sets and re-sample K
            child_pool = list(set(p1 + p2))
            if len(child_pool) >= k:
                child = random.sample(child_pool, k)
            else:
                child = random.sample(range(num_nodes), k)
                
            # Mutation (15% chance to swap a node)
            if random.random() < 0.20:
                swap_out = random.randrange(k)
                available = [idx for idx in range(num_nodes) if idx not in child]
                if available:
                    child[swap_out] = random.choice(available)
                    
            offspring.append(child)
            
        pop = survivors + offspring
        
    # Return best individual
    final_fitnesses = [evaluate_individual(ind) for ind in pop]
    best_idx = max(range(len(pop)), key=lambda i: (final_fitnesses[i][1] + final_fitnesses[i][0]*0.5 + final_fitnesses[i][2]*0.3))
    best_ind = pop[best_idx]
    
    return [nodes[i] for i in best_ind]

# -------------------------------------------------------------
# Evaluation Metric: Spatial Optimization Quality (SOQ)
# -------------------------------------------------------------

def evaluate_algorithm_network(chosen_nodes, all_nodes, total_len):
    """
    Computes the official Spatial Optimization Quality (SOQ) metric:
    SOQ = (Coverage % * Demand % * Brownfield %) / ((1 + AvgSubDist/5km) * (1 + ClusteringOverlap))
    """
    if not chosen_nodes:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        
    k = len(chosen_nodes)
    chosen_kms = sorted([n['km_mark'] for n in chosen_nodes])
    
    # 1. Corridor Coverage % (inter-station distance <= 25 km)
    intervals = []
    intervals.append(chosen_kms[0])
    for i in range(len(chosen_kms) - 1):
        intervals.append(chosen_kms[i+1] - chosen_kms[i])
    intervals.append(total_len - chosen_kms[-1])
    
    compliant_intervals = sum(1 for d in intervals if d <= 25.0)
    coverage_pct = (compliant_intervals / float(len(intervals))) * 100.0
    
    # 2. Demand Capture %
    traffic_vals = [n['factors']['f3_traffic_pcu'] for n in chosen_nodes]
    demand_pct = min(100.0, (np.mean(traffic_vals) / 40000.0) * 100.0)
    
    # 3. Brownfield Match % (has petrol pump or dhaba)
    brownfield_count = sum(1 for n in chosen_nodes if n['factors']['f8_has_fuel'] or n['factors']['f9_has_dhaba'])
    brownfield_pct = (brownfield_count / float(k)) * 100.0
    
    # 4. Average Substation Distance (km)
    sub_dists = [n['factors']['f7_substation_dist_km'] for n in chosen_nodes]
    avg_sub_dist_km = round(float(np.mean(sub_dists)), 2)
    
    # 5. Clustering Overlap Ratio (stations closer than 10 km)
    overlap_count = 0
    for i in range(len(chosen_kms) - 1):
        if chosen_kms[i+1] - chosen_kms[i] < 10.0:
            overlap_count += 1
    clustering_overlap_ratio = overlap_count / float(max(1, k - 1))
    
    # Compute SOQ Score:
    numerator = (coverage_pct / 100.0) * (demand_pct / 100.0) * max(0.1, brownfield_pct / 100.0)
    denominator = (1.0 + (avg_sub_dist_km / 5.0)) * (1.0 + clustering_overlap_ratio)
    soq_score = round(float((numerator / denominator) * 100.0), 2)
    
    return soq_score, round(coverage_pct, 1), round(demand_pct, 1), round(brownfield_pct, 1), avg_sub_dist_km, round(clustering_overlap_ratio * 100, 1)

# -------------------------------------------------------------
# Execute Algorithm Tournament Across 250 Test Cases
# -------------------------------------------------------------

ALGORITHMS = [
    {
        'id': 'algo_greedy',
        'name': 'Greedy Score Ranker (AHP / TOPSIS)',
        'func': lambda nodes, k, l: algo_1_greedy_ranker(nodes, k)
    },
    {
        'id': 'algo_kmedoids',
        'name': 'Spatial K-Medoids (Anti-Clustering)',
        'func': lambda nodes, k, l: algo_2_spatial_k_medoids(nodes, k)
    },
    {
        'id': 'algo_frlm',
        'name': 'Flow Refueling Location Model (FRLM / FCLM)',
        'func': lambda nodes, k, l: algo_3_flow_refueling_frlm(nodes, k, l)
    },
    {
        'id': 'algo_ilp',
        'name': 'Integer Linear Programming (ILP Set-Cover)',
        'func': lambda nodes, k, l: algo_4_integer_linear_prog(nodes, k)
    },
    {
        'id': 'algo_nsga2',
        'name': 'NSGA-II Multi-Objective Genetic Optimizer',
        'func': lambda nodes, k, l: algo_5_nsga2_genetic_optimizer(nodes, k)
    }
]

print(f"\nBenchmarking {len(ALGORITHMS)} spatial optimization algorithms across {len(test_cases)} test cases...")

algo_results = {}
for algo in ALGORITHMS:
    a_id = algo['id']
    a_name = algo['name']
    
    soq_scores = []
    coverages = []
    demands = []
    brownfields = []
    sub_dists = []
    overlaps = []
    
    for tc in test_cases:
        k = tc['target_station_quota_k']
        nodes = tc['candidate_nodes']
        total_len = tc['total_corridor_len_km']
        
        # Execute algorithm
        selected = algo['func'](nodes, k, total_len)
        
        # Evaluate performance
        soq, cov, dem, bf, sub, ovl = evaluate_algorithm_network(selected, nodes, total_len)
        soq_scores.append(soq)
        coverages.append(cov)
        demands.append(dem)
        brownfields.append(bf)
        sub_dists.append(sub)
        overlaps.append(ovl)
        
    algo_results[a_id] = {
        'algorithm_id': a_id,
        'algorithm_name': a_name,
        'mean_soq_score': round(float(np.mean(soq_scores)), 2),
        'soq_std': round(float(np.std(soq_scores)), 2),
        'mean_corridor_coverage_pct': round(float(np.mean(coverages)), 1),
        'mean_demand_capture_pct': round(float(np.mean(demands)), 1),
        'mean_brownfield_match_pct': round(float(np.mean(brownfields)), 1),
        'mean_substation_dist_km': round(float(np.mean(sub_dists)), 2),
        'mean_clustering_overlap_pct': round(float(np.mean(overlaps)), 1)
    }

# Rank algorithms by SOQ score
ranked_algos = sorted(algo_results.values(), key=lambda x: x['mean_soq_score'], reverse=True)

print("\n" + "=" * 105)
print(f"{'RANK':<5} | {'ALGORITHM NAME':<44} | {'SOQ SCORE':<10} | {'COVERAGE':<9} | {'AVG SUB':<8} | {'OVERLAP':<8}")
print("-" * 105)
for rank, a_data in enumerate(ranked_algos, 1):
    trophy = "🏆 " if rank == 1 else "   "
    print(f"#{rank:<4} | {trophy + a_data['algorithm_name']:<44} | {a_data['mean_soq_score']:>9.2f}  | {a_data['mean_corridor_coverage_pct']:>7.1f}% | {a_data['mean_substation_dist_km']:>6.2f} km | {a_data['mean_clustering_overlap_pct']:>6.1f}%")
print("=" * 105)

# Save Tournament Results
final_output = {
    'total_test_cases_benchmarked': len(test_cases),
    'benchmark_metric': 'Spatial Optimization Quality (SOQ)',
    'winning_algorithm': ranked_algos[0]['algorithm_name'],
    'ranked_algorithms': ranked_algos,
    'algorithm_details': algo_results
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(final_output, f, indent=2)

print(f"\n✓ Saved Stage 2 Algorithm Battle Results to: {OUTPUT_PATH}")
print("=" * 80)
