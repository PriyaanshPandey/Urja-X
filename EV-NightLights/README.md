# EV-NightLights: India Night-time Radiance & Economic Vitality

This module processes, analyzes, and visualizes night-time light (NTL) radiance along Indian highway corridors and expressways using **NOAA/VIIRS Visible Infrared Imaging Radiometer Suite** and **NASA Black Marble** satellite sensors.

---

## 🛰️ Dataset & Sensor Specifications
- **Sensor**: Suomi NPP / NOAA-20 VIIRS (Day/Night Band - DNB)
- **Spectral Band**: `avg_rade9h` (Cloud-free average radiance)
- **Resolution**: ~500 meters (15 arc-seconds)
- **Unit**: $nW / cm^2 / sr$ (nanoWatts per square centimeter per steradian)
- **Significance**: Validated global proxy for regional GDP, commercial activity, industrial electrification, and urban density.

---

## 🚀 Usage

### 1. View Corridor Economic Radiance Table
```powershell
# View all corridors ranked by night-time light radiance
python nightlights_table_viewer.py

# Filter specific highway corridor (e.g., NH48, MPE, NH44, DME)
python nightlights_table_viewer.py --filter "NH48"
python nightlights_table_viewer.py --filter "MPE"
```

### 2. Export Latest VIIRS Composite via Google Earth Engine (GEE)
Open [gee_export_india_ntl.js](file:///c:/Users/Priyansh%20Pandey/OneDrive/Desktop/urjax/Urja-X/EV-NightLights/gee_export_india_ntl.js) in the [Google Earth Engine Code Editor](https://code.earthengine.google.com/) to export the latest composite GeoTIFF directly to your Google Drive.

---

## 📈 Economic Tiers & Commercial Viability Benchmarks

| Mean Radiance ($nW/cm^2/sr$) | Economic Tier | EV Charging Commercial Viability |
|---|---|---|
| **$\ge$ 40.0** | 🌟 Tier 1: Prime Economic Hub | 🚀 Ultra-Fast DC Hubs ($\ge$ 150 kW) with 24/7 fleet utilization |
| **30.0 – 40.0** | ⚡ Tier 2: Strong Industrial Corridor | ⚡ High Demand (60–120 kW dual-gun DC fast chargers) |
| **20.0 – 30.0** | 📈 Tier 3: Developing Intercity Link | 🔌 Moderate Demand (30–60 kW fast chargers) |
| **$<$ 20.0** | 🌱 Tier 4: Emerging / Remote Route | 🔋 Captive / Destination Charging (AC + Solar backup) |
