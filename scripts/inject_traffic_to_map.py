"""
Urja-X Traffic Layer Integrator
Injects IHMCL FASTag Toll Plaza Monthly Traffic markers, styled volume tiers,
search autocomplete, popups, and layer control into india_multimodal_heatmap.html.
Preserves all multimodal heatmaps, electricity infrastructure, and EV charger/fleet layers.
"""

import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

HTML_PATH = BASE_DIR / "india_multimodal_heatmap.html"
TRAFFIC_BUNDLE = BASE_DIR / "Trafic data" / "urja_traffic_bundle.js"

def get_traffic_js(map_var, lc_var):
    return f"""
// ============================================================================
// 🚦 URJA-X TRAFFIC (IHMCL FASTAG TOLL PLAZAS) INTEGRATION
// ============================================================================
function initUrjaTraffic(map, layerControl) {{
    if (typeof URJA_TRAFFIC_DATA === 'undefined') {{
        console.warn("[Urja-X] Traffic data bundle not detected.");
        return;
    }}
    if (!map || !layerControl) {{
        console.error("[Urja-X] Leaflet map or layerControl instance not provided.");
        return;
    }}

    console.log("[Urja-X] Initializing Traffic Toll Plazas layer...");

    // 1. TRAFFIC MARKER CLUSTER GROUP
    var trafficCluster = L.markerClusterGroup({{
        maxClusterRadius: 40,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        iconCreateFunction: function(cluster) {{
            var count = cluster.getChildCount();
            return L.divIcon({{
                html: '<div style="background: rgba(234, 88, 12, 0.95); color: #ffffff; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; border: 2px solid #fed7aa; box-shadow: 0 2px 8px rgba(0,0,0,0.45);">' + count + '</div>',
                className: 'urja-traffic-cluster',
                iconSize: L.point(34, 34)
            }});
        }}
    }});

    // Marker lookup map for search & direct navigation
    var markerRegistry = [];

    // 2. PLOT TOLL PLAZAS
    URJA_TRAFFIC_DATA.locations.forEach(function(loc) {{
        var m = L.circleMarker([loc.lat, loc.lon], {{
            radius: loc.radius || 6,
            fillColor: loc.color || '#ea580c',
            color: '#ffffff',
            weight: 1.8,
            opacity: 1.0,
            fillOpacity: 0.92
        }});

        // Format underlying records (handles single & paired/multi records gracefully)
        var recordsHtml = loc.records.map(function(r, idx) {{
            var pairHeader = loc.records.length > 1 
                ? '<div style="font-size: 10.5px; font-weight: bold; color: #ea580c; margin-bottom: 4px; padding-bottom: 2px; border-bottom: 1px dashed #fed7aa;">Record ' + (idx + 1) + ' of ' + loc.records.length + ' (Paired / Dual Plaza)</div>'
                : '';

            var carJeep = Number(r.car_jeep_cnt || 0).toLocaleString();
            var lcv = Number(r.lcv_cnt || 0).toLocaleString();
            var busTruck = Number(r.bus_truck_cnt || 0).toLocaleString();
            var totalCnt = Number(r.total_cnt || 0).toLocaleString();
            var revenue = r.total_amt ? '₹' + Number(r.total_amt).toLocaleString() : 'N/A';
            var authority = (r.piu || r.ro) ? ('PIU: ' + (r.piu || 'N/A') + ' | RO: ' + (r.ro || 'N/A')) : '';

            return `
                <div style="margin-bottom: 8px;">
                    ${{pairHeader}}
                    <div style="font-size: 11px; line-height: 1.6; color: #334155;">
                        <div><b>IHMCL Plaza:</b> <span style="font-weight: 600; color: #0f172a;">${{r.plaza_name_report}}</span></div>
                        <div><b>Matched Plaza:</b> <span style="color: #475569;">${{r.plaza_name_source}}</span></div>
                    </div>
                    <div style="margin: 6px 0; background: #fff7ed; padding: 6px 8px; border-radius: 5px; border-left: 3px solid #ea580c;">
                        <div style="font-size: 12px; font-weight: bold; color: #c2410c;">
                            Total Monthly Count: ${{totalCnt}}
                        </div>
                        <div style="font-size: 10px; color: #9a3412;">Reporting Month: ${{r.reporting_month}} (Monthly Volume)</div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-size: 10.5px; background: #f8fafc; padding: 6px; border-radius: 4px; border: 1px solid #e2e8f0; margin-bottom: 4px;">
                        <div>🚗 <b>Car/Jeep:</b> <br><span style="font-weight: 600; color: #1e293b;">${{carJeep}}</span></div>
                        <div>🚐 <b>LCV:</b> <br><span style="font-weight: 600; color: #1e293b;">${{lcv}}</span></div>
                        <div>🚛 <b>Bus/Truck:</b> <br><span style="font-weight: 600; color: #1e293b;">${{busTruck}}</span></div>
                        <div>💰 <b>Toll Revenue:</b> <br><span style="font-weight: 600; color: #059669;">${{revenue}}</span></div>
                    </div>
                    ${{authority ? '<div style="font-size: 9.5px; color: #64748b; margin-top: 2px;">🏛️ <b>Authority:</b> ' + authority + '</div>' : ''}}
                </div>
            `;
        }}).join('<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 8px 0;">');

        var popupHtml = `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; min-width: 270px; max-width: 330px; padding: 4px; color: #0f172a;">
                <div style="background: linear-gradient(135deg, #ea580c, #c2410c); color: #fff; padding: 8px 12px; border-radius: 6px 6px 0 0; margin: -4px -4px 8px -4px;">
                    <div style="font-weight: bold; font-size: 13px; display: flex; align-items: center; justify-content: space-between;">
                        <span>🚦 ${{loc.name}}</span>
                    </div>
                    <div style="font-size: 10px; color: #ffedd5; display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
                        <span>${{loc.tier}}</span>
                        <span>Combined: ${{Number(loc.combined_total).toLocaleString()}}</span>
                    </div>
                </div>
                <div style="margin-bottom: 6px; font-size: 10px; color: #64748b; display: flex; justify-content: space-between;">
                    <span>📍 <b>Lat/Lon:</b> ${{loc.lat.toFixed(6)}}, ${{loc.lon.toFixed(6)}}</span>
                    <span>${{loc.records.length > 1 ? '<b style="color:#ea580c;">' + loc.records.length + ' Plazas At Coords</b>' : ''}}</span>
                </div>
                ${{recordsHtml}}
                <div style="margin-top: 8px; padding: 6px 8px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 5px; font-size: 9.5px; color: #be123c; line-height: 1.35;">
                    <b>⚠️ Monthly Traffic Count (January 2026):</b> These figures reflect the cumulative monthly toll throughput and must <u>NOT</u> be interpreted as daily traffic counts or AADT.
                </div>
            </div>
        `;

        m.bindPopup(popupHtml, {{ maxWidth: 350 }});
        m.bindTooltip('🚦 ' + loc.name + ' (' + Number(loc.combined_total).toLocaleString() + ' /mo)', {{ sticky: true }});
        trafficCluster.addLayer(m);

        // Store for search
        markerRegistry.push({{
            name: loc.name,
            lat: loc.lat,
            lon: loc.lon,
            total: loc.combined_total,
            marker: m,
            searchKeys: loc.records.map(function(r) {{ return (r.plaza_name_report + ' ' + r.plaza_name_source + ' ' + (r.piu || '') + ' ' + (r.ro || '')).toLowerCase(); }}).join(' ')
        }});
    }});

    // Add traffic layer to map by default so it's immediately active
    trafficCluster.addTo(map);

    // 3. REGISTER IN LAYER CONTROL
    layerControl.addOverlay(trafficCluster, '<span style="color:#ea580c; font-weight:bold;">🚦 [Traffic] NHAI Toll Plazas (Jan 2026 Monthly)</span>');

    // 4. FORMAT LAYER SWITCHER WITH TRAFFIC SECTION DIVIDER
    function formatTrafficControl() {{
        var container = document.querySelector('.leaflet-control-layers-overlays');
        if (!container) return;
        var labels = container.querySelectorAll('label');
        var firstTrafficLabel = null;
        labels.forEach(function(lbl) {{
            var txt = lbl.textContent || '';
            if (txt.includes('[Traffic]')) {{
                if (!firstTrafficLabel) firstTrafficLabel = lbl;
                lbl.style.display = 'block';
                lbl.style.paddingLeft = '4px';
            }}
        }});

        if (firstTrafficLabel && !document.getElementById('urja-traffic-divider')) {{
            var div = document.createElement('div');
            div.id = 'urja-traffic-divider';
            div.style.cssText = 'margin: 10px 0 6px 0; border-top: 1px solid rgba(234, 88, 12, 0.4); padding-top: 8px;';
            div.innerHTML = '<div style="font-weight: 700; color: #ea580c; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">🚦 Traffic & Corridor Demand</div>';
            firstTrafficLabel.parentNode.insertBefore(div, firstTrafficLabel);
        }}
    }}
    setTimeout(formatTrafficControl, 350);
    setTimeout(formatTrafficControl, 1000);

    // 5. SEARCH & FILTER CONTROL FOR TOLL PLAZAS
    var searchControl = L.control({{ position: 'topleft' }});
    searchControl.onAdd = function() {{
        var div = L.DomUtil.create('div', 'urja-traffic-search-container');
        div.style.cssText = 'background: rgba(15, 23, 42, 0.90); backdrop-filter: blur(8px); padding: 7px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 4px 14px rgba(0,0,0,0.4); font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin-top: 10px; width: 220px;';
        div.innerHTML = `
            <div style="position: relative;">
                <input id="urja-plaza-search-input" type="text" placeholder="🔍 Find Toll Plaza..." 
                    style="width: 100%; box-sizing: border-box; padding: 6px 9px; background: rgba(30, 41, 59, 0.95); border: 1px solid #475569; border-radius: 6px; color: #f8fafc; font-size: 11px; outline: none;">
                <div id="urja-search-dropdown" style="display: none; position: absolute; top: 32px; left: 0; right: 0; max-height: 220px; overflow-y: auto; background: #0f172a; border: 1px solid #334155; border-radius: 6px; z-index: 1500; box-shadow: 0 8px 16px rgba(0,0,0,0.6);"></div>
            </div>
        `;
        L.DomEvent.disableClickPropagation(div);
        L.DomEvent.disableScrollPropagation(div);
        return div;
    }};
    searchControl.addTo(map);

    // Wire up search input handling
    setTimeout(function() {{
        var input = document.getElementById('urja-plaza-search-input');
        var dropdown = document.getElementById('urja-search-dropdown');
        if (!input || !dropdown) return;

        input.addEventListener('input', function() {{
            var query = input.value.trim().toLowerCase();
            if (query.length < 2) {{
                dropdown.style.display = 'none';
                dropdown.innerHTML = '';
                return;
            }}

            var matches = markerRegistry.filter(function(item) {{
                return item.searchKeys.includes(query);
            }}).slice(0, 8);

            if (matches.length === 0) {{
                dropdown.innerHTML = '<div style="padding: 8px 10px; color: #94a3b8; font-size: 11px; font-style: italic;">No toll plazas found</div>';
                dropdown.style.display = 'block';
                return;
            }}

            dropdown.innerHTML = matches.map(function(item) {{
                return `
                    <div class="urja-search-item" data-lat="${{item.lat}}" data-lon="${{item.lon}}" 
                        style="padding: 7px 10px; border-bottom: 1px solid #1e293b; cursor: pointer; color: #f1f5f9; font-size: 11px; transition: background 0.15s ease;">
                        <div style="font-weight: bold; color: #fdba74;">🚦 ${{item.name}}</div>
                        <div style="font-size: 9.5px; color: #94a3b8; display: flex; justify-content: space-between; margin-top: 2px;">
                            <span>Monthly Count:</span>
                            <span style="color: #fb923c; font-weight: 600;">${{Number(item.total).toLocaleString()}}</span>
                        </div>
                    </div>
                `;
            }}).join('');

            dropdown.style.display = 'block';

            // Click on suggestion to navigate
            dropdown.querySelectorAll('.urja-search-item').forEach(function(el) {{
                el.addEventListener('mouseover', function() {{ el.style.background = '#1e293b'; }});
                el.addEventListener('mouseout', function() {{ el.style.background = 'transparent'; }});
                el.addEventListener('click', function() {{
                    var lat = parseFloat(el.getAttribute('data-lat'));
                    var lon = parseFloat(el.getAttribute('data-lon'));
                    var target = markerRegistry.find(function(it) {{ return Math.abs(it.lat - lat) < 0.0001 && Math.abs(it.lon - lon) < 0.0001; }});

                    if (!map.hasLayer(trafficCluster)) {{
                        map.addLayer(trafficCluster);
                    }}

                    map.setView([lat, lon], 13);
                    if (target && target.marker) {{
                        trafficCluster.zoomToShowLayer(target.marker, function() {{
                            target.marker.openPopup();
                        }});
                    }}
                    dropdown.style.display = 'none';
                    input.value = target ? target.name : '';
                }});
            }});
        }});

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {{
            if (!e.target.closest('.urja-traffic-search-container')) {{
                dropdown.style.display = 'none';
            }}
        }});
    }}, 400);

    console.log("[Urja-X] Traffic Toll Plazas layer initialized successfully (" + URJA_TRAFFIC_DATA.locations.length + " locations, " + URJA_TRAFFIC_DATA.metadata.total_records + " records).");
}}
"""

