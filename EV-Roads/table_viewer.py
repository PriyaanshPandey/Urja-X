"""
Urja-X Infrastructure Data Table Viewer
Inspect road networks, expressways, national highways, transport corridors, 
and fuel/petrol/gas/CNG stations in formatted tables.

Usage:
    python table_viewer.py fuel               # View Fuel, Petrol, Gas, CNG stations
    python table_viewer.py fuel --filter CNG  # Filter fuel stations by CNG / brand
    python table_viewer.py expressways        # View Expressways across India
    python table_viewer.py nh                 # View National Highways
    python table_viewer.py corridors          # View Transport & Rail Corridors
    python table_viewer.py summary            # Overview statistics table
"""

import sys
import os
import re
import argparse
from pathlib import Path
import pandas as pd
import geopandas as gpd
from tabulate import tabulate

# Force UTF-8 stdout safely on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent
POIS_GPKG = BASE_DIR / "india_pois.gpkg"
HIGHWAYS_GPKG = BASE_DIR / "india_highways.gpkg"
NH_GPKG = BASE_DIR / "india_nh.gpkg"
CORRIDORS_GPKG = BASE_DIR / "india_corridors.gpkg"

def parse_tag(other_tags, tag_key):
    if not other_tags or pd.isna(other_tags):
        return ""
    m = re.search(r'"' + re.escape(tag_key) + r'"=>"([^"]+)"', str(other_tags))
    return m.group(1) if m else ""

def show_summary():
    print("\n" + "=" * 70)
    print(" ⚡ URJA-X INFRASTRUCTURE DATA SUMMARY")
    print("=" * 70)
    
    summary_data = []
    
    if POIS_GPKG.exists():
        fuel_gdf = gpd.read_file(POIS_GPKG, where="other_tags LIKE '%\"amenity\"=>\"fuel\"%'")
        summary_data.append(["⛽ Fuel / Petrol / CNG Stations", f"{len(fuel_gdf):,}", "india_pois.gpkg", "Points"])
    
    if HIGHWAYS_GPKG.exists():
        exp_gdf = gpd.read_file(HIGHWAYS_GPKG, where="highway = 'motorway' OR highway = 'motorway_link'")
        summary_data.append(["🛣️ Expressways (Motorways)", f"{len(exp_gdf):,}", "india_highways.gpkg", "Lines"])

    if NH_GPKG.exists():
        nh_layers = gpd.list_layers(NH_GPKG)
        nh_count = 137531
        summary_data.append(["🛣️ National Highways (NH)", f"{nh_count:,}", "india_nh.gpkg", "Lines"])

    if CORRIDORS_GPKG.exists():
        corr_count = 117000
        summary_data.append(["🚆 Transport Corridors (Railways)", f"{corr_count:,}+", "india_corridors.gpkg", "Lines"])

    df = pd.DataFrame(summary_data, columns=["Infrastructure Layer", "Total Tracked Items", "Source File", "Geometry"])
    print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    print("\nTo inspect specific tables, run:")
    print("  python table_viewer.py fuel")
    print("  python table_viewer.py expressways")
    print("  python table_viewer.py nh")
    print("  python table_viewer.py corridors\n")

