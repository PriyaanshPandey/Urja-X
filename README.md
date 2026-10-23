# ⚡ Urja-X: India Electric Vehicle (EV) Infrastructure & Mobility Intelligence

**Urja-X** is an end-to-end open data and geospatial intelligence platform for India's Electric Vehicle (EV) charging ecosystem, National Highway corridors, and vehicular mobility data.

---

## 📁 Repository Structure

```
Urja-X/
├── EV-Charger/                  # Nationwide EV charging infrastructure dataset
│   └── india_ev_charging_raw.csv # 39,600+ verified EV charging stations (CPO, kW, connector, GPS)
│
├── EV-Vehicle/                  # EV sales and registration datasets
│   ├── EV Sales Data.xlsx       # Comprehensive EV sales benchmarks
│   ├── scrape_vahan.py          # Vahan scraping utilities
│   ├── charging_infra_raw/      # Charging infrastructure raw data
│   ├── opencity_ev_data/        # OpenCity state/district-level vehicle registrations
│   └── vahan_raw_data/          # Year-wise Vahan fuel and registration figures
│
├── EV-Roads/                    # OpenStreetMap spatial corridor extraction pipeline
│   ├── filter_and_export.py     # Automated Osmium + GDAL GeoPackage extraction script
│   ├── table_viewer.py          # Interactive table viewer for expressways, NH, and fuel stations
│   ├── visualize_ev_infrastructure.py # Interactive web map visualizer & analytics engine
│   ├── Urja_X_Infrastructure.qgs# Pre-styled QGIS project file (ready to double-click & view)
│   ├── ev_corridors_map.html    # Interactive Leaflet web map (highways + fuel stations)
│   └── README.md                # Dedicated EV-Roads documentation
│
├── EV-Population/               # WorldPop 1km gridded population density & corridor demographics
│   ├── data/                    # WorldPop GeoTIFF (excluded from Git via .gitignore)
│   ├── download_worldpop.py     # Automated streaming downloader for India GeoTIFF
│   ├── population_table_viewer.py # Demographic density & EV spacing table viewer
│   └── README.md                # Population metrics & methodology
│
└── EV-NightLights/              # NOAA/VIIRS night-time lights & economic vitality indicators
    ├── data/                    # Radiance GeoTIFFs (excluded from Git via .gitignore)
    ├── gee_export_india_ntl.js  # Headless Google Earth Engine export script
    ├── nightlights_table_viewer.py # Corridor economic radiance & commercial viability table viewer
    └── README.md                # Night-time lights documentation
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

## 🚀 How to Reproduce & Extract GeoPackages Locally

Because raw OSM binary files and processed GeoPackages are several gigabytes in size, they are kept locally (via `.gitignore`). Any user can reproduce them in minutes:

### 1. Environment Setup
Install the spatial tools using Conda:
```bash
# Create conda environment with Osmium and GDAL
conda create -n osm -c conda-forge osmium-tool gdal python=3.11 -y
conda activate osm

# Install visualization packages
pip install folium geopandas pandas shapely
```

### 2. Download the India OpenStreetMap Dataset
Download the whole India OSM PBF file (~1.6 GB) from Geofabrik:
```powershell
cd EV-Roads
curl.exe -L -C - -o india-latest.osm.pbf https://download.geofabrik.de/asia/india-latest.osm.pbf
```

### 3. Run the Extraction Pipeline
Run either the Python or PowerShell pipeline:
```bash
# Using Python
python filter_and_export.py

# Or using PowerShell (Windows)
.\filter_and_export.ps1
```
This automatically extracts:
- `india_highways.gpkg`
- `india_nh.gpkg`
- `india_corridors.gpkg`
- `india_pois.gpkg`
- `india_roads.gpkg`

---

## 📊 Visualizing the Data

### Option A: Interactive Web Map (Browser)
Generate and open the Leaflet web map:
```bash
python visualize_ev_infrastructure.py
```
Open `ev_corridors_map.html` in your browser. Features include:
- 🛣️ **National Highway Network Overlay** (Golden corridors)
- ⚡ **39,000+ EV Chargers** categorized by Fast DC (`>=25 kW` green bolt) vs Standard AC (blue plug)
- 🔥 **Heatmap Density View** showing charging gaps along highway routes
- 🔍 **Interactive Popups**: CPO name, capacity (kW), connector type, city, and state

### Option B: QGIS (Professional GIS Desktop)
1. Install [QGIS](https://qgis.org/) (free, open source).
2. Double-click **`EV-Roads/Urja_X_Infrastructure.qgs`**.
3. All layers (National Highways, Rail Corridors, POIs, Major Highways) load automatically with custom styling and spatial indexing.

---

## 📈 Analytics Snapshot

From our nationwide integration of EV charging and highway networks:
- **Total Verified EV Stations**: 39,640 stations across all states and Union Territories.
- **Fast DC Chargers (>=25 kW)**: 8,894 units.
- **Top CPOs**: IOCL (8,363), UJOY (7,644), BPCL (6,617), Reliance BP (3,635), Tata Power (3,240).
- **Leading States by Infrastructure**: Karnataka (8,246), Maharashtra (5,747), Delhi (3,475), Haryana (2,873), Uttar Pradesh (2,612).
- **Dense Highway Corridors**: NH 44 (Kanyakumari–Srinagar), NH 48 (Delhi–Chennai), NH 27 (Porbandar–Silchar), NH 19 (Delhi–Kolkata).

---

## 📄 License
Data derived from OpenStreetMap Contributors under [ODbL 1.0](https://opendatacommons.org/licenses/odbl/).
Urja-X codebase is released under the MIT License.
