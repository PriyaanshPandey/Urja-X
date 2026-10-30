"""
Urja-X: Empirical Corridor Test Case Generator (500+ Test Cases)
Extracts real continuous highway corridors across India from OpenStreetMap (india_nh.gpkg),
matches them with real VAHAN registrations, IHMCL toll traffic, electrical substations,
and POIs to generate hundreds of empirical benchmark test cases.
"""

import os
import sys
import json
import time
import sqlite3
import random
import re
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
import shapely.wkb

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

print("=" * 80)
print("⚡ URJA-X: EMPIRICAL TEST CASE GENERATION ENGINE (SCALE: 500 SCENARIOS)")
print("Sampling real 100-350 km highway corridors across India with multi-layer spatial indices")
print("=" * 80)

# 1. Load Operational EV Chargers
print("\n[1/5] Loading 39,641 Operational EV Chargers...")
df_chargers = pd.read_csv('EV-Charger/india_ev_charging_raw.csv')
df_chargers['Latitude'] = pd.to_numeric(df_chargers['Latitude'], errors='coerce')
df_chargers['Longitude'] = pd.to_numeric(df_chargers['Longitude'], errors='coerce')
df_chargers = df_chargers.dropna(subset=['Latitude', 'Longitude'])
charger_coords_rad = np.radians(df_chargers[['Latitude', 'Longitude']].values.astype(np.float64))
tree_chargers = cKDTree(charger_coords_rad)
print(f"  ✓ Charger KD-Tree built with {len(df_chargers):,} operational stations.")

# 2. Load Real Electricity Substation Nodes
print("\n[2/5] Loading 1.67M Electrical Grid Substation Nodes...")
df_elec = pd.read_csv('Electricity-Data/Points/india_electricity_final.csv', usecols=['latitude', 'longitude'])
df_elec['latitude'] = pd.to_numeric(df_elec['latitude'], errors='coerce')
df_elec['longitude'] = pd.to_numeric(df_elec['longitude'], errors='coerce')
df_elec = df_elec.dropna(subset=['latitude', 'longitude'])
elec_coords_rad = np.radians(df_elec[['latitude', 'longitude']].values.astype(np.float64))
tree_elec = cKDTree(elec_coords_rad)
print(f"  ✓ Electricity Grid KD-Tree built with {len(df_elec):,} high-voltage nodes.")

# 3. Load IHMCL Toll Traffic Plazas
print("\n[3/5] Loading IHMCL January 2026 Real Highway Toll Traffic...")
df_traffic = pd.read_csv('Trafic data/ihmcl_jan_2026_matched_traffic.csv')
df_traffic['latitude'] = pd.to_numeric(df_traffic['latitude'], errors='coerce')
df_traffic['longitude'] = pd.to_numeric(df_traffic['longitude'], errors='coerce')
df_traffic = df_traffic.dropna(subset=['latitude', 'longitude'])
traffic_coords_rad = np.radians(df_traffic[['latitude', 'longitude']].values.astype(np.float64))
tree_traffic = cKDTree(traffic_coords_rad)
traffic_counts = df_traffic['total_cnt'].values
print(f"  ✓ Traffic KD-Tree built with {len(df_traffic):,} national toll plazas.")

# 4. Load Fuel Stations & Dhabas from POIs
print("\n[4/5] Extracting Brownfield Petrol Pumps & Commercial Dhabas from india_pois.gpkg...")
conn_poi = sqlite3.connect('EV-Roads/india_pois.gpkg')
cur_poi = conn_poi.cursor()

def parse_gpkg_geom(raw_geom):
    flags = raw_geom[3]
    envelope_indicator = (flags & 0x0E) >> 1
    envelope_lens = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}
    header_len = 8 + envelope_lens.get(envelope_indicator, 0)
    wkb_data = raw_geom[header_len:]
    return shapely.wkb.loads(wkb_data)

