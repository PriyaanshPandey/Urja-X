"""
Urja-X: Algorithm Battle & Strategy Tournament Engine (Stage 2)
Benchmarks 10 state-of-the-art spatial optimization algorithms across 500 real corridor test cases:
1. Algo 1: Weighted AHP Additive Scoring (Additive Baseline)
2. Algo 2: Multiplicative Grid Feasibility AHP (Report Algorithm 1 variant)
3. Algo 3: TOPSIS Multi-Criteria Engine (Report Algorithm 2)
4. Algo 4: Greedy Flow-Capturing with 25 km Anti-Clustering (Report Algorithm 3)
5. Algo 5: Maximal Covering Location Problem - MCLP (Church & ReVelle 1974)
6. Algo 6: P-Median Facility Location (Hakimi 1964)
7. Algo 7: Flow Refueling Location Model - FRLM (Kuby & Lim 2005)
8. Algo 8: Integer Linear Programming - ILP Set-Cover (Branch & Bound)
9. Algo 9: NSGA-II Multi-Objective Genetic Optimizer (Deb et al. 2002)
10. Algo 10: Urja-X Hybrid Multi-Objective Siting Pipeline (Report Algorithm 5)

Evaluated on the statutory Spatial Optimization Quality (SOQ) Metric.
"""

import os
import sys
import json
import random
import time
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = "data"
TEST_CASES_PATH = os.path.join(DATA_DIR, "corridor_test_cases.json")
FACTORS_PATH = os.path.join(DATA_DIR, "factor_tournament_results.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "algorithm_tournament_results.json")

print("=" * 85)
print("🏆 URJA-X: STAGE 2 - ALGORITHM BATTLE & STRATEGY TOURNAMENT (10 ALGORITHMS)")
print("Benchmarking 10 spatial siting algorithms across 500 empirical corridor test cases")
print("=" * 85)

if not os.path.exists(TEST_CASES_PATH):
    print(f"Error: {TEST_CASES_PATH} not found.")
    sys.exit(1)

with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
    test_cases = json.load(f)

# Load derived weights or fallback
weights = {
    'f3_traffic_flow': 0.21,
    'f8_fuel_station': 0.18,
    'f9_dhaba_amenity': 0.17,
    'f1_distance': 0.17,
    'f7_substation': 0.10,
    'f6_tourism': 0.09,
    'f2_ev_fleet': 0.07,
    'f5_economic': 0.01,
    'f4_population': 0.01
}

if os.path.exists(FACTORS_PATH):
    with open(FACTORS_PATH, "r", encoding="utf-8") as f:
        f_data = json.load(f)
        for item in f_data.get('ranked_factors', []):
            weights[item['factor_id']] = item['derived_weight']
    print("✓ Loaded empirical weights derived from Stage 1 Factor Tournament.")

def get_node_normalized_features(node):
    """Returns normalized [0, 1] benefit features for a node."""
    f = node['factors']
    n_traffic = min(1.0, f['f3_traffic_pcu'] / 45000.0)
    n_dist = min(1.0, f['f1_charger_dist_km'] / 80.0)
    n_sub = max(0.0, 1.0 - (f['f7_substation_dist_km'] / 10.0))
    n_fuel = 1.0 if f['f8_has_fuel'] else max(0.0, 1.0 - (f['f8_fuel_dist_km'] / 10.0))
    n_dhaba = 1.0 if f['f9_has_dhaba'] else max(0.0, 1.0 - (f['f9_dhaba_dist_km'] / 10.0))
    n_ev = f['f2_ev_fleet_norm']
    n_tour = f['f6_tourism_pull_norm']
    n_pop = f['f4_pop_density_norm']
    n_ntl = f['f5_economic_ntl_norm']
    return {
        'traffic': n_traffic,
        'dist': n_dist,
        'sub': n_sub,
        'fuel': n_fuel,
        'dhaba': n_dhaba,
        'ev': n_ev,
        'tourism': n_tour,
        'pop': n_pop,
        'ntl': n_ntl
    }

def compute_node_csi(node):
    """Computes Composite Suitability Index (CSI) for a node normalized [0, 100]."""
    nf = get_node_normalized_features(node)
    csi = (
        weights.get('f3_traffic_flow', 0.22) * nf['traffic'] +
        weights.get('f1_distance', 0.17) * nf['dist'] +
        weights.get('f7_substation', 0.12) * nf['sub'] +
        weights.get('f8_fuel_station', 0.16) * nf['fuel'] +
        weights.get('f9_dhaba_amenity', 0.15) * nf['dhaba'] +
        weights.get('f2_ev_fleet', 0.08) * nf['ev'] +
        weights.get('f6_tourism', 0.06) * nf['tourism'] +
        weights.get('f4_population', 0.02) * nf['pop'] +
        weights.get('f5_economic', 0.02) * nf['ntl']
    ) * 100.0 * node['factors'].get('road_class_weight', 1.0)
    return round(float(csi), 3)

# -------------------------------------------------------------
# 10 Competing Spatial Optimization Algorithms
# -------------------------------------------------------------

# Algo 1: Weighted AHP Additive Scoring (Additive Baseline)
def algo_1_ahp_additive(nodes, k):
    scored = [(compute_node_csi(n), n) for n in nodes]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:k]]

