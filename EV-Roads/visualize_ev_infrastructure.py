"""
Urja-X Infrastructure Visualizer and Corridor Analysis Engine
Focuses on:
1. Expressways (Yamuna, Mumbai-Pune, Delhi-Mumbai, etc.)
2. National Highways Network (NH 44, NH 48, NH 27, etc.)
3. Transport Corridors & Railways
4. Fuel, Petrol, Gas & CNG Stations across India
Generates an interactive web map with integrated searchable data tables.
"""

import sys
import io
import re
import json
from pathlib import Path
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap, Fullscreen

# Force UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
POIS_GPKG = BASE_DIR / "india_pois.gpkg"
HIGHWAYS_GPKG = BASE_DIR / "india_highways.gpkg"
NH_GPKG = BASE_DIR / "india_nh.gpkg"
CORRIDORS_GPKG = BASE_DIR / "india_corridors.gpkg"
OUTPUT_HTML = BASE_DIR / "ev_corridors_map.html"
REPORT_MD = BASE_DIR / "infrastructure_analysis_report.md"

def parse_tag(other_tags, tag_key):
    if not other_tags or pd.isna(other_tags):
        return ""
    m = re.search(r'"' + re.escape(tag_key) + r'"=>"([^"]+)"', str(other_tags))
    return m.group(1) if m else ""