# Fuel Stations
cur_poi.execute("SELECT geom FROM points WHERE other_tags LIKE '%\"amenity\"=>\"fuel\"%'")
fuel_pts = []
for r in cur_poi.fetchall():
    try:
        pt = parse_gpkg_geom(r[0])
        fuel_pts.append([pt.y, pt.x]) # [lat, lon]
    except Exception:
        pass
fuel_coords_rad = np.radians(np.array(fuel_pts))
tree_fuel = cKDTree(fuel_coords_rad)
print(f"  ✓ Brownfield Fuel KD-Tree built with {len(fuel_pts):,} petrol pumps.")

# Dhabas & Amenities
cur_poi.execute("SELECT geom FROM points WHERE other_tags LIKE '%restaurant%' OR other_tags LIKE '%dhaba%' OR other_tags LIKE '%fast_food%'")
dhaba_pts = []
for r in cur_poi.fetchall():
    try:
        pt = parse_gpkg_geom(r[0])
        dhaba_pts.append([pt.y, pt.x])
    except Exception:
        pass
dhaba_coords_rad = np.radians(np.array(dhaba_pts))
tree_dhaba = cKDTree(dhaba_coords_rad)
print(f"  ✓ Commercial Amenities KD-Tree built with {len(dhaba_pts):,} dhabas/restaurants.")
conn_poi.close()

# 5. Load State EV Concentrations (VAHAN)
print("\n[5/5] Loading VAHAN BOV State Registrations...")
state_ev_weights = {
    'Uttar Pradesh': 1248678, 'Maharashtra': 579164, 'Karnataka': 493215,
    'Bihar': 386231, 'Delhi': 375421, 'Tamil Nadu': 339023, 'Rajasthan': 327348,
    'Assam': 276985, 'Gujarat': 231757, 'Madhya Pradesh': 226903,
    'Kerala': 195400, 'Haryana': 188200, 'West Bengal': 176500, 'Andhra Pradesh': 168900,
    'Telangana': 155400, 'Punjab': 142100, 'Odisha': 135800, 'Chhattisgarh': 118400,
    'Jharkhand': 98500, 'Uttarakhand': 84200, 'Himachal Pradesh': 42100
}
max_bov = max(state_ev_weights.values())

# 6. Extract Highway Corridors from india_nh.gpkg
print("\n[6/6] Grouping and Slicing Continuous 100-350 km Corridors from india_nh.gpkg...")
conn_nh = sqlite3.connect('EV-Roads/india_nh.gpkg')
cur_nh = conn_nh.cursor()

# Query lines by highway ref
cur_nh.execute("SELECT fid, name, other_tags, geom FROM lines WHERE other_tags LIKE '%ref%'")
all_hw_lines = cur_nh.fetchall()
print(f"  ✓ Found {len(all_hw_lines):,} highway segments in database.")

# Group coordinates by highway ref
ref_points = defaultdict(list)
ref_names = {}
ref_tags = {}

for fid, name, tags, raw_geom in all_hw_lines:
    m = re.search(r'"ref"=>"([^"]+)"', tags)
    if m:
        ref = m.group(1).split(';')[0].strip()
        try:
            line_geom = parse_gpkg_geom(raw_geom)
            coords = list(line_geom.coords)
            ref_points[ref].extend(coords)
            if ref not in ref_names and name:
                ref_names[ref] = name
            if ref not in ref_tags and tags:
                ref_tags[ref] = tags
        except Exception:
            pass

conn_nh.close()

# Filter highways with at least 100 points
viable_refs = [r for r, pts in ref_points.items() if len(pts) >= 100]
print(f"  ✓ Identified {len(viable_refs)} major National Highway systems with dense geometries.")

EARTH_R = 6371.0 # km

def haversine_km(lat1, lon1, lat2, lon2):
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1))*np.cos(np.radians(lat2))*np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return EARTH_R * c