UPDATED_LEGEND_CARD = """
    <div style="
        position: fixed;
        bottom: 25px;
        left: 25px;
        z-index: 1000;
        background: rgba(15, 23, 42, 0.90);
        backdrop-filter: blur(12px);
        color: #f8fafc;
        padding: 14px 18px;
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5), 0 8px 10px -6px rgba(0,0,0,0.5);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        border: 1px solid rgba(255,255,255,0.15);
        max-width: 355px;
        font-size: 11px;
    ">
        <h4 style="margin: 0 0 10px 0; font-size: 13.5px; color: #38bdf8; display: flex; align-items: center; gap: 6px;">
            ⚡ Urja-X Unified Multimodal, Grid & EV Map
        </h4>

        <!-- Population Density -->
        <div style="margin-bottom: 6px;">
            <b style="color: #cbd5e1;">👥 Population Density (WorldPop):</b><br>
            <div style="margin-top: 3px; width: 100%; height: 8px; border-radius: 4px; background: linear-gradient(to right, #00ffff, #00ff00, #ffff00, #ff0000); opacity: 0.85;"></div>
            <div style="display: flex; justify-content: space-between; font-size: 9px; color: #94a3b8; margin-top: 2px;">
                <span>Rural (Low)</span><span>Industrial</span><span>Mega-City Core</span>
            </div>
        </div>

        <!-- Night-time Lights -->
        <div style="margin-bottom: 6px;">
            <b style="color: #cbd5e1;">🌃 Night-time Lights (VIIRS NTL):</b><br>
            <div style="margin-top: 3px; width: 100%; height: 8px; border-radius: 4px; background: linear-gradient(to right, #2c003e, #6a0d83, #d74b76, #f39060, #fed7aa); opacity: 0.85;"></div>
            <div style="display: flex; justify-content: space-between; font-size: 9px; color: #94a3b8; margin-top: 2px;">
                <span>Unlit</span><span>Suburban</span><span>Economic Hub</span>
            </div>
        </div>

        <!-- Road Network Density -->
        <div style="margin-bottom: 6px;">
            <b style="color: #cbd5e1;">🛣️ Highway & Road Density:</b><br>
            <div style="margin-top: 3px; width: 100%; height: 8px; border-radius: 4px; background: linear-gradient(to right, #10b981, #06b6d4, #6366f1, #1e1b4b); opacity: 0.85;"></div>
            <div style="display: flex; justify-content: space-between; font-size: 9px; color: #94a3b8; margin-top: 2px;">
                <span>Local</span><span>Connecting</span><span>Dense Corridor</span>
            </div>
        </div>

        <!-- Electricity Grid Infrastructure -->
        <div style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px;">
            <b style="color: #fde047; display: flex; align-items: center; justify-content: space-between;">
                <span>⚡ Power Grid Transmission (OSM):</span>
                <span style="font-size: 9px; color: #94a3b8; font-weight: normal;">47K+ km</span>
            </b>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top: 4px; font-size: 10px;">
                <span style="display: flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; width:12px; height:3px; background:#dc2626;"></span>
                    <span><b>765+ kV</b> (UHV)</span>
                </span>
                <span style="display: flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; width:12px; height:2.5px; background:#ea580c;"></span>
                    <span><b>400 kV</b> (EHV)</span>
                </span>
                <span style="display: flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; width:12px; height:2px; background:#eab308;"></span>
                    <span><b>220 kV</b> (HV)</span>
                </span>
                <span style="display: flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; width:12px; height:1.5px; background:#38bdf8;"></span>
                    <span><b>132/66 kV</b> (MV)</span>
                </span>
            </div>
        </div>

        <!-- EV Infrastructure & Fleet -->
        <div style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px;">
            <b style="color: #38bdf8; display: flex; align-items: center; justify-content: space-between;">
                <span>🚗 EV Charging & Fleet Adoption:</span>
                <span style="font-size: 9px; color: #94a3b8; font-weight: normal;">39.5K Plugs</span>
            </b>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top: 4px; font-size: 10px;">
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

        <!-- Traffic Toll Plazas (Jan 2026 Monthly) -->
        <div style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px;">
            <b style="color: #fed7aa; display: flex; align-items: center; justify-content: space-between;">
                <span>🚦 NHAI/IHMCL Toll Traffic (Jan 2026):</span>
                <span style="font-size: 9px; color: #fb923c; font-weight: 600;">Monthly Counts</span>
            </b>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top: 4px; font-size: 10px;">
                <span style="display: flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; width:9px; height:9px; background:#dc2626; border-radius:50%; border:1px solid #fff;"></span>
                    <span>≥ 500K / mo</span>
                </span>
                <span style="display: flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; width:8px; height:8px; background:#ea580c; border-radius:50%; border:1px solid #fff;"></span>
                    <span>250K - 500K</span>
                </span>
                <span style="display: flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; width:7px; height:7px; background:#eab308; border-radius:50%; border:1px solid #fff;"></span>
                    <span>100K - 250K</span>
                </span>
                <span style="display: flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; width:6px; height:6px; background:#14b8a6; border-radius:50%; border:1px solid #fff;"></span>
                    <span>< 100K / mo</span>
                </span>
            </div>
            <div style="font-size: 8.5px; color: #fca5a5; margin-top: 3px; font-style: italic;">
                * Monthly traffic counts (Jan 2026). Not daily counts or AADT.
            </div>
        </div>

        <div style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px; color: #94a3b8; font-size: 8.5px; line-height: 1.3;">
            <i>* Sources: OpenStreetMap (ODbL), BEE, VAHAN (MoRTH), and IHMCL/NHAI FASTag. Mapped lines do not imply grid-connection feasibility.</i>
        </div>
    </div>
"""

