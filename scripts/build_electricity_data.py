"""
Urja-X Electricity Infrastructure Data Processor
Processes raw compressed datasets from Electricity-Data/ into an optimized
bundle for interactive web map visualization.
"""

import sys
import os
import re
import json
import gzip
import time
from pathlib import Path
from shapely.geometry import shape, mapping

BASE_DIR = Path(__file__).resolve().parent.parent
ELEC_DIR = BASE_DIR / "Electricity-Data"
LINES_GZ = ELEC_DIR / "Transmission-Lines" / "india_transmission_lines.geojson.gz"
LINES_JSON = ELEC_DIR / "Transmission-Lines" / "india_transmission_lines.geojson"
POINTS_GZ = ELEC_DIR / "Points" / "india_electricity_final.csv.gz"
POINTS_CSV = ELEC_DIR / "Points" / "india_electricity_final.csv"
OUTPUT_BUNDLE_JS = ELEC_DIR / "urja_electricity_bundle.js"

def parse_voltage(val):
    if not val or str(val).strip().lower() in ('none', '', '0'):
        return None
    parts = re.findall(r'\d+', str(val))
    if not parts:
        return None
    nums = [int(p) for p in parts]
    max_v = max(nums)
    if 11 <= max_v <= 1200:
        max_v = max_v * 1000
    return max_v if max_v > 0 else None

def get_voltage_tier(v):
    """
    Classify voltage according to Central Electricity Authority (CEA) / PowerGrid standards.
    Returns: (tier_id, tier_label, color, weight, dash_array)
    """
    if v is None:
        return 'unspecified', 'Unspecified Voltage (Heuristic Corridor)', '#94a3b8', 1.4, '4, 4'
    elif v >= 765000:
        return 'uhv_765kv', f'{v//1000} kV (Ultra High Voltage Interstate Backbone)', '#e11d48', 4.5, None
    elif v >= 350000:
        return 'ehv_400kv', f'{v//1000} kV (Extra High Voltage National Grid)', '#ea580c', 3.5, None
    elif v >= 180000:
        return 'hv_220kv', f'{v//1000} kV (High Voltage State Transmission)', '#f59e0b', 2.5, None
    elif v >= 90000:
        return 'sub_132kv', f'{v//1000} kV (Sub-Transmission Regional Grid)', '#06b6d4', 1.8, None
    elif v >= 30000:
        return 'dist_66kv', f'{v//1000} kV (High-Voltage Distribution)', '#3b82f6', 1.3, None
    else:
        return 'feed_11kv', f'{v//1000} kV (Medium-Voltage Feeder Line)', '#60a5fa', 1.1, None

def process_transmission_lines():
    print(f"[*] Processing transmission lines from {LINES_GZ.name if LINES_GZ.exists() else LINES_JSON.name}...")
    t0 = time.time()
    
    source = LINES_GZ if LINES_GZ.exists() else LINES_JSON
    if str(source).endswith('.gz'):
        with gzip.open(source, 'rt', encoding='utf-8', errors='replace') as f:
            raw = json.load(f)
    else:
        with open(source, 'r', encoding='utf-8', errors='replace') as f:
            raw = json.load(f)
            
    features = raw.get('features', [])
    print(f"    Loaded {len(features):,} raw line features.")
    
    clean_features = []
    tier_counts = {}
    
    for feat in features:
        geom = feat.get('geometry')
        if not geom or 'coordinates' not in geom or not geom['coordinates']:
            continue
            
        props = feat.get('properties', {})
        v_raw = props.get('voltage')
        pv = parse_voltage(v_raw)
        tier_id, tier_label, color, weight, dash = get_voltage_tier(pv)
        tier_counts[tier_label] = tier_counts.get(tier_label, 0) + 1
        
        # Geometry simplification ~10 meters (0.0001 deg) preserving shape
        s = shape(geom)
        simp = s.simplify(0.0001, preserve_topology=True)
        m = mapping(simp)
        coords = m['coordinates']
        
        if simp.geom_type == 'LineString':
            rounded_coords = [[round(p[0], 5), round(p[1], 5)] for p in coords]
        elif simp.geom_type == 'MultiLineString':
            rounded_coords = [[[round(p[0], 5), round(p[1], 5)] for p in line] for line in coords]
        else:
            continue
            
        p = {
            'v': pv,
            't': tier_label,
            'c': color,
            'w': weight,
        }
        if dash:
            p['d'] = dash
        if props.get('name'):
            p['n'] = str(props['name']).strip()
        if props.get('operator'):
            p['o'] = str(props['operator']).strip()
        if props.get('circuits'):
            p['circ'] = str(props['circuits']).strip()
        if props.get('cables'):
            p['cabl'] = str(props['cables']).strip()
            
        clean_features.append({
            'type': 'Feature',
            'geometry': {'type': simp.geom_type, 'coordinates': rounded_coords},
            'properties': p
        })
        
    print(f"[+] Processed {len(clean_features):,} transmission lines in {time.time()-t0:.2f}s:")
    for t_name, count in sorted(tier_counts.items(), key=lambda x: -x[1]):
        print(f"    - {t_name}: {count:,}")
        
    return {'type': 'FeatureCollection', 'features': clean_features}

