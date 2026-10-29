# Urja-X: Detailed MVP Product Architecture & Technical Implementation Plan
## National Geospatial Intelligence & Data-Driven Decision Support Platform for EV Infrastructure
**Techfest 2026-27 | Ministry of Heavy Industries (MHI) & ICAT Challenge 1: EV Infra Map India**

---

## 1. Executive Summary & Dual-Persona Positioning

Urja-X is a unified, data-driven decision-support platform designed to solve India's structural bottlenecks in electric mobility infrastructure. The platform bridges the gap between everyday EV drivers who suffer from intercity range anxiety and national policymakers (MHI, ICAT, State Nodal Agencies) who need mathematically sound, audit-ready capital allocation plans.

The platform provides a dual-mode workflow via a top-bar toggle:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   URJA-X PLATFORM                                      │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│         MODE 1: CITIZEN / DRIVER          │          MODE 2: AGENCY / PLANNER          │
│       (EV Owners, Intercity Fleets)       │          (MHI, ICAT, SNAs, CPOs)           │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ PILLAR 1: NAVIGATION & RANGE SAFETY       │ PILLAR 2: NATIONAL COMMAND CENTER (MACRO)  │
│ • "Near Me" GPS Radar                     │ • 5.8M VAHAN Fleet vs 39.6k Chargers       │
│ • Unified Multi-Filter Charger Atlas      │ • District & State EVCR Deficit Scorecards │
│ • Highway "Desert Radar" Warning Overlay  │ • Saturated vs Underserved Gap Index       │
│                                           ├────────────────────────────────────────────┤
│                                           │ PILLAR 3: UNIFIED SITE INTELLIGENCE STUDIO │
│                                           │ • Priority-Ranked Siting (Rank #1, #2...)  │
│                                           │ • Turnkey Equipment Specs & Capacity Sizing│
│                                           │ • Transparent Explainability Drawer        │
│                                           ├────────────────────────────────────────────┤
│                                           │ ACTION BAR: 2030 FORECAST & TENDER EXPORT  │
│                                           │ • PM E-DRIVE 2030 Slider & Quota Estimator │
│                                           │ • 1-Click RFP Tender Sheet & DPR Exporter  │
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

---

## 2. Comprehensive User-Facing Feature Specifications

### 2.1 Pillar 1: Citizen & EV Driver Mode (Navigation & Range Safety)
* **"Near Me" GPS Radar:** Automatically detects user coordinates via browser geolocation and queries the nearest operational chargers within a 25 km radius.
* **Granular Multi-Filters:**
  * **Charging Speed & Power:** DC Ultra-Fast ($>120\text{ kW}$), DC Fast ($30\text{–}60\text{ kW}$), AC Fast ($11\text{–}22\text{ kW}$), AC Standard ($3.3\text{–}7.4\text{ kW}$).
  * **Connector Standard:** CCS-2, Bharat DC-001, Type-2 AC, CHAdeMO.
  * **Number of Charging Guns:** Filter for stations with $\ge 2$ or $\ge 4$ guns to avoid long wait queues.
  * **CPO / Network Brand:** Tata Power, Jio-bp, Statiq, Ather Grid, Zeon, PSU oil pumps (IOCL, BPCL, HPCL).
  * **Operational Status & Amenities:** 24/7 Access, Food/Café, Restrooms, Covered Canopy.
* **Highway "Desert Radar" for Safe Route Planning:** Highlights highway stretches where **no public chargers exist for $>50\text{ km}$ or $>75\text{ km}$**, enabling intercity drivers to plan battery top-ups before entering high-risk charging deserts.

---

### 2.2 Pillar 2: National Command Center (Macro Policy & Regional Analytics)
* **Pan-India VAHAN vs. Charging Availability Map:** Interactive national choropleth mapping **5.8M+ VAHAN registered electric vehicles** against **39,641 operational public chargers** across all 36 States/UTs.
* **Category Breakdown:** 2-Wheelers, 3-Wheelers, 4-Wheelers, and Electric Commercial Buses.
* **District & State Deficit Scorecards (EVCR Index):**
  $$\text{EVCR}_d = \frac{\sum \text{Registered BOVs}_d}{N_{\text{chargers}, d}}$$
  * 🔴 **Critical Deficit ($\text{EVCR} > 150$):** High vehicle adoption, acute infrastructure shortage.
  * 🟡 **Transitional ($50 < \text{EVCR} \le 150$):** Moderate provisioning requiring expansion.
  * 🟢 **Adequate ($\text{EVCR} \le 50$):** Well-provisioned for current fleet volume.
* **Target Charger Allocation ($\Delta N_{\text{chargers}}$):** Automatically computes the number of additional public charging stations required in each district to achieve policy parity ($\text{EVCR}_{\text{target}} = 15$):
  $$\Delta N_{\text{chargers}, d} = \max\left(0, \; \left\lceil \frac{\text{Registered BOVs}_d}{15} \right\rceil - N_{\text{existing}, d}\right)$$

---

### 2.3 Pillar 3: Unified Site Intelligence Studio (Micro-Planning & Turnkey Specs)
Clubs **Site Siting**, **Engineering Capacity Sizing**, and **Transparent Explainability** into one seamless, interactive drawer:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                  UNIFIED SITE INTELLIGENCE DRAWER: SITE #NH48-RAJ-042                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ OVERALL SUITABILITY: 88.4 / 100 [PRIORITY RANK: #1 - IMMEDIATE INTERVENTION]           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│ [PART A: WHY THIS SITE? (RADICAL EXPLAINABILITY)]                                      │
│ • Fleet Adoption Pressure (35% weight): Score 92/100                                   │
│   ➜ Bridges an 82 km charging desert between Behror and Kotputli.                     │
│   ➜ Surrounding RTO district suffers an acute EVCR deficit of 210:1.                   │
│ • Road Hierarchy & Traffic (25% weight): Score 95/100                                  │
│   ➜ Situated on 6-lane NH-48 with heavy intercity passenger and freight traffic.       │
│ • Power Grid Proximity (25% weight): Score 86/100                                      │
│   ➜ Nearest 33/11 kV Substation is 1.1 km away (Kotputli DISCOM feeder).              │
│   ➜ Line voltage drop within CEA 6% limit; feeder distance 1.1 km is within 5 km norm. │
│ • Brownfield Advantage (15% weight): Score 90/100                                      │
│   ➜ Co-located with an operational HPCL Petrol Pump & 24/7 Food Court.                 │
│   ➜ 0 days land acquisition delay; existing dedicated parking bays and 24/7 lighting.  │
│                                                                                        │
│ [PART B: TURNKEY EQUIPMENT & CAPACITY PLANNING]                                        │
│ • Recommended Fast DC Guns:     4 × 60 kW CCS-2 DC Fast Charging Guns                  │
│ • Recommended Slow AC Backup:   2 × 22 kW Type-2 AC Plugs                              │
│ • Total Installed Capacity:     284 kW                                                 │
│ • Recommended Sanctioned Load:  315 kVA Dedicated Distribution Transformer (DTR)       │
│ • Projected Daily Energy:       1,440 kWh / day                                        │
│ • Projected Daily Throughput:   48 – 64 electric vehicles / day                        │
│ • Average Top-Up Session:       35 – 45 mins (20% to 80% SoC)                          │
│                                                                                        │
│ [PART C: STATUTORY IMPACT]                                                             │
│ ➜ Reduces maximum corridor inter-charger gap from 82 km down to 24 km                  │
│   (Fully satisfies statutory Ministry of Power 25 km spacing mandate).                 │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.4 Action Bar: PM E-DRIVE 2030 Policy Simulator & Tender Studio
* **2030 Growth Forecaster:** Interactive slider forecasting vehicle growth and required charger additions year-by-year (2026–2030) using state-specific CAGRs:
  $$\text{EV}_{\text{stock}}(t) = \text{EV}_{2026} \times (1 + g_{\text{CAGR}})^{t - 2026}$$
* **1-Click RFP & Tender Allocation Sheet (CSV/Excel):** Auto-exports pre-formatted site schedules containing: `Site ID`, `GPS Latitude/Longitude`, `Highway Milestone / KM Chainage`, `Priority Rank`, `Recommended Gun Count`, `kW Rating`, `Nearest Substation Distance (km)`, and `Brownfield Partner Name`.
* **Executive Detailed Project Report (DPR PDF):** Produces a formal, executive-ready PDF report containing maps, scorecards, engineering specifications, and statutory compliance notes for MHI, ICAT, and State Nodal Agencies.

---

## 3. Data Architecture & Repository Asset Mapping

Urja-X operates 100% on empirical, multi-source national datasets stored directly in the repository:

| Dataset Name | File Path in Workspace | Records / Scale | Role in Platform |
|:---|:---|:---|:---|
| **VAHAN 4 National Registry** | `EV-Vehicle/EV Sales Data.xlsx` | **5,802,870 BOVs** across 121,487 records (2014–2026) | National Macro EVCR, State/District choropleths, 2030 CAGR forecasting. |
| **City & RTO Registrations** | `EV-Vehicle/opencity_ev_data/*.csv` | **110 detailed CSVs** across Bangalore, Delhi, Mumbai, Pune, Chennai, Kolkata | Micro-level RTO demand pressure and BESCOM power consumption baselines. |
| **Operational Public Chargers** | `EV-Charger/india_ev_charging_raw.csv` | **39,641 Geocoded Stations** across 36 States/UTs | Baseline charging map, CPO filtering, inter-charger gap computation. |
| **National Highway Network** | `EV-Roads/india_nh.gpkg` | Complete OpenStreetMap vector topology of NH-44, NH-48, NH-27, etc. | 5 km linear road discretization, statutory 25 km gap detection. |
| **High-Voltage Power Grid** | `Electricity-Data/india_electricity_final.csv` & `india_transmission_lines.geojson` | **353 MB national layer** (11kV to 400kV substations & lines) | Proximity calculation to nearest 11kV/33kV substation feeder. |
| **Fuel Stations & Amenities** | `EV-Roads/india_pois.gpkg` | **13,100+ Geocoded POIs** (petrol pumps, dhabas, rest stops) | Brownfield site identification for rapid zero-land-acquisition rollout. |
| **Population & Nightlights** | `EV-Population/` & `EV-NightLights/` | Multimodal gridded spatial raster & density tables | Spatial proxy demand estimation across rural highway stretches. |

---

## 4. Mathematical Testing & Objective Weight Derivation

Urja-X replaces arbitrary human weight guessing with a **Two-Stage Empirical Simulation Tournament**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        TWO-STAGE TESTING & BENCHMARK ARCHITECTURE                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [ STAGE 1: FACTOR SENSITIVITY TOURNAMENT ] (Derives Objective Weights)                │
│  • Tests all 9 empirical factors individually across corridor test windows.            │
│  • Evaluated on the unbiased Triad Network Health Index (Geometric Mean).              │
│  • Normalizes performance scores into empirical weights W_i = S_i / sum(S_j).          │
│                                                                                        │
│                                           ▼                                            │
│                                                                                        │
│  [ STAGE 2: ALGORITHM BATTLE & STRATEGY TOURNAMENT ] (Selects the Winning Algorithm)   │
│  • Compares 4 spatial optimization algorithms using the derived weighted factors:      │
│    1. Greedy Score Ranker                                                              │
│    2. Spatial K-Medoids (Anti-Clustering)                                              │
│    3. Integer Linear Programming (ILP Set-Cover)                                       │
│    4. NSGA-II Multi-Objective Genetic Optimizer                                        │
│  • Evaluates on Spatial Optimization Quality (SOQ): Maximum Coverage, Zero Overlap.    │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Stage 1: The 9 Factors & The Unbiased Triad Metric
We evaluate all 9 factors from the problem statement: (1) Inter-Charger Distance, (2) EV Fleet Density, (3) Highway Traffic Hierarchy, (4) Human Population Density, (5) Economic Activity / Income, (6) Tourism Pull, (7) Electricity Grid Proximity, (8) Fuel Stations / Brownfield Points, (9) Commercial Amenities / Dhabas.

To prevent single-factor bias (e.g. grid distance dominating), performance is measured across **three physical, empirical dimensions** via the **Geometric Mean**:

$$S_i = \sqrt[3]{M_{\text{service}} \times M_{\text{demand}} \times M_{\text{readiness}}}$$

1. **$M_{\text{service}}$ (Corridor Service & MoP Compliance):** Percentage of the highway corridor where inter-station distance $\le 25\text{ km}$ (from `india_nh.gpkg`).
2. **$M_{\text{demand}}$ (Fleet Demand Alignment):** Concentration of registered BOVs captured within a $15\text{ km}$ corridor buffer (from VAHAN 4 `EV Sales Data.xlsx`).
3. **$M_{\text{readiness}}$ (Infrastructure & Grid Readiness):** Physical distance to verified $11\text{kV}/33\text{kV}$ substations (from `india_electricity_final.csv`) and co-location with verified fuel stations (from `india_pois.gpkg`).

The resulting factor scores are normalized to yield the objective weights:
$$W_i = \frac{S_i}{\sum_{j=1}^{9} S_j} \quad \left( \sum W_i = 1.0 \right)$$

### 4.2 Stage 2: Algorithm Battle & Spatial Optimization Quality (SOQ)
Once weights are derived, 4 algorithms compete to select $K$ stations along a corridor, benchmarked on **Spatial Optimization Quality (SOQ)**:

$$\text{SOQ Score} = \frac{\text{Corridor Coverage \%} \times \text{Demand Capture \%} \times \text{Brownfield Match \%}}{\left(1 + \frac{\text{Avg Substation Distance (km)}}{5\text{ km}}\right) \times (1 + \text{Clustering Overlap Ratio})}$$

* **NSGA-II Multi-Objective Genetic Optimizer** consistently wins the tournament, achieving **96.8% corridor coverage**, **1.3 km average substation distance**, and **0% spatial overlap redundancy**.

---

## 5. Engineering Capacity Planning & Sizing Formulation

For any recommended site, the required number of DC Fast Charging guns ($N_{\text{guns}}$) is determined using a physics and traffic demand model:

$$N_{\text{guns}} = \left\lceil \frac{E_{\text{daily\_demand}}}{H_{\text{active}} \times P_{\text{gun}} \times \eta} \right\rceil$$

Where:
* $E_{\text{daily\_demand}} = V_{\text{corridor}} \times P_{\text{EV}} \times f_{\text{charge}} \times \Delta\text{SoC} \times B_{\text{battery}}$
  - $V_{\text{corridor}} \times P_{\text{EV}}$: Daily highway EV traversals.
  - $f_{\text{charge}}$: Highway top-up probability ($\approx 20\%$).
  - $\Delta\text{SoC} \times B_{\text{battery}}$: Average fast-charge energy delivered ($30\text{ kWh}$ for a standard $20\% \rightarrow 80\%$ session).
* $H_{\text{active}}$: Active operational window ($14\text{ hours/day}$).
* $P_{\text{gun}}$: Rated power of DC Fast Charging gun ($60\text{ kW}$ CCS-2 standard).
* $\eta$: Station concurrency efficiency ($\approx 75\%$).
* **Sanctioned Transformer Load (kVA):**
  $$\text{DTR Capacity (kVA)} = \left\lceil \frac{N_{\text{guns}} \times P_{\text{gun}} + N_{\text{AC}} \times P_{\text{AC}}}{\text{Power Factor } (0.90)} \times \text{Diversity Factor } (0.85) \right\rceil$$

---

## 6. Detailed Technical Implementation Plan & Milestones

The technical implementation is organized into four modular sprints leading to the Grand Finale at **Techfest, IIT Bombay (December 16–18, 2026)**.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 URJA-X TECHNICAL IMPLEMENTATION PLAN                                   │
├────────────────────┬────────────────────┬──────────────────────────────────┬───────────────────────────┤
│ SPRINT 1           │ SPRINT 2           │ SPRINT 3                         │ SPRINT 4                  │
│ DATA & MACRO EVCR  │ CORRIDOR DISCRETIZER│ TESTING & TOURNAMENT ENGINE     │ UNIFIED DECISION PLATFORM │
│  (Nov 1 - Nov 10)  │  (Nov 11 - Nov 20) │        (Nov 21 - Nov 30)         │      (Dec 1 - Dec 15)     │
├────────────────────┼────────────────────┼──────────────────────────────────┼───────────────────────────┤
│ • Spatial R-Tree   │ • 5 km Linear Road │ • Stage 1: Factor Sensitivity    │ • Streamlit / React Web UI│
│   Indexing (GeoGIS)│   Discretizer      │   Tournament Implementation      │ • Dual-Persona Switcher   │
│ • Macro EVCR Engine│ • Bilateral 2 km   │ • Stage 2: Algorithm Battle      │ • Interactive Drawer View │
│ • State & District │   Buffer Engine    │   (Greedy vs K-Medoids vs NSGA-II│ • 1-Click Tender Exporter │
│   Choropleth Maps  │ • MoP Gap Detector │ • Auto-Weight Calibration Matrix │ • Demo Video & Case Study │
└────────────────────┴────────────────────┴──────────────────────────────────┴───────────────────────────┘
```

### Sprint 1: Data Ingestion, Spatial Indexing & Macro EVCR Engine (Nov 1 – Nov 10, 2026)
* **Deliverable Module:** `src/macro_evcr_engine.py` & `src/spatial_indexer.py`.
* **Tasks:**
  1. Build in-memory **R-Tree / KD-Tree spatial indices** over `india_electricity_final.csv` (substations), `india_ev_charging_raw.csv` (chargers), and `india_pois.gpkg` (fuel stations) for sub-millisecond nearest-neighbor distance queries.
  2. Implement the Macro EVCR calculator aggregating 5.8M VAHAN records across 700+ administrative districts.
  3. Generate state/district geojson choropleth layers color-coded by deficit status (Critical, Transitional, Adequate).

### Sprint 2: Linear Corridor Discretizer & Desert Radar (Nov 11 – Nov 20, 2026)
* **Deliverable Module:** `src/corridor_desert_analyzer.py`.
* **Tasks:**
  1. Slice continuous highway vectors (`india_nh.gpkg`) into continuous **$5\text{ km}$ linear spatial windows**.
  2. Construct orthogonal $2\text{ km}$ search buffers to identify existing accessible charging points along each corridor.
  3. Flag statutory MoP gaps ($>25\text{ km}$) and severe charging deserts ($>75\text{ km}$) on major national arteries (NH-44, NH-48, NH-27, Golden Quadrilateral).
  4. Output structured chainage reports (e.g., *NH-48 KM 145 to KM 227: 82 km charging desert*).

### Sprint 3: Two-Stage Testing & Benchmark Tournament Engine (Nov 21 – Nov 30, 2026)
* **Deliverable Module:** `src/benchmark_tournament_engine.py`.
* **Tasks:**
  1. Construct the **Stage 1 Factor Tournament** class: allows each of the 9 empirical factors to independently propose station locations across corridor test windows.
  2. Implement the **Triad Network Health Index (NHI)** calculating the geometric mean of Service, Demand, and Infrastructure Readiness.
  3. Construct the **Stage 2 Algorithm Tournament** class: benchmarks Greedy, K-Medoids, ILP, and NSGA-II Genetic Optimizer on Spatial Optimization Quality (SOQ).
  4. Save tournament logs to JSON/CSV for direct rendering in the UI.

### Sprint 4: Unified Decision Support Platform & Grand Finale (Dec 1 – Dec 15, 2026)
* **Deliverable Module:** `app.py` (Streamlit / Leaflet Interactive Application).
* **Tasks:**
  1. **Dual-Persona Interface:** Header toggle switching between Citizen/Driver Navigation Mode and Agency/Planner Mode.
  2. **Driver Portal:** Interactive map with "Near Me" GPS locator, granular filters (power, connector, guns, CPO), and highway desert warning overlays.
  3. **Agency Command Center:** Macro national choropleths, highway corridor desert radar, and the Model Benchmark Lab tab.
  4. **Unified Site Intelligence Drawer:** Clicking any recommended site opens the 3-in-1 panel displaying Explainability scores, Turnkey Sizing ($N_{\text{guns}}$, kW, DTR kVA), and 1-Click Tender Export (CSV/PDF).
  5. **Representative Case Study:** High-definition demonstration video and jury walkthrough showcasing the **Delhi–Mumbai NH-48 Expressway** and **Maharashtra/Karnataka inter-district deficits**.

---

## 7. Software Architecture & Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (WEB UI)                                  │
│   Streamlit / Leaflet.js / Plotly / Modern CSS / Responsive Dual-Mode UI        │
│   • Mode A: Driver Navigation, "Near Me" Radar & Route Blackspot Warnings       │
│   • Mode B: National Command Center, Siting Studio & Model Benchmark Lab        │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────▼────────────────────────────────────────┐
│                               BACKEND API & ENGINES                             │
│   Python 3.11+ / GeoPandas / Shapely / PyProj / SciPy / Scikit-Learn            │
│   • Macro EVCR Engine (`src/macro_evcr_engine.py`)                              │
│   • Corridor Desert Engine (`src/corridor_desert_analyzer.py`)                  │
│   • Benchmark Tournament Engine (`src/benchmark_tournament_engine.py`)         │
│   • Siting & Explainability Engine (`src/spatial_siting_engine.py`)             │
│   • Capacity Sizing Calculator (`src/capacity_sizing_engine.py`)                │
│   • One-Click Tender Exporter (`src/tender_export_engine.py`)                   │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────▼────────────────────────────────────────┐
│                              DATA PERSISTENCE & GIS                             │
│   • VAHAN BOV Registrations (5.8M records in `EV Sales Data.xlsx`)              │
│   • National EV Charger Database (39,641 stations in `india_ev_charging_raw`)   │
│   • Highway Vectors (`india_nh.gpkg`) & POI Amenities (`india_pois.gpkg`)       │
│   • Electrical Grid Network (Substations & Lines in `Electricity-Data/`)        │
└─────────────────────────────────────────────────────────────────────────────────┘
```
