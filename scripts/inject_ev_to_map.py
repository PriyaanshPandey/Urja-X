"""
Urja-X EV Infrastructure & Fleet Map Integrator
Injects Fast DC chargers, Standard AC chargers, State EV Fleet Adoption Badges,
and EV Fleet Density heatmap into india_multimodal_heatmap.html.
"""

import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
HTML_PATH = BASE_DIR / "india_multimodal_heatmap.html"
CHARGER_BUNDLE = BASE_DIR / "EV-Charger" / "urja_ev_bundle.js"

def get_ev_js(map_var, lc_var):
    return f"""
// ============================================================================
// 🚗 URJA-X EV CHARGERS & VEHICLE FLEET INTEGRATION
// ============================================================================
function initUrjaEV(map, layerControl) {{
    if (typeof URJA_EV_DATA === 'undefined') {{
        console.warn("[Urja-X] EV data bundle not detected.");
        return;
    }}
    if (!map || !layerControl) {{
        console.error("[Urja-X] Leaflet map or layerControl instance not provided.");
        return;
    }}

    console.log("[Urja-X] Initializing EV Chargers & Vehicle Fleet layers...");

    // 1. FAST DC CHARGING STATIONS (>= 25 kW)
    var fastDcCluster = L.markerClusterGroup({{
        maxClusterRadius: 45,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        iconCreateFunction: function(cluster) {{
            return L.divIcon({{
                html: '<div style="background: rgba(6, 182, 212, 0.95); color: white; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; border: 2px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4);">' + cluster.getChildCount() + '</div>',
                className: 'urja-dc-cluster',
                iconSize: L.point(34, 34)
            }});
        }}
    }});

    URJA_EV_DATA.dc_chargers.forEach(function(c) {{
        var lat = c[0], lon = c[1], cpo = c[2], loc = c[3], conn = c[4], rating = c[5], ports = c[6], govtPvt = c[7], city = c[8], state = c[9];
        
        var m = L.circleMarker([lat, lon], {{
            radius: 5,
            fillColor: '#06b6d4',
            color: '#ffffff',
            weight: 1.8,
            opacity: 1.0,
            fillOpacity: 0.92
        }});

        var popupHtml = `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; min-width: 250px; padding: 4px; color: #0f172a;">
                <div style="background: #0891b2; color: #f8fafc; padding: 8px 12px; border-radius: 6px 6px 0 0; margin: -4px -4px 8px -4px;">
                    <div style="font-weight: bold; font-size: 13px;">⚡ ${{cpo}} Fast DC Hub</div>
                    <span style="font-size: 10px; color: #cffafe; font-weight: 600; text-transform: uppercase;">${{govtPvt}} CPO</span>
                </div>
                <div style="font-size: 11px; line-height: 1.6; color: #334155; padding-top: 4px;">
                    <div><b>Power Output:</b> <span style="color: #0891b2; font-weight: bold;">${{rating > 0 ? rating + ' kW DC Fast' : 'High-Power DC'}}</span></div>
                    <div><b>Connectors:</b> ${{conn}} (${{ports}} port${{ports > 1 ? 's' : ''}})</div>
                    <div><b>Location:</b> ${{loc || city || 'Highway Transit Site'}}</div>
                    <div><b>Region:</b> ${{city ? city + ', ' : ''}}${{state}}</div>
                    <div style="margin-top: 8px; padding-top: 6px; border-top: 1px dashed #cbd5e1; font-size: 10px; color: #64748b; font-style: italic;">
                        ⚡ Verified Operational Public DC Fast Charger.
                    </div>
                </div>
            </div>
        `;
        m.bindPopup(popupHtml, {{ maxWidth: 290 }});
        m.bindTooltip('⚡ ' + cpo + ' (' + rating + ' kW DC)', {{ sticky: true }});
        fastDcCluster.addLayer(m);
    }});

    // 2. STANDARD AC CHARGERS (< 25 kW)
    var standardAcCluster = L.markerClusterGroup({{
        maxClusterRadius: 45,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        iconCreateFunction: function(cluster) {{
            return L.divIcon({{
                html: '<div style="background: rgba(16, 185, 129, 0.95); color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; border: 2px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4);">' + cluster.getChildCount() + '</div>',
                className: 'urja-ac-cluster',
                iconSize: L.point(32, 32)
            }});
        }}
    }});

    URJA_EV_DATA.ac_chargers.forEach(function(c) {{
        var lat = c[0], lon = c[1], cpo = c[2], loc = c[3], conn = c[4], rating = c[5], ports = c[6], govtPvt = c[7], city = c[8], state = c[9];
        
        var m = L.circleMarker([lat, lon], {{
            radius: 4,
            fillColor: '#10b981',
            color: '#ffffff',
            weight: 1.4,
            opacity: 0.9,
            fillOpacity: 0.85
        }});

        var popupHtml = `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; min-width: 240px; padding: 4px; color: #0f172a;">
                <div style="background: #059669; color: #f8fafc; padding: 8px 12px; border-radius: 6px 6px 0 0; margin: -4px -4px 8px -4px;">
                    <div style="font-weight: bold; font-size: 13px;">🔌 ${{cpo}} AC Station</div>
                    <span style="font-size: 10px; color: #d1fae5; font-weight: 600;">${{govtPvt}} Operator</span>
                </div>
                <div style="font-size: 11px; line-height: 1.6; color: #334155; padding-top: 4px;">
                    <div><b>Rating:</b> ${{rating > 0 ? rating + ' kW AC' : 'Standard AC'}}</div>
                    <div><b>Connector Type:</b> ${{conn}}</div>
                    <div><b>Location:</b> ${{loc || city || 'Urban / Commercial Hub'}}</div>
                    <div><b>Region:</b> ${{city ? city + ', ' : ''}}${{state}}</div>
                </div>
            </div>
        `;
        m.bindPopup(popupHtml, {{ maxWidth: 280 }});
        m.bindTooltip('🔌 ' + cpo + ' (' + (rating > 0 ? rating + ' kW' : 'AC') + ')', {{ sticky: true }});
        standardAcCluster.addLayer(m);
    }});

    // 3. STATE EV FLEET ADOPTION BADGES (5.8M Registered Vehicles from VAHAN)
    var stateFleetGroup = L.featureGroup();

    function formatNumber(num) {{
        if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
        if (num >= 1000) return Math.round(num / 1000) + 'K';
        return num.toLocaleString();
    }}

    URJA_EV_DATA.state_fleet.forEach(function(sf) {{
        var countStr = formatNumber(sf.total);
        var iconHtml = `
            <div style="
                background: linear-gradient(135deg, #4f46e5, #7c3aed);
                color: #ffffff;
                padding: 4px 8px;
                border-radius: 12px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-weight: 800;
                font-size: 11px;
                white-space: nowrap;
                box-shadow: 0 4px 12px rgba(79, 70, 229, 0.45);
                border: 2px solid #ffffff;
                display: flex;
                align-items: center;
                gap: 4px;
            ">
                <span style="font-size: 10px;">🚗</span> ${{sf.state.length > 10 ? sf.state.substring(0, 8) + '..' : sf.state}}: <span style="color: #fde047;">${{countStr}}</span>
            </div>
        `;

        var badgeIcon = L.divIcon({{
            html: iconHtml,
            className: 'urja-fleet-badge',
            iconSize: [110, 26],
            iconAnchor: [55, 13]
        }});

        var m = L.marker([sf.lat, sf.lon], {{ icon: badgeIcon }});

        var w2Pct = sf.total > 0 ? ((sf.w2 / sf.total) * 100).toFixed(1) : 0;
        var w3Pct = sf.total > 0 ? ((sf.w3 / sf.total) * 100).toFixed(1) : 0;
        var w4Pct = sf.total > 0 ? ((sf.w4 / sf.total) * 100).toFixed(1) : 0;

        var popupHtml = `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; min-width: 270px; padding: 4px; color: #0f172a;">
                <div style="background: linear-gradient(135deg, #4338ca, #6d28d9); color: #f8fafc; padding: 10px 14px; border-radius: 6px 6px 0 0; margin: -4px -4px 8px -4px;">
                    <div style="font-weight: bold; font-size: 14px;">🚗 ${{sf.state}} EV Fleet</div>
                    <div style="font-size: 11px; color: #c7d2fe; margin-top: 2px;">
                        Total Registered EVs: <b style="color: #fde047; font-size: 13px;">${{sf.total.toLocaleString()}}</b>
                    </div>
                </div>
                <div style="font-size: 11.5px; line-height: 1.6; color: #334155;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 2px 0;">
                        <span>🛵 <b>2-Wheelers (E-2W):</b></span>
                        <span><b>${{sf.w2.toLocaleString()}}</b> <span style="color:#64748b; font-size:10px;">(${{w2Pct}}%)</span></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 2px 0;">
                        <span>🛺 <b>3-Wheelers (E-3W / Rickshaws):</b></span>
                        <span><b>${{sf.w3.toLocaleString()}}</b> <span style="color:#64748b; font-size:10px;">(${{w3Pct}}%)</span></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 2px 0;">
                        <span>🚙 <b>4-Wheelers (Personal & Cabs):</b></span>
                        <span><b>${{sf.w4.toLocaleString()}}</b> <span style="color:#64748b; font-size:10px;">(${{w4Pct}}%)</span></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 2px 0;">
                        <span>🚌 <b>Electric Buses:</b></span>
                        <span><b>${{sf.bus.toLocaleString()}}</b></span>
                    </div>
                    ${{sf.others > 0 ? `
                    <div style="display: flex; justify-content: space-between; padding: 2px 0;">
                        <span>📦 <b>Commercial Goods & Others:</b></span>
                        <span><b>${{sf.others.toLocaleString()}}</b></span>
                    </div>` : ''}}
                    <div style="margin-top: 8px; padding-top: 6px; border-top: 1px dashed #cbd5e1; font-size: 10px; color: #64748b; font-style: italic;">
                        📊 Official VAHAN Dashboard Ground Truth (MoRTH, Govt. of India).
                    </div>
                </div>
            </div>
        `;
        m.bindPopup(popupHtml, {{ maxWidth: 300 }});
        m.bindTooltip('🚗 ' + sf.state + ': ' + sf.total.toLocaleString() + ' EVs', {{ sticky: true }});
        stateFleetGroup.addLayer(m);
    }});

    // 4. EV FLEET DENSITY HEATMAP
    var evFleetHeatLayer = L.heatLayer(URJA_EV_DATA.heat_points, {{
        name: "EV Fleet Heatmap",
        radius: 35,
        blur: 32,
        max_zoom: 9,
        min_opacity: 0.35,
        gradient: {{
            0.15: "#312e81",
            0.40: "#6366f1",
            0.65: "#a855f7",
            0.85: "#ec4899",
            1.00: "#fde047"
        }}
    }});

    // ADD TO MAP (Default: Fast DC & State Fleet ON)
    fastDcCluster.addTo(map);
    stateFleetGroup.addTo(map);

    // REGISTER IN LAYER CONTROL
    layerControl.addOverlay(fastDcCluster, "⚡ [EV] Fast DC Chargers (12K Stations)");
    layerControl.addOverlay(standardAcCluster, "🔌 [EV] Standard AC Chargers (27.5K Stations)");
    layerControl.addOverlay(stateFleetGroup, "🚗 [EV] State Fleet Adoption Badges (5.8M EVs)");
    layerControl.addOverlay(evFleetHeatLayer, "🔥 [EV] Vehicle Fleet Density Heatmap");

    // FORMAT LAYER SWITCHER WITH EV INFRASTRUCTURE SECTION
    function formatEVControl() {{
        var container = document.querySelector('.leaflet-control-layers-overlays');
        if (!container) return;
        var labels = container.querySelectorAll('label');
        var firstEVLabel = null;
        labels.forEach(function(lbl) {{
            var txt = lbl.textContent || '';
            if (txt.includes('[EV]')) {{
                if (!firstEVLabel) firstEVLabel = lbl;
                lbl.style.display = 'block';
                lbl.style.paddingLeft = '4px';
            }}
        }});

        if (firstEVLabel && !document.getElementById('urja-ev-divider')) {{
            var div = document.createElement('div');
            div.id = 'urja-ev-divider';
            div.style.cssText = 'margin: 10px 0 6px 0; border-top: 1px solid rgba(6, 182, 212, 0.4); padding-top: 8px;';
            div.innerHTML = '<div style="font-weight: 700; color: #0891b2; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">🚗 EV Chargers & Fleet Demand</div>';
            firstEVLabel.parentNode.insertBefore(div, firstEVLabel);
        }}
    }}
    setTimeout(formatEVControl, 300);
    setTimeout(formatEVControl, 900);

    console.log("[Urja-X] EV Chargers & Vehicle Fleet layers initialized successfully.");
}}
"""

