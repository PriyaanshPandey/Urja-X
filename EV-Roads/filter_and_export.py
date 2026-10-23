"""
OSM Data Extraction and Filtering Pipeline for India
Extracts roads, major highways, transport corridors, and POIs from OSM PBF files.
Supports both Osmium CLI (fast C++) and Python pyosmium.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_PBF = BASE_DIR / "india-latest.osm.pbf"

OUTPUT_FILES = {
    "roads": BASE_DIR / "india_roads.osm.pbf",
    "highways": BASE_DIR / "india_highways.osm.pbf",
    "corridors": BASE_DIR / "india_corridors.osm.pbf",
    "pois": BASE_DIR / "india_pois.osm.pbf",
}

FILTERS = {
    "roads": ["w/highway"],
    "highways": [
        "w/highway=motorway,trunk,primary,secondary,motorway_link,trunk_link,primary_link,secondary_link"
    ],
    "corridors": [
        "w/railway=rail,light_rail,subway,narrow_gauge",
        "r/route=road,railway,bus",
    ],
    "pois": [
        "nwr/amenity=charging_station,fuel,bus_station,parking",
        "nwr/amenity",
        "nwr/shop",
        "nwr/tourism",
    ],
}

<<<<<<< HEAD
# def find_osmium_binary():
#     # 1. Check system PATH
#     bin_path = shutil.which("osmium")
#     if bin_path:
#         return bin_path
    
#     # 2. Check conda environments
#     user_home = Path.home()
#     possible_conda_paths = [
#         user_home / "anaconda3" / "envs" / "osm" / "Library" / "bin" / "osmium.exe",
#         user_home / "miniconda3" / "envs" / "osm" / "Library" / "bin" / "osmium.exe",
#         user_home / "anaconda3" / "Scripts" / "osmium.exe",
#     ]
#     for p in possible_conda_paths:
#         if p.exists():
#             return str(p)
#     return None

# def find_osmium_binary():
#     # 1. Check system PATH first
#     bin_path = shutil.which("osmium")
#     if bin_path:
#         return bin_path
    
#     # 2. Check conda environments for osmium (without .exe suffix first, or general lookup)
#     user_home = Path.home()
#     possible_conda_paths = [
#         user_home / "anaconda3" / "envs" / "osm" / "Library" / "bin" / "osmium",
#         user_home / "miniconda3" / "envs" / "osm" / "Library" / "bin" / "osmium",
#         user_home / "anaconda3" / "envs" / "osm" / "Library" / "bin" / "osmium.exe",
#         user_home / "miniconda3" / "envs" / "osm" / "Library" / "bin" / "osmium.exe",
#     ]
#     for p in possible_conda_paths:
#         if p.exists():
#             return str(p)
            
#     # Fallback to general lookup if active in path
#     return shutil.which("osmium")

def find_osmium_binary():
    # Force use of the global system/conda command path directly
    return "osmium"
=======
def find_osmium_binary():
    # 1. Check system PATH
    bin_path = shutil.which("osmium")
    if bin_path:
        return bin_path
    
    # 2. Check conda environments
    user_home = Path.home()
    possible_conda_paths = [
        user_home / "anaconda3" / "envs" / "osm" / "Library" / "bin" / "osmium.exe",
        user_home / "miniconda3" / "envs" / "osm" / "Library" / "bin" / "osmium.exe",
        user_home / "anaconda3" / "Scripts" / "osmium.exe",
    ]
    for p in possible_conda_paths:
        if p.exists():
            return str(p)
    return None
>>>>>>> 1b22c1d78ecd2551d2a162bb3305036e18304b4c

def find_ogr2ogr_binary():
    bin_path = shutil.which("ogr2ogr")
    if bin_path:
        return bin_path
    user_home = Path.home()
    possible_paths = [
        user_home / "anaconda3" / "envs" / "osm" / "Library" / "bin" / "ogr2ogr.exe",
        user_home / "miniconda3" / "envs" / "osm" / "Library" / "bin" / "ogr2ogr.exe",
    ]
    for p in possible_paths:
        if p.exists():
            return str(p)
    return None

def filter_with_osmium(osmium_cmd, filter_name, filter_rules, input_file, output_file, force=False):
    if not force and output_file.exists() and output_file.stat().st_size > 0:
        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"[i] {output_file.name} already exists ({size_mb:.2f} MB). Skipping. Use --force to re-extract.")
        return

    print(f"\n==========================================")
    print(f"[*] Filtering: {filter_name}")
    print(f"    Input:  {input_file.name}")
    print(f"    Output: {output_file.name}")
    print(f"==========================================")
    
    cmd = [osmium_cmd, "tags-filter", str(input_file)] + filter_rules + ["-o", str(output_file), "--overwrite"]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"[+] Successfully generated {output_file.name} ({size_mb:.2f} MB)")
    else:
        print(f"[-] Error filtering {filter_name} (exit code {result.returncode})")

def convert_to_gpkg(ogr_cmd, osm_pbf, layer_type, gpkg_output, where_clause=None):
    print(f"\n[*] Converting {osm_pbf.name} to {gpkg_output.name} ({layer_type})...")
    cmd = [ogr_cmd, "-f", "GPKG", str(gpkg_output), str(osm_pbf), layer_type]
    if where_clause:
        cmd += ["-where", where_clause]
    print(f"Running: {' '.join(cmd)}")
    env = os.environ.copy()
    gdal_share = Path(ogr_cmd).parents[1] / "share" / "gdal"
    if gdal_share.exists():
        env["GDAL_DATA"] = str(gdal_share)
        osmconf = gdal_share / "osmconf.ini"
        if osmconf.exists():
            env["OSM_CONFIG_FILE"] = str(osmconf)
    subprocess.run(cmd, env=env)

def main():
    if not INPUT_PBF.exists():
        print(f"[!] Target input file not found: {INPUT_PBF}")
        print("Please ensure download finishes before running the extraction.")
        return 1
    
    osmium_bin = find_osmium_binary()
    if not osmium_bin:
        print("[!] osmium CLI executable not found in PATH or conda env 'osm'.")
        print("Run: conda activate osm")
        return 1
    
    print(f"[+] Found osmium: {osmium_bin}")
    
    # 1. Major Highways
    filter_with_osmium(
        osmium_bin,
        "Major Highways",
        FILTERS["highways"],
        INPUT_PBF,
        OUTPUT_FILES["highways"],
    )

    # 2. Transport Corridors (Railways & Road relations)
    filter_with_osmium(
        osmium_bin,
        "Transport Corridors",
        FILTERS["corridors"],
        INPUT_PBF,
        OUTPUT_FILES["corridors"],
    )

    # 3. All Roads
    filter_with_osmium(
        osmium_bin,
        "All Roads",
        FILTERS["roads"],
        INPUT_PBF,
        OUTPUT_FILES["roads"],
    )

    # 4. Points of Interest (POIs)
    filter_with_osmium(
        osmium_bin,
        "POIs",
        FILTERS["pois"],
        INPUT_PBF,
        OUTPUT_FILES["pois"],
    )

    # Optional GDAL conversion
    ogr_bin = find_ogr2ogr_binary()
    if ogr_bin:
        print(f"\n[+] Found ogr2ogr: {ogr_bin}")
        # Convert highways to GeoPackage
        convert_to_gpkg(ogr_bin, OUTPUT_FILES["highways"], "lines", BASE_DIR / "india_highways.gpkg")
        # Extract National Highways specifically
        convert_to_gpkg(
            ogr_bin,
            OUTPUT_FILES["highways"],
            "lines",
            BASE_DIR / "india_nh.gpkg",
            where_clause='other_tags LIKE \'%"ref"=>"NH%\'',
        )
        # Convert Corridors to GeoPackage
        convert_to_gpkg(ogr_bin, OUTPUT_FILES["corridors"], "lines", BASE_DIR / "india_corridors.gpkg")
        # Convert POIs to GeoPackage (points)
        convert_to_gpkg(ogr_bin, OUTPUT_FILES["pois"], "points", BASE_DIR / "india_pois.gpkg")
    else:
        print("\n[i] ogr2ogr not found. GeoPackage conversion skipped (PBF files are ready for QGIS/GDAL).")

if __name__ == "__main__":
    sys.exit(main() or 0)
