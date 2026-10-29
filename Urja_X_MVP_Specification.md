# Urja-X: Simplified MVP Product Specification
**National Geospatial Intelligence & Data-Driven Decision Support Platform for EV Infrastructure**  
*Aligned with Ministry of Heavy Industries (MHI), ICAT, and Techfest 2026-27 Guidelines*

---

## 1. Product Overview & Dual-Persona Architecture

Urja-X streamlines national EV charging planning into **three core functional pillars** serving two distinct user personas through a simple toggle switch:

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

## 2. Pillar 1: Citizen & EV Driver Mode (Navigation & Range Safety)

Designed for everyday EV owners, commercial cab fleets, and intercity travelers.

### 2.1 Unified EV Charger Map with "Near Me" GPS Radar
* **"Near Me" GPS Locator:** One-click GPS toggle automatically centers on the driver's current position and returns operational public chargers sorted by driving distance.
* **Granular Multi-Filters:**
  * **Charging Speed & Power:** DC Ultra-Fast ($>120\text{ kW}$), DC Fast ($30\text{–}60\text{ kW}$), AC Fast ($11\text{–}22\text{ kW}$), AC Standard ($3.3\text{–}7.4\text{ kW}$).
  * **Connector Standard:** CCS-2, Bharat DC-001, Type-2 AC, CHAdeMO.
  * **Number of Charging Guns:** Filter for stations with $\ge 2$ or $\ge 4$ guns to avoid long wait queues.
  * **CPO / Network Brand:** Tata Power, Jio-bp, Statiq, Ather Grid, Zeon, PSU oil pumps (IOCL, BPCL, HPCL).
  * **Operational Status & Amenities:** 24/7 Access, Food/Café, Restrooms, Covered Canopy.

### 2.2 Highway "Desert Radar" for Safe Route Planning
* **Visual Highway Blackspot Overlay:** Renders colored risk segments along major expressways and National Highways.
* **Driver Range Warning:** Highlights highway stretches where **no public chargers exist for $>50\text{ km}$ or $>75\text{ km}$**, enabling intercity drivers to plan battery top-ups before entering high-risk charging deserts.

---

## 3. Pillar 2: National Command Center (Macro Policy & Regional Analytics)

Designed for the Ministry of Heavy Industries (MHI), ICAT, and State Nodal Agencies (SNAs).

### 3.1 Pan-India VAHAN vs. Charging Availability Map
* Interactive national choropleth mapping **5.8M+ VAHAN registered electric vehicles** against **39,641 operational public chargers** across all 36 States/UTs.
* Category-level breakdown: 2-Wheelers, 3-Wheelers, 4-Wheelers, and Electric Commercial Buses.

### 3.2 District & State Deficit Scorecards (EVCR Index)
* Real-time **EV-to-Charger Ratio (EVCR)** benchmarking against the international **IEA standard (10–20:1)**:
  * 🔴 **Critical Deficit ($\text{EVCR} > 150$):** High vehicle adoption, acute infrastructure shortage.
  * 🟡 **Transitional ($50 < \text{EVCR} \le 150$):** Moderate provisioning requiring expansion.
  * 🟢 **Adequate ($\text{EVCR} \le 50$):** Well-provisioned for current fleet volume.
* **Target Charger Allocation ($\Delta N_{\text{chargers}}$):** Automatically computes the number of additional public charging stations required in each district to achieve policy parity ($\text{EVCR}_{\text{target}} = 15$).

---

## 4. Pillar 3: Unified Site Intelligence Studio (Micro-Planning & Turnkey Specs)

*This is the core engine of Urja-X. It unifies **Site Siting**, **Engineering Capacity Sizing**, and **Transparent Explainability** into one seamless, interactive workflow.*

Inside any selected corridor desert or deficit district, clicking a candidate site pin reveals a comprehensive **Three-in-One Site Intelligence Drawer**:

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
│   ➜ Line voltage drop within CEA 6% limit; feeder distance 1.1 km is well within the 5 km technical limit.           │
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

## 5. Action Bar: PM E-DRIVE 2030 Policy Simulator & Tender Studio

Embedded at the bottom of the Agency portal for instant policy execution:

1. **PM E-DRIVE 2030 Growth Forecaster:**
   * Interactive slider forecasting vehicle growth and required charger additions year-by-year (2026–2030) using state-specific CAGRs.
2. **1-Click RFP & Tender Allocation Sheet (CSV/Excel):**
   * Instant export of structured tender schedules containing: `Site ID`, `GPS Coordinates`, `Nearest Highway Milestone`, `Priority Rank`, `Recommended Gun Count`, `Power Rating (kW)`, `Substation Distance (km)`, and `Brownfield Partner Name`.
3. **Executive Detailed Project Report (DPR PDF):**
   * One-click generation of a formal, executive-ready PDF document containing regional maps, scorecards, engineering specifications, and economic justifications for state and national ministries.

---

## 6. Key Product USPs

| Product Feature | Urja-X Solution | Competitor / Status Quo Limitation |
|---|---|---|
| **Dual-Persona Utility** | Seamlessly serves both everyday EV drivers (route safety) and government agencies (capital planning). | Competitor tools are either pure driver apps or purely theoretical academic dashboards. |
| **Unified Site Intelligence** | Clubs Siting, Capacity Sizing, and Explainability into one turnkey site specification. | Existing tools output isolated pins without equipment sizing or grid feasibility context. |
| **Corridor Desert Radar** | Discretizes linear highway vectors into 5 km windows to pinpoint real-world range anxiety. | Others rely on district centroid circles that fail on linear intercity corridors. |
| **Grid-Feasible Siting** | Pre-evaluates proximity to $11\text{kV}/33\text{kV}$ substations using empirical electrical grid data. | Blind placement on roads lacking high-voltage grid access, causing massive commissioning delays. |
| **Policy-to-Tender Workflow** | One-click export of PM E-DRIVE compliant tender spreadsheets and executive DPRs. | Manual, months-long consulting cycles to translate GIS maps into actionable procurement tenders. |

