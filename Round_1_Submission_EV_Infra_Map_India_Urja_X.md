# Techfest 2026-27 | EV Infra & Green Mobility AI Challenge
## Ministry of Heavy Industries (MHI) & ICAT (International Centre for Automotive Technology)
### Challenge 1: EV Infra Map India
**Mapping and Integration of Nationwide EV Charger Installations Based on Vehicle Population Using VAHAN Data**

---

# ROUND 1 SUBMISSION: METHODOLOGY DOCUMENT & IMPLEMENTATION ROADMAP
**Project Title:** **Urja-X: Nationwide Geospatial Intelligence & Data-Driven Decision Support Platform for EV Infrastructure**  
**Submission Date:** October 30, 2026  

---

## 1. Team Information

| Field | Details |
| :--- | :--- |
| **Team Name** | *Urja-X Analytics* |
| **Team ID** | *[Insert Official Techfest Team ID]* |
| **Institution / College** | *[Insert Institution / University Name]* |
| **Team Leader Name** | *[Insert Team Leader Name]* |
| **Team Leader Email** | *[Insert Team Leader Email]* |
| **Team Leader Phone** | *[Insert Contact Phone Number]* |
| **Team Members** | 1. *[Member 1 Name & Roll/Dept]*<br>2. *[Member 2 Name & Roll/Dept]*<br>3. *[Member 3 Name & Roll/Dept]*<br>4. *[Member 4 Name & Roll/Dept]* |

---

## 2. Problem Understanding & Relevance (Evaluation Weight: 25%)

### 2.1 The Core Challenge
India’s automotive sector is experiencing a generational shift towards electric mobility, spearheaded by flagship government initiatives such as **FAME-II** and the newly launched **PM Electric Drive Revolution in Innovative Vehicle Enhancement (PM E-DRIVE)** scheme. Over **5.8 million Battery-Operated Electric Vehicles (BOVs)** are registered across Indian states and union territories. However, the deployment of public EV charging infrastructure exhibits two major structural bottlenecks:

1. **Fragmentation of Charger Data:** Charging infrastructure information is siloed across independent Charge Point Operators (CPOs), municipal databases, oil marketing companies (IOCL, BPCL, HPCL), and power distribution utilities. There is no unified, high-integrity national GIS layer mapping existing operational chargers, connector types, and kW capacities.
2. **Misalignment Between EV Adoption and Charger Provisioning:** EV charger deployments have historically been ad-hoc or concentrated strictly within elite metropolitan pockets, leading to acute regional disparities. While urban areas face localized queue congestion, national and state highways suffer from vast **"Charging Deserts"** (inter-charger distances $> 100\text{ km}$), causing crippling range anxiety for intercity travel and commercial freight.

### 2.2 Relevance to Stakeholders (MHI, ICAT, State Nodal Agencies, and CPOs)
Under PM E-DRIVE, the Ministry of Heavy Industries (MHI) has committed substantial budgetary support for public charging stations (targeting 72,300 public chargers). To maximize the capital efficiency of public subsidies, policy makers cannot rely on intuitive or uncoordinated private siting.

**Urja-X** provides a mathematically defensible, empirical national planning platform that:
- Aggregates and standardizes nationwide EV charging assets ($39,600+$ operational stations).
- Evaluates the **EV-to-Charger Ratio (EVCR)** against global standards to identify priority deficit districts.
- Converts national highway corridors into continuous **spatial analysis grids** to identify critical charging blackspots based on official **Ministry of Power (MoP) spacing benchmarks**.
- Recommends the exact **micro-location and number of charging guns (ports)** required per site, incorporating power grid proximity ($11\text{kV}/33\text{kV}$ substations) and brownfield amenities.

---

## 3. Comprehensive Data Strategy & Acquisition Pipeline (Evaluation Weight: 10%)

To eliminate guesswork and synthetic bias, the Urja-X platform is built entirely upon empirical, multi-source national datasets.

### 3.1 Data Inventory Table

