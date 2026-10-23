/**
 * Google Earth Engine (GEE) Script: Export India Annual VIIRS Nighttime Lights
 * Dataset: NOAA/VIIRS/DNB/ANNUAL_V22 (Visible Infrared Imaging Radiometer Suite)
 * Band: avg_rade9h (Average Cloud-free DNB Radiance, nanoWatts/cm2/sr)
 * 
 * Instructions:
 * 1. Open https://code.earthengine.google.com/
 * 2. Paste this script into the Code Editor.
 * 3. Click 'Run' and open the 'Tasks' tab to click 'Run' on the export task.
 */

// 1. Define India Administrative Boundary
var india = ee.FeatureCollection("FAO/GAUL/2015/level0")
  .filter(ee.Filter.eq('ADM0_NAME', 'India'));

// 2. Load VIIRS Annual Nighttime Lights Collection (Latest Year)
var viirsAnnual = ee.ImageCollection("NOAA/VIIRS/DNB/ANNUAL_V22")
  .filterDate('2023-01-01', '2023-12-31')
  .select('avg_rade9h')
  .first()
  .clip(india);

// 3. Visualization on Map Canvas
var visParams = {
  min: 0.0,
  max: 60.0,
  palette: ['000004', '2c105c', '711f81', 'b63679', 'ee605e', 'fba40a', 'fcfdbf']
};

Map.centerObject(india, 5);
Map.addLayer(viirsAnnual, visParams, 'India Nighttime Lights (VIIRS)');

// 4. Export to Google Drive as GeoTIFF
Export.image.toDrive({
  image: viirsAnnual,
  description: 'india_viirs_nightlights_2023_500m',
  folder: 'Urja_X_Data',
  fileNamePrefix: 'india_viirs_ntl_500m',
  region: india.geometry(),
  scale: 500, // 500 meter resolution
  maxPixels: 1e10,
  crs: 'EPSG:4326',
  fileFormat: 'GeoTIFF'
});