def process_electricity_points():
    print(f"[*] Processing electricity points from {POINTS_GZ.name if POINTS_GZ.exists() else POINTS_CSV.name}...")
    t0 = time.time()
    
    source = POINTS_GZ if POINTS_GZ.exists() else POINTS_CSV
    opener = gzip.open(source, 'rt', encoding='utf-8', errors='replace') if str(source).endswith('.gz') else open(source, 'r', encoding='utf-8', errors='replace')
    
    import csv
    substations = []
    transformers = []
    generators = []
    poles = []
    towers_by_cell = {}
    tower_cell_stats = {}
    
    with opener as f:
        reader = csv.DictReader(f)
        for r in reader:
            pt_type = r.get('type', '')
            try:
                lat = float(r.get('latitude', ''))
                lon = float(r.get('longitude', ''))
            except (ValueError, TypeError):
                continue
                
            # Geographic bounding box for India (including territorial waters / islands)
            if not (6.0 <= lat <= 38.0 and 68.0 <= lon <= 98.5):
                continue
                
            lat_r = round(lat, 5)
            lon_r = round(lon, 5)
            
            if pt_type == 'substation':
                substations.append({
                    'lat': lat_r,
                    'lon': lon_r,
                    'name': r.get('name', '').strip() or 'Substation (OSM Node)',
                    'voltage': r.get('voltage', '').strip() or 'Not recorded in OSM',
                    'operator': r.get('operator', '').strip() or 'Not recorded in OSM',
                    'substation': r.get('substation', '').strip() or 'transmission',
                    'frequency': r.get('frequency', '').strip(),
                    'location': r.get('location', '').strip()
                })
            elif pt_type == 'transformer':
                transformers.append([
                    lat_r, lon_r,
                    r.get('name', '').strip() or 'Distribution Transformer',
                    r.get('voltage', '').strip() or 'Not recorded',
                    r.get('operator', '').strip() or 'Not recorded'
                ])
            elif pt_type in ('generator', 'plant'):
                generators.append([
                    lat_r, lon_r,
                    r.get('name', '').strip() or ('Power Generation Plant' if pt_type == 'plant' else 'Power Generator'),
                    r.get('operator', '').strip() or 'Not recorded',
                    'plant' if pt_type == 'plant' else 'generator'
                ])
            elif pt_type == 'pole':
                poles.append([
                    lat_r, lon_r,
                    r.get('operator', '').strip() or 'Distribution Utility',
                    r.get('name', '').strip() or 'Utility Pole'
                ])
            elif pt_type == 'tower':
                cell = f"{int(lat)}_{int(lon)}"
                if cell not in tower_cell_stats:
                    tower_cell_stats[cell] = {'count': 0, 'sum_lat': 0.0, 'sum_lon': 0.0}
                    towers_by_cell[cell] = []
                tower_cell_stats[cell]['count'] += 1
                tower_cell_stats[cell]['sum_lat'] += lat
                tower_cell_stats[cell]['sum_lon'] += lon
                towers_by_cell[cell].append([round(lat, 4), round(lon, 4)])
                
    # Build regional tower summary tiles (centroid + count)
    towers_summary = []
    for cell, stats in tower_cell_stats.items():
        count = stats['count']
        c_lat = round(stats['sum_lat'] / count, 4)
        c_lon = round(stats['sum_lon'] / count, 4)
        towers_summary.append({
            'cell': cell,
            'lat': c_lat,
            'lon': c_lon,
            'count': count
        })
        
    print(f"[+] Loaded points in {time.time()-t0:.2f}s:")
    print(f"    - Substations: {len(substations):,}")
    print(f"    - Transformers: {len(transformers):,}")
    print(f"    - Generators & Plants: {len(generators):,}")
    print(f"    - Utility Poles: {len(poles):,}")
    print(f"    - Transmission Towers: {sum(t['count'] for t in towers_summary):,} in {len(towers_summary)} regional grid cells.")
    
    return {
        'substations': substations,
        'transformers': transformers,
        'generators': generators,
        'poles': poles,
        'towers_summary': towers_summary,
        'towers_by_cell': towers_by_cell
    }

def build_bundle():
    print("\n=======================================================")
    print(" ⚡ COMPILING URJA-X ELECTRICITY INFRASTRUCTURE BUNDLE")
    print("=======================================================")
    
    lines_fc = process_transmission_lines()
    pts_data = process_electricity_points()
    
    bundle_data = {
        'transmission_lines': lines_fc,
        'substations': pts_data['substations'],
        'transformers': pts_data['transformers'],
        'generators': pts_data['generators'],
        'poles': pts_data['poles'],
        'towers_summary': pts_data['towers_summary'],
        'towers_by_cell': pts_data['towers_by_cell'],
        'metadata': {
            'source': 'OpenStreetMap contributors (ODbL 1.0)',
            'standards': 'Central Electricity Authority (CEA) / PowerGrid Corporation of India',
            'disclaimer': 'Mapped electrical infrastructure is sourced from public OpenStreetMap telemetry. Grid proximity does not represent or verify electrical capacity, interconnection feasibility, or substation availability.',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    print(f"[*] Serializing bundle to {OUTPUT_BUNDLE_JS.name}...")
    js_content = "window.URJA_ELECTRICITY_DATA = " + json.dumps(bundle_data, separators=(',', ':')) + ";\n"
    OUTPUT_BUNDLE_JS.write_text(js_content, encoding='utf-8')
    size_mb = OUTPUT_BUNDLE_JS.stat().st_size / (1024 * 1024)
    print(f"[+] Successfully generated electricity bundle: {OUTPUT_BUNDLE_JS.name} ({size_mb:.2f} MB)")

if __name__ == '__main__':
    build_bundle()

