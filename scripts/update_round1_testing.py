import os

file_path = "Round_1_Submission_EV_Infra_Map_India_Urja_X.md"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect where 4.5 ends and section 5 begins
target = """### 4.5 Temporal Forecasting Model (Target Year 2030)

To align with national targets under the PM E-DRIVE horizon, we forecast vehicle stock and charger demand using a compound annual growth rate (CAGR) model fitted on historical VAHAN registrations (2014–2026):

$$\\text{EV}_{\\text{stock}}(t) = \\text{EV}_{2026} \\times (1 + g_{\\text{CAGR}})^{t - 2026}$$

$$\\text{Target Public Chargers}(t) = \\frac{\\text{EV}_{\\text{stock}}(t)}{\\text{EVCR}_{\\text{target}}}$$

Where $g_{\\text{CAGR}}$ is computed per state (e.g., $32.4\\%$ national CAGR observed across 2021–2025). This provides MHI with a multi-year trajectory of required infrastructure capital allocations.

---

## 5. Innovation & Novelty of Proposed Solution (Evaluation Weight: 20%)"""

addition = """### 4.5 Temporal Forecasting Model (Target Year 2030)

To align with national targets under the PM E-DRIVE horizon, we forecast vehicle stock and charger demand using a compound annual growth rate (CAGR) model fitted on historical VAHAN registrations (2014–2026):

$$\\text{EV}_{\\text{stock}}(t) = \\text{EV}_{2026} \\times (1 + g_{\\text{CAGR}})^{t - 2026}$$

$$\\text{Target Public Chargers}(t) = \\frac{\\text{EV}_{\\text{stock}}(t)}{\\text{EVCR}_{\\text{target}}}$$

Where $g_{\\text{CAGR}}$ is computed per state (e.g., $32.4\\%$ national CAGR observed across 2021–2025). This provides MHI with a multi-year trajectory of required infrastructure capital allocations.

---

### 4.6 Simulation Testing & Benchmark Tournament Engine (Eliminating Arbitrary Weights)

To eliminate any accusation of arbitrary human bias or guess-work in selecting weights, Urja-X introduces a **Two-Stage Digital Twin Simulation & Benchmark Tournament Engine**. 

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                     URJA-X TWO-STAGE TESTING & VALIDATION ENGINE                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  STAGE 1: SINGLE-FACTOR SENSITIVITY TOURNAMENT (Derives Objective Weights)             │
│  • Tests all 9 empirical factors individually on randomized corridor grids.           │
│  • Evaluated on an unbiased multi-dimensional metric: Triad Network Health Index (NHI).│
│  • Factors that create the most balanced, real-world viable networks get top weights.  │
│                                                                                        │
│                                           ▼                                            │
│                                                                                        │
│  STAGE 2: ALGORITHM BATTLE & STRATEGY TOURNAMENT (Optimizes Siting Strategy)          │
│  • Benchmarks 4 candidate algorithms using the derived weighted factors:               │
│    1. Greedy Score Ranker  2. Spatial K-Medoids  3. Integer Linear Prog.  4. NSGA-II GA│
│  • Evaluated on Optimization Quality: Maximum Coverage with Zero Clustering Waste.     │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 1. The 9 Empirical Factors Evaluated
We test all nine real-world parameters outlined in national planning guidelines:
1. **Inter-Charger Distance ($\\Delta S$):** Road spacing and spatial gap elimination ($<100\\text{ km}$).
2. **EV Fleet Density:** Registered electric vehicle concentrations from VAHAN.
3. **Highway Traffic Flow:** Passenger Car Units (PCU) and freight transit volume.
4. **Human Population Density:** District and urban demographic pressure.
5. **Income & Economic Activity:** Purchasing power and commercial mobility demand.
6. **Tourism & Waypoint Pull:** Weekend and seasonal passenger corridor peaks.
7. **Electricity Grid Proximity:** Distance to verified $11\\text{kV}/33\\text{kV}$ substations.
8. **Fuel Stations / Brownfield Points:** Existing retail outlets (IOCL/BPCL/HPCL) for rapid rollout.
9. **Commercial Amenities & Dhabas:** Restroom facilities, food courts, and 24/7 safe parking.

#### 2. Stage 1: How We Test Individual Factors Without Metric Bias
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

The algorithms are benchmarked on **Capital-Adjusted Service Efficiency (CASE)**, measuring total highway coverage percentage achieved per crore of public investment with zero spatial redundancy.

---

## 5. Innovation & Novelty of Proposed Solution (Evaluation Weight: 20%)"""

if target in text:
    text = text.replace(target, addition, 1)
    
    # Also update Section 5 Innovation #5
    old_innov = "4. **Transparent, Zero-Guesswork Mathematical Sizing:**  \n   Recommendations output specific charging gun counts ($N_{\\text{guns}}$) and kW specifications based on physics and traffic demand equations rather than arbitrary guesses."
    new_innov = """4. **Transparent, Zero-Guesswork Mathematical Sizing:**  
   Recommendations output specific charging gun counts ($N_{\\text{guns}}$) and kW specifications based on physics and traffic demand equations rather than arbitrary guesses.
5. **Two-Stage Simulation & Algorithm Tournament Engine:**  
   Eliminates arbitrary weight guessing. Tests all 9 empirical factors against an unbiased geometric mean metric (Service, Commercial, Operability) and benchmarks 4 optimization algorithms (Greedy, K-Medoids, ILP, NSGA-II Genetic Optimizer) to prove superior real-world performance."""
    
    if old_innov in text:
        text = text.replace(old_innov, new_innov, 1)
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("SUCCESS: Updated Round 1 document with simulation testing framework!")
else:
    print("Target not found in Round 1 doc.")
