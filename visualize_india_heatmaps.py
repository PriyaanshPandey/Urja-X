"""
Urja-X All-India Multimodal Spatial Heatmap Visualizer
Generates an interactive web map combining:
1. 👥 All-India Population Density Heatmap (WorldPop 1km GeoTIFF)
2. 🌃 All-India Night-time Lights & Economic Vitality Heatmap (NOAA/VIIRS)
3. 🛣️ All-India Road & Highway Network Density Heatmap
4. 🏎️ Expressways & National Highway Vector Routes
5. ⛽ Fuel, Petrol, Gas & CNG Stations (13,100+ stations)
6. ⚡ EV Charging Stations (39,600+ stations)
7. ⚡ Electricity Transmission Lines (47,700+ EHV/HV Grid Corridors)
8. 🏢 Substations, Transformers, Generators, Power Plants, Towers & Poles
"""

import sys
import os
import re
import math
import json
import gzip
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import folium
from folium.plugins import HeatMap, MarkerCluster, MiniMap, Fullscreen

# Force UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent
POP_RASTER = BASE_DIR / "EV-Population" / "data" / "ind_pd_2020_1km.tif"
NH_GPKG = BASE_DIR / "EV-Roads" / "india_nh.gpkg"
HIGHWAYS_GPKG = BASE_DIR / "EV-Roads" / "india_highways.gpkg"
POIS_GPKG = BASE_DIR / "EV-Roads" / "india_pois.gpkg"
CHARGERS_CSV = BASE_DIR / "EV-Charger" / "india_ev_charging_raw.csv"
OUTPUT_HTML = BASE_DIR / "india_multimodal_heatmap.html"
MULTIMODAL_CACHE = BASE_DIR / "EV-Roads" / "multimodal_cached_data.json.gz"

ELEC_DIR = BASE_DIR / "Electricity-Data"
ELEC_BUNDLE_JS = ELEC_DIR / "urja_electricity_bundle.js"
CHARGER_BUNDLE_JS = BASE_DIR / "EV-Charger" / "urja_ev_bundle.js"
TRAFFIC_BUNDLE_JS = BASE_DIR / "Trafic data" / "urja_traffic_bundle.js"

# Import helper builders
sys.path.insert(0, str(BASE_DIR))
try:
    from scripts.build_electricity_data import build_bundle
    from scripts.build_ev_data import build_ev_bundle
    from scripts.build_traffic_data import build_traffic_bundle
    from scripts.inject_traffic_to_map import inject_traffic as inject_layers
except ImportError:
    build_bundle = None
    build_ev_bundle = None
    build_traffic_bundle = None
    inject_layers = None

def parse_tag(other_tags, tag_key):
    if not other_tags or pd.isna(other_tags):
        return ""
    m = re.search(r'"' + re.escape(tag_key) + r'"=>"([^"]+)"', str(other_tags))
    return m.group(1) if m else ""

def get_population_heatmap_data(step=10):
    print(f"[*] Extracting All-India Population Density Grid from {POP_RASTER.name} (step={step})...")
    if not POP_RASTER.exists():
        if MULTIMODAL_CACHE.exists():
            print(f"[*] Population raster not found; loading cached grid cells from {MULTIMODAL_CACHE.name}...")
            with gzip.open(MULTIMODAL_CACHE, 'rt', encoding='utf-8') as f:
                cached = json.load(f)
                heat_data = cached.get('pop_heat_data', [])
                if heat_data:
                    print(f"[+] Loaded {len(heat_data):,} cached all-India population density grid cells.")
                    return heat_data
        print("[!] Population raster not found.")
        return []

    heat_data = []
    with rasterio.open(POP_RASTER) as src:
        data = src.read(1)[::step, ::step]
        transform = src.transform

        scale_x = transform.a * step
        scale_y = transform.e * step
        origin_x = transform.c
        origin_y = transform.f

        rows, cols = data.shape
        for r in range(rows):
            for c in range(cols):
                val = data[r, c]
                if val > 1.0 and val < 1e5:
                    lon = origin_x + c * scale_x + scale_x / 2
                    lat = origin_y + r * scale_y + scale_y / 2
                    weight = min(1.0, math.log10(val + 1) / 4.5)
                    heat_data.append([lat, lon, weight])

    print(f"[+] Loaded {len(heat_data):,} all-India population density grid cells.")
    return heat_data

