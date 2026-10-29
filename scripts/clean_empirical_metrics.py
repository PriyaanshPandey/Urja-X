import os

# 1. Update Round_1_Submission_EV_Infra_Map_India_Urja_X.md
round1_path = "Round_1_Submission_EV_Infra_Map_India_Urja_X.md"
with open(round1_path, "r", encoding="utf-8") as f:
    text = f.read()

target_sec46 = """#### 2. Stage 1: How We Test Individual Factors Without Metric Bias
If an evaluation metric only measured grid cost, the grid factor would unfairly win 100% of the weight. If it only measured EV count, vehicle density would win 100%. 

To give every factor an equal, unbiased chance, Urja-X evaluates each factor's proposed network across **three physical, non-negotiable dimensions** combined using a **Geometric Mean** (so failing on any one dimension collapses the factor's score):

$$\\text{Factor Score } S_i = \\sqrt[3]{M_{\\text{service}} \\times M_{\\text{commercial}} \\times M_{\\text{operability}}}$$

* **$M_{\\text{service}}$ (Service Effectiveness):** Trip completion percentage and reduction of highway charging deserts (prevents stranded vehicles).
* **$M_{\\text{commercial}}$ (Commercial Viability):** Station utilization rate and daily kWh throughput (prevents under-utilized "ghost stations").
* **$M_{\\text{operability}}$ (Technical Operability):** Proximity to electrical grid substations and presence of brownfield amenities (prevents multi-year commissioning delays).

**Why This Is Fair:**
* If a strategy sites chargers based **only on the Power Grid**, it scores 100% on Operability, but nearly 0% on Commercial Viability and Service (chargers end up in empty fields with no traffic).
* If a strategy sites chargers based **only on EV Density**, it clumps all chargers in big cities, stranding long-distance highway travelers.
* Factors that achieve a balanced, high score across all three real-world dimensions naturally receive higher empirical weights ($W_i = S_i / \\sum S_j$).

#### 3. Stage 2: Algorithm Battle & Tournament
Once the objective weights are derived, we test which **algorithm** best selects the final $K$ stations across a highway corridor:
* **Algorithm A (Greedy Ranker):** Picks highest-scoring sites directly (prone to clustering).
* **Algorithm B (Spatial K-Medoids):** Balances high scores with anti-clustering distance constraints.
* **Algorithm C (Integer Linear Programming - ILP):** Formulates placement as an optimal set-cover problem.
* **Algorithm D (NSGA-II Multi-Objective Genetic Optimizer):** Evolves station combinations over 50 generations to maximize total corridor coverage while minimizing infrastructure capex.

The algorithms are benchmarked on **Capital-Adjusted Service Efficiency (CASE)**, measuring total highway coverage percentage achieved per crore of public investment with zero spatial redundancy."""

replacement_sec46 = """#### 2. Stage 1: How We Test Individual Factors Without Metric Bias
If an evaluation metric only measured substation distance, the grid factor would unfairly win 100% of the weight. If it only measured vehicle count, EV density would unfairly win 100%. 

To ensure absolute fairness without relying on unverified financial cost data, Urja-X evaluates each factor across **three empirical physical dimensions** grounded in our verified datasets, combined using a **Geometric Mean**:

$$\\text{Factor Score } S_i = \\sqrt[3]{M_{\\text{service}} \\times M_{\\text{demand}} \\times M_{\\text{readiness}}}$$

* **$M_{\\text{service}}$ (Corridor Service & Desert Elimination):** Percentage of the highway corridor where inter-station distance satisfies the statutory $25\\text{ km}$ MoP benchmark (derived from `india_nh.gpkg`).
* **$M_{\\text{demand}}$ (Fleet Demand Alignment):** Concentration of registered electric vehicles captured within a $15\\text{ km}$ corridor catchment buffer (derived from VAHAN 4 `EV Sales Data.xlsx`).
* **$M_{\\text{readiness}}$ (Infrastructure & Grid Readiness):** Physical distance to verified $11\\text{kV}/33\\text{kV}$ substations (from `india_electricity_final.csv`) and co-location with verified fuel retail outlets (from `india_pois.gpkg`).

**Why This Is Fair:**
* If a strategy sites chargers based **only on the Power Grid**, it scores 100% on Infrastructure Readiness, but near 0% on Demand and Service (chargers end up placed in rural empty fields with no traffic).
* If a strategy sites chargers based **only on EV Density**, it clumps all chargers in big cities, stranding long-distance highway travelers.
* If a strategy sites chargers based **only on Distance**, it places chargers in remote forests 20 km away from any electrical substation.
* Factors that achieve a balanced, high score across all three physical dimensions naturally receive higher empirical weights ($W_i = S_i / \\sum S_j$).

#### 3. Stage 2: Algorithm Battle & Strategy Tournament
Once objective weights are derived, we benchmark which **optimization algorithm** selects the best set of $K$ stations along a highway:
* **Algorithm A (Greedy Ranker):** Picks highest-scoring sites directly (prone to spatial clustering).
* **Algorithm B (Spatial K-Medoids):** Partitions candidate points into clusters, enforcing spatial dispersion.
* **Algorithm C (Integer Linear Programming - ILP):** Formulates placement as an optimal binary set-cover problem.
* **Algorithm D (NSGA-II Multi-Objective Genetic Optimizer):** Evolves station combinations over 50 generations to simultaneously maximize corridor coverage and brownfield matching while minimizing substation distance.

The algorithms are benchmarked on **Spatial Optimization Quality (SOQ)**: measuring corridor coverage percentage ($\\%$), average physical distance to substations (km), and zero spatial clustering overlap."""

if target_sec46 in text:
    text = text.replace(target_sec46, replacement_sec46, 1)
    with open(round1_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("SUCCESS: Updated Round 1 submission file with strictly empirical metrics!")
else:
    print("Target section not found in Round 1 doc.")

# 2. Update Urja_X_MVP_Specification.md to remove cost guesses
mvp_path = "Urja_X_MVP_Specification.md"
with open(mvp_path, "r", encoding="utf-8") as f:
    mvp_text = f.read()

old_cost = "➜ Line voltage drop within CEA 6% limit; HV extension capex < ₹4.5 Lakhs."
new_cost = "➜ Line voltage drop within CEA 6% limit; feeder distance 1.1 km is well within the 5 km technical limit."

if old_cost in mvp_text:
    mvp_text = mvp_text.replace(old_cost, new_cost, 1)
    with open(mvp_path, "w", encoding="utf-8") as f:
        f.write(mvp_text)
    print("SUCCESS: Updated MVP Specification file!")
else:
    print("Target cost text not found in MVP spec.")
