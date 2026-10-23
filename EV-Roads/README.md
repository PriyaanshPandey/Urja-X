# EV-Roads: OpenStreetMap (OSM) Infrastructure Data

This directory contains OpenStreetMap extraction pipelines and data for India's roads, highways, transport corridors, and Points of Interest (POIs).

## Data Source
- **Geofabrik OpenStreetMap Extracts**: [India OSM PBF](https://download.geofabrik.de/asia/india.html)
- Source file: `india-latest.osm.pbf` (~1.6 GB)

## Extracted Layers

| Layer | Output PBF | Tags / Filter Criteria | Description |
|---|---|---|---|
| **Major Highways** | `india_highways.osm.pbf` | `w/highway=motorway,trunk,primary,secondary,motorway_link,trunk_link,primary_link,secondary_link` | Expressways, National Highways (NH), and State Highways |
| **Transport Corridors** | `india_corridors.osm.pbf` | `w/railway=rail,light_rail,subway,narrow_gauge` & `r/route=road,railway,bus` | Railways, freight/passenger rail corridors, and key transit routes |
| **All Roads** | `india_roads.osm.pbf` | `w/highway` | Complete road network across all road classifications |
| **POIs** | `india_pois.osm.pbf` | `nwr/amenity`, `nwr/shop`, `nwr/tourism`, `nwr/leisure` | Charging stations, fuel stations, bus terminals, public amenities |

## Running the Extraction

### Prerequisites
Activate the Conda environment containing Osmium and GDAL:
```powershell
conda activate osm
```

### Run Extraction Pipeline
Run either via PowerShell or Python:
```powershell
# Using PowerShell
cd EV-Roads
.\filter_and_export.ps1

# Or using Python
python filter_and_export.py
```

### Manual CLI Commands (Osmium)
```bash
# 1. Major Highways
osmium tags-filter india-latest.osm.pbf w/highway=motorway,trunk,primary,secondary,motorway_link,trunk_link,primary_link,secondary_link -o india_highways.osm.pbf --overwrite

# 2. Transport Corridors
osmium tags-filter india-latest.osm.pbf w/railway=rail,light_rail,subway,narrow_gauge r/route=road,railway,bus -o india_corridors.osm.pbf --overwrite

# 3. All Roads
osmium tags-filter india-latest.osm.pbf w/highway -o india_roads.osm.pbf --overwrite

# 4. POIs
osmium tags-filter india-latest.osm.pbf nwr/amenity nwr/shop nwr/tourism nwr/leisure -o india_pois.osm.pbf --overwrite
```

### GeoPackage (GPKG) Export via GDAL
```bash
# Convert Major Highways to GeoPackage
ogr2ogr -f GPKG india_highways.gpkg india_highways.osm.pbf lines

# Filter National Highways (ref starts with 'NH')
ogr2ogr -f GPKG india_nh.gpkg india_highways.osm.pbf lines -where "other_tags LIKE '%\"ref\"=>\"NH%'"
```
