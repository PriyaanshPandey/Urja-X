"""
Urja-X EV Infrastructure & Vehicle Fleet Data Processor
Processes raw datasets from EV-Charger/ and EV-Vehicle/ into an optimized
bundle for interactive web map visualization.
"""

import sys
import os
import json
import time
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
CHARGER_CSV = BASE_DIR / "EV-Charger" / "india_ev_charging_raw.csv"
VEHICLE_XL = BASE_DIR / "EV-Vehicle" / "EV Sales Data.xlsx"
OUTPUT_BUNDLE_JS = BASE_DIR / "EV-Charger" / "urja_ev_bundle.js"

# Coordinates for all 36 States & Union Territories of India
STATE_COORDINATES = {
    "Andaman & Nicobar Island": (11.667, 92.735),
    "Andhra Pradesh": (16.506, 80.648),
    "Arunachal Pradesh": (27.084, 93.605),
    "Assam": (26.144, 91.736),
    "Bihar": (25.594, 85.137),
    "Chandigarh": (30.733, 76.779),
    "Chhattisgarh": (21.251, 81.629),
    "DNH and DD": (20.428, 72.839),
    "Delhi": (28.613, 77.209),
    "Goa": (15.498, 73.827),
    "Gujarat": (23.215, 72.636),
    "Haryana": (29.058, 76.085),
    "Himachal Pradesh": (31.104, 77.173),
    "Jammu and Kashmir": (34.083, 74.797),
    "Jharkhand": (23.344, 85.309),
    "Karnataka": (12.971, 77.594),
    "Kerala": (8.524, 76.936),
    "Ladakh": (34.152, 77.577),
    "Lakshadweep": (10.566, 72.641),
    "Madhya Pradesh": (23.259, 77.412),
    "Maharashtra": (19.076, 72.877),
    "Manipur": (24.817, 93.936),
    "Meghalaya": (25.578, 91.893),
    "Mizoram": (23.727, 92.717),
    "Nagaland": (25.675, 94.108),
    "Odisha": (20.296, 85.824),
    "Puducherry": (11.941, 79.808),
    "Punjab": (30.901, 75.857),
    "Rajasthan": (26.912, 75.787),
    "Sikkim": (27.338, 88.606),
    "Tamil Nadu": (13.082, 80.270),
    "Telangana": (17.385, 78.486),
    "Tripura": (23.831, 91.286),
    "Uttar Pradesh": (26.846, 80.946),
    "Uttarakhand": (30.316, 78.032),
    "West Bengal": (22.572, 88.363)
}