UPDATED_LEGEND_CARD = """
    <div style="
        position: fixed;
        bottom: 25px;
        left: 25px;
        z-index: 9999;
        background: rgba(15, 23, 42, 0.94);
        backdrop-filter: blur(12px);
        color: #f8fafc;
        padding: 16px 20px;
        border-radius: 12px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 10px 32px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.15);
        max-width: 350px;
        font-size: 11px;
    ">
        <h4 style="margin: 0 0 10px 0; font-size: 13.5px; color: #38bdf8; display: flex; align-items: center; gap: 6px;">
            ⚡ Urja-X Unified Multimodal, Grid & EV Map
        </h4>

        <!-- Population Density -->
        <div style="margin-bottom: 6px;">
            <b style="color: #cbd5e1;">👥 Population Density (WorldPop):</b><br>
            <div style="height: 7px; background: linear-gradient(to right, #10b981, #facc15, #f97316, #dc2626); border-radius: 4px; margin: 3px 0;"></div>
            <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 9.5px;">
                <span>Rural</span>
                <span>Industrial</span>
                <span>Mega-City Core</span>
            </div>
        </div>

        <!-- Night-time Lights -->
        <div style="margin-bottom: 6px;">
            <b style="color: #cbd5e1;">🌃 Night-time Lights (VIIRS NTL):</b><br>
            <div style="height: 7px; background: linear-gradient(to right, #312e81, #8b5cf6, #ec4899, #f59e0b, #ffffff); border-radius: 4px; margin: 3px 0;"></div>
            <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 9.5px;">
                <span>Unlit</span>
                <span>Suburban</span>
                <span>Economic Hub</span>
            </div>
        </div>

        <!-- Electricity Grid Infrastructure -->
        <div style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.15); padding-top: 7px;">
            <b style="color: #38bdf8;">⚡ Power Transmission Grid (CEA Tiers):</b>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top: 4px; font-size: 10px;">
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:13px; height:4px; background:#e11d48; border-radius:2px;"></span>
                    <span>≥ 765 kV UHV</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:13px; height:3px; background:#ea580c; border-radius:2px;"></span>
                    <span>400 kV EHV</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:13px; height:2.5px; background:#f59e0b; border-radius:2px;"></span>
                    <span>220 kV HV</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:13px; height:2px; background:#06b6d4; border-radius:2px;"></span>
                    <span>110–132 kV Sub</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:13px; height:1.5px; background:#3b82f6; border-radius:2px;"></span>
                    <span>33–66 kV Dist</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:13px; height:1.5px; background:#94a3b8; border-top:1px dashed #94a3b8;"></span>
                    <span>Unspecified *</span>
                </div>
            </div>
            <div style="margin-top: 5px; display: flex; flex-wrap: wrap; gap: 8px; font-size: 9.5px; color: #cbd5e1;">
                <span><span style="display:inline-block; width:7px; height:7px; background:#8b5cf6; border-radius:50%; border:1px solid #fff;"></span> Substations</span>
                <span><span style="display:inline-block; width:7px; height:7px; background:#d97706; border-radius:50%;"></span> Transformers</span>
                <span><span style="display:inline-block; width:7px; height:7px; background:#10b981; border-radius:50%;"></span> Power Plants</span>
            </div>
        </div>

        <!-- EV Charging & Vehicle Fleet -->
        <div style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.15); padding-top: 7px;">
            <b style="color: #22d3ee;">🚗 EV Charging Supply & Vehicle Fleet:</b>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; font-size: 10px;">
                <span style="display: flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; width:8px; height:8px; background:#06b6d4; border-radius:50%; border:1.5px solid #fff;"></span>
                    <span><b>Fast DC</b> (≥25 kW)</span>
                </span>
                <span style="display: flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; width:8px; height:8px; background:#10b981; border-radius:50%; border:1.5px solid #fff;"></span>
                    <span><b>Standard AC</b></span>
                </span>
                <span style="display: flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; padding: 1px 4px; background:#4f46e5; border-radius:4px; color:#fff; font-size:9px; font-weight:bold;">5.8M EVs</span>
                    <span><b>VAHAN Fleet</b></span>
                </span>
            </div>
        </div>

        <div style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px; color: #94a3b8; font-size: 9px; line-height: 1.3;">
            <i>* Sources: OpenStreetMap (ODbL), Bureau of Energy Efficiency (BEE), and VAHAN (MoRTH). Grid proximity does not guarantee available capacity.</i>
        </div>
    </div>
"""