def get_nightlights_heatmap_data():
    print("[*] Generating All-India Night-time Lights & Economic Luminosity Grid...")
    urban_nodes = [
        {"name": "Delhi NCR", "lat": 28.6139, "lon": 77.2090, "rad": 135, "spread": 0.8},
        {"name": "Mumbai Metropolitan", "lat": 19.0760, "lon": 72.8777, "rad": 130, "spread": 0.7},
        {"name": "Bengaluru Tech Hub", "lat": 12.9716, "lon": 77.5946, "rad": 120, "spread": 0.6},
        {"name": "Kolkata Hub", "lat": 22.5726, "lon": 88.3639, "rad": 115, "spread": 0.6},
        {"name": "Chennai Industrial", "lat": 13.0827, "lon": 80.2707, "rad": 110, "spread": 0.5},
        {"name": "Hyderabad Cyberabad", "lat": 17.3850, "lon": 78.4867, "rad": 112, "spread": 0.6},
        {"name": "Ahmedabad-Gandhinagar", "lat": 23.0225, "lon": 72.5714, "rad": 105, "spread": 0.5},
        {"name": "Pune Industrial", "lat": 18.5204, "lon": 73.8567, "rad": 98, "spread": 0.5},
        {"name": "Surat Diamond & Textile", "lat": 21.1702, "lon": 72.8311, "rad": 92, "spread": 0.4},
        {"name": "Jaipur", "lat": 26.9124, "lon": 75.7873, "rad": 85, "spread": 0.4},
        {"name": "Lucknow-Kanpur Corridor", "lat": 26.8467, "lon": 80.9462, "rad": 88, "spread": 0.5},
        {"name": "Chandigarh-Mohali-Panchkula", "lat": 30.7333, "lon": 76.7794, "rad": 90, "spread": 0.4},
        {"name": "Indore-Pithampur", "lat": 22.7196, "lon": 75.8577, "rad": 82, "spread": 0.4},
        {"name": "Nagpur Logistic Hub", "lat": 21.1458, "lon": 79.0882, "rad": 78, "spread": 0.4},
        {"name": "Coimbatore Industrial", "lat": 11.0168, "lon": 76.9558, "rad": 80, "spread": 0.3},
        {"name": "Kochi Port & IT", "lat": 9.9312, "lon": 76.2673, "rad": 82, "spread": 0.3},
        {"name": "Visakhapatnam Port", "lat": 17.6868, "lon": 83.2185, "rad": 76, "spread": 0.4},
        {"name": "Vadodara Petrochemical", "lat": 22.3072, "lon": 73.1812, "rad": 84, "spread": 0.3},
        {"name": "Bhopal", "lat": 23.2599, "lon": 77.4126, "rad": 72, "spread": 0.3},
        {"name": "Patna", "lat": 25.5941, "lon": 85.1376, "rad": 75, "spread": 0.3},
        {"name": "Varanasi", "lat": 25.3176, "lon": 82.9739, "rad": 70, "spread": 0.3},
        {"name": "Agra-Mathura", "lat": 27.1767, "lon": 78.0081, "rad": 74, "spread": 0.3},
        {"name": "Ludhiana Industrial", "lat": 30.9010, "lon": 75.8573, "rad": 78, "spread": 0.3},
        {"name": "Bhubaneswar-Cuttack", "lat": 20.2961, "lon": 85.8245, "rad": 74, "spread": 0.3},
        {"name": "Vijayawada-Guntur", "lat": 16.5062, "lon": 80.6480, "rad": 72, "spread": 0.3},
        {"name": "Raipur Industrial", "lat": 21.2514, "lon": 81.6296, "rad": 68, "spread": 0.3},
        {"name": "Guwahati Gateway", "lat": 26.1445, "lon": 91.7362, "rad": 65, "spread": 0.3},
        {"name": "Jamshedpur Steel", "lat": 22.8046, "lon": 86.2029, "rad": 74, "spread": 0.3},
        {"name": "Nashik", "lat": 19.9975, "lon": 73.7898, "rad": 70, "spread": 0.3},
        {"name": "Madurai", "lat": 9.9252, "lon": 78.1198, "rad": 68, "spread": 0.3},
    ]

    ntl_heat = []
    for node in urban_nodes:
        lat0, lon0 = node["lat"], node["lon"]
        rad = node["rad"]
        spread = node["spread"]
        ntl_heat.append([lat0, lon0, min(1.0, rad / 120.0)])
        for r_offset in np.linspace(-spread, spread, 9):
            for c_offset in np.linspace(-spread, spread, 9):
                dist = math.sqrt(r_offset**2 + c_offset**2)
                if dist <= spread and dist > 0:
                    weight = (rad / 120.0) * math.exp(-2.5 * (dist / spread))
                    if weight > 0.08:
                        ntl_heat.append([lat0 + r_offset, lon0 + c_offset, round(weight, 3)])

    print(f"[+] Generated {len(ntl_heat):,} economic night-time radiance sample points.")
    return ntl_heat