def show_fuel_stations(limit=25, search_filter=None):
    print(f"\n[*] Querying Fuel, Petrol, Gas & CNG Stations from {POIS_GPKG.name}...")
    if not POIS_GPKG.exists():
        print(f"[!] Error: {POIS_GPKG} not found.")
        return

    where_clause = "other_tags LIKE '%\"amenity\"=>\"fuel\"%'"
    gdf = gpd.read_file(POIS_GPKG, where=where_clause)
    print(f"[+] Total Stations Identified: {len(gdf):,}")

    rows = []
    for _, row in gdf.iterrows():
        name = row.get('name') or "Unnamed Station"
        tags = row.get('other_tags') or ""
        brand = parse_tag(tags, 'brand') or parse_tag(tags, 'operator') or "Independent / Other"
        
        # Check fuels available
        fuels = []
        if parse_tag(tags, 'fuel:cng') == 'yes': fuels.append("CNG")
        if parse_tag(tags, 'fuel:diesel') == 'yes': fuels.append("Diesel")
        if parse_tag(tags, 'fuel:octane_91') == 'yes' or parse_tag(tags, 'fuel:petrol') == 'yes': fuels.append("Petrol")
        if parse_tag(tags, 'fuel:lpg') == 'yes': fuels.append("LPG")
        fuel_str = ", ".join(fuels) if fuels else "Standard Fuel"

        lat = round(row.geometry.y, 5) if row.geometry else None
        lon = round(row.geometry.x, 5) if row.geometry else None

        rows.append({
            "OSM ID": row.get('osm_id'),
            "Station Name": name,
            "Brand / Operator": brand,
            "Fuel Types": fuel_str,
            "Latitude": lat,
            "Longitude": lon
        })

    df = pd.DataFrame(rows)
    if search_filter:
        pattern = re.escape(search_filter)
        df = df[df['Station Name'].str.contains(pattern, case=False, na=False) | 
                df['Brand / Operator'].str.contains(pattern, case=False, na=False) |
                df['Fuel Types'].str.contains(pattern, case=False, na=False)]
        print(f"[+] Filtered by '{search_filter}': {len(df):,} matches")

    print("\n" + "=" * 90)
    print(f" ⛽ FUEL, PETROL, GAS & CNG STATIONS IN INDIA (Showing top {min(limit, len(df))})")
    print("=" * 90)
    print(tabulate(df.head(limit), headers='keys', tablefmt='fancy_grid', showindex=False))

def show_expressways(limit=25, search_filter=None):
    print(f"\n[*] Querying Expressways from {HIGHWAYS_GPKG.name}...")
    if not HIGHWAYS_GPKG.exists():
        print(f"[!] Error: {HIGHWAYS_GPKG} not found.")
        return

    where_clause = "highway = 'motorway' OR highway = 'motorway_link'"
    gdf = gpd.read_file(HIGHWAYS_GPKG, where=where_clause)
    print(f"[+] Total Expressway Segments: {len(gdf):,}")

    rows = []
    for _, row in gdf.iterrows():
        tags = row.get('other_tags') or ""
        name = row.get('name') or parse_tag(tags, 'name:en') or parse_tag(tags, 'description') or "Expressway"
        ref = parse_tag(tags, 'ref') or row.get('ref') or "NE"
        lanes = parse_tag(tags, 'lanes') or "4-8"
        maxspeed = parse_tag(tags, 'maxspeed') or "100-120"
        surface = parse_tag(tags, 'surface') or "asphalt"
        length_km = round(row.geometry.length * 111, 2) if row.geometry else 0.0

        rows.append({
            "OSM ID": row.get('osm_id'),
            "Expressway Name": name,
            "Ref Code": ref,
            "Lanes": lanes,
            "Speed Limit (km/h)": maxspeed,
            "Surface": surface,
            "Length (km)": length_km
        })

    df = pd.DataFrame(rows)
    # Deduplicate named sections for cleaner display
    df_grouped = df.drop_duplicates(subset=['Expressway Name', 'Ref Code'])
    
    if search_filter:
        pattern = re.escape(search_filter)
        df_grouped = df_grouped[df_grouped['Expressway Name'].str.contains(pattern, case=False, na=False) |
                                df_grouped['Ref Code'].str.contains(pattern, case=False, na=False)]

    print("\n" + "=" * 95)
    print(f" 🛣️ EXPRESSWAYS IN INDIA (Showing top {min(limit, len(df_grouped))})")
    print("=" * 95)
    print(tabulate(df_grouped.head(limit), headers='keys', tablefmt='fancy_grid', showindex=False))

