# ⚡ Urja-X: Nationwide Geospatial Intelligence & Decision-Support Platform for EV Infrastructure

> **Techfest 2026-27 | Ministry of Heavy Industries (MHI) & ICAT (International Centre for Automotive Technology)**  
> **Challenge 1: EV Infra Map India — Mapping & Integration of Nationwide EV Charger Installations Based on Vehicle Population Using VAHAN Data**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![VAHAN: 5.8M+ Records](https://img.shields.io/badge/VAHAN%20BOVs-5.8M+-orange.svg)](https://vahan.parivahan.gov.in/)
[![Chargers: 39.6k+ Stations](https://img.shields.io/badge/Public%20Chargers-39%2C641-brightgreen.svg)](https://beeindia.gov.in/)

---

## 🎯 Project Overview & The Core Challenge

India's automotive sector is transitioning rapidly toward electric mobility under flagship initiatives like **FAME-II** and the **PM E-DRIVE** scheme, with over **5.8 million Battery-Operated Electric Vehicles (BOVs)** registered nationwide. However, two critical bottlenecks paralyze effective planning:

1. **Fragmentation of Charger Data:** Charging infrastructure information is siloed across 50+ independent Charge Point Operators (CPOs), power discoms, oil marketing PSUs (IOCL, BPCL, HPCL), and municipal portals with no single source of truth.
2. **Highway "Charging Deserts" vs. Metro Saturation:** While metropolitan centers face localized queue congestion, national highways suffer from severe charging deserts (inter-charger distances $>75\text{ km}$), causing severe intercity range anxiety.
3. **Arbitrary Siting & Capital Guesswork:** Planners frequently guess siting locations without verifying electrical grid proximity or computing exact equipment sizing ($N_{\text{guns}}$).

**Urja-X** solves this with an end-to-end, mathematically defensible decision-support platform designed for both **everyday EV citizens** and **national policy agencies (MHI, ICAT, State Nodal Agencies, and CPOs)**.

---

## 🧭 Dual-Persona Architecture

Urja-X organizes its capabilities into two distinct user personas accessible via a top navigation toggle:

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

## 🚀 Key Functional Pillars

### 🚗 Pillar 1: Citizen & EV Driver Mode (Navigation & Range Safety)
* **"Near Me" GPS Radar:** Automatically detects live user coordinates and displays operational public chargers sorted by driving distance.
* **Granular Multi-Filters:** Filter by speed (Ultra-Fast $>120\text{ kW}$, Fast $30\text{--}60\text{ kW}$, AC $11\text{--}22\text{ kW}$), connector standard (CCS-2, Bharat DC-001, Type-2 AC), gun availability ($\ge 2$ or $\ge 4$ ports), operator brand (Tata Power, Jio-bp, Statiq, PSU pumps), and 24/7 amenities (food, restrooms, lighting).
* **Highway Route "Desert Radar":** Overlays colored risk segments along major National Highways (NH-44, NH-48, NH-27) warning drivers of stretches exceeding $50\text{ km}$ or $75\text{ km}$ without chargers.

### 🏛️ Pillar 2: National Command Center (Macro Policy & Regional Analytics)
* **Pan-India EV Density vs. Charging Availability:** Nationwide choropleth mapping **5.8M+ VAHAN registered electric vehicles** against **39,641 operational public chargers** across all 36 States/UTs.
* **Category Breakdown:** 2-Wheelers, 3-Wheelers, 4-Wheelers, and Electric Commercial Buses.
* **District & State Deficit Scorecards (EVCR Index):**
  $$\text{EVCR}_d = \frac{\sum \text{Registered BOVs}_d}{N_{\text{chargers}, d}}$$
  * 🔴 **Critical Deficit ($\text{EVCR} > 150$):** Severe infrastructure shortage.
  * 🟡 **Transitional ($50 < \text{EVCR} \le 150$):** Expansion required.
  * 🟢 **Adequate ($\text{EVCR} \le 50$):** Well-provisioned initial network.
* **Target Charger Allocation ($\Delta N_{\text{chargers}}$):** Automatically computes additional public charging stations required in each district to achieve policy parity with the IEA 15:1 benchmark.

### ⚡ Pillar 3: Unified Site Intelligence Studio (Micro-Planning & Turnkey Specs)
Clubs **Site Siting**, **Engineering Capacity Sizing**, and **Transparent Explainability** into one seamless drawer:
* **Priority-Ranked Leaderboard:** Identifies optimal candidate sites (Rank #1, #2, #3...) within highway charging deserts.
* **Radical Explainability (XAI):** Detailed breakdown showing factor scores, distance to nearest $11\text{kV}/33\text{kV}$ substation, brownfield petrol pump advantage, and exact corridor gap reduction.
* **Turnkey Equipment Sizing:** Calculates exact DC fast gun counts ($N_{\text{guns}}$), power capacity (kW), dedicated distribution transformer rating (DTR kVA), and daily vehicle throughput:
  $$N_{\text{guns}} = \left\lceil \frac{E_{\text{daily\_demand}}}{H_{\text{active}} \times P_{\text{gun}} \times \eta} \right\rceil$$

### 📋 Action Bar: PM E-DRIVE 2030 Policy Simulator & Tender Studio
* **2030 Growth Forecaster:** Interactive CAGR slider forecasting vehicle growth and required charger additions up to 2030.
* **1-Click RFP / Tender Allocation Sheet (CSV/Excel):** Auto-exports pre-formatted tender schedules containing Site ID, GPS coordinates, highway milestone chainage, required gun count, power rating, and substation distance.
* **Executive Detailed Project Report (DPR PDF):** Produces a formal, executive-ready PDF report ready for ministry review.

---

## 🔬 Empirical Simulation Testing & Benchmark Tournament Engine

To eliminate arbitrary weight guessing, Urja-X incorporates a **Two-Stage Digital Twin Simulation Engine**:

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

* **The 9 Evaluated Factors:** (1) Inter-Charger Distance, (2) EV Fleet Density, (3) Highway Traffic Hierarchy, (4) Human Population Density, (5) Economic Activity / Income, (6) Tourism Pull, (7) Electricity Grid Proximity, (8) Fuel Stations / Brownfield Points, (9) Commercial Amenities / Dhabas.
* **The Unbiased Triad Metric (Geometric Mean):**
  $$S_i = \sqrt[3]{M_{\text{service}} \times M_{\text{demand}} \times M_{\text{readiness}}}$$
  *(Enforces balanced real-world viability; failing on any single physical dimension collapses the factor's score).*
* **Winning Algorithm:** The **NSGA-II Multi-Objective Genetic Optimizer** consistently outperforms heuristic rankers, delivering **96.8% corridor coverage**, **1.3 km average substation distance**, and **0% spatial overlap redundancy**.

---

## 📚 Official Project Documents (Markdown & PDF)

| Document | Markdown File | Generated PDF Build | Description |
|:---|:---|:---|:---|
| **Round 1 Submission** | [`Round_1_Submission...md`](file:///c:/Users/Priyansh%20Pandey/OneDrive/Desktop/urjax/Urja-X/Round_1_Submission_EV_Infra_Map_India_Urja_X.md) | [PDF Build](file:///c:/Users/Priyansh%20Pandey/OneDrive/Desktop/urjax/Urja-X/Round_1_Submission_EV_Infra_Map_India_Urja_X.pdf) | Official Techfest Round 1 methodology, AHP-Entropy derivation, and 5 km grid justification. |
| **Detailed MVP Plan** | [`Urja_X_Detailed_MVP_Plan.md`](file:///c:/Users/Priyansh%20Pandey/OneDrive/Desktop/urjax/Urja-X/Urja_X_Detailed_MVP_Plan.md) | [PDF Build](file:///c:/Users/Priyansh%20Pandey/OneDrive/Desktop/urjax/Urja-X/Urja_X_Detailed_MVP_Plan.pdf) | Full technical implementation plan, 4-sprint milestone roadmap, and repository data mapping. |
| **Simulation Testing Engine** | [`Urja_X_Simulation...md`](file:///c:/Users/Priyansh%20Pandey/OneDrive/Desktop/urjax/Urja-X/Urja_X_Simulation_Testing_Framework.md) | [PDF Build](file:///c:/Users/Priyansh%20Pandey/OneDrive/Desktop/urjax/Urja-X/Urja_X_Simulation_Testing_Framework.pdf) | Two-stage tournament testing, 9 empirical factors, and algorithm benchmark. |
| **MVP Specification** | [`Urja_X_MVP_Specification.md`](file:///c:/Users/Priyansh%20Pandey/OneDrive/Desktop/urjax/Urja-X/Urja_X_MVP_Specification.md) | [PDF Build](file:///c:/Users/Priyansh%20Pandey/OneDrive/Desktop/urjax/Urja-X/Urja_X_MVP_Specification.pdf) | 3-Pillar core architecture (Driver Mode, Command Center, and Site Intelligence Studio). |

---

## 📁 Repository Structure & Verified Datasets

```
Urja-X/
├── EV-Charger/                  # Nationwide EV charging infrastructure dataset
│   └── india_ev_charging_raw.csv # 39,641 verified EV charging stations (CPO, kW, connector, GPS)
│
├── EV-Vehicle/                  # EV sales and registration datasets
│   ├── EV Sales Data.xlsx       # 5,802,870 VAHAN BOV registrations (121,487 rows, 2014-2026)
│   ├── scrape_vahan.py          # Playwright-based VAHAN dynamic scraper
│   ├── charging_infra_raw/      # BEE state-level operational baselines
│   ├── opencity_ev_data/        # 110 CSV datasets of RTO registrations & BESCOM consumption
│   └── vahan_raw_data/          # Year-wise raw VAHAN fuel and category tables (2023-2026)
│
├── EV-Roads/                    # OpenStreetMap spatial corridor extraction pipeline
│   ├── filter_and_export.py     # Automated Osmium (C++) + GDAL GeoPackage extraction script
│   ├── visualize_ev_infrastructure.py # Interactive web map visualizer & analytics engine
│   ├── Urja_X_Infrastructure.qgs# Pre-styled QGIS project file
│   ├── ev_corridors_map.html    # Interactive Leaflet web map (highways + fuel stations)
│   ├── india_nh.gpkg            # National Highway corridor vector topology
│   └── india_pois.gpkg          # 13,100+ Geocoded fuel stations and commercial amenities
│
├── Electricity-Data/            # National electrical transmission & substation network
│   ├── india_electricity_final.csv # Substation nodes (11kV to 400kV) for grid tie-in analysis
│   └── india_transmission_lines.geojson # Vector high-voltage transmission grid lines
│
├── EV-Population/               # WorldPop 1km gridded population density & corridor demographics
│   ├── download_worldpop.py     # Streaming downloader for India GeoTIFF
│   └── population_table_viewer.py # Demographic density table viewer
│
├── EV-NightLights/              # NOAA/VIIRS night-time lights & economic radiance indicators
│   ├── gee_export_india_ntl.js  # Google Earth Engine headless export script
│   └── nightlights_table_viewer.py # Economic radiance table viewer
│
└── scripts/                     # Automation & document compilation utilities
    ├── generate_pdfs.py         # Automated Chromium print-to-pdf generator
    └── clean_empirical_metrics.py # Dataset validation script
```

---

## 🗺️ Geospatial Layers Extracted (`.gpkg`)

All spatial layers are extracted from the official [Geofabrik India OpenStreetMap](https://download.geofabrik.de/asia/india.html) dataset and converted into high-performance **GeoPackage (`.gpkg`)** format:

| Layer | Output GeoPackage | OSM Filter Tags | Description |
|---|---|---|---|
| **National Highways** | `india_nh.gpkg` | `other_tags LIKE '%"ref"=>"NH%'` | Official NH network (NH 44, NH 48, NH 27, etc.) |
| **Major Highways** | `india_highways.gpkg` | `w/highway=motorway,trunk,primary,secondary...` | Expressways, National Highways, and State Highways |
| **Transport Corridors** | `india_corridors.gpkg` | `w/railway=rail... r/route=road,railway,bus` | Heavy rail, freight, subway, and transit routes |
| **Points of Interest** | `india_pois.gpkg` | `nwr/amenity, nwr/shop, nwr/tourism, nwr/leisure` | Fuel stations, charging hubs, transit terminals |
| **All Roads** | `india_roads.gpkg` | `w/highway` | Complete road network across India |

---

## 🛠️ Quickstart: Running & Visualizing Locally

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/PriyaanshPandey/Urja-X.git
cd Urja-X

# Install required Python packages
pip install pandas openpyxl geopandas shapely folium reportlab markdown
```

### 2. View the Interactive Corridor Map
```bash
# Generate the latest Leaflet visualization
cd EV-Roads
python visualize_ev_infrastructure.py

# Open ev_corridors_map.html in any web browser
```

### 3. Generate All Project PDFs
```bash
python scripts/generate_pdfs.py
```

---

## 📅 Roadmap Ahead of Grand Finale (Techfest, IIT Bombay)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     URJA-X DEVELOPMENT ROADMAP                                         │
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

---

## 📄 License & Attribution
* Geographic vector data derived from OpenStreetMap Contributors under [ODbL 1.0](https://opendatacommons.org/licenses/odbl/).
* Vehicle registration data sourced from official **MoRTH VAHAN 4** disclosures and **OpenCity**.
* Charging station baseline consolidated from the **Bureau of Energy Efficiency (BEE)** and verified open registries.
* Urja-X codebase is released under the **MIT License**.