def inject_traffic():
    print(f"[*] Reading {HTML_PATH.name}...")
    content = HTML_PATH.read_text(encoding="utf-8")

    # 1. Ensure script tags for all 3 bundles are in <head>
    script_elec = '<script src="Electricity-Data/urja_electricity_bundle.js"></script>'
    script_ev = '<script src="EV-Charger/urja_ev_bundle.js"></script>'
    script_traffic = '<script src="Trafic data/urja_traffic_bundle.js"></script>'

    if script_elec not in content:
        content = content.replace("</head>", f"    {script_elec}\n</head>")
    if script_ev not in content:
        content = content.replace("</head>", f"    {script_ev}\n</head>")
    if script_traffic not in content:
        content = content.replace("</head>", f"    {script_traffic}\n</head>")

    # 2. Update Legend Card
    idx_title = content.find('Urja-X')
    if idx_title != -1:
        legend_start = content.rfind('<div style="', 0, idx_title)
        legend_end = content.find('</body>', legend_start)
        if legend_start != -1 and legend_end != -1:
            print("[*] Updating legend card with Unified Multimodal, Grid, EV & Traffic symbology...")
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

    # Import generators
    from scripts.inject_electricity_to_map import get_electricity_js
    from scripts.inject_ev_to_map import get_ev_js

    elec_js = get_electricity_js(map_var, lc_var)
    ev_js = get_ev_js(map_var, lc_var)
    traffic_js = get_traffic_js(map_var, lc_var)

    combined_js = f"""
{elec_js}

{ev_js}
initUrjaEV({map_var}, {lc_var});

{traffic_js}
initUrjaTraffic({map_var}, {lc_var});
"""

    final_content = folium_base_code + f"\n{combined_js}\n</script>\n</html>\n"
    HTML_PATH.write_text(final_content, encoding="utf-8")
    print(f"[+] Successfully integrated Traffic into {HTML_PATH.name}!")
    return True

if __name__ == "__main__":
    inject_traffic()

