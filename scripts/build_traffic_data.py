"""
Urja-X Traffic Dataset Compiler & Bundler
Processes ihmcl_jan_2026_matched_traffic.csv into urja_traffic_bundle.js
Grouping co-located plazas to prevent visual stacking while preserving 100% of underlying records.
"""

import sys
import json
import datetime
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

CANDIDATE_PATHS = [
    BASE_DIR / "Trafic data" / "ihmcl_jan_2026_matched_traffic.csv",
    BASE_DIR / "Traffic data" / "ihmcl_jan_2026_matched_traffic.csv",
    BASE_DIR / "ihmcl_jan_2026_matched_traffic.csv",
]

OUTPUT_BUNDLE = BASE_DIR / "Trafic data" / "urja_traffic_bundle.js"

def find_traffic_csv():
    for p in CANDIDATE_PATHS:
        if p.exists():
            return p
    return None

def build_traffic_bundle():
    csv_path = find_traffic_csv()
    if not csv_path:
        print("[!] Error: Could not find ihmcl_jan_2026_matched_traffic.csv in expected locations.")
        return None

    print(f"[*] Reading traffic dataset from: {csv_path}...")
    df = pd.read_csv(csv_path)
    total_records = len(df)
    print(f"[+] Total raw records: {total_records}")

    # Validate coordinates
    valid_mask = (
        df['latitude'].notnull() & 
        df['longitude'].notnull() & 
        (df['latitude'] >= 6.0) & (df['latitude'] <= 38.0) &
        (df['longitude'] >= 68.0) & (df['longitude'] <= 98.5)
    )
    
    valid_df = df[valid_mask].copy()
    invalid_count = total_records - len(valid_df)
    print(f"[+] Valid coordinate records in India bounds: {len(valid_df)}")
    print(f"[+] Invalid / out-of-bounds records: {invalid_count}")

    # Group by coordinate pair to handle duplicate/paired plazas
    grouped = {}
    for _, row in valid_df.iterrows():
        lat = float(row['latitude'])
        lon = float(row['longitude'])
        coord_key = (round(lat, 6), round(lon, 6))

        total_cnt = int(row['total_cnt']) if pd.notnull(row['total_cnt']) else 0
        car_jeep_cnt = int(row['car_jeep_cnt']) if pd.notnull(row['car_jeep_cnt']) else 0
        lcv_cnt = int(row['lcv_cnt']) if pd.notnull(row['lcv_cnt']) else 0
        bus_truck_cnt = int(row['bus_truck_cnt']) if pd.notnull(row['bus_truck_cnt']) else 0
        month = str(row['reporting_month']) if pd.notnull(row['reporting_month']) else "2026-01"

        record_entry = {
            "plaza_name_report": str(row['plaza_name_report']).strip(),
            "plaza_name_source": str(row['plaza_name_source']).strip(),
            "car_jeep_cnt": car_jeep_cnt,
            "lcv_cnt": lcv_cnt,
            "bus_truck_cnt": bus_truck_cnt,
            "total_cnt": total_cnt,
            "reporting_month": month,
            "piu": str(row['piu']).strip() if pd.notnull(row.get('piu')) else "",
            "ro": str(row['ro']).strip() if pd.notnull(row.get('ro')) else "",
            "total_amt": int(row['total_amt']) if pd.notnull(row.get('total_amt')) else 0
        }

        if coord_key not in grouped:
            grouped[coord_key] = {
                "lat": lat,
                "lon": lon,
                "records": [record_entry],
                "combined_total": total_cnt
            }
        else:
            grouped[coord_key]["records"].append(record_entry)
            grouped[coord_key]["combined_total"] += total_cnt

    locations = []
    for coord_key, data in grouped.items():
        comb_tot = data["combined_total"]
        # Determine styling scale based on combined monthly count
        if comb_tot >= 500000:
            color = "#dc2626"  # Red / Very High
            radius = 8.0
            tier = "Ultra High (≥500K/mo)"
        elif comb_tot >= 250000:
            color = "#ea580c"  # Orange / High
            radius = 6.5
            tier = "High (250K-500K/mo)"
        elif comb_tot >= 100000:
            color = "#eab308"  # Amber Gold / Moderate
            radius = 5.0
            tier = "Moderate (100K-250K/mo)"
        else:
            color = "#14b8a6"  # Teal / Low
            radius = 4.0
            tier = "Standard (<100K/mo)"

        primary_title = data["records"][0]["plaza_name_report"]
        if len(data["records"]) > 1:
            primary_title += f" (+{len(data['records'])-1} paired)"

        locations.append({
            "lat": data["lat"],
            "lon": data["lon"],
            "name": primary_title,
            "combined_total": comb_tot,
            "tier": tier,
            "color": color,
            "radius": radius,
            "count": len(data["records"]),
            "records": data["records"]
        })

    # Sort locations descending by combined traffic for snappy rendering and search prioritization
    locations.sort(key=lambda x: x["combined_total"], reverse=True)

    bundle_obj = {
        "metadata": {
            "source_file": csv_path.name,
            "total_records": total_records,
            "valid_records": len(valid_df),
            "invalid_records": invalid_count,
            "unique_marker_locations": len(locations),
            "reporting_month": "2026-01",
            "metric_type": "Monthly Traffic Volume (FASTag / IHMCL)",
            "built_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "locations": locations
    }

    OUTPUT_BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    json_str = json.dumps(bundle_obj, ensure_ascii=False, separators=(',', ':'))
    js_content = f"window.URJA_TRAFFIC_DATA = {json_str};\n"
    OUTPUT_BUNDLE.write_text(js_content, encoding="utf-8")
    
    file_size_kb = len(js_content) / 1024
    print(f"[+] Generated {OUTPUT_BUNDLE.name} ({file_size_kb:.1f} KB)")
    print(f"[+] Locations: {len(locations)}, Records encapsulated: {total_records}")
    return bundle_obj

if __name__ == "__main__":
    build_traffic_bundle()