| Data Layer | Dataset Details | Scope & Coverage | Acquisition / Scraping Strategy |
| :--- | :--- | :--- | :--- |
| **EV Population & Registrations** | VAHAN 4 Dashboard & OpenCity State Portals | **5,802,870 BOVs** across 121,487 state & RTO-level records (2014–2026). Fuel-wise, category-wise. | **Automated Playwright Browser Scripting** on VAHAN 4 dynamic reporting UI + CKAN REST API querying on OpenCity. |
| **Operational EV Charging Infra** | India EV Charging Database & BEE National Registry | **39,641 Geocoded Public Stations** across 36 States/UTs. Includes CPO, kW rating, connector standard, Govt/Private status. | Direct extraction from verified national open registries + Open Charge Map (OCM) geocoded REST API. |
| **National Highway Corridor Network** | OpenStreetMap (OSM) India Highway Topology | Complete vector geometry of National Highways (NH-44, NH-48, NH-27, NH-19, etc.), expressways, and trunk roads. | **C++ Osmium & GDAL Pipeline** filtering 1.6 GB Geofabrik OSM PBF (`other_tags LIKE '%"ref"=>"NH%'`). |
| **Power Grid & Substation Infrastructure** | India High-Voltage Electrical Infrastructure Database | **224 MB vector/point dataset** containing transmission lines, substations, transformer nodes, and voltage levels ($11\text{kV} - 400\text{kV}$). | Geospatial extraction of OpenStreetMap power network ontology (`power=substation`, `power=line`, `power=transformer`). |
| **Brownfield Amenities & Fuel Stations** | Points of Interest (POI) Infrastructure Layer | **13,100+ Geocoded Fuel & CNG retail outlets**, highway rest stops, and transit terminals. | Tag-filtered spatial extraction (`amenity=fuel`, `shop`, `tourism`) via GDAL into high-performance GeoPackage (`.gpkg`). |
| **Official Policy Benchmarks** | PIB Disclosures & Bureau of Energy Efficiency (BEE) | State-wise operational Public Charging Stations (PCS) baselines and Tier classifications. | Consolidated from official Ministry of Power and BEE gazette disclosures. |

### 3.2 Automated Data Collection & Scraping Methodology

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATA INGESTION PIPELINE                               │
├───────────────────┬───────────────────────────┬─────────────────────────────────┤
│   VAHAN SCRAPER   │    OPENCITY CKAN API      │    OSM SPATIAL TOOLCHAIN        │
│ (Playwright Sync) │      (Requests/JSON)      │   (Osmium C++ / GDAL Engine)    │
│  • Headless Chrome│  • Package Search Endpoint│  • Stream-filter 1.6 GB OSM PBF │
│  • Dynamic Select │  • Automated pagination   │  • Regex tag extraction         │
│  • Year loop 23-26│  • District RTO CSVs      │  • Output OGC GeoPackage (.gpkg)│
└─────────┬─────────┴─────────────┬─────────────┴────────────────┬────────────────┘
          │                       │                              │
          ▼                       ▼                              ▼
  [vahan_raw_data/]      [opencity_ev_data/]             [EV-Roads/ GeoPackages]