def process_ev_chargers():
    print(f"[*] Processing EV chargers from {CHARGER_CSV.name}...")
    t0 = time.time()
    df = pd.read_csv(CHARGER_CSV)

    df['lat'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['lon'] = pd.to_numeric(df['Longitude'], errors='coerce')
    valid = (df['lat'] >= 6.0) & (df['lat'] <= 38.0) & (df['lon'] >= 68.0) & (df['lon'] <= 98.5)
    df_clean = df[valid].copy()

    def is_fast_dc(row):
        t = str(row['Types of Chargers Installed/ Connector']).upper()
        r = row['Charger Rating']
        if 'CCS' in t or 'DC' in t or 'CHADEMO' in t or r >= 25.0:
            return True
        return False

    df_clean['is_dc'] = df_clean.apply(is_fast_dc, axis=1)

    dc_chargers = []
    ac_chargers = []

    for _, row in df_clean.iterrows():
        lat = round(row['lat'], 5)
        lon = round(row['lon'], 5)
        cpo = str(row['CPO Name']).strip()
        loc = str(row['Location']).strip()
        conn = str(row['Types of Chargers Installed/ Connector']).strip()
        rating = float(row['Charger Rating']) if pd.notna(row['Charger Rating']) else 0.0
        ports = int(row['No. of Connector']) if pd.notna(row['No. of Connector']) else 1
        govt_pvt = str(row['Govt/Private']).strip()
        city = str(row['City/Village']).strip() if pd.notna(row['City/Village']) else ''
        state = str(row['State']).strip() if pd.notna(row['State']) else ''

        record = [lat, lon, cpo, loc, conn, rating, ports, govt_pvt, city, state]

        if row['is_dc']:
            dc_chargers.append(record)
        else:
            ac_chargers.append(record)

    print(f"[+] Processed {len(df_clean):,} EV chargers in {time.time()-t0:.2f}s:")
    print(f"    - Fast DC Chargers (≥25 kW): {len(dc_chargers):,}")
    print(f"    - Standard AC Chargers: {len(ac_chargers):,}")

    return dc_chargers, ac_chargers

def process_ev_vehicles():
    print(f"[*] Processing EV vehicle fleet registrations from {VEHICLE_XL.name}...")
    t0 = time.time()
    df = pd.read_excel(VEHICLE_XL, sheet_name='evdb_statewise')

    agg = df.groupby(['State', 'Vehicle Category'])['ELECTRIC(BOV)'].sum().unstack(fill_value=0)
    agg['Total_EVs'] = agg.sum(axis=1)

    state_fleet = []
    heat_points = []

    max_ev = agg['Total_EVs'].max()

    for state, row in agg.iterrows():
        coords = STATE_COORDINATES.get(state)
        if not coords:
            continue

        lat, lon = coords
        tot = int(row.get('Total_EVs', 0))
        w2 = int(row.get('2-Wheelers', 0))
        w3 = int(row.get('3-Wheelers', 0))
        w4 = int(row.get('4-Wheelers', 0))
        bus = int(row.get('Bus', 0))
        others = tot - (w2 + w3 + w4 + bus)

        state_fleet.append({
            'state': state,
            'lat': lat,
            'lon': lon,
            'total': tot,
            'w2': w2,
            'w3': w3,
            'w4': w4,
            'bus': bus,
            'others': max(0, others)
        })

        # Add heat points with normalized weight (logarithmic)
        import math
        weight = min(1.0, math.log10(tot + 1) / 6.2)
        heat_points.append([lat, lon, round(weight, 3)])
        # Spread radius for state heat
        for lat_off in (-0.5, 0.5):
            for lon_off in (-0.5, 0.5):
                heat_points.append([lat + lat_off, lon + lon_off, round(weight * 0.7, 3)])

    print(f"[+] Loaded EV fleet data for {len(state_fleet)} States & UTs (Total: {sum(s['total'] for s in state_fleet):,} EVs) in {time.time()-t0:.2f}s")
    return state_fleet, heat_points

def build_ev_bundle():
    print("\n=======================================================")
    print(" 🚗 COMPILING URJA-X EV CHARGER & VEHICLE FLEET BUNDLE")
    print("=======================================================")

    dc_chargers, ac_chargers = process_ev_chargers()
    state_fleet, heat_points = process_ev_vehicles()

    bundle = {
        'dc_chargers': dc_chargers,
        'ac_chargers': ac_chargers,
        'state_fleet': state_fleet,
        'heat_points': heat_points,
        'metadata': {
            'charger_count': len(dc_chargers) + len(ac_chargers),
            'total_ev_fleet': sum(s['total'] for s in state_fleet),
            'source_chargers': 'National EV Charging Infrastructure Telemetry',
            'source_vehicles': 'VAHAN Dashboard / Ministry of Road Transport and Highways (MoRTH)',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    }

    print(f"[*] Serializing EV bundle to {OUTPUT_BUNDLE_JS.name}...")
    js_content = "window.URJA_EV_DATA = " + json.dumps(bundle, separators=(',', ':')) + ";\n"
    OUTPUT_BUNDLE_JS.write_text(js_content, encoding='utf-8')
    size_mb = OUTPUT_BUNDLE_JS.stat().st_size / (1024 * 1024)
    print(f"[+] Successfully generated EV bundle: {OUTPUT_BUNDLE_JS.name} ({size_mb:.2f} MB)")

if __name__ == '__main__':
    build_ev_bundle()