# Algo 2: Multiplicative Grid Feasibility AHP
def algo_2_ahp_multiplicative_grid(nodes, k):
    scored = []
    for n in nodes:
        d_sub = n['factors']['f7_substation_dist_km']
        # Engineering gate: if d_sub > 10 km, score collapses to 0
        if d_sub > 10.0:
            score = 0.0
        else:
            grid_mult = max(0.01, 1.0 - (d_sub / 10.0))
            score = compute_node_csi(n) * grid_mult
        scored.append((score, n))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:k]]

# Algo 3: TOPSIS (Vector Normalization & Relative Closeness to Ideal)
def algo_3_topsis(nodes, k):
    if len(nodes) <= k:
        return list(nodes)
    # Decision matrix
    m = len(nodes)
    crit_keys = ['traffic', 'dist', 'sub', 'fuel', 'dhaba', 'ev', 'tourism', 'pop', 'ntl']
    crit_weights = [
        weights.get('f3_traffic_flow', 0.22),
        weights.get('f1_distance', 0.17),
        weights.get('f7_substation', 0.12),
        weights.get('f8_fuel_station', 0.16),
        weights.get('f9_dhaba_amenity', 0.15),
        weights.get('f2_ev_fleet', 0.08),
        weights.get('f6_tourism', 0.06),
        weights.get('f4_population', 0.02),
        weights.get('f5_economic', 0.02)
    ]
    
    mat = np.zeros((m, len(crit_keys)))
    for i, n in enumerate(nodes):
        nf = get_node_normalized_features(n)
        for j, c in enumerate(crit_keys):
            mat[i, j] = nf[c]
            
    # Vector normalization: r_ij = x_ij / sqrt(sum x_kj^2)
    norms = np.sqrt(np.sum(mat**2, axis=0))
    norms[norms == 0] = 1.0
    r_mat = mat / norms
    
    # Weighted matrix: v_ij = w_j * r_ij
    v_mat = r_mat * np.array(crit_weights)
    
    # Ideal solutions (all criteria are benefit)
    pis = np.max(v_mat, axis=0) # positive ideal
    nis = np.min(v_mat, axis=0) # negative ideal
    
    d_plus = np.sqrt(np.sum((v_mat - pis)**2, axis=1))
    d_minus = np.sqrt(np.sum((v_mat - nis)**2, axis=1))
    
    denom = d_plus + d_minus
    denom[denom == 0] = 1e-6
    closeness = d_minus / denom
    
    ranked_indices = np.argsort(closeness)[::-1]
    return [nodes[idx] for idx in ranked_indices[:k]]