```

1. **VAHAN 4 Dynamic Dashboard Scraping (`scrape_vahan.py`):**
   * *Challenge:* The Ministry of Road Transport & Highways (MoRTH) VAHAN dashboard (`vahan.parivahan.gov.in`) utilizes dynamic JavaServer Faces (PrimeFaces) components with asynchronous AJAX updates, preventing standard HTTP GET/POST scraping.
   * *Strategy:* Implemented an automated browser script using **Playwright**. The script programmatically configures the multi-dimensional pivot table: setting Y-Axis to `Fuel Wise`, X-Axis to `State`, filtering by `Electric(BOV)`, iterating across calendar years (2023–2026), and triggering structured Excel export listeners.
2. **OpenCity CKAN API Harvesting (`download_opencity_data.py`):**
   * *Strategy:* Utilized the CKAN Action API (`/api/3/action/package_search`) to programmatically query high-value civic transport repositories for queries including `"EV charging"`, `"EV consumption"`, `"BESCOM"`, and `"vehicle registration"`. Automated resource downloads yielded historical district-level registration data and commercial vehicle splits.
3. **OSM High-Performance Spatial Vector Pipeline (`filter_and_export.py`):**
   * *Strategy:* Processing the entire road and power infrastructure of India from raw OSM XML is computationally intractable. We engineered a dual-engine pipeline using **Osmium (C++ binary)** and **GDAL/OGR**. The pipeline filters a 1.6 GB compressed PBF file (`india-latest.osm.pbf`) into indexed GeoPackages:
     - `india_nh.gpkg`: National highway vectors filtered by reference codes.
     - `india_pois.gpkg`: 13,100+ fuel stations and commercial waypoints.
     - `india_electricity_final.csv` & `india_transmission_lines.geojson`: Extracted electrical grid network.
4. **Data Standardization & CRS Alignment:**
   * All geospatial vector layers are projected and normalized to the **WGS 84 (EPSG:4326)** coordinate reference system for vector math and **Web Mercator (EPSG:3857)** for Euclidean buffer distance calculations.

---

## 4. Analytical Methodology & Gap Assessment Framework (Evaluation Weight: 25%)

The core intelligence of Urja-X is organized into a **Three-Tier Hierarchical Planning Framework** that transitions from macro policy targeting down to exact highway grid coordinate recommendations.

```
   TIER 1: MACRO TARGETING     ──► Calculate EV-to-Charger Ratio (EVCR) by State & District
              │                    Compare against IEA Benchmark (10-20 EVs/Charger)
              ▼
   TIER 2: CORRIDOR DESERTS    ──► Discretize National Highways into 5 km Corridor Grid Windows
              │                    Flag Gaps > 25 km (MoP Benchmark) as "Charging Deserts"
              ▼
   TIER 3: MICRO-GRID SITING   ──► Multi-Criteria AHP Scoring (Demand, Grid, Road, Amenity)
                                   Size exact number of charging guns (N_guns) per site