def inject_all():
    print(f"[*] Reading {HTML_PATH.name}...")
    content = HTML_PATH.read_text(encoding="utf-8")

    # 1. Ensure script tags for both bundles are in <head>
    script_elec = '<script src="Electricity-Data/urja_electricity_bundle.js"></script>'
    script_ev = '<script src="EV-Charger/urja_ev_bundle.js"></script>'

    if script_elec not in content:
        content = content.replace("</head>", f"    {script_elec}\n</head>")
    if script_ev not in content:
        content = content.replace("</head>", f"    {script_ev}\n</head>")

    # 2. Update Legend Card
    idx_title = content.find('Urja-X')
    if idx_title != -1:
        legend_start = content.rfind('<div style="', 0, idx_title)
        legend_end = content.find('</body>', legend_start)
        if legend_start != -1 and legend_end != -1:
            print("[*] Updating legend card with Unified Multimodal, Grid & EV symbology...")
            content = content[:legend_start] + UPDATED_LEGEND_CARD.strip() + "\n    " + content[legend_end:]

    # 3. Find Map and LayerControl variable names
    m_map = re.search(r'var\s+(map_[a-f0-9]+)\s*=\s*L\.map\(', content)
    m_lc = re.search(r'let\s+(layer_control_[a-f0-9]+)\s*=\s*L\.control\.layers\(', content)
    if not m_map or not m_lc:
        print("[!] Could not locate map or layer control variable in HTML.")
        return False

    map_var = m_map.group(1)
    lc_var = m_lc.group(1)
    print(f"[+] Found map variable: {map_var}, layer control variable: {lc_var}")

    # 4. Locate Folium layer_control addTo statement
    lc_addTo_idx = content.rfind(f'.addTo({map_var});')
    if lc_addTo_idx == -1:
        lc_addTo_idx = content.rfind(f'.addTo({map_var})')
    if lc_addTo_idx == -1:
        print("[!] Could not find layer control addTo statement in script.")
        return False

    semi_idx = content.find(';', lc_addTo_idx)
    if semi_idx == -1:
        semi_idx = lc_addTo_idx + len(f'.addTo({map_var})')

    # Cut everything after Folium's layer control statement
    folium_base_code = content[:semi_idx + 1]

    # Import electricity JS generator from inject_electricity_to_map
    from scripts.inject_electricity_to_map import get_electricity_js
    elec_js = get_electricity_js(map_var, lc_var)
    ev_js = get_ev_js(map_var, lc_var)

    combined_js = f"""
{elec_js}

{ev_js}
initUrjaEV({map_var}, {lc_var});
"""

    final_content = folium_base_code + f"\n{combined_js}\n</script>\n</html>\n"
    HTML_PATH.write_text(final_content, encoding="utf-8")
    print(f"[+] Successfully integrated EV Chargers & Vehicle Fleet into {HTML_PATH.name}!")
    return True

if __name__ == "__main__":
    inject_all()
