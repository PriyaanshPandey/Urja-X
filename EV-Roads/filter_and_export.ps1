# PowerShell OSM Data Extraction and Filtering Pipeline
param (
    [string]$InputPbf = "india-latest.osm.pbf"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " OSM India Data Extraction: Roads, Highways, Corridors, POIs" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Check if osmium is in PATH, otherwise look in conda osm env
$osmiumCmd = Get-Command osmium -ErrorAction SilentlyContinue
if (-not $osmiumCmd) {
    $condaOsmium = "$env:USERPROFILE\anaconda3\envs\osm\Library\bin\osmium.exe"
    if (Test-Path $condaOsmium) {
        $osmiumExe = $condaOsmium
    } else {
        Write-Error "osmium executable not found. Please activate conda env: conda activate osm"
        exit 1
    }
} else {
    $osmiumExe = $osmiumCmd.Source
}

Write-Host "[+] Using Osmium: $osmiumExe" -ForegroundColor Green

if (-not (Test-Path $InputPbf)) {
    Write-Error "Input file $InputPbf does not exist yet. Please wait for download to finish."
    exit 1
}

# 1. Major Highways
Write-Host "`n[*] Extracting Major Highways..." -ForegroundColor Yellow
& $osmiumExe tags-filter $InputPbf "w/highway=motorway,trunk,primary,secondary,motorway_link,trunk_link,primary_link,secondary_link" -o india_highways.osm.pbf --overwrite
Write-Host "[+] Major Highways extracted -> india_highways.osm.pbf" -ForegroundColor Green

# 2. Transport Corridors (Railways & Route relations)
Write-Host "`n[*] Extracting Transport Corridors..." -ForegroundColor Yellow
& $osmiumExe tags-filter $InputPbf "w/railway=rail,light_rail,subway,narrow_gauge" "r/route=road,railway,bus" -o india_corridors.osm.pbf --overwrite
Write-Host "[+] Transport Corridors extracted -> india_corridors.osm.pbf" -ForegroundColor Green

# 3. All Roads
Write-Host "`n[*] Extracting All Roads..." -ForegroundColor Yellow
& $osmiumExe tags-filter $InputPbf "w/highway" -o india_roads.osm.pbf --overwrite
Write-Host "[+] All Roads extracted -> india_roads.osm.pbf" -ForegroundColor Green

# 4. Points of Interest (POIs: charging stations, fuel, amenities, transport)
Write-Host "`n[*] Extracting POIs..." -ForegroundColor Yellow
& $osmiumExe tags-filter $InputPbf "nwr/amenity" "nwr/shop" "nwr/tourism" "nwr/leisure" -o india_pois.osm.pbf --overwrite
Write-Host "[+] POIs extracted -> india_pois.osm.pbf" -ForegroundColor Green

# Check for GDAL ogr2ogr
$ogrCmd = Get-Command ogr2ogr -ErrorAction SilentlyContinue
$ogrExe = $null
if ($ogrCmd) {
    $ogrExe = $ogrCmd.Source
} else {
    $condaOgr = "$env:USERPROFILE\anaconda3\envs\osm\Library\bin\ogr2ogr.exe"
    if (Test-Path $condaOgr) { $ogrExe = $condaOgr }
}

if ($ogrExe) {
    $gdalShare = "$env:USERPROFILE\anaconda3\envs\osm\Library\share\gdal"
    if (Test-Path $gdalShare) {
        $env:GDAL_DATA = $gdalShare
        $env:OSM_CONFIG_FILE = "$gdalShare\osmconf.ini"
    }

    Write-Host "`n[+] Converting Major Highways to GeoPackage..." -ForegroundColor Yellow
    & $ogrExe -f GPKG india_highways.gpkg india_highways.osm.pbf lines
    Write-Host "[+] Converted -> india_highways.gpkg" -ForegroundColor Green

    Write-Host "`n[+] Converting National Highways to GeoPackage..." -ForegroundColor Yellow
    & $ogrExe -f GPKG india_nh.gpkg india_highways.osm.pbf lines -where 'other_tags LIKE ''%"ref"=>"NH%"'''
    Write-Host "[+] Converted -> india_nh.gpkg" -ForegroundColor Green
} else {
    Write-Host "`n[i] ogr2ogr not found in PATH or osm env. PBF outputs are complete and ready for QGIS." -ForegroundColor Yellow
}

Write-Host "`n[+] All extractions completed successfully!" -ForegroundColor Cyan