```

---

### 4.1 Tier 1: Macro-Deficit & Quota Allocation (District & State Level)

To determine which districts require immediate capital intervention, we formulate the **Regional EV-to-Charger Ratio (EVCR)**:

$$\text{EVCR}_{d} = \frac{\sum \text{Registered BOVs}_{d}}{N_{\text{chargers}, d}}$$

* **International Benchmark (IEA Global EV Outlook):** The global healthy benchmark ranges between **$10\text{ and }20\text{ EVs per public charger}$** (ideal target $\approx 15:1$).
* **National Deficit Classification:**
  - **Critical Deficit Zone:** $\text{EVCR} > 150$ (Severe infrastructure shortage; high queue times; immediate intervention required).
  - **Transitional Zone:** $50 < \text{EVCR} \le 150$ (Moderate availability; expansion required to track sales growth).
  - **Adequate Zone:** $\text{EVCR} \le 50$ (Well-provisioned initial network; focus shifts to corridor and rural expansion).

#### District Target Charger Allocation Formula:
For any administrative district $d$, the required public charging stations ($N_{\text{target}, d}$) to achieve a sustainable target ratio ($\text{EVCR}_{\text{target}} = 15$) is computed as:

$$\Delta N_{\text{chargers}, d} = \max\left(0, \; \left\lceil \frac{\text{Registered BOVs}_{d}}{\text{EVCR}_{\text{target}}} \right\rceil - N_{\text{existing}, d}\right)$$

---

### 4.2 Tier 2: Highway Corridor Discretization & "Charging Desert" Detection

Evaluating charging gaps along national highways cannot be performed using administrative centroid buffers, as highways traverse rural districts with deceptive boundaries. 

**Methodology:**
1. **Corridor Vector Slicing:** Continuous National Highway vectors (e.g., NH-44, NH-48, NH-27) are parsed from `india_nh.gpkg` and discretized into **$5\text{ km}$ spatial corridor grid windows** ($G_k$).
2. **Orthogonal Buffer Search:** A $2\text{ km}$ bilateral buffer is projected along each corridor segment to capture accessible off-highway charging stations.
3. **Inter-Charger Distance Computation:** For every sequential charger pair $(C_i, C_{i+1})$ along the corridor vector, the geodesic distance $\Delta S$ is evaluated:

$$\Delta S = \text{Distance}(C_i, C_{i+1})$$

#### Scientific & Engineering Justification for the 5 km Grid Size:
The selection of a **$5\text{ km}$ discretization window** is rigorously grounded in four complementary mathematical, physical, and policy constraints:
1. **Nyquist-Shannon Spatial Sampling of Statutory Norms:** The Ministry of Power (MoP) statutory guideline mandates at least one charging station every $25\text{ km}$. Under spatial sampling theory (Nyquist-Shannon), to detect and place points within an interval $L_{\text{target}} = 25\text{ km}$ without aliasing or skipping viable sites, the sampling resolution must be $\Delta x \le L_{\text{target}} / N$ with $N \ge 2\text{ to }5$. A $5\text{ km}$ window ($N=5$) guarantees 5 discrete candidate evaluation windows inside any statutory $25\text{ km}$ block.
2. **Central Electricity Authority (CEA) 11 kV Feeder Voltage-Drop Physics:** Commercial EV fast-charging loads ($\sim 250\text{--}500\text{ kVA}$) on highways connect to $33/11\text{ kV}$ DISCOM substations. Under CEA and State Electricity Regulatory Commission (SERC) regulations, the statutory voltage drop ($\Delta V$) on $11\text{ kV}$ distribution lines must not exceed $6\%$. The maximum economic and technical radial reach of an $11\text{ kV}$ line before requiring high-cost capacitor banks or intermediate substations is **$3\text{ to }5\text{ km}$**. A $5\text{ km}$ grid window precisely matches this physical distribution limit.
3. **Driver Detour Equivalence Window:** At standard Indian highway speeds ($80\text{--}100\text{ km/h}$), a $5\text{ km}$ segment represents $\approx 3.3\text{ minutes}$ of transit time. Across an intercity corridor journey, any candidate site within this 3-minute window offers identical driver utility, preventing unnecessary computational overhead of sub-kilometer micro-meshing.
4. **NHAI Wayside Amenities (WSA) Spacing Norms:** National Highways Authority of India (NHAI) planning guidelines specify access spacing for wayside rest areas and retail concessions between $5\text{ km}$ and $10\text{ km}$ to preserve uninterrupted trunk traffic flow.

#### Statutory Spacing Thresholds (MoP / BEE Guidelines):
As notified in the *Ministry of Power Charging Infrastructure Guidelines & Standards (Revised 2022 / PM E-DRIVE)*:
- **Standard Highway Threshold:** At least one charging station every **$25\text{ km}$** on both sides of the highway.
- **Heavy-Duty / Commercial EV Threshold:** At least one fast charging station every **$100\text{ km}$** on each side.

**Algorithmic Flagging:**
- If $\Delta S > 25\text{ km}$: Flagged as **Highway Charging Deficit**.
- If $\Delta S > 75\text{ km}$: Flagged as a **Severe Charging Desert** (High priority for immediate site allocation).

---

### 4.3 Tier 3: Micro-Grid Multi-Criteria Siting & Hybrid AHP-Entropy Framework

Inside identified deficit corridor grids ($G_k$), candidate sites are evaluated using an **integrated Multi-Criteria Decision Making (MCDM)** engine.

To eliminate subjectivity and prevent arbitrary weight selection, Urja-X synthesizes **Domain Policy Guidelines (Top-Down AHP)** with **Empirical Data Dispersion (Bottom-Up Shannon Entropy)** into a **Hybrid AHP-Entropy Weight Model (AHP-EWM)**:

$$\text{Composite Suitability Index (CSI)} = \sum_{j=1}^{4} W_j^{\text{combined}} \cdot F_j^{\text{norm}} \quad \in [0, 100]$$

| Pillar ($F_j$) | Evaluated Parameter | Data Source | Baseline AHP Weight ($W_j^{\text{AHP}}$) | Authoritative Policy & Engineering Justification |
| :--- | :--- | :--- | :---: | :--- |
| **1. Regional EV Fleet Pressure ($F_1$)** | BOV registration density in surrounding RTO | `EV Sales Data.xlsx` | **35%** | **NITI Aayog & WRI India EV Handbook (2021, Sec 3.2):** Siting must be demand-led to guarantee station utilization ($>30\%$) and commercial viability under PM E-DRIVE. |
| **2. Road Hierarchy & Traffic Flow ($F_2$)** | Highway classification (Expressway / NH / State Highway) | `india_nh.gpkg` | **25%** | **MoP Revised Guidelines (2022):** Expressways and heavy freight corridors receive priority DC fast-charging allocations before secondary arterials. |
| **3. Power Grid Proximity ($F_3$)** | Euclidean distance to nearest $11\text{kV}/33\text{kV}$ substation | `india_electricity_final.csv` | **25%** | **CEA Grid Standards & DISCOM Capex Rules:** High-voltage extension costs ₹8–15 Lakhs/km; sites near substations minimize grid interconnection delays and transmission losses. |
| **4. Spatial Deficit & Brownfield Readiness ($F_4$)** | Anti-clustering distance + presence of fuel station/amenity | `india_ev_charging_raw.csv` + `india_pois.gpkg` | **15%** | **MoPNG & MoRTH Directives:** Co-location at existing retail outlets (petrol pumps, dhabas) eliminates land acquisition time, cutting commissioning from 9 months to 4 weeks. |

#### Mathematical Derivation of Baseline Weights via Saaty's Pairwise Matrix:
The baseline policy weights are mathematically validated using Thomas Saaty’s pairwise comparison methodology:

$$A = \begin{pmatrix}
1 & 1.5 & 1.5 & 2.5 \\
0.67 & 1 & 1 & 1.67 \\
0.67 & 1 & 1 & 1.67 \\
0.40 & 0.60 & 0.60 & 1
\end{pmatrix}$$

* Principal Eigenvalue ($\lambda_{\max}$): $4.004$
* Consistency Index ($\text{CI} = \frac{\lambda_{\max} - n}{n - 1}$): $0.0013$
* **Consistency Ratio ($\text{CR} = \frac{\text{CI}}{\text{RI}}$ with $\text{RI}=0.90$):** **$0.0015 \ll 0.10$** *(Mathematically consistent; zero logical contradiction).*

#### Objective Entropy Weight Calibration (Shannon Entropy Method):
To ensure weights are not purely subjective, the baseline AHP weights are balanced against the **information entropy** of candidate site data:

1. **Normalized Decision Matrix ($p_{ij}$):**
   $$p_{ij} = \frac{x_{ij}}{\sum_{i=1}^{m} x_{ij}}$$
2. **Shannon Entropy for Criterion $j$ ($e_j$):**
   $$e_j = -\frac{1}{\ln(m)} \sum_{i=1}^{m} p_{ij} \ln(p_{ij})$$
3. **Information Divergence ($d_j$) & Objective Weight ($W_j^{\text{Entropy}}$):**
   $$d_j = 1 - e_j \implies W_j^{\text{Entropy}} = \frac{d_j}{\sum_{k=1}^{n} d_k}$$

Criteria with high geographical variance (such as substation distances ranging from $0.5\text{ km}$ to $20\text{ km}$) naturally yield higher entropy weights, reflecting their strong discriminatory power.

4. **Hybrid Combined Weight Formulation ($W_j^{\text{combined}}$):**
   $$W_j^{\text{combined}} = \frac{\alpha \cdot W_j^{\text{AHP}} + (1 - \alpha) \cdot W_j^{\text{Entropy}}}{\sum_{k=1}^{n} \left[ \alpha \cdot W_k^{\text{AHP}} + (1 - \alpha) \cdot W_k^{\text{Entropy}} \right]}$$
   *(Where $\alpha = 0.50$, harmonizing top-down statutory policy priorities with bottom-up empirical data variance).*

#### Handling Brownfield vs. Greenfield Opportunities:
* Fuel stations, CNG retail outlets, and highway dhabas (`india_pois.gpkg`) within the grid cell are treated as **high-scoring brownfield candidates** because they already possess land, parking bays, and 24/7 security.
* If a charging desert grid contains no fuel station, the algorithm evaluates **greenfield candidate waypoints** nearest to electrical grid nodes.

---

### 4.4 Sizing Module: Determining the Number of Charging Points (Guns)

MHI planning requires knowing not just where to place a station, but **how many charging guns (ports)** must be installed. Rather than using arbitrary station counts, we apply the following mathematical sizing model:

$$N_{\text{guns}} = \left\lceil \frac{E_{\text{daily\_demand}}}{H_{\text{active}} \times P_{\text{gun}} \times \eta} \right\rceil$$

Where:
* $E_{\text{daily\_demand}} = V_{\text{corridor}} \times P_{\text{EV}} \times f_{\text{charge}} \times \Delta\text{SoC} \times B_{\text{battery}}$
  - $V_{\text{corridor}} \times P_{\text{EV}}$: Daily EV traffic volume traversals.
  - $f_{\text{charge}}$: Intercity highway top-up probability ($\approx 20\%$).
  - $\Delta\text{SoC} \times B_{\text{battery}}$: Average fast-charge energy delivered ($30\text{ kWh}$ for a standard $20\% \rightarrow 80\%$ session).
* $H_{\text{active}}$: Active operating window ($14\text{ hours/day}$).
* $P_{\text{gun}}$: Rated power of DC Fast Charging gun ($60\text{ kW}$ CCS-2 standard).
* $\eta$: Concurrency factor / station efficiency ($\approx 75\%$).

---

### 4.5 Temporal Forecasting Model (Target Year 2030)

To align with national targets under the PM E-DRIVE horizon, we forecast vehicle stock and charger demand using a compound annual growth rate (CAGR) model fitted on historical VAHAN registrations (2014–2026):

$$\text{EV}_{\text{stock}}(t) = \text{EV}_{2026} \times (1 + g_{\text{CAGR}})^{t - 2026}$$

$$\text{Target Public Chargers}(t) = \frac{\text{EV}_{\text{stock}}(t)}{\text{EVCR}_{\text{target}}}$$

Where $g_{\text{CAGR}}$ is computed per state (e.g., $32.4\%$ national CAGR observed across 2021–2025). This provides MHI with a multi-year trajectory of required infrastructure capital allocations.

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
1. **Inter-Charger Distance ($\Delta S$):** Road spacing and spatial gap elimination ($<100\text{ km}$).
2. **EV Fleet Density:** Registered electric vehicle concentrations from VAHAN.
3. **Highway Traffic Flow:** Passenger Car Units (PCU) and freight transit volume.
4. **Human Population Density:** District and urban demographic pressure.
5. **Income & Economic Activity:** Purchasing power and commercial mobility demand.
6. **Tourism & Waypoint Pull:** Weekend and seasonal passenger corridor peaks.
7. **Electricity Grid Proximity:** Distance to verified $11\text{kV}/33\text{kV}$ substations.
8. **Fuel Stations / Brownfield Points:** Existing retail outlets (IOCL/BPCL/HPCL) for rapid rollout.
9. **Commercial Amenities & Dhabas:** Restroom facilities, food courts, and 24/7 safe parking.

#### 2. Stage 1: How We Test Individual Factors Without Metric Bias
If an evaluation metric only measured grid cost, the grid factor would unfairly win 100% of the weight. If it only measured EV count, vehicle density would win 100%. 

To give every factor an equal, unbiased chance, Urja-X evaluates each factor's proposed network across **three physical, non-negotiable dimensions** combined using a **Geometric Mean** (so failing on any one dimension collapses the factor's score):

$$\text{Factor Score } S_i = \sqrt[3]{M_{\text{service}} \times M_{\text{commercial}} \times M_{\text{operability}}}$$

* **$M_{\text{service}}$ (Service Effectiveness):** Trip completion percentage and reduction of highway charging deserts (prevents stranded vehicles).
* **$M_{\text{commercial}}$ (Commercial Viability):** Station utilization rate and daily kWh throughput (prevents under-utilized "ghost stations").
* **$M_{\text{operability}}$ (Technical Operability):** Proximity to electrical grid substations and presence of brownfield amenities (prevents multi-year commissioning delays).

**Why This Is Fair:**
* If a strategy sites chargers based **only on the Power Grid**, it scores 100% on Operability, but nearly 0% on Commercial Viability and Service (chargers end up in empty fields with no traffic).
* If a strategy sites chargers based **only on EV Density**, it clumps all chargers in big cities, stranding long-distance highway travelers.
* Factors that achieve a balanced, high score across all three real-world dimensions naturally receive higher empirical weights ($W_i = S_i / \sum S_j$).

#### 3. Stage 2: Algorithm Battle & Tournament
Once the objective weights are derived, we test which **algorithm** best selects the final $K$ stations across a highway corridor:
* **Algorithm A (Greedy Ranker):** Picks highest-scoring sites directly (prone to clustering).
* **Algorithm B (Spatial K-Medoids):** Balances high scores with anti-clustering distance constraints.
* **Algorithm C (Integer Linear Programming - ILP):** Formulates placement as an optimal set-cover problem.
* **Algorithm D (NSGA-II Multi-Objective Genetic Optimizer):** Evolves station combinations over 50 generations to maximize total corridor coverage while minimizing infrastructure capex.

The algorithms are benchmarked on **Capital-Adjusted Service Efficiency (CASE)**, measuring total highway coverage percentage achieved per crore of public investment with zero spatial redundancy.

---

## 5. Innovation & Novelty of Proposed Solution (Evaluation Weight: 20%)

1. **Continuous Road-Corridor Discretization vs. Static Centroids:**  
   Most existing hackathon entries perform basic district-level radius clustering, which fails on long linear highways. Urja-X discretizes roads into linear spatial grid cells, solving the true real-world problem: **intercity highway range anxiety**.
2. **Power Grid Feasibility Matching:**  
   Unlike generic mapping tools that suggest charging locations on isolated roads, Urja-X directly computes proximity to the **$11\text{kV}/33\text{kV}$ transmission and substation network** using our $224\text{ MB}$ electrical grid dataset, ensuring technical feasibility for DISCOM interconnects.
3. **Dual Greenfield/Brownfield Adaptive Siting:**  
   The platform does not restrict itself to petrol pumps. It prioritizes existing amenities where available for rapid low-cost commissioning, while dynamically generating greenfield site recommendations in severe infrastructure deserts.
4. **Transparent, Zero-Guesswork Mathematical Sizing:**  
   Recommendations output specific charging gun counts ($N_{\text{guns}}$) and kW specifications based on physics and traffic demand equations rather than arbitrary guesses.
5. **Two-Stage Simulation & Algorithm Tournament Engine:**  
   Eliminates arbitrary weight guessing. Tests all 9 empirical factors against an unbiased geometric mean metric (Service, Commercial, Operability) and benchmarks 4 optimization algorithms (Greedy, K-Medoids, ILP, NSGA-II Genetic Optimizer) to prove superior real-world performance.

---

## 6. Implementation Roadmap Ahead of Grand Finale (Evaluation Weight: 20%)

The implementation plan is structured into four milestone-driven sprints leading directly to the Grand Finale at **Techfest, IIT Bombay (December 16–18, 2026)**.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     URJA-X DEVELOPMENT ROADMAP                                         │
├────────────────────┬────────────────────┬──────────────────────────────────┬───────────────────────────┤
│ ROUND 1 SUBMISSION │ PHASE 2: GAP ENGINE│ PHASE 3: SITING & SIZING ENGINE  │ PHASE 4: DECISION PLATFORM│
│  (Oct 29 - Oct 30) │  (Nov 1 - Nov 15)  │        (Nov 16 - Nov 30)         │     (Dec 1 - Dec 15)      │
├────────────────────┼────────────────────┼──────────────────────────────────┼───────────────────────────┤
│ • Methodology Doc  │ • Compute State &  │ • Hexagonal / Linear Road Mesh   │ • Interactive Web GUI     │
│ • Roadmap Finalized│   District EVCR    │ • AHP Siting Algorithm Execution │ • Highway Route Inspector │
│ • Data Pipeline OK │ • Highway Corridor │ • Substation Distance Indexing   │ • Video Walkthrough Demo  │
│                    │   Desert Detection │ • Gun Sizing Module (N_guns)     │ • Presentation for Jury   │
└────────────────────┴────────────────────┴──────────────────────────────────┴───────────────────────────┘
```

