# EV-Population: India Population Density & Corridor Demographics

This module extracts, processes, and analyzes high-resolution gridded population density across India's National Highway network and Expressways using the **WorldPop Global 1km Dataset**.

---

## 📊 Dataset Specifications
- **Source**: [WorldPop Hub / HDX](https://data.worldpop.org/GIS/Population_Density/Global_2000_2020_1km/2020/IND/)
- **Resolution**: 1 km grid (approx 30 arc-seconds)
- **Local File**: `data/ind_pd_2020_1km.tif` (17.24 MB GeoTIFF)
- **Metric**: People per square kilometer ($ppl / km^2$)

---

## 🚀 Usage

### 1. Download WorldPop GeoTIFF
```powershell
python download_worldpop.py
```

### 2. View Highway Corridor Population Density Table
```powershell
# View top 25 corridors ranked by population density
python population_table_viewer.py

# Filter specific highway corridor (e.g., NH44, NH48, MPE)
python population_table_viewer.py --filter "NH44"
python population_table_viewer.py --filter "NH48"
```

---

## 📈 Catchment Classification & EV Hub Spacing Metrics

| Population Density (Mean) | Catchment Profile | Recommended EV Fast Charging Spacing |
|---|---|---|
| **$\ge$ 2,000 ppl/km²** | 🔴 Mega-Urban Core | ⚡ Every 15 – 25 km (High throughput DC fast hubs) |
| **800 – 2,000 ppl/km²** | 🟠 High-Density Industrial | ⚡ Every 25 – 40 km (Standard multi-bay fast hubs) |
| **300 – 800 ppl/km²** | 🟡 Medium Intercity | ⚡ Every 40 – 60 km |
| **$<$ 300 ppl/km²** | 🟢 Low-Density Rural / Mountain | ⚡ Every 60 – 80 km |