def generate_interactive_map():
    print("[*] Loading Infrastructure Data from GeoPackages...")

    # Base Map: 100% Free & Keyless OpenStreetMap
    m = folium.Map(
        location=[22.5, 79.5],
        zoom_start=5,
        tiles=None,
        control_scale=True,
    )

    folium.TileLayer(
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        name="OpenStreetMap (Default)",
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr='Tiles &copy; Esri',
        name="Esri World Street Map",
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr='Tiles &copy; Esri',
        name="Esri Satellite View",
        control=True
    ).add_to(m)

    table_records = []

    # 1. Overlay Expressways (Motorways)
    if HIGHWAYS_GPKG.exists():
        print("[*] Processing Expressways (Motorways)...")
        exp_gdf = gpd.read_file(HIGHWAYS_GPKG, where="highway = 'motorway' OR highway = 'motorway_link'")
        exp_group = folium.FeatureGroup(name="🏎️ Expressways (Motorways)", show=True)
        
        sample_exp = exp_gdf.sample(min(3500, len(exp_gdf)), random_state=42) if len(exp_gdf) > 3500 else exp_gdf
        for _, row in sample_exp.iterrows():
            if row.geometry and row.geometry.geom_type == 'LineString':
                coords = [(lat, lon) for lon, lat in row.geometry.coords]
                name = row.get('name') or parse_tag(row.get('other_tags'), 'name:en') or "Expressway"
                ref = parse_tag(row.get('other_tags'), 'ref') or "Expressway"
                speed = parse_tag(row.get('other_tags'), 'maxspeed') or "100-120"
                lanes = parse_tag(row.get('other_tags'), 'lanes') or "4-8"

                folium.PolyLine(
                    locations=coords,
                    color="#dc2626", # Bold crimson
                    weight=4,
                    opacity=0.9,
                    tooltip=f"<b>Expressway:</b> {name} ({ref}) | {lanes} Lanes | Max {speed} km/h"
                ).add_to(exp_group)
        exp_group.add_to(m)

    # 2. Overlay National Highways
    if NH_GPKG.exists():
        print("[*] Processing National Highways (NH)...")
        nh_gdf = gpd.read_file(NH_GPKG)
        nh_group = folium.FeatureGroup(name="🛣️ National Highways Network (NH)", show=True)
        
        sample_nh = nh_gdf.sample(min(3000, len(nh_gdf)), random_state=42) if len(nh_gdf) > 3000 else nh_gdf
        for _, row in sample_nh.iterrows():
            if row.geometry and row.geometry.geom_type == 'LineString':
                coords = [(lat, lon) for lon, lat in row.geometry.coords]
                tags = row.get('other_tags') or ""
                ref = parse_tag(tags, 'ref') or "NH"
                name = row.get('name') or "National Highway"

                folium.PolyLine(
                    locations=coords,
                    color="#f59e0b", # Amber/Gold
                    weight=3,
                    opacity=0.8,
                    tooltip=f"<b>{ref}</b>: {name}"
                ).add_to(nh_group)
        nh_group.add_to(m)

    # 3. Overlay Transport Corridors (Railways & Transit)
    if CORRIDORS_GPKG.exists():
        print("[*] Processing Transport & Rail Corridors...")
        corr_gdf = gpd.read_file(CORRIDORS_GPKG, rows=5000)
        corr_group = folium.FeatureGroup(name="🚆 Transport & Rail Corridors", show=False)
        
        for _, row in corr_gdf.iterrows():
            if row.geometry and row.geometry.geom_type == 'LineString':
                coords = [(lat, lon) for lon, lat in row.geometry.coords]
                name = row.get('name') or "Indian Railways Corridor"
                folium.PolyLine(
                    locations=coords,
                    color="#0284c7", # Cyan/Blue
                    weight=2.5,
                    dash_array='4, 4',
                    opacity=0.75,
                    tooltip=f"<b>Transit Corridor:</b> {name}"
                ).add_to(corr_group)
        corr_group.add_to(m)

    # 4. Overlay Fuel, Petrol, Gas & CNG Stations
    if POIS_GPKG.exists():
        print("[*] Processing Fuel, Petrol, Gas & CNG Stations...")
        fuel_gdf = gpd.read_file(POIS_GPKG, where="other_tags LIKE '%\"amenity\"=>\"fuel\"%'")
        print(f"[+] Total Fuel/Gas Stations in database: {len(fuel_gdf):,}")

        # Fuel station cluster
        fuel_cluster = MarkerCluster(
            name="⛽ Fuel, Petrol, Gas & CNG Stations",
            show=True,
            options={'maxClusterRadius': 40}
        )

        # Heatmap of fuel availability
        fuel_heat_data = [[row.geometry.y, row.geometry.x, 1] for _, row in fuel_gdf.iterrows() if row.geometry]
        fuel_heatmap = folium.FeatureGroup(name="🔥 Fuel Station Density Heatmap", show=False)
        HeatMap(fuel_heat_data, radius=14, blur=18, min_opacity=0.3).add_to(fuel_heatmap)
        fuel_heatmap.add_to(m)

        sample_fuel = fuel_gdf.sample(min(4000, len(fuel_gdf)), random_state=42) if len(fuel_gdf) > 4000 else fuel_gdf
        for _, row in sample_fuel.iterrows():
            if not row.geometry:
                continue
            lat = row.geometry.y
            lon = row.geometry.x
            tags = row.get('other_tags') or ""
            name = row.get('name') or "Petrol Pump / Fuel Station"
            brand = parse_tag(tags, 'brand') or parse_tag(tags, 'operator') or "Oil Marketing Co."
            
            # Detect fuel types
            fuels = []
            if parse_tag(tags, 'fuel:cng') == 'yes': fuels.append("CNG")
            if parse_tag(tags, 'fuel:diesel') == 'yes': fuels.append("Diesel")
            if parse_tag(tags, 'fuel:octane_91') == 'yes' or parse_tag(tags, 'fuel:petrol') == 'yes': fuels.append("Petrol")
            if parse_tag(tags, 'fuel:lpg') == 'yes': fuels.append("Auto LPG")
            fuel_desc = ", ".join(fuels) if fuels else "Petrol & Diesel"

            popup_html = f"""
            <div style="font-family: sans-serif; font-size: 12px; width: 230px;">
                <h4 style="margin: 0 0 6px 0; color: #b91c1c;">
                    ⛽ {brand}
                </h4>
                <b>Station:</b> {name}<br>
                <b>Available Fuels:</b> <span style="color: #047857; font-weight: bold;">{fuel_desc}</span><br>
                <b>Coordinates:</b> {lat:.4f}, {lon:.4f}<br>
                <small style="color: #64748b;">OSM ID: {row.get('osm_id')}</small>
            </div>
            """

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"⛽ {brand}: {name}",
                icon=folium.Icon(color="red", icon="tint", prefix="fa")
            ).add_to(fuel_cluster)

        fuel_cluster.add_to(m)

    # UI Controls
    Fullscreen().add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    # Embed Searchable HTML Data Table
    print("[*] Generating Data Table HTML overlay...")
    html_content = m.get_root().render()

    # Build data table preview
    table_preview_rows = []
    if POIS_GPKG.exists():
        sample_for_table = fuel_gdf.head(100)
        for _, r in sample_for_table.iterrows():
            tags = r.get('other_tags') or ""
            b = parse_tag(tags, 'brand') or parse_tag(tags, 'operator') or "Oil Co."
            table_preview_rows.append(f"""
            <tr>
                <td>⛽ Fuel Station</td>
                <td><b>{b}</b></td>
                <td>{r.get('name') or 'Fuel Station'}</td>
                <td>{r.geometry.y:.4f}, {r.geometry.x:.4f}</td>
            </tr>
            """)

    custom_table_panel = f"""
    <div id="data-drawer" style="
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        max-height: 280px;
        background: #0f172a;
        color: #e2e8f0;
        z-index: 9999;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.5);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        border-top: 2px solid #38bdf8;
        display: flex;
        flex-direction: column;
    ">
        <div style="padding: 8px 16px; background: #1e293b; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 600; font-size: 14px; color: #38bdf8;">
                📊 Urja-X Infrastructure Data Explorer (13,162 Fuel Stations | 24,604 Expressway Segments | 137,531 NH Segments)
            </span>
            <span style="font-size: 12px; color: #94a3b8;">
                To view full tables in terminal: <code>python table_viewer.py fuel</code>
            </span>
        </div>
        <div style="overflow-y: auto; padding: 10px 16px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                <thead>
                    <tr style="border-bottom: 2px solid #334155; color: #38bdf8;">
                        <th style="padding: 6px;">Category</th>
                        <th style="padding: 6px;">Brand / Route</th>
                        <th style="padding: 6px;">Name / Details</th>
                        <th style="padding: 6px;">Latitude, Longitude</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(table_preview_rows[:40])}
                </tbody>
            </table>
        </div>
    </div>
    """

    # Inject panel into rendered HTML
    html_content = html_content.replace("</body>", f"{custom_table_panel}</body>")
    OUTPUT_HTML.write_text(html_content, encoding="utf-8")
    print(f"[+] Saved updated interactive map to: {OUTPUT_HTML.name}")

def main():
    generate_interactive_map()
    print("\n[+] Infrastructure Visualizer successfully updated!")

if __name__ == "__main__":
    main()