### Detailed Phase Breakdown

#### Phase 1: Round 1 Formal Submission (October 29 – October 30, 2026)
* Submission of Methodology Document and Implementation Roadmap via the official Techfest portal.
* Repository hygiene, code freeze for Phase 1, and benchmark validation.

#### Phase 2: Macro EVCR & Corridor Desert Engine (November 1 – November 15, 2026)
* **Deliverable:** `src/macro_evcr_engine.py` & `src/corridor_desert_analyzer.py`.
* Automate the calculation of EV-to-charger ratios across all 700+ districts.
* Execute corridor vector segmentation along the Golden Quadrilateral, NH-44, NH-48, and NH-27.
* Generate a national tabular database of highway charging gaps ($> 25\text{ km}$ and $> 75\text{ km}$).

#### Phase 3: Spatial Grid Siting & Sizing Implementation (November 16 – November 30, 2026)
* **Deliverable:** `src/spatial_siting_engine.py`.
* Implement the AHP Composite Suitability Index (CSI) across candidate grid cells.
* Integrate spatial indexing (R-Tree / KD-Tree) for rapid distance calculation against $224\text{ MB}$ of electrical substations (`india_electricity_final.csv`).
* Run the gun sizing equation across the top 100 national deficit corridor segments.

#### Phase 4: Unified Decision-Support Platform & Finale Preparation (December 1 – December 15, 2026)
* **Deliverable:** Interactive Web-Based Decision Support Platform (built with Streamlit / Python / Leaflet):
  1. **Macro Policy View:** State/District choropleth map with live EVCR filters, historical VAHAN charts, and 2030 forecasted targets.
  2. **Corridor Inspector:** Highway selector displaying red-flagged "Charging Deserts" and greenfield/brownfield candidate pins.
  3. **Site Recommendation Card:** Detailed breakdown for any selected grid point showing CSI score, distance to nearest substation ($11\text{kV}/33\text{kV}$), nearest CPO competitor, and recommended $60\text{ kW}$ gun count.
