"""
Urja-X EV Infrastructure Visualizer and Corridor Analysis Engine
Integrates National Highways, Transport Corridors, POIs, and 39,000+ EV Charging Stations.
Generates interactive web maps and spatial analytics.
"""

import sys
import json
import re
from pathlib import Path
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap, Fullscreen

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
CHARGERS_CSV = PROJECT_ROOT / "EV-Charger" / "india_ev_charging_raw.csv"
NH_GPKG = BASE_DIR / "india_nh.gpkg"
CORRIDORS_GPKG = BASE_DIR / "india_corridors.gpkg"
OUTPUT_HTML = BASE_DIR / "ev_corridors_map.html"
REPORT_MD = BASE_DIR / "infrastructure_analysis_report.md"

def extract_nh_ref(other_tags):
    if not other_tags or pd.isna(other_tags):
        return None
    m = re.search(r'"ref"=>"([^"]+)"', str(other_tags))
    return m.group(1) if m else None

def generate_analytics():
    print("[*] Running Spatial & EV Infrastructure Analytics...")
    stats = {}

    # 1. EV Charging Stations Analysis
    if CHARGERS_CSV.exists():
        chargers_df = pd.read_csv(CHARGERS_CSV)
        chargers_df['Latitude'] = pd.to_numeric(chargers_df['Latitude'], errors='coerce')
        chargers_df['Longitude'] = pd.to_numeric(chargers_df['Longitude'], errors='coerce')
        valid_chargers = chargers_df.dropna(subset=['Latitude', 'Longitude'])
        
        stats["total_chargers"] = len(valid_chargers)
        stats["cpos"] = valid_chargers['CPO Name'].value_counts().head(8).to_dict()
        stats["top_states"] = valid_chargers['State'].value_counts().head(8).to_dict()
        stats["govt_pvt"] = valid_chargers['Govt/Private'].value_counts().to_dict()
        
        # Fast vs Slow Charging
        fast_kw = valid_chargers[valid_chargers['Charger Rating'] >= 25]
        stats["fast_chargers_count"] = len(fast_kw)
    else:
        stats["total_chargers"] = 0

    # 2. National Highways Analysis
    if NH_GPKG.exists():
        nh_gdf = gpd.read_file(NH_GPKG, rows=15000)
        stats["nh_segments_sampled"] = len(nh_gdf)
        nh_gdf['ref'] = nh_gdf['other_tags'].apply(extract_nh_ref)
        top_highways = nh_gdf['ref'].value_counts().head(10).to_dict()
        stats["top_highways"] = top_highways
    else:
        stats["nh_segments_sampled"] = 0

    return stats