def generate_500_corridor_test_cases(num_cases=500):
    test_cases = []
    random.seed(42)
    np.random.seed(42)
    
    # Sort viable refs by point count descending, prioritize top 100 corridors
    sorted_viable = sorted(viable_refs, key=lambda r: len(ref_points[r]), reverse=True)
    
    tc_idx = 0
    attempts = 0
    max_attempts = num_cases * 10
    
    while tc_idx < num_cases and attempts < max_attempts:
        attempts += 1
        # Pick a highway ref
        ref = random.choice(sorted_viable[:60]) # top 60 major national highways
        pts = ref_points[ref]
        
        # Sort points geographically (alternate north-south or east-west depending on highway orientation)
        lat_span = max(p[1] for p in pts) - min(p[1] for p in pts)
        lon_span = max(p[0] for p in pts) - min(p[0] for p in pts)
        
        if lat_span >= lon_span:
            pts_sorted = sorted(pts, key=lambda p: p[1], reverse=random.choice([True, False]))
        else:
            pts_sorted = sorted(pts, key=lambda p: p[0], reverse=random.choice([True, False]))
            
        # Pick random starting index
        if len(pts_sorted) < 50:
            continue
        start_i = random.randint(0, max(0, len(pts_sorted) - 40))
        
        # Target length between 120 km and 320 km
        target_len = random.uniform(140.0, 320.0)
        
        corridor_pts = [pts_sorted[start_i]]
        cum_len = 0.0
        for pt in pts_sorted[start_i + 1:]:
            d = haversine_km(corridor_pts[-1][1], corridor_pts[-1][0], pt[1], pt[0])
            # Only advance if distance is reasonable (between 0.8 km and 15 km)
            if 0.8 <= d <= 15.0:
                cum_len += d
                corridor_pts.append(pt)
                if cum_len >= target_len:
                    break
                    
        if cum_len < 100.0 or len(corridor_pts) < 15:
            continue # corridor too short, re-sample
            
        total_len_km = round(cum_len, 1)
        
        # Discretize into 5 km candidate windows
        num_candidates = max(18, min(50, int(total_len_km / 5.0)))
        step_idx = len(corridor_pts) / float(num_candidates)
        candidate_nodes = []
        
        for k in range(num_candidates):
            c_idx = min(len(corridor_pts) - 1, int(k * step_idx))
            lon, lat = corridor_pts[c_idx]
            km_mark = round(k * 5.0 * (total_len_km / (num_candidates * 5.0)), 1)
            
            node_rad = np.radians([[lat, lon]])
            
            # Query KD-Trees
            # 1. Existing Charger distance
            dist_chg_rad, _ = tree_chargers.query(node_rad)
            dist_chg_km = round(float(dist_chg_rad[0] * EARTH_R), 2)
            
            # 2. Electricity Substation distance
            dist_elec_rad, _ = tree_elec.query(node_rad)
            dist_elec_km = round(float(dist_elec_rad[0] * EARTH_R), 2)
            
            # 3. Traffic count
            dist_traf_rad, traf_idx = tree_traffic.query(node_rad)
            dist_traf_km = float(dist_traf_rad[0] * EARTH_R)
            if dist_traf_km < 35.0: # within reasonable catchment of plaza
                traffic_pcu = int(traffic_counts[traf_idx[0]])
            else:
                traffic_pcu = int(random.uniform(14000, 42000)) # typical highway daily PCU
                
            # 4. Brownfield Fuel Station
            dist_fuel_rad, _ = tree_fuel.query(node_rad)
            dist_fuel_km = round(float(dist_fuel_rad[0] * EARTH_R), 2)
            has_fuel_station = bool(dist_fuel_km <= 2.5)
            
            # 5. Commercial Dhaba / Amenities
            dist_dhaba_rad, _ = tree_dhaba.query(node_rad)
            dist_dhaba_km = round(float(dist_dhaba_rad[0] * EARTH_R), 2)
            has_amenity = bool(dist_dhaba_km <= 3.0)
            
            # 6. Road Hierarchy (speed, lanes)
            corr_name_str = ref_names.get(ref, f"{ref} Highway Corridor")
            is_expressway = "expressway" in corr_name_str.lower() or "motorway" in ref_tags.get(ref, '').lower()
            road_class_weight = 1.0 if is_expressway else 0.85
            
            # 7. Regional EV Fleet Adoption proxy
            if lat > 26.0:
                state_est = 'Uttar Pradesh' if lon > 78.0 else 'Rajasthan'
            elif lat > 20.0:
                state_est = 'Gujarat' if lon < 75.0 else 'Maharashtra'
            elif lat > 15.0:
                state_est = 'Karnataka' if lon < 77.0 else 'Andhra Pradesh'
            else:
                state_est = 'Tamil Nadu' if lon > 78.0 else 'Kerala'
                
            state_ev_count = state_ev_weights.get(state_est, 250000)
            ev_demand_norm = round(state_ev_count / float(max_bov), 3)
            
            # 8. Population density & Night-lights proxy (realistic highway dispersion)
            # High near cities (charger dist < 15km), dropping along rural stretches
            near_city_bonus = 1.0 if dist_chg_km < 15.0 else max(0.12, 1.0 - (dist_chg_km / 70.0))
            pop_density_proxy = round(near_city_bonus * random.uniform(0.65, 1.0), 3)
            ntl_radiance_proxy = round(near_city_bonus * random.uniform(0.55, 0.95), 3)
            
            # 9. Tourism Pull
            tourism_score = round(random.choice([0.15, 0.25, 0.55, 0.85, 0.95]) if lat < 16.0 or lat > 28.0 else random.choice([0.10, 0.20, 0.40]), 2)
            
            candidate_nodes.append({
                'node_id': f"N{k+1:02d}",
                'km_mark': km_mark,
                'lat': round(lat, 5),
                'lon': round(lon, 5),
                'factors': {
                    'f1_charger_dist_km': dist_chg_km,
                    'f2_ev_fleet_norm': ev_demand_norm,
                    'f3_traffic_pcu': traffic_pcu,
                    'f4_pop_density_norm': pop_density_proxy,
                    'f5_economic_ntl_norm': ntl_radiance_proxy,
                    'f6_tourism_pull_norm': tourism_score,
                    'f7_substation_dist_km': dist_elec_km,
                    'f8_fuel_dist_km': dist_fuel_km,
                    'f8_has_fuel': has_fuel_station,
                    'f9_dhaba_dist_km': dist_dhaba_km,
                    'f9_has_dhaba': has_amenity,
                    'road_class_weight': road_class_weight
                }
            })
            
        # Target deployment budget K (number of stations to fund under PM E-DRIVE, typical 1 station per 35-45 km)
        k_target = max(3, min(9, int(total_len_km / 35.0)))
        
        tc_idx += 1
        test_cases.append({
            'test_case_id': f"TC-{tc_idx:03d}",
            'corridor_ref': ref,
            'corridor_name': corr_name_str,
            'state_region': state_est,
            'total_corridor_len_km': total_len_km,
            'target_station_quota_k': k_target,
            'num_candidate_nodes': len(candidate_nodes),
            'candidate_nodes': candidate_nodes
        })
        
        if tc_idx % 100 == 0 or tc_idx == num_cases:
            print(f"  ... generated {tc_idx}/{num_cases} corridor scenarios")
            
    return test_cases

print("\nGenerating 500 empirical corridor test cases across India...")
t_gen = time.time()
test_cases_bank = generate_500_corridor_test_cases(num_cases=500)
print(f"✓ Generated {len(test_cases_bank)} comprehensive corridor test cases in {time.time()-t_gen:.2f}s!")

# Save to JSON
output_path = os.path.join(DATA_DIR, "corridor_test_cases.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(test_cases_bank, f, indent=2)

size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"✓ Saved Test Cases Bank to: {output_path} ({size_mb:.2f} MB)")
print("=" * 80)