* Record high-definition demonstration video and prepare the final presentation slide deck for the expert jury at IIT Bombay.

---

## 7. Software Architecture & Technology Stack

```
┌────────────────────────────────────────────────────────────────────────┐
│                          TECHNOLOGY STACK                              │
├───────────────────┬────────────────────────────────────────────────────┤
│ GIS & Spatial     │ GDAL / OGR, Osmium Toolchain (C++), GeoPandas,     │
│ Computing         │ Shapely, PyProj, Rtree Spatial Indexing            │
├───────────────────┼────────────────────────────────────────────────────┤
│ Data Processing & │ Python 3.11+, Pandas, NumPy, Scipy (AHP Eigenvalue │
│ Analytics         │ Solver), OpenPyXL                                  │
├───────────────────┼────────────────────────────────────────────────────┤
│ Web GIS &         │ Folium / Leaflet.js, OpenStreetMap Carto Tiles,    │
│ Visualization     │ Streamlit / Dash Interactive Web Framework         │
├───────────────────┼────────────────────────────────────────────────────┤
│ Data Scraping &   │ Playwright (Chromium Automation), Requests,        │
│ Extraction        │ Beautiful Soup, CKAN Client                        │
└───────────────────┴────────────────────────────────────────────────────┘
```

---

## 8. Authoritative References & Standards

1. **Ministry of Power (MoP), Government of India:** *Charging Infrastructure for Electric Vehicles - Revised Consolidated Guidelines & Standards* (January 2022 / PM E-DRIVE 2024).
2. **NITI Aayog, Ministry of Power, BEE, & WRI India:** *Handbook for Electric Vehicle Charging Infrastructure Implementation* (2021).
3. **Bureau of Energy Efficiency (BEE):** *National EV Charging Infrastructure Database and State Nodal Agency (SNA) Operational Reports* (2024–2026).
4. **International Energy Agency (IEA):** *Global EV Outlook: Public Charging Infrastructure Metrics and Vehicle-to-Charger Ratios* (2023/2024).
5. **Ministry of Heavy Industries (MHI):** *PM Electric Drive Revolution in Innovative Vehicle Enhancement (PM E-DRIVE) Scheme Notification* (October 2024).
6. **Saaty, Thomas L.:** *The Analytic Hierarchy Process: Planning, Priority Setting, Resource Allocation*, McGraw-Hill (1980).

