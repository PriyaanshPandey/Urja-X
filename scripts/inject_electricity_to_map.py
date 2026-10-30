"""
Urja-X Electricity Map Integrator
Injects electricity infrastructure layers, voltage styling, popups, and layer switcher
controls into india_multimodal_heatmap.html while preserving all existing layers.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_PATH = BASE_DIR / "india_multimodal_heatmap.html"
BUNDLE_PATH = BASE_DIR / "Electricity-Data" / "urja_electricity_bundle.js"

def get_electricity_js(map_var, lc_var):
    return f"""
// ============================================================================
// ⚡ URJA-X ELECTRICITY INFRASTRUCTURE INTEGRATION
// ============================================================================
function initUrjaElectricity(map, layerControl) {{
    if (typeof URJA_ELECTRICITY_DATA === 'undefined') {{
        console.warn("[Urja-X] Electricity data bundle not detected.");
        return;
    }}
    if (!map || !layerControl) {{
        console.error("[Urja-X] Leaflet map or layerControl instance not provided.");
        return;
    }}

    console.log("[Urja-X] Initializing Electricity Infrastructure layers...");

    // 1. TRANSMISSION LINES (HTML5 Canvas Renderer for 60fps performance)
    var linesRenderer = L.canvas({{ tolerance: 5 }});
    var transmissionLinesLayer = L.geoJSON(URJA_ELECTRICITY_DATA.transmission_lines, {{
        renderer: linesRenderer,
        style: function(feat) {{
            var p = feat.properties || {{}};
            var isUHV = p.v && p.v >= 765000;
            var isEHV = p.v && p.v >= 350000;
            return {{
                color: p.c || '#94a3b8',
                weight: p.w || 2,
                opacity: isUHV ? 0.95 : (isEHV ? 0.90 : 0.80),
                dashArray: p.d || null
            }};
        }},
        onEachFeature: function(feat, layer) {{
            var p = feat.properties || {{}};
            var vDisplay = p.v ? ((p.v / 1000).toLocaleString() + ' kV (' + p.v.toLocaleString() + ' V)') : 'Unspecified (Heuristic Grid Corridor)';
            var opDisplay = p.o ? p.o : 'Not specified in OSM';
            var nameDisplay = p.n ? ('⚡ ' + p.n) : '⚡ Power Transmission Corridor';
            var circInfo = p.circ ? ('<div><b>Circuits:</b> ' + p.circ + ' | <b>Cables:</b> ' + (p.cabl || 'N/A') + '</div>') : '';
            
            var popupHtml = `
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; min-width: 260px; padding: 4px; color: #0f172a;">
                    <div style="background: #1e293b; color: #f8fafc; padding: 8px 12px; border-radius: 6px 6px 0 0; margin: -4px -4px 8px -4px;">
                        <div style="font-weight: bold; font-size: 13px;">${{nameDisplay}}</div>
                        <span style="display: inline-block; margin-top: 4px; background: ${{p.c}}; color: #fff; font-size: 10px; font-weight: bold; padding: 2px 7px; border-radius: 4px;">
                            ${{p.t}}
                        </span>
                    </div>
                    <div style="font-size: 11px; line-height: 1.6; color: #334155;">
                        <div><b>Operating Voltage:</b> <span style="color: #0284c7; font-weight: bold;">${{vDisplay}}</span></div>
                        <div><b>Grid Operator:</b> ${{opDisplay}}</div>
                        ${{circInfo}}
                        <div style="margin-top: 8px; padding-top: 6px; border-top: 1px dashed #cbd5e1; font-size: 10px; color: #64748b; font-style: italic;">
                            ℹ️ Mapped OSM grid infrastructure. Proximity does not infer available electrical capacity or verified grid connection feasibility.
                        </div>
                    </div>
                </div>
            `;
            layer.bindPopup(popupHtml, {{ maxWidth: 300 }});
            layer.bindTooltip('⚡ ' + p.t + (p.o ? ' (' + p.o + ')' : ''), {{ sticky: true }});
        }}
    }});

    // 2. SUBSTATIONS (Distinctive High-Visibility Markers)
    var substationsLayer = L.featureGroup();
    URJA_ELECTRICITY_DATA.substations.forEach(function(sub) {{
        var marker = L.circleMarker([sub.lat, sub.lon], {{
            radius: 8,
            fillColor: '#8b5cf6',
            color: '#ffffff',
            weight: 2.5,
            opacity: 1.0,
            fillOpacity: 0.95
        }});
        
        var nameDisplay = sub.name || 'Substation (OSM Node)';
        var voltDisplay = sub.voltage || 'Not recorded in OSM';
        var operDisplay = sub.operator || 'Not recorded in OSM';
        var subType = (sub.substation || 'Grid').toUpperCase();
        
        var popupHtml = `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; min-width: 250px; padding: 4px; color: #0f172a;">
                <div style="background: #5b21b6; color: #f8fafc; padding: 8px 12px; border-radius: 6px 6px 0 0; margin: -4px -4px 8px -4px;">
                    <div style="font-weight: bold; font-size: 13px;">🏢 ${{nameDisplay}}</div>
                    <span style="font-size: 10px; color: #ddd6fe; text-transform: uppercase; font-weight: 600;">${{subType}} SUBSTATION</span>
                </div>
                <div style="font-size: 11px; line-height: 1.6; color: #334155; padding-top: 4px;">
                    <div><b>Operating Voltage:</b> <span style="color: #7c3aed; font-weight: bold;">${{voltDisplay}}</span></div>
                    <div><b>Grid Operator / Utility:</b> ${{operDisplay}}</div>
                    <div><b>Coordinates:</b> ${{sub.lat.toFixed(5)}}, ${{sub.lon.toFixed(5)}}</div>
                    <div style="margin-top: 8px; padding-top: 6px; border-top: 1px dashed #cbd5e1; font-size: 10px; color: #64748b; font-style: italic;">
                        ℹ️ Verified OSM node location. Interconnection feasibility requires utility load-flow and transformer headroom studies.
                    </div>
                </div>
            </div>
        `;
        marker.bindPopup(popupHtml, {{ maxWidth: 290 }});
        marker.bindTooltip('🏢 ' + nameDisplay + ' (' + voltDisplay + ')', {{ sticky: true }});
        marker.addTo(substationsLayer);
    }});

    // 3. TRANSFORMERS (Clustered)
    var transformersCluster = L.markerClusterGroup({{
        maxClusterRadius: 45,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        iconCreateFunction: function(cluster) {{
            return L.divIcon({{
                html: '<div style="background:rgba(217, 119, 6, 0.92);color:white;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:11px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4);">' + cluster.getChildCount() + '</div>',
                className: 'urja-tr-cluster',
                iconSize: L.point(32, 32)
            }});
        }}
    }});
    URJA_ELECTRICITY_DATA.transformers.forEach(function(tr) {{
        var m = L.circleMarker([tr[0], tr[1]], {{
            radius: 4.5,
            fillColor: '#d97706',
            color: '#ffffff',
            weight: 1.5,
            opacity: 0.9,
            fillOpacity: 0.85
        }});
        m.bindTooltip('🔌 ' + tr[2] + (tr[3] ? ' (' + tr[3] + ')' : ''), {{ sticky: true }});
        m.bindPopup(`
            <div style="font-family:sans-serif; font-size:11px; padding:2px;">
                <b>🔌 ${{tr[2]}}</b><br>
                <b>Voltage:</b> ${{tr[3] || 'Not recorded'}}<br>
                <b>Operator:</b> ${{tr[4] || 'Not recorded'}}<br>
                <b>Coordinates:</b> ${{tr[0]}}, ${{tr[1]}}
            </div>
        `);
        transformersCluster.addLayer(m);
    }});

    // 4. POWER GENERATORS & PLANTS (Clustered)
    var generatorsCluster = L.markerClusterGroup({{
        maxClusterRadius: 45,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        iconCreateFunction: function(cluster) {{
            return L.divIcon({{
                html: '<div style="background:rgba(16, 185, 129, 0.92);color:white;border-radius:50%;width:34px;height:34px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:11px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4);">' + cluster.getChildCount() + '</div>',
                className: 'urja-gen-cluster',
                iconSize: L.point(34, 34)
            }});
        }}
    }});
    URJA_ELECTRICITY_DATA.generators.forEach(function(gen) {{
        var isPlant = gen[3] === 'plant';
        var m = L.circleMarker([gen[0], gen[1]], {{
            radius: isPlant ? 6.5 : 4,
            fillColor: isPlant ? '#047857' : '#10b981',
            color: '#ffffff',
            weight: isPlant ? 2 : 1.2,
            opacity: 0.95,
            fillOpacity: 0.85
        }});
        m.bindTooltip('🏭 ' + gen[2] + (isPlant ? ' [Power Plant]' : ' [Generator]'), {{ sticky: true }});
        m.bindPopup(`
            <div style="font-family:sans-serif; font-size:11px; padding:2px;">
                <b>🏭 ${{gen[2]}}</b><br>
                <b>Facility:</b> ${{isPlant ? 'Power Generation Plant' : 'Power Generator'}}<br>
                <b>Operator:</b> ${{gen[3] || 'Not recorded'}}<br>
                <b>Coordinates:</b> ${{gen[0]}}, ${{gen[1]}}
            </div>
        `);
        generatorsCluster.addLayer(m);
    }});

    // 5. UTILITY POLES (Clustered)
    var polesCluster = L.markerClusterGroup({{
        maxClusterRadius: 40,
        showCoverageOnHover: false,
        iconCreateFunction: function(cluster) {{
            return L.divIcon({{
                html: '<div style="background:rgba(2, 132, 199, 0.90);color:white;border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:10px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4);">' + cluster.getChildCount() + '</div>',
                className: 'urja-pole-cluster',
                iconSize: L.point(30, 30)
            }});
        }}
    }});
    URJA_ELECTRICITY_DATA.poles.forEach(function(pol) {{
        var m = L.circleMarker([pol[0], pol[1]], {{
            radius: 3,
            fillColor: '#0284c7',
            color: '#ffffff',
            weight: 1,
            opacity: 0.85,
            fillOpacity: 0.8
        }});
        m.bindTooltip('📍 ' + pol[3] + (pol[2] ? ' (' + pol[2] + ')' : ''), {{ sticky: true }});
        polesCluster.addLayer(m);
    }});

    // 6. TRANSMISSION TOWERS (Tiled Regional Loading Strategy for 1.6M nodes)
    var towersLayerGroup = L.layerGroup();
    var towersCanvasRenderer = L.canvas({{ tolerance: 3 }});
    var towersActiveDetailLayer = L.layerGroup();
    var towersActiveSummaryLayer = L.layerGroup();
    towersLayerGroup.addLayer(towersActiveSummaryLayer);
    towersLayerGroup.addLayer(towersActiveDetailLayer);

    function updateTowersView() {{
        if (!map.hasLayer(towersLayerGroup)) return;
        var zoom = map.getZoom();
        if (zoom < 10) {{
            towersActiveDetailLayer.clearLayers();
            if (towersActiveSummaryLayer.getLayers().length === 0) {{
                URJA_ELECTRICITY_DATA.towers_summary.forEach(function(ts) {{
                    var rad = Math.min(24, Math.max(9, Math.round(Math.log10(ts.count + 1) * 4.6)));
                    var m = L.circleMarker([ts.lat, ts.lon], {{
                        radius: rad,
                        fillColor: '#475569',
                        color: '#f8fafc',
                        weight: 1.5,
                        fillOpacity: 0.75
                    }});
                    m.bindTooltip(`🗼 Regional Tower Cluster: <b>${{ts.count.toLocaleString()}}</b> towers<br><span style="font-size:10px;color:#94a3b8;">Zoom in (level 10+) to view individual towers</span>`, {{ sticky: true }});
                    towersActiveSummaryLayer.addLayer(m);
                }});
            }}
        }} else {{
            towersActiveSummaryLayer.clearLayers();
            towersActiveDetailLayer.clearLayers();
            var bounds = map.getBounds();
            var minLat = Math.floor(bounds.getSouth());
            var maxLat = Math.floor(bounds.getNorth());
            var minLon = Math.floor(bounds.getWest());
            var maxLon = Math.floor(bounds.getEast());
            
            for (var latIdx = minLat; latIdx <= maxLat; latIdx++) {{
                for (var lonIdx = minLon; lonIdx <= maxLon; lonIdx++) {{
                    var cellKey = latIdx + '_' + lonIdx;
                    var cellTowers = URJA_ELECTRICITY_DATA.towers_by_cell[cellKey];
                    if (cellTowers) {{
                        for (var i = 0; i < cellTowers.length; i++) {{
                            var tLat = cellTowers[i][0];
                            var tLon = cellTowers[i][1];
                            if (bounds.contains([tLat, tLon])) {{
                                var tm = L.circleMarker([tLat, tLon], {{
                                    renderer: towersCanvasRenderer,
                                    radius: 3,
                                    fillColor: '#94a3b8',
                                    color: '#334155',
                                    weight: 1,
                                    fillOpacity: 0.8
                                }});
                                tm.bindTooltip('🗼 Transmission Tower', {{ sticky: true }});
                                towersActiveDetailLayer.addLayer(tm);
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    map.on('moveend', updateTowersView);
    map.on('layeradd', function(e) {{
        if (e.layer === towersLayerGroup) updateTowersView();
    }});

    // 7. ADD TO MAP (Default Core Layers ON)
    transmissionLinesLayer.addTo(map);
    substationsLayer.addTo(map);

    // 8. REGISTER OVERLAYS IN LAYER CONTROL
    layerControl.addOverlay(transmissionLinesLayer, "⚡ [Grid] Transmission Lines (EHV/HV)");
    layerControl.addOverlay(substationsLayer, "🏢 [Grid] Substations (OSM Nodes)");
    layerControl.addOverlay(transformersCluster, "🔌 [Grid] Transformers (5.7K Clustered)");
    layerControl.addOverlay(generatorsCluster, "🏭 [Grid] Power Plants & Generators (37.7K)");
    layerControl.addOverlay(towersLayerGroup, "🗼 [Grid] Transmission Towers (1.6M Tiled)");
    layerControl.addOverlay(polesCluster, "📍 [Grid] Utility Poles (15K Clustered)");

    // 9. FORMAT LAYER SWITCHER WITH ELECTRICITY SECTION
    function formatControl() {{
        var container = document.querySelector('.leaflet-control-layers-overlays');
        if (!container) return;
        var labels = container.querySelectorAll('label');
        var firstGridLabel = null;
        labels.forEach(function(lbl) {{
            var txt = lbl.textContent || '';
            if (txt.includes('[Grid]')) {{
                if (!firstGridLabel) firstGridLabel = lbl;
                lbl.style.display = 'block';
                lbl.style.paddingLeft = '4px';
            }}
        }});

        if (firstGridLabel && !document.getElementById('urja-elec-divider')) {{
            var div = document.createElement('div');
            div.id = 'urja-elec-divider';
            div.style.cssText = 'margin: 10px 0 6px 0; border-top: 1px solid rgba(56, 189, 248, 0.4); padding-top: 8px;';
            div.innerHTML = '<div style="font-weight: 700; color: #0284c7; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">⚡ Electricity Infrastructure</div>';
            firstGridLabel.parentNode.insertBefore(div, firstGridLabel);
        }}
    }}
    setTimeout(formatControl, 200);
    setTimeout(formatControl, 800);

    console.log("[Urja-X] Electricity Infrastructure layers initialized successfully.");
}}
initUrjaElectricity({map_var}, {lc_var});
"""

UPDATED_LEGEND_CARD = """
    <div style="
        position: fixed;
        bottom: 25px;
        left: 25px;
        z-index: 9999;
        background: rgba(15, 23, 42, 0.92);
        backdrop-filter: blur(10px);
        color: #f8fafc;
        padding: 16px 20px;
        border-radius: 12px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 10px 30px rgba(0,0,0,0.45);
        border: 1px solid rgba(255,255,255,0.15);
        max-width: 340px;
        font-size: 11px;
    ">
        <h4 style="margin: 0 0 10px 0; font-size: 13.5px; color: #38bdf8; display: flex; align-items: center; gap: 6px;">
            ⚡ Urja-X Multimodal & Electricity Dashboard
        </h4>

        <!-- Population Density -->
        <div style="margin-bottom: 7px;">
            <b style="color: #cbd5e1;">👥 Population Density (WorldPop):</b><br>
            <div style="height: 8px; background: linear-gradient(to right, #10b981, #facc15, #f97316, #dc2626); border-radius: 4px; margin: 3px 0;"></div>
            <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 9.5px;">
                <span>Rural</span>
                <span>Industrial</span>
                <span>Mega-City Core</span>
            </div>
        </div>

        <!-- Night-time Lights -->
        <div style="margin-bottom: 7px;">
            <b style="color: #cbd5e1;">🌃 Night-time Lights (VIIRS NTL):</b><br>
            <div style="height: 8px; background: linear-gradient(to right, #312e81, #8b5cf6, #ec4899, #f59e0b, #ffffff); border-radius: 4px; margin: 3px 0;"></div>
            <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 9.5px;">
                <span>Unlit</span>
                <span>Suburban</span>
                <span>Economic Hub</span>
            </div>
        </div>

        <!-- Electricity Infrastructure -->
        <div style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.15); padding-top: 8px;">
            <b style="color: #38bdf8;">⚡ Transmission Lines (CEA Voltage Tiers):</b>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top: 5px; font-size: 10px;">
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:14px; height:4px; background:#e11d48; border-radius:2px;"></span>
                    <span>≥ 765 kV UHV</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:14px; height:3.5px; background:#ea580c; border-radius:2px;"></span>
                    <span>400 kV EHV</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:14px; height:2.5px; background:#f59e0b; border-radius:2px;"></span>
                    <span>220 kV HV</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:14px; height:2px; background:#06b6d4; border-radius:2px;"></span>
                    <span>110–132 kV Sub</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:14px; height:1.5px; background:#3b82f6; border-radius:2px;"></span>
                    <span>33–66 kV Dist</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <span style="display:inline-block; width:14px; height:1.5px; background:#94a3b8; border-top: 1px dashed #94a3b8;"></span>
                    <span>Unspecified *</span>
                </div>
            </div>

            <div style="margin-top: 6px; display: flex; flex-wrap: wrap; gap: 8px; font-size: 10px; color: #e2e8f0;">
                <span><span style="display:inline-block; width:8px; height:8px; background:#8b5cf6; border-radius:50%; border:1px solid #fff;"></span> Substations</span>
                <span><span style="display:inline-block; width:8px; height:8px; background:#d97706; border-radius:50%;"></span> Transformers</span>
                <span><span style="display:inline-block; width:8px; height:8px; background:#10b981; border-radius:50%;"></span> Generators</span>
            </div>
        </div>

        <div style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px; color: #94a3b8; font-size: 9.5px; line-height: 1.3;">
            <i>* Data: OpenStreetMap (ODbL). Proximity does not verify available electrical capacity or grid connection feasibility.</i>
        </div>
    </div>
"""

def inject():
    print(f"[*] Reading {HTML_PATH.name}...")
    content = HTML_PATH.read_text(encoding="utf-8")
    
    # 1. Add script tag to <head> if not present
    script_tag = '<script src="Electricity-Data/urja_electricity_bundle.js"></script>'
    if script_tag not in content:
        print("[*] Adding script tag for urja_electricity_bundle.js...")
        content = content.replace("</head>", f"    {script_tag}\n</head>")
        
    # 2. Update Legend Card using exact string boundary
    idx_title = content.find('Urja-X Multimodal')
    if idx_title != -1:
        legend_start = content.rfind('<div style="', 0, idx_title)
        legend_end = content.find('</body>', legend_start)
        if legend_start != -1 and legend_end != -1:
            print("[*] Updating legend card with Electricity Infrastructure symbology...")
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
    
    # Find the end of Folium's layer_control addTo statement:
    # e.g. let layer_control_... = L.control.layers(...).addTo(map_...);
    lc_addTo_idx = content.rfind(f'.addTo({map_var});')
    if lc_addTo_idx == -1:
        lc_addTo_idx = content.rfind(f'.addTo({map_var})')
    if lc_addTo_idx == -1:
        print("[!] Could not find layer control addTo statement in script.")
        return False
        
    semi_idx = content.find(';', lc_addTo_idx)
    if semi_idx == -1:
        semi_idx = lc_addTo_idx + len(f'.addTo({map_var})')
        
    # Cut everything after Folium's layer control statement up to </script>
    folium_base_code = content[:semi_idx + 1]
    
    # Generate clean electricity JavaScript
    js_code = get_electricity_js(map_var, lc_var)
    
    final_content = folium_base_code + f"\n{js_code}\n</script>\n</html>\n"
    HTML_PATH.write_text(final_content, encoding="utf-8")
    print(f"[+] Successfully integrated electricity infrastructure into {HTML_PATH.name}!")
    return True

if __name__ == "__main__":
    inject()
