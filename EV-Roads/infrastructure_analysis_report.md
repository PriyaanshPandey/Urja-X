# Urja-X: India EV Infrastructure & Spatial Corridors Analysis

## Executive Summary
This report analyzes India's nationwide Electric Vehicle (EV) charging ecosystem overlaid across national highway corridors, transit routes, and Points of Interest extracted from OpenStreetMap.

---

## 1. Key Metrics

- **Total Verified EV Charging Stations**: 39,640
- **High-Capacity / DC Fast Chargers (>=25 kW)**: 8,894
- **Sampled National Highway Segments**: 15,000
- **Data Layers Integrated**: National Highways, Rail Corridors, All Roads, and POIs.

---

## 2. Top Charge Point Operators (CPOs)

| CPO Name | Station Count |
|---|---|
| IOCL | 8,363 |
| UJOY | 7,644 |
| BPCL | 6,617 |
| Reliance BP | 3,635 |
| Tata Power | 3,240 |
| HPCL | 2,316 |
| Ather | 1,207 |
| KAZAM | 909 |

---

## 3. Top States by EV Charging Density

| State | Station Count |
|---|---|
| Karnataka | 8,246 |
| Maharashtra | 5,747 |
| Delhi | 3,475 |
| Haryana | 2,873 |
| Uttar Pradesh | 2,612 |
| Tamil Nadu | 2,568 |
| Kerala | 1,975 |
| Rajasthan | 1,671 |

---

## 4. Key National Highway Corridors Covered

Top National Highway references identified in OpenStreetMap data:
- **NH44**: 1,117 tracked segments
- **NH48**: 1,052 tracked segments
- **NH27**: 854 tracked segments
- **NH19**: 611 tracked segments
- **NH52**: 220 tracked segments
- **NH30**: 211 tracked segments
- **NH5**: 186 tracked segments
- **NH9**: 177 tracked segments
- **NH34**: 175 tracked segments
- **NH66**: 171 tracked segments

---

## 5. How to View the Interactive Map
Open the interactive map dashboard in any web browser:
```powershell
Start-Process "EV-Roads/ev_corridors_map.html"
```
Features available in the map:
- **Toggleable Layers**: Switch between National Highway lines, Clustered EV Charging Points, and Density Heatmap.
- **Fast vs Slow Filter**: Fast DC chargers (CCS-2) are highlighted with green lightning markers.
- **Base Map Chooser**: Switch between Positron (light mode), Dark Matter (night mode), and OpenStreetMap.