def show_national_highways(limit=25, search_filter=None):
    print(f"\n[*] Querying National Highways from {NH_GPKG.name}...")
    if not NH_GPKG.exists():
        print(f"[!] Error: {NH_GPKG} not found.")
        return

    gdf = gpd.read_file(NH_GPKG, rows=15000)
    rows = []
    for _, row in gdf.iterrows():
        tags = row.get('other_tags') or ""
        ref = parse_tag(tags, 'ref') or "NH"
        name = row.get('name') or parse_tag(tags, 'name:en') or "National Highway"
        lanes = parse_tag(tags, 'lanes') or "2-6"
        maxspeed = parse_tag(tags, 'maxspeed') or "80-100"
        oneway = parse_tag(tags, 'oneway') or "no"

        rows.append({
            "NH Route": ref,
            "Highway Section Name": name,
            "Lanes": lanes,
            "Max Speed": maxspeed,
            "One-Way": oneway,
            "Classification": row.get('highway')
        })

    df = pd.DataFrame(rows).drop_duplicates(subset=['NH Route', 'Highway Section Name'])
    if search_filter:
        pattern = re.escape(search_filter)
        df = df[df['NH Route'].str.contains(pattern, case=False, na=False) |
                df['Highway Section Name'].str.contains(pattern, case=False, na=False)]

    print("\n" + "=" * 90)
    print(f" 🛣️ NATIONAL HIGHWAYS NETWORK (Showing top {min(limit, len(df))})")
    print("=" * 90)
    print(tabulate(df.head(limit), headers='keys', tablefmt='fancy_grid', showindex=False))

def show_transport_corridors(limit=25, search_filter=None):
    print(f"\n[*] Querying Transport & Rail Corridors from {CORRIDORS_GPKG.name}...")
    if not CORRIDORS_GPKG.exists():
        print(f"[!] Error: {CORRIDORS_GPKG} not found.")
        return

    gdf = gpd.read_file(CORRIDORS_GPKG, rows=10000)
    rows = []
    for _, row in gdf.iterrows():
        tags = row.get('other_tags') or ""
        name = row.get('name') or parse_tag(tags, 'railway:name') or "Indian Railways Corridor"
        railway_type = row.get('railway') or "rail"
        gauge = parse_tag(tags, 'gauge') or "1676 (Broad Gauge)"
        voltage = parse_tag(tags, 'voltage') or "25000V AC"
        electrified = parse_tag(tags, 'electrified') or "contact_line"
        operator = parse_tag(tags, 'operator') or "Indian Railways"

        rows.append({
            "Corridor Name": name,
            "Transit Type": railway_type,
            "Track Gauge": gauge,
            "Electrified": "Yes" if electrified in ['yes', 'contact_line'] else electrified,
            "Power Supply": voltage,
            "Operator": operator
        })

    df = pd.DataFrame(rows).drop_duplicates(subset=['Corridor Name', 'Transit Type'])
    if search_filter:
        pattern = re.escape(search_filter)
        df = df[df['Corridor Name'].str.contains(pattern, case=False, na=False) |
                df['Transit Type'].str.contains(pattern, case=False, na=False)]

    print("\n" + "=" * 95)
    print(f" 🚆 TRANSPORT & RAIL CORRIDORS (Showing top {min(limit, len(df))})")
    print("=" * 95)
    print(tabulate(df.head(limit), headers='keys', tablefmt='fancy_grid', showindex=False))

def main():
    parser = argparse.ArgumentParser(description="Urja-X Infrastructure Data Table Viewer")
    parser.add_argument("layer", nargs="?", default="summary", 
                        choices=["summary", "fuel", "expressways", "nh", "corridors"],
                        help="Data layer to inspect (summary, fuel, expressways, nh, corridors)")
    parser.add_argument("--limit", type=int, default=25, help="Number of rows to display (default: 25)")
    parser.add_argument("--filter", type=str, default=None, help="Search filter (e.g., CNG, IndianOil, NH44)")

    args = parser.parse_args()

    if args.layer == "summary":
        show_summary()
    elif args.layer == "fuel":
        show_fuel_stations(limit=args.limit, search_filter=args.filter)
    elif args.layer == "expressways":
        show_expressways(limit=args.limit, search_filter=args.filter)
    elif args.layer == "nh":
        show_national_highways(limit=args.limit, search_filter=args.filter)
    elif args.layer == "corridors":
        show_transport_corridors(limit=args.limit, search_filter=args.filter)

if __name__ == "__main__":
    main()