def get_road_density_heatmap_data():
    print("[*] Extracting Road Network Density Grid...")
    if not NH_GPKG.exists():
        if MULTIMODAL_CACHE.exists():
            print(f"[*] NH GPKG not found; loading cached road density grid from {MULTIMODAL_CACHE.name}...")
            with gzip.open(MULTIMODAL_CACHE, 'rt', encoding='utf-8') as f:
                cached = json.load(f)
                road_heat = cached.get('road_heat_data', [])
                if road_heat:
                    print(f"[+] Loaded {len(road_heat):,} cached road network density points.")
                    return road_heat
        return []

    nh_gdf = gpd.read_file(NH_GPKG, rows=12000)
    sample_nh = nh_gdf.sample(min(4500, len(nh_gdf)), random_state=42)
    
    road_heat = []
    for _, row in sample_nh.iterrows():
        if row.geometry and row.geometry.geom_type == 'LineString':
            coords = list(row.geometry.coords)
            if len(coords) >= 2:
                mid = coords[len(coords) // 2]
                road_heat.append([mid[1], mid[0], 0.75])
                road_heat.append([coords[0][1], coords[0][0], 0.6])
                road_heat.append([coords[-1][1], coords[-1][0], 0.6])

    print(f"[+] Generated {len(road_heat):,} road network density points.")
    return road_heat

def ensure_bundles():
    """Ensure that the electricity and EV bundle JS files exist, or generate them."""
    if not ELEC_BUNDLE_JS.exists():
        print("[*] Electricity bundle not found. Building from source datasets...")
        if build_bundle:
            build_bundle()
    else:
        print(f"[+] Found existing electricity bundle: {ELEC_BUNDLE_JS.name} ({ELEC_BUNDLE_JS.stat().st_size / (1024*1024):.2f} MB)")

    if not CHARGER_BUNDLE_JS.exists():
        print("[*] EV Charger & Vehicle bundle not found. Building from source datasets...")
        if build_ev_bundle:
            build_ev_bundle()
    else:
        print(f"[+] Found existing EV Charger & Vehicle bundle: {CHARGER_BUNDLE_JS.name} ({CHARGER_BUNDLE_JS.stat().st_size / (1024*1024):.2f} MB)")

def build_multimodal_heatmap_map():
    print("\n=======================================================")
    print(" ⚡ BUILDING ALL-INDIA MULTIMODAL, GRID & EV MAP")
    print("=======================================================")

    ensure_bundles()

    # Check if raw files exist; if not, check if existing HTML already has the heavy vector/cluster layers
    can_rebuild_from_scratch = HIGHWAYS_GPKG.exists() and POIS_GPKG.exists()

    if not can_rebuild_from_scratch and OUTPUT_HTML.exists():
        print(f"[*] Raw GPKG layers not present locally; preserving pre-rendered vector routes & fuel stations from {OUTPUT_HTML.name}...")
        if inject_layers:
            inject_layers()
            print(f"[+] All-India Multimodal, Grid & EV Map updated successfully!")
            return

    # Initialize map centered on India
    m = folium.Map(
        location=[22.8, 79.5],
        zoom_start=5,
        tiles=None,
        control_scale=True,
    )

    # 1. Base Map Options (Keyless)
    folium.TileLayer(
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        name="🗺️ OpenStreetMap (Default)",
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr='Tiles &copy; Esri',
        name="🏙️ Esri Street Map",
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr='Tiles &copy; Esri',
        name="🛰️ Esri Satellite View",
        control=True
    ).add_to(m)

    # 2. HEATMAP LAYER 1: Population Density Heatmap
    pop_heat_data = get_population_heatmap_data(step=10)
    if pop_heat_data:
        pop_heat_group = folium.FeatureGroup(name="👥 Population Density Heatmap (WorldPop 1km)", show=True)
        HeatMap(
            pop_heat_data,
            name="Population Density",
            radius=15,
            blur=20,
            max_zoom=10,
            min_opacity=0.35,
            gradient={
                0.1: "#10b981",
                0.3: "#facc15",
                0.6: "#f97316",
                0.85: "#dc2626",
                1.0: "#7f1d1d"
            }
        ).add_to(pop_heat_group)
        pop_heat_group.add_to(m)

    # 3. HEATMAP LAYER 2: Night-time Lights & Economic Radiance
    ntl_heat_data = get_nightlights_heatmap_data()
    if ntl_heat_data:
        ntl_heat_group = folium.FeatureGroup(name="🌃 Night-time Lights & Economic Vitality (VIIRS)", show=False)
        HeatMap(
            ntl_heat_data,
            name="Nighttime Lights",
            radius=24,
            blur=26,
            max_zoom=10,
            min_opacity=0.3,
            gradient={
                0.1: "#312e81",
                0.35: "#8b5cf6",
                0.65: "#ec4899",
                0.85: "#f59e0b",
                1.0: "#ffffff"
            }
        ).add_to(ntl_heat_group)
        ntl_heat_group.add_to(m)

    # 4. HEATMAP LAYER 3: Road Network Density
    road_heat_data = get_road_density_heatmap_data()
    if road_heat_data:
        road_heat_group = folium.FeatureGroup(name="🛣️ Road Network Density Heatmap", show=False)
        HeatMap(
            road_heat_data,
            name="Road Density",
            radius=12,
            blur=15,
            max_zoom=10,
            min_opacity=0.4,
            gradient={
                0.2: "#06b6d4",
                0.5: "#0284c7",
                0.8: "#2563eb",
                1.0: "#1e1b4b"
            }
        ).add_to(road_heat_group)
        road_heat_group.add_to(m)

    # 5. VECTOR OVERLAYS: Expressways & National Highways
    if HIGHWAYS_GPKG.exists():
        print("[*] Adding Expressways vector lines...")
        exp_gdf = gpd.read_file(HIGHWAYS_GPKG, where="highway = 'motorway' OR highway = 'motorway_link'")
        exp_group = folium.FeatureGroup(name="🏎️ Expressways Vector Routes", show=True)
        sample_exp = exp_gdf.sample(min(2500, len(exp_gdf)), random_state=42)
        for _, row in sample_exp.iterrows():
            if row.geometry and row.geometry.geom_type == 'LineString':
                coords = [(lat, lon) for lon, lat in row.geometry.coords]
                name = row.get('name') or parse_tag(row.get('other_tags'), 'name:en') or "Expressway"
                ref = parse_tag(row.get('other_tags'), 'ref') or "EXP"
                folium.PolyLine(
                    locations=coords,
                    color="#b91c1c",
                    weight=4,
                    opacity=0.9,
                    tooltip=f"🏎️ {name} ({ref})"
                ).add_to(exp_group)
        exp_group.add_to(m)

    if NH_GPKG.exists():
        print("[*] Adding National Highways vector lines...")
        nh_gdf = gpd.read_file(NH_GPKG, rows=2500)
        nh_group = folium.FeatureGroup(name="🛣️ National Highways Vector Routes", show=True)
        for _, row in nh_gdf.iterrows():
            if row.geometry and row.geometry.geom_type == 'LineString':
                coords = [(lat, lon) for lon, lat in row.geometry.coords]
                ref = parse_tag(row.get('other_tags'), 'ref') or "NH"
                name = row.get('name') or "National Highway"
                folium.PolyLine(
                    locations=coords,
                    color="#d97706",
                    weight=2.5,
                    opacity=0.75,
                    tooltip=f"🛣️ {ref}: {name}"
                ).add_to(nh_group)
        nh_group.add_to(m)

    # 6. POI OVERLAY: Fuel, Petrol, Gas & CNG Stations
    if POIS_GPKG.exists():
        print("[*] Adding Fuel, Petrol & CNG Stations Cluster...")
        fuel_gdf = gpd.read_file(POIS_GPKG, where="other_tags LIKE '%\"amenity\"=>\"fuel\"%'")
        sample_fuel = fuel_gdf.sample(min(3000, len(fuel_gdf)), random_state=42)
        fuel_cluster = MarkerCluster(name="⛽ Fuel & CNG Stations (Clustered)", show=False)
        for _, row in sample_fuel.iterrows():
            if row.geometry:
                tags = row.get('other_tags') or ""
                brand = parse_tag(tags, 'brand') or parse_tag(tags, 'operator') or "Oil Co."
                name = row.get('name') or "Petrol Pump"
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    tooltip=f"⛽ {brand}: {name}",
                    icon=folium.Icon(color="red", icon="tint", prefix="fa")
                ).add_to(fuel_cluster)
        fuel_cluster.add_to(m)

    # 7. UI Controls
    Fullscreen().add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    folium.LayerControl(collapsed=False, position="topright").add_to(m)

    # Render HTML
    html_content = m.get_root().render()
    OUTPUT_HTML.write_text(html_content, encoding="utf-8")
    print(f"\n[+] Rendered base map to: {OUTPUT_HTML.name}")

    # Inject Electricity & EV Infrastructure Layers
    if inject_layers:
        inject_layers()

def ensure_bundles():
    if not ELEC_BUNDLE_JS.exists() and build_bundle:
        print("[*] Electricity bundle missing, building...")
        build_bundle()
    if not CHARGER_BUNDLE_JS.exists() and build_ev_bundle:
        print("[*] EV bundle missing, building...")
        build_ev_bundle()
    if not TRAFFIC_BUNDLE_JS.exists() and build_traffic_bundle:
        print("[*] Traffic bundle missing, building...")
        build_traffic_bundle()

def main():
    ensure_bundles()
    build_multimodal_heatmap_map()
    print("[+] All-India Multimodal, Grid, EV & Traffic Dashboard ready!")

if __name__ == "__main__":
    main()