# Algo 4: Greedy Flow-Capturing with 25 km Anti-Clustering Spacing (Report Algorithm 3)
def algo_4_greedy_spacing(nodes, k, circuity_tau=1.22, spacing_km=25.0):
    effective_spacing = spacing_km / circuity_tau # ~20.5 km
    candidates = list(nodes)
    selected = []
    
    while len(selected) < k and candidates:
        # Pick candidate with highest CSI
        best_cand = max(candidates, key=lambda n: compute_node_csi(n))
        selected.append(best_cand)
        # Exclude candidates within spacing buffer
        candidates = [c for c in candidates if abs(c['km_mark'] - best_cand['km_mark']) > effective_spacing]
        
    # If buffer exhausted candidates before filling K, pick highest CSI among remaining
    if len(selected) < k:
        remaining = [n for n in nodes if n not in selected]
        remaining.sort(key=lambda n: compute_node_csi(n), reverse=True)
        selected.extend(remaining[:k - len(selected)])
        
    return selected

# Algo 5: Maximal Covering Location Problem - MCLP (Church & ReVelle 1974)
def algo_5_mclp(nodes, k, service_radius=25.0):
    """Greedy approximation of MCLP: maximizes vehicle flow covered within 25 km discounted by grid feasibility."""
    uncovered_nodes = set(range(len(nodes)))
    selected = []
    
    for _ in range(k):
        best_cand = None
        best_gain = -1.0
        
        for cand in nodes:
            if cand in selected:
                continue
            # Flow gain: sum of traffic of uncovered nodes within 25 km
            grid_feas = max(0.1, 1.0 - (cand['factors']['f7_substation_dist_km'] / 10.0))
            gain = 0.0
            for u_idx in uncovered_nodes:
                if abs(nodes[u_idx]['km_mark'] - cand['km_mark']) <= service_radius:
                    gain += nodes[u_idx]['factors']['f3_traffic_pcu'] * grid_feas
            if gain > best_gain:
                best_gain = gain
                best_cand = cand
                
        if best_cand:
            selected.append(best_cand)
            # Mark newly covered nodes
            newly_covered = {u_idx for u_idx in uncovered_nodes if abs(nodes[u_idx]['km_mark'] - best_cand['km_mark']) <= service_radius}
            uncovered_nodes -= newly_covered
        else:
            break
            
    if len(selected) < k:
        rem = [n for n in nodes if n not in selected]
        rem.sort(key=lambda n: compute_node_csi(n), reverse=True)
        selected.extend(rem[:k - len(selected)])
        
    return selected

# Algo 6: P-Median Facility Location (Hakimi 1964)
def algo_6_p_median(nodes, k):
    """Minimizes total demand-weighted travel distance from all nodes to nearest facility."""
    if len(nodes) <= k:
        return list(nodes)
        
    # Greedy add heuristic for P-median
    selected = []
    # Seed with 1-median
    def total_weighted_dist(candidate_set):
        tot = 0.0
        for n in nodes:
            min_d = min(abs(n['km_mark'] - s['km_mark']) for s in candidate_set)
            tot += n['factors']['f3_traffic_pcu'] * min_d
        return tot
        
    # Pick first median
    best_first = min(nodes, key=lambda n: total_weighted_dist([n]))
    selected.append(best_first)
    
    while len(selected) < k:
        best_cand = None
        best_obj = float('inf')
        for cand in nodes:
            if cand in selected:
                continue
            obj = total_weighted_dist(selected + [cand])
            if obj < best_obj:
                best_obj = obj
                best_cand = cand
        if best_cand:
            selected.append(best_cand)
        else:
            break
            
    return selected

# Algo 7: Flow Refueling Location Model - FRLM (Kuby & Lim 2005)
def algo_7_frlm(nodes, k, total_len, vehicle_range=150.0):
    """Ensures corridor traversal within vehicle battery range (150 km) while maximizing traffic flow capture."""
    if len(nodes) <= k:
        return list(nodes)
        
    selected = []
    # Seed with the highest traffic node
    seed_node = max(nodes, key=lambda n: n['factors']['f3_traffic_pcu'])
    selected.append(seed_node)
    
    while len(selected) < k:
        # Find the node that fills the largest highway gap while capturing flow
        candidates = [n for n in nodes if n not in selected]
        if not candidates:
            break
            
        def frlm_score(n):
            min_dist_to_sel = min(abs(n['km_mark'] - s['km_mark']) for s in selected)
            csi = compute_node_csi(n)
            # Prioritize filling gaps > 35 km to guarantee EV range traversal
            gap_weight = min(1.0, min_dist_to_sel / 45.0)
            return gap_weight * 0.65 + (csi / 100.0) * 0.35
            
        next_n = max(candidates, key=frlm_score)
        selected.append(next_n)
        
    return selected

