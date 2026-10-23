# EV-Roads: OpenStreetMap (OSM) Infrastructure & Spatial Intelligence

This directory provides extraction pipelines, GeoPackage spatial datasets, interactive web visualizers, and QGIS projects for India's roads, highways, transport corridors, and Points of Interest (POIs).

---

## 🗺️ Layers Extracted (`.gpkg`)

| Layer | File Name | Description |
|---|---|---|
| **National Highways** | `india_nh.gpkg` | Filtered National Highway network (`ref` starting with `NH`) |
| **Major Highways** | `india_highways.gpkg` | Expressways, National Highways (NH), State Highways & trunk roads |
| **Transport Corridors** | `india_corridors.gpkg` | Railway tracks, subways, light rail, and primary transit routes |
| **Points of Interest** | `india_pois.gpkg` | Charging stations, fuel stations, bus terminals, public amenities |
| **All Roads (Complete)** | `india_roads.gpkg` | Complete road network across all road classifications |
| **Raw Source File** | `india-latest.osm.pbf` | Original OpenStreetMap extract (~1.71 GB, kept for future filtering) |

---

## 🖥️ Visualization & Analysis

### 1. Interactive Web Map (`ev_corridors_map.html`)
Generate and open the interactive map:
```powershell
python visualize_ev_infrastructure.py
Start-Process "ev_corridors_map.html"
```
- **Layer Controls**: Toggle National Highways, Clustered EV Stations, and Charging Density Heatmap.
- **Fast vs Slow EV Charging**: Fast DC chargers (CCS-2, `>=25 kW`) marked in green; standard chargers marked in blue.
- **Popups**: CPO name, capacity (kW), connector type, city, and state.

### 2. QGIS Project (`Urja_X_Infrastructure.qgs`)
Double-click `Urja_X_Infrastructure.qgs` to open the project in QGIS. All GeoPackage layers will load automatically with pre-configured color schemes:
- **National Highways**: Orange stroke
- **Transport Corridors**: Blue stroke
- **Points of Interest**: Emerald point markers
- **Major Highways**: Red/Amber stroke

---

## ⚡ How to Reproduce Extraction

1. **Install Prerequisites**:
   ```powershell
   conda create -n osm -c conda-forge osmium-tool gdal -y
   conda activate osm
   pip install folium geopandas pandas shapely
   ```

2. **Download OSM PBF**:
   ```powershell
   curl.exe -L -C - -o india-latest.osm.pbf https://download.geofabrik.de/asia/india-latest.osm.pbf
   ```

3. **Run Extraction Pipeline**:
   ```powershell
   # PowerShell
   .\filter_and_export.ps1

   # Or Python
   python filter_and_export.py
   ```

4. **Run Visualizer**:
   ```powershell
   python visualize_ev_infrastructure.py
   ```