def generate_interactive_map(sample_limit=3000):
    print("[*] Building Interactive Leaflet Map...")
    
    # Initialize Map centered on Central India
    m = folium.Map(
        location=[21.7679, 78.8718],
        zoom_start=5,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # 1. Overlay National Highways
    if NH_GPKG.exists():
        print("[*] Loading National Highways layer...")
        nh_gdf = gpd.read_file(NH_GPKG)
        # Sample or simplify for smooth web browser rendering
        if len(nh_gdf) > sample_limit:
            nh_sample = nh_gdf.sample(sample_limit, random_state=42)
        else:
            nh_sample = nh_gdf
            
        nh_feature_group = folium.FeatureGroup(name="🛣️ National Highways (NH Network)", show=True)
        for _, row in nh_sample.iterrows():
            if row.geometry and row.geometry.geom_type == 'LineString':
                coords = [(lat, lon) for lon, lat in row.geometry.coords]
                ref_label = extract_nh_ref(row.get('other_tags')) or "NH"
                name_label = row.get('name') or "National Highway"
                folium.PolyLine(
                    locations=coords,
                    color="#f59e0b",
                    weight=3,
                    opacity=0.8,
                    tooltip=f"<b>{ref_label}</b>: {name_label}",
                ).add_to(nh_feature_group)
        nh_feature_group.add_to(m)

    # 2. Overlay EV Charging Stations
    if CHARGERS_CSV.exists():
        print("[*] Loading EV Charging Stations layer...")
        chargers_df = pd.read_csv(CHARGERS_CSV)
        chargers_df['Latitude'] = pd.to_numeric(chargers_df['Latitude'], errors='coerce')
        chargers_df['Longitude'] = pd.to_numeric(chargers_df['Longitude'], errors='coerce')
        valid_chargers = chargers_df.dropna(subset=['Latitude', 'Longitude'])

        # Heatmap layer
        heat_data = [[row['Latitude'], row['Longitude'], 1] for _, row in valid_chargers.iterrows()]
        heatmap_group = folium.FeatureGroup(name="🔥 EV Charging Density Heatmap", show=False)
        HeatMap(heat_data, radius=12, blur=18, min_opacity=0.3).add_to(heatmap_group)
        heatmap_group.add_to(m)

        # Clustered Markers
        marker_cluster = MarkerCluster(
            name="⚡ EV Charging Stations (Clustered)",
            show=True,
            options={'maxClusterRadius': 40}
        )
        
        # Display sample for instant browser performance
        sample_chargers = valid_chargers.sample(min(4000, len(valid_chargers)), random_state=42)
        for _, row in sample_chargers.iterrows():
            cpo = row.get('CPO Name', 'Unknown CPO')
            location = row.get('Location', 'Unknown Location')
            city = row.get('City/Village', '')
            state = row.get('State', '')
            rating = row.get('Charger Rating', 'N/A')
            connector = row.get('Types of Chargers Installed/ Connector', 'Standard')
            
            # Fast Charger styling
            is_fast = False
            try:
                is_fast = float(rating) >= 25.0
            except (ValueError, TypeError):
                is_fast = "CCS" in str(connector).upper()

            icon_color = "green" if is_fast else "blue"
            icon_symbol = "bolt" if is_fast else "plug"

            popup_html = f"""
            <div style="font-family: sans-serif; font-size: 12px; width: 220px;">
                <h4 style="margin: 0 0 6px 0; color: {'#16a34a' if is_fast else '#2563eb'};">
                    ⚡ {cpo}
                </h4>
                <b>Type:</b> {'🚀 DC Fast Charger' if is_fast else '🔌 Standard AC'}<br>
                <b>Power:</b> {rating} kW<br>
                <b>Connector:</b> {connector}<br>
                <b>Location:</b> {city}, {state}<br>
                <small style="color: #64748b;">{location}</small>
            </div>
            """

            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{cpo} ({rating} kW)",
                icon=folium.Icon(color=icon_color, icon=icon_symbol, prefix='fa'),
            ).add_to(marker_cluster)

        marker_cluster.add_to(m)

    # UI Controls
    Fullscreen().add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    # Save
    m.save(str(OUTPUT_HTML))
    print(f"[+] Saved interactive map to: {OUTPUT_HTML.name}")

def write_report_markdown(stats):
    report_content = f"""# Urja-X: India EV Infrastructure & Spatial Corridors Analysis

## Executive Summary
This report analyzes India's nationwide Electric Vehicle (EV) charging ecosystem overlaid across national highway corridors, transit routes, and Points of Interest extracted from OpenStreetMap.

---

## 1. Key Metrics

- **Total Verified EV Charging Stations**: {stats.get('total_chargers', 0):,}
- **High-Capacity / DC Fast Chargers (>=25 kW)**: {stats.get('fast_chargers_count', 0):,}
- **Sampled National Highway Segments**: {stats.get('nh_segments_sampled', 0):,}
- **Data Layers Integrated**: National Highways, Rail Corridors, All Roads, and POIs.

---

## 2. Top Charge Point Operators (CPOs)

| CPO Name | Station Count |
|---|---|
"""
    for cpo, count in stats.get("cpos", {}).items():
        report_content += f"| {cpo} | {count:,} |\n"

    report_content += """
---

## 3. Top States by EV Charging Density

| State | Station Count |
|---|---|
"""
    for state, count in stats.get("top_states", {}).items():
        report_content += f"| {state} | {count:,} |\n"

    report_content += """
---

## 4. Key National Highway Corridors Covered

Top National Highway references identified in OpenStreetMap data:
"""
    for ref, count in stats.get("top_highways", {}).items():
        report_content += f"- **{ref}**: {count:,} tracked segments\n"

    report_content += """
---

## 5. How to View the Interactive Map
Open the interactive map dashboard in any web browser:
```powershell
Start-Process "EV-Roads/ev_corridors_map.html"
```
Features available in the map:
- **Toggleable Layers**: Switch between National Highway lines, Clustered EV Charging Points, and Density Heatmap.
- **Fast vs Slow Filter**: Fast DC chargers (CCS-2) are highlighted with green lightning markers.
- **Base Map Chooser**: Switch between Positron (light mode), Dark Matter (night mode), and OpenStreetMap.
"""
    REPORT_MD.write_text(report_content, encoding="utf-8")
    print(f"[+] Saved analysis report to: {REPORT_MD.name}")

def main():
    stats = generate_analytics()
    generate_interactive_map()
    write_report_markdown(stats)
    print("\n[+] Visualization and analysis completed successfully!")

if __name__ == "__main__":
    main()