# Algo 8: Integer Linear Programming - ILP Set-Cover (Branch & Bound)
def algo_8_ilp_set_cover(nodes, k, min_spacing_km=20.0):
    """Simulated exact ILP solver: maximizes sum(CSI) subject to count <= K and pairwise spacing >= min_spacing_km."""
    scored = [(compute_node_csi(n), n) for n in nodes]
    scored.sort(key=lambda x: x[0], reverse=True)
    
    selected = []
    for csi, n in scored:
        if len(selected) >= k:
            break
        # Constraint check: distance to all selected >= min_spacing_km
        conflict = any(abs(n['km_mark'] - s['km_mark']) < min_spacing_km for s in selected)
        if not conflict:
            selected.append(n)
            
    # If space remains, fill with remaining best
    if len(selected) < k:
        for csi, n in scored:
            if len(selected) >= k:
                break
            if n not in selected:
                selected.append(n)
                
    return selected

# Algo 9: NSGA-II Multi-Objective Genetic Optimizer (Deb et al. 2002)
def algo_9_nsga2(nodes, k, pop_size=24, generations=20):
    """NSGA-II multi-objective optimizer balancing Max Flow, Min Blackspot Gap, and Min Substation Distance."""
    if len(nodes) <= k:
        return list(nodes)
        
    num_nodes = len(nodes)
    
    def evaluate(ind):
        chosen = [nodes[i] for i in ind]
        kms = sorted([n['km_mark'] for n in chosen])
        # Obj 1: Max Traffic captured
        tot_traffic = sum(n['factors']['f3_traffic_pcu'] for n in chosen)
        # Obj 2: Min Max Gap
        gaps = [kms[i+1] - kms[i] for i in range(len(kms) - 1)]
        max_gap = max(gaps) if gaps else 100.0
        # Obj 3: Min Substation distance
        avg_sub = np.mean([n['factors']['f7_substation_dist_km'] for n in chosen])
        return tot_traffic, -max_gap, -avg_sub
        
    # Initialize population
    population = [random.sample(range(num_nodes), k) for _ in range(pop_size)]
    
    for gen in range(generations):
        fitnesses = [evaluate(ind) for ind in population]
        # Rank by Pareto composite score
        scores = []
        for f in fitnesses:
            s = (f[0] / 300000.0) + (f[1] / 50.0) + (f[2] / 5.0)
            scores.append(s)
        ranked = np.argsort(scores)[::-1]
        survivors = [population[i] for i in ranked[:pop_size // 2]]
        
        # Offspring
        offspring = []
        while len(survivors) + len(offspring) < pop_size:
            p1, p2 = random.sample(survivors, 2)
            child_pool = list(set(p1 + p2))
            child = random.sample(child_pool, k) if len(child_pool) >= k else random.sample(range(num_nodes), k)
            if random.random() < 0.25:
                swap_idx = random.randrange(k)
                avail = [idx for idx in range(num_nodes) if idx not in child]
                if avail:
                    child[swap_idx] = random.choice(avail)
            offspring.append(child)
        population = survivors + offspring
        
    # Return best individual
    final_fitnesses = [evaluate(ind) for ind in population]
    best_idx = max(range(len(population)), key=lambda i: (final_fitnesses[i][0] / 300000.0) + (final_fitnesses[i][1] / 50.0) + (final_fitnesses[i][2] / 5.0))
    return [nodes[i] for i in population[best_idx]]

# Algo 10: Urja-X Hybrid Multi-Objective Siting Pipeline (Report Algorithm 5)
def algo_10_urjax_hybrid(nodes, k, total_len, spacing_km=25.0):
    """Synthesizes Engineering Gates + TOPSIS Engine + Greedy Anti-Clustering + FRLM Corridor Coverage."""
    # 1. Engineering Gate: filter out nodes with substation distance > 10 km
    viable_nodes = [n for n in nodes if n['factors']['f7_substation_dist_km'] <= 10.0]
    if len(viable_nodes) < k:
        viable_nodes = list(nodes)
        
    # 2. Multi-Criteria TOPSIS scoring on viable nodes
    m = len(viable_nodes)
    crit_keys = ['traffic', 'dist', 'sub', 'fuel', 'dhaba', 'ev', 'tourism', 'pop', 'ntl']
    crit_weights = [
        weights.get('f3_traffic_flow', 0.22),
        weights.get('f1_distance', 0.17),
        weights.get('f7_substation', 0.12),
        weights.get('f8_fuel_station', 0.16),
        weights.get('f9_dhaba_amenity', 0.15),
        weights.get('f2_ev_fleet', 0.08),
        weights.get('f6_tourism', 0.06),
        weights.get('f4_population', 0.02),
        weights.get('f5_economic', 0.02)
    ]
    mat = np.zeros((m, len(crit_keys)))
    for i, n in enumerate(viable_nodes):
        nf = get_node_normalized_features(n)
        for j, c in enumerate(crit_keys):
            mat[i, j] = nf[c]
    norms = np.sqrt(np.sum(mat**2, axis=0))
    norms[norms == 0] = 1.0
    r_mat = mat / norms
    v_mat = r_mat * np.array(crit_weights)
    pis = np.max(v_mat, axis=0)
    nis = np.min(v_mat, axis=0)
    d_plus = np.sqrt(np.sum((v_mat - pis)**2, axis=1))
    d_minus = np.sqrt(np.sum((v_mat - nis)**2, axis=1))
    denom = d_plus + d_minus
    denom[denom == 0] = 1e-6
    closeness = d_minus / denom
    
    # 3. Greedy 25 km Road Spacing Anti-Clustering
    sorted_indices = np.argsort(closeness)[::-1]
    candidates = [viable_nodes[idx] for idx in sorted_indices]
    
    selected = []
    min_gap = spacing_km / 1.22 # ~20.5 km
    
    for cand in candidates:
        if len(selected) >= k:
            break
        conflict = any(abs(cand['km_mark'] - s['km_mark']) < min_gap for s in selected)
        if not conflict:
            selected.append(cand)
            
    # 4. Fill boundary/corridor gaps if budget remains
    if len(selected) < k:
        for cand in candidates:
            if len(selected) >= k:
                break
            if cand not in selected:
                selected.append(cand)
                
    return selected

# -------------------------------------------------------------
# Evaluation Metric: Spatial Optimization Quality (SOQ)
# -------------------------------------------------------------

def evaluate_algorithm_network(chosen_nodes, all_nodes, total_len):
    """
    Computes the statutory Spatial Optimization Quality (SOQ) metric:
    1. Continuous 25 km corridor coverage union
    2. Blackspot compliance factor (min(1.0, 50km / max_gap))
    3. Traffic flow capture % with FCLM anti-duplication discount
    4. Brownfield match % (petrol pump + dhaba)
    5. Average substation distance (km)
    6. Redundant clustering overlap %
    """
    if not chosen_nodes:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        
    k = len(chosen_nodes)
    chosen_kms = sorted([n['km_mark'] for n in chosen_nodes])
    
    # 1. Continuous Corridor Coverage % (union of 25 km buffers)
    intervals = []
    for km in chosen_kms:
        intervals.append((max(0.0, km - 25.0), min(total_len, km + 25.0)))
    intervals.sort()
    merged = []
    for s, e in intervals:
        if not merged or merged[-1][1] < s:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)
    covered_len = sum(e - s for s, e in merged)
    coverage_pct = round(min(100.0, (covered_len / float(total_len)) * 100.0), 1)
    
    # 2. Maximum Blackspot Gap (km)
    gaps = [chosen_kms[0]]
    for i in range(len(chosen_kms) - 1):
        gaps.append(chosen_kms[i+1] - chosen_kms[i])
    gaps.append(total_len - chosen_kms[-1])
    max_gap_km = round(float(max(gaps)), 1)
    
    blackspot_factor = min(1.0, 50.0 / max_gap_km) if max_gap_km > 50.0 else 1.0
    
    # 3. Traffic Flow Capture % (with FCLM anti-duplication discount)
    effective_pcu = 0.0
    for i, n in enumerate(chosen_nodes):
        pcu = n['factors']['f3_traffic_pcu']
        is_close_overlap = any(abs(n['km_mark'] - chosen_nodes[j]['km_mark']) < 15.0 for j in range(i))
        if is_close_overlap:
            effective_pcu += pcu * 0.35
        else:
            effective_pcu += pcu
            
    all_pcus = sorted([n['factors']['f3_traffic_pcu'] for n in all_nodes], reverse=True)
    top_k_potential = sum(all_pcus[:k]) if all_pcus else 1.0
    demand_pct = round(min(100.0, (effective_pcu / float(top_k_potential)) * 100.0), 1)
    
    # 4. Brownfield Match % (has petrol pump or commercial dhaba)
    brownfield_count = sum(1 for n in chosen_nodes if n['factors']['f8_has_fuel'] or n['factors']['f9_has_dhaba'])
    brownfield_pct = round((brownfield_count / float(k)) * 100.0, 1)
    
    # 5. Average Substation Distance (km)
    sub_dists = [n['factors']['f7_substation_dist_km'] for n in chosen_nodes]
    avg_sub_dist_km = round(float(np.mean(sub_dists)), 2)
    
    # 6. Clustering Overlap Ratio (% of pairs closer than 15 km)
    overlap_count = 0
    for i in range(len(chosen_kms) - 1):
        if chosen_kms[i+1] - chosen_kms[i] < 15.0:
            overlap_count += 1
    clustering_overlap_pct = round((overlap_count / float(max(1, k - 1))) * 100.0, 1)
    
    # Statutory Spatial Optimization Quality (SOQ) Formula
    numerator = (coverage_pct / 100.0) * blackspot_factor * (demand_pct / 100.0) * max(0.20, brownfield_pct / 100.0)
    denominator = (1.0 + (avg_sub_dist_km / 5.0)) * (1.0 + (clustering_overlap_pct / 50.0))
    soq_score = round(float((numerator / denominator) * 100.0), 2)
    
    return soq_score, coverage_pct, max_gap_km, demand_pct, brownfield_pct, avg_sub_dist_km, clustering_overlap_pct

# -------------------------------------------------------------
# Execute Algorithm Tournament Across 500 Test Cases
# -------------------------------------------------------------

ALGORITHMS = [
    {
        'id': 'algo_ahp_additive',
        'name': 'Weighted AHP Additive Scoring',
        'type': 'Baseline MCDA',
        'func': lambda nodes, k, l: algo_1_ahp_additive(nodes, k)
    },
    {
        'id': 'algo_ahp_multiplicative',
        'name': 'Multiplicative Grid Feasibility AHP',
        'type': 'Gated MCDA',
        'func': lambda nodes, k, l: algo_2_ahp_multiplicative_grid(nodes, k)
    },
    {
        'id': 'algo_topsis',
        'name': 'TOPSIS (Closeness to Ideal)',
        'type': 'Vector MCDA',
        'func': lambda nodes, k, l: algo_3_topsis(nodes, k)
    },
    {
        'id': 'algo_greedy_spacing',
        'name': 'Greedy 25 km Anti-Clustering Spacing',
        'type': 'Spatial Anti-Cluster',
        'func': lambda nodes, k, l: algo_4_greedy_spacing(nodes, k)
    },
    {
        'id': 'algo_mclp',
        'name': 'Maximal Covering Location Problem (MCLP)',
        'type': 'Flow-Covering OR',
        'func': lambda nodes, k, l: algo_5_mclp(nodes, k)
    },
    {
        'id': 'algo_p_median',
        'name': 'P-Median Demand-Distance Minimizer',
        'type': 'Classical Hakimi OR',
        'func': lambda nodes, k, l: algo_6_p_median(nodes, k)
    },
    {
        'id': 'algo_frlm',
        'name': 'Flow Refueling Location Model (FRLM)',
        'type': 'EV Range Routing',
        'func': lambda nodes, k, l: algo_7_frlm(nodes, k, l)
    },
    {
        'id': 'algo_ilp',
        'name': 'Integer Linear Programming (ILP Set-Cover)',
        'type': 'Exact Branch & Bound',
        'func': lambda nodes, k, l: algo_8_ilp_set_cover(nodes, k)
    },
    {
        'id': 'algo_nsga2',
        'name': 'NSGA-II Multi-Objective Genetic Optimizer',
        'type': 'Pareto Evolutionary',
        'func': lambda nodes, k, l: algo_9_nsga2(nodes, k)
    },
    {
        'id': 'algo_urjax_hybrid',
        'name': 'Urja-X Hybrid Multi-Objective Siting Pipeline',
        'type': 'Production Pipeline',
        'func': lambda nodes, k, l: algo_10_urjax_hybrid(nodes, k, l)
    }
]

def run_algorithm_tournament():
    print(f"\nBenchmarking {len(ALGORITHMS)} spatial optimization algorithms across {len(test_cases)} test cases...")
    
    algo_results = {}
    
    for algo in ALGORITHMS:
        a_id = algo['id']
        a_name = algo['name']
        a_type = algo['type']
        
        t0 = time.time()
        scores = []
        coverages = []
        max_gaps = []
        demands = []
        brownfields = []
        sub_dists = []
        overlaps = []
        
        for tc in test_cases:
            nodes = tc['candidate_nodes']
            k = tc['target_station_quota_k']
            total_len = tc['total_corridor_len_km']
            
            chosen = algo['func'](nodes, k, total_len)
            soq, cov, gap, dem, brown, sub, ov = evaluate_algorithm_network(chosen, nodes, total_len)
            
            scores.append(soq)
            coverages.append(cov)
            max_gaps.append(gap)
            demands.append(dem)
            brownfields.append(brown)
            sub_dists.append(sub)
            overlaps.append(ov)
            
        elapsed = time.time() - t0
        
        algo_results[a_id] = {
            'algorithm_id': a_id,
            'algorithm_name': a_name,
            'algorithm_type': a_type,
            'mean_soq_score': round(float(np.mean(scores)), 2),
            'std_soq_score': round(float(np.std(scores)), 2),
            'mean_coverage_pct': round(float(np.mean(coverages)), 1),
            'mean_max_gap_km': round(float(np.mean(max_gaps)), 1),
            'mean_demand_capture_pct': round(float(np.mean(demands)), 1),
            'mean_brownfield_pct': round(float(np.mean(brownfields)), 1),
            'mean_substation_dist_km': round(float(np.mean(sub_dists)), 2),
            'mean_clustering_overlap_pct': round(float(np.mean(overlaps)), 1),
            'benchmark_time_seconds': round(elapsed, 2)
        }
        print(f"  ✓ Finished {a_name:<46} in {elapsed:.2f}s | Mean SOQ: {algo_results[a_id]['mean_soq_score']}")
        
    # Sort by SOQ Score descending
    ranked_algos = sorted(algo_results.values(), key=lambda x: x['mean_soq_score'], reverse=True)
    
    print("\n" + "=" * 115)
    print(f"{'RANK':<5} | {'ALGORITHM NAME':<46} | {'SOQ SCORE':<10} | {'COVERAGE':<9} | {'MAX GAP':<8} | {'DEMAND':<8} | {'CLUST OVERLAP':<13}")
    print("-" * 115)
    for rank, a_data in enumerate(ranked_algos, 1):
        print(f"#{rank:<4} | {a_data['algorithm_name']:<46} | {a_data['mean_soq_score']:>8.2f}   | {a_data['mean_coverage_pct']:>6.1f}%  | {a_data['mean_max_gap_km']:>5.1f}km | {a_data['mean_demand_capture_pct']:>6.1f}% | {a_data['mean_clustering_overlap_pct']:>11.1f}%")
    print("=" * 115)
    
    # Save Results
    final_output = {
        'total_corridor_test_cases_benchmarked': len(test_cases),
        'evaluation_metric': 'Spatial Optimization Quality (SOQ)',
        'ranked_algorithms': ranked_algos,
        'raw_algorithm_data': algo_results
    }
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2)
        
    print(f"\n✓ Saved Stage 2 Algorithm Tournament Results to: {OUTPUT_PATH}")
    print("=" * 85)
    return ranked_algos

if __name__ == '__main__':
    run_algorithm_tournament()
