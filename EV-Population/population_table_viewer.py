"""
Urja-X Population Density & Highway Corridor Table Viewer
Integrates WorldPop 1km GeoTIFF raster with National Highways and Expressways.
Displays formatted tables of corridor demographic density and catchment metrics.

Usage:
    python population_table_viewer.py                 # Summary table of all corridors
    python population_table_viewer.py --filter NH44   # Filter specific highway
    python population_table_viewer.py --limit 20      # Limit rows displayed
"""

import sys
import re
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from tabulate import tabulate

# Force UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
POP_RASTER = BASE_DIR / "data" / "ind_pd_2020_1km.tif"
NH_GPKG = PROJECT_ROOT / "EV-Roads" / "india_nh.gpkg"
HIGHWAYS_GPKG = PROJECT_ROOT / "EV-Roads" / "india_highways.gpkg"

def parse_tag(other_tags, tag_key):
    if not other_tags or pd.isna(other_tags):
        return ""
    m = re.search(r'"' + re.escape(tag_key) + r'"=>"([^"]+)"', str(other_tags))
    return m.group(1) if m else ""

def sample_raster_density(src, coords):
    """Sample raster values at given (lon, lat) coordinate pairs."""
    densities = []
    for lon, lat in coords:
        try:
            row, col = src.index(lon, lat)
            if 0 <= row < src.height and 0 <= col < src.width:
                val = src.read(1, window=((row, row+1), (col, col+1)))[0, 0]
                if val > 0 and val < 1e6:
                    densities.append(val)
        except Exception:
            continue
    return densities

def analyze_corridors(limit=25, search_filter=None):
    if not POP_RASTER.exists():
        print(f"[!] Error: {POP_RASTER} not found. Please run download_worldpop.py first.")
        return

    print(f"[*] Analyzing Population Density along Indian Highway Corridors...")
    print(f"    Raster: {POP_RASTER.name} (WorldPop 1km)")

    # Read highway samples
    routes_data = []

    with rasterio.open(POP_RASTER) as src:
        # 1. Expressways
        if HIGHWAYS_GPKG.exists():
            exp_gdf = gpd.read_file(HIGHWAYS_GPKG, where="highway = 'motorway' OR highway = 'motorway_link'")
            sample_exp = exp_gdf.sample(min(800, len(exp_gdf)), random_state=42)
            
            for _, r in sample_exp.iterrows():
                if r.geometry and r.geometry.geom_type == 'LineString':
                    name = r.get('name') or parse_tag(r.get('other_tags'), 'name:en') or "Expressway"
                    ref = parse_tag(r.get('other_tags'), 'ref') or "EXP"
                    pts = list(r.geometry.coords)[::3] # sample points along line
                    vals = sample_raster_density(src, pts)
                    if vals:
                        routes_data.append({
                            "Route Type": "🏎️ Expressway",
                            "Ref": ref,
                            "Corridor / Section": name,
                            "Mean Density (ppl/km²)": round(float(np.mean(vals)), 1),
                            "Peak Density (ppl/km²)": round(float(np.max(vals)), 1),
                            "Length (km)": round(r.geometry.length * 111, 2)
                        })

        # 2. National Highways
        if NH_GPKG.exists():
            nh_gdf = gpd.read_file(NH_GPKG, rows=3000)
            sample_nh = nh_gdf.sample(min(1200, len(nh_gdf)), random_state=42)
            
            for _, r in sample_nh.iterrows():
                if r.geometry and r.geometry.geom_type == 'LineString':
                    tags = r.get('other_tags') or ""
                    ref = parse_tag(tags, 'ref') or "NH"
                    name = r.get('name') or "National Highway"
                    pts = list(r.geometry.coords)[::3]
                    vals = sample_raster_density(src, pts)
                    if vals:
                        routes_data.append({
                            "Route Type": "🛣️ National Highway",
                            "Ref": ref,
                            "Corridor / Section": name,
                            "Mean Density (ppl/km²)": round(float(np.mean(vals)), 1),
                            "Peak Density (ppl/km²)": round(float(np.max(vals)), 1),
                            "Length (km)": round(r.geometry.length * 111, 2)
                        })

    df = pd.DataFrame(routes_data)
    
    # Group by Route Ref to get overall corridor density
    corridor_summary = df.groupby(['Route Type', 'Ref']).agg({
        'Corridor / Section': lambda s: s.iloc[0] if s.iloc[0] != "National Highway" else (s.dropna().iloc[0] if len(s.dropna())>0 else "NH Route"),
        'Mean Density (ppl/km²)': 'mean',
        'Peak Density (ppl/km²)': 'max',
        'Length (km)': 'sum'
    }).reset_index()

    # Add Catchment & Recommended EV Spacing
    def classify_catchment(density):
        if density >= 2000:
            return "🔴 Mega-Urban Core"
        elif density >= 800:
            return "🟠 High-Density Industrial"
        elif density >= 300:
            return "🟡 Medium Intercity"
        else:
            return "🟢 Low-Density Rural"

    def recommend_spacing(density):
        if density >= 2000:
            return "⚡ Every 15 - 25 km"
        elif density >= 800:
            return "⚡ Every 25 - 40 km"
        elif density >= 300:
            return "⚡ Every 40 - 60 km"
        else:
            return "⚡ Every 60 - 80 km"

    corridor_summary['Catchment Profile'] = corridor_summary['Mean Density (ppl/km²)'].apply(classify_catchment)
    corridor_summary['Recommended EV Hub Spacing'] = corridor_summary['Mean Density (ppl/km²)'].apply(recommend_spacing)

    # Sort by population density
    corridor_summary = corridor_summary.sort_values(by='Mean Density (ppl/km²)', ascending=False)

    if search_filter:
        pattern = re.escape(search_filter)
        corridor_summary = corridor_summary[
            corridor_summary['Ref'].str.contains(pattern, case=False, na=False) |
            corridor_summary['Corridor / Section'].str.contains(pattern, case=False, na=False)
        ]
        print(f"[+] Filtered by '{search_filter}': {len(corridor_summary)} matching corridors")

    # Format numbers
    corridor_summary['Mean Density (ppl/km²)'] = corridor_summary['Mean Density (ppl/km²)'].round(1)
    corridor_summary['Peak Density (ppl/km²)'] = corridor_summary['Peak Density (ppl/km²)'].round(1)
    corridor_summary['Length (km)'] = corridor_summary['Length (km)'].round(1)

    print("\n" + "=" * 115)
    print(" 👥 HIGHWAY & EXPRESSWAY CORRIDOR POPULATION DENSITY & EV SPACING TABLE")
    print("=" * 115)
    print(tabulate(corridor_summary.head(limit), headers='keys', tablefmt='fancy_grid', showindex=False))

def main():
    parser = argparse.ArgumentParser(description="Urja-X Highway Population Density Table Viewer")
    parser.add_argument("--limit", type=int, default=25, help="Number of rows to display (default: 25)")
    parser.add_argument("--filter", type=str, default=None, help="Filter by Highway Ref (e.g. NH44, NH48, MPE)")
    args = parser.parse_args()

    analyze_corridors(limit=args.limit, search_filter=args.filter)

if __name__ == "__main__":
    main()
