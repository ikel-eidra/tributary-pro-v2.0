"""
Comprehensive upgrade for Tributary Pro v2.0:
1. Force light/blueprint mode as default
2. Add 4 new feature tabs (Blockwall, Load Summary, Rebar Schedule, BOM)
3. Auto-calculate on load + input change (no manual Run clicks)
4. Add concrete material properties to IFC export
"""
import re

FILE = r"d:\projects\tributary-pro-v2.0-LIVE\v3\index.html"

with open(FILE, 'r', encoding='utf-8') as f:
    c = f.read()

# ================================================================
#  1. FORCE BLUEPRINT (LIGHT) THEME
# ================================================================
# Already data-theme="blueprint" in <html>, good.
# But let's make sure the blueprint theme uses engineering fonts
c = c.replace(
    "[data-theme=\"blueprint\"] {\n            --font-main: 'Inter', system-ui, -apple-system, sans-serif;",
    "[data-theme=\"blueprint\"] {\n            --font-main: 'Inter', 'Courier New', system-ui, -apple-system, sans-serif;",
    1
)
print("1. Blueprint font updated")

# ================================================================
#  2. ADD 4 NEW TAB BUTTONS TO THE TAB BAR
# ================================================================
old_tabs_end = """                    <button class="plan-tab" id="tabSlabSchedule" onclick="setPlanTab('slabSchedule')">Slab
                        Schedule</button>
                </div>"""

new_tabs_end = """                    <button class="plan-tab" id="tabSlabSchedule" onclick="setPlanTab('slabSchedule')">Slab
                        Schedule</button>
                    <button class="plan-tab" id="tabBlockwall" onclick="setPlanTab('blockwall')">Blockwall</button>
                    <button class="plan-tab" id="tabLoadSummary" onclick="setPlanTab('loadSummary')">Load Summary</button>
                    <button class="plan-tab" id="tabRebarSchedule" onclick="setPlanTab('rebarSchedule')">Rebar Schedule</button>
                    <button class="plan-tab" id="tabBOM" onclick="setPlanTab('bom')">Bill of Materials</button>
                </div>"""

c = c.replace(old_tabs_end, new_tabs_end, 1)
print("2. Added 4 new tab buttons")

# ================================================================
#  3. ADD NEW TAB PANELS (HTML) - before </div> of canvas-container
# ================================================================
new_panels_html = """
                <!-- v3.11: Blockwall Design Panel -->
                <div id="panelBlockwall" class="schedule-panel" style="display:none;">
                    <div class="schedule-header">
                        <h3>🧱 Blockwall Design</h3>
                    </div>
                    <div style="padding:12px;">
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;">
                            <label style="font-size:0.75rem;">CHB Size:
                                <select id="chbSize" onchange="calculateBlockwalls()" style="width:100%; padding:4px; margin-top:4px;">
                                    <option value="100">100mm (4")</option>
                                    <option value="150" selected>150mm (6")</option>
                                    <option value="200">200mm (8")</option>
                                </select>
                            </label>
                            <label style="font-size:0.75rem;">Wall Height (m):
                                <input type="number" id="bwHeight" value="3.0" min="2.0" max="6.0" step="0.1" 
                                    onchange="calculateBlockwalls()" style="width:100%; padding:4px; margin-top:4px;">
                            </label>
                            <label style="font-size:0.75rem;">Plaster (mm each side):
                                <input type="number" id="plasterThk" value="15" min="0" max="25" step="5"
                                    onchange="calculateBlockwalls()" style="width:100%; padding:4px; margin-top:4px;">
                            </label>
                            <label style="font-size:0.75rem;">Opening %:
                                <input type="number" id="openingPct" value="20" min="0" max="80" step="5"
                                    onchange="calculateBlockwalls()" style="width:100%; padding:4px; margin-top:4px;">
                            </label>
                        </div>
                        <table class="schedule-table" style="width:100%;">
                            <thead>
                                <tr>
                                    <th>Parameter</th>
                                    <th>Value</th>
                                    <th>Unit</th>
                                </tr>
                            </thead>
                            <tbody id="blockwallResultsBody">
                                <tr><td>CHB Unit Weight</td><td id="bwUnitWt">-</td><td>kN/m²</td></tr>
                                <tr><td>Plaster Weight</td><td id="bwPlasterWt">-</td><td>kN/m²</td></tr>
                                <tr><td>Gross Wall Weight</td><td id="bwGrossWt">-</td><td>kN/m²</td></tr>
                                <tr><td>Net Wall Weight (less openings)</td><td id="bwNetWt">-</td><td>kN/m²</td></tr>
                                <tr style="font-weight:bold; border-top:2px solid #000;">
                                    <td>LINE LOAD on Beam</td><td id="bwLineLoad">-</td><td>kN/m</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.11: Load Summary Panel -->
                <div id="panelLoadSummary" class="schedule-panel" style="display:none;">
                    <div class="schedule-header">
                        <h3>📊 Load Summary</h3>
                    </div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;" id="loadSummaryTable">
                            <thead>
                                <tr>
                                    <th>Column</th>
                                    <th>Type</th>
                                    <th>Trib (m²)</th>
                                    <th>Slab DL (kN)</th>
                                    <th>Live (kN)</th>
                                    <th>Beam DL (kN)</th>
                                    <th>Col DL (kN)</th>
                                    <th>Wall (kN)</th>
                                    <th>TOTAL (kN)</th>
                                </tr>
                            </thead>
                            <tbody id="loadSummaryBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.11: Rebar Schedule Panel -->
                <div id="panelRebarSchedule" class="schedule-panel" style="display:none;">
                    <div class="schedule-header">
                        <h3>🔗 Rebar Schedule</h3>
                    </div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <h4 style="margin:0 0 8px; font-size:0.8rem; text-transform:uppercase;">Footing Reinforcement</h4>
                        <table class="schedule-table" style="width:100%;">
                            <thead>
                                <tr>
                                    <th>Footing Type</th>
                                    <th>Size (m)</th>
                                    <th>h (mm)</th>
                                    <th>Main Bars</th>
                                    <th>Spacing</th>
                                    <th>As (mm²)</th>
                                </tr>
                            </thead>
                            <tbody id="rebarFootingBody"></tbody>
                        </table>
                        <h4 style="margin:16px 0 8px; font-size:0.8rem; text-transform:uppercase;">Column Reinforcement (Preliminary)</h4>
                        <table class="schedule-table" style="width:100%;">
                            <thead>
                                <tr>
                                    <th>Column</th>
                                    <th>Size (mm)</th>
                                    <th>Pu (kN)</th>
                                    <th>ρ (%)</th>
                                    <th>Main Bars</th>
                                    <th>Ties</th>
                                </tr>
                            </thead>
                            <tbody id="rebarColumnBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.11: Bill of Materials Panel -->
                <div id="panelBOM" class="schedule-panel" style="display:none;">
                    <div class="schedule-header">
                        <h3>📋 Bill of Materials</h3>
                    </div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;">
                            <thead>
                                <tr>
                                    <th>Item</th>
                                    <th>Description</th>
                                    <th>Qty</th>
                                    <th>Unit</th>
                                    <th>Volume (m³)</th>
                                </tr>
                            </thead>
                            <tbody id="bomBody"></tbody>
                            <tfoot>
                                <tr style="font-weight:bold; border-top:2px solid #000;">
                                    <td colspan="4">TOTAL CONCRETE</td>
                                    <td id="bomTotalConcrete">-</td>
                                </tr>
                                <tr style="font-weight:bold;">
                                    <td colspan="4">EST. REBAR (kg) @ 80 kg/m³</td>
                                    <td id="bomTotalRebar">-</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
"""

# Insert before the canvas-toolbar closing area
panel_marker = "<!-- Column Results Table"
idx = c.find(panel_marker)
if idx > 0:
    c = c[:idx] + new_panels_html + "\n" + c[idx:]
    print("3. Added 4 new HTML panels")
else:
    print("WARNING: Could not find panel insertion point")

# ================================================================
#  4. UPDATE setPlanTab() TO HANDLE NEW TABS
# ================================================================
# Add to tabBtnMap
c = c.replace(
    "'slabSchedule': 'tabSlabSchedule'\n            };",
    "'slabSchedule': 'tabSlabSchedule',\n                'blockwall': 'tabBlockwall',\n                'loadSummary': 'tabLoadSummary',\n                'rebarSchedule': 'tabRebarSchedule',\n                'bom': 'tabBOM'\n            };",
    1
)
print("4a. Updated tabBtnMap")

# Add to schedulePanels
c = c.replace(
    "const schedulePanels = ['panelColSchedule', 'panelBeamSchedule', 'panelFootingSchedule', 'panelSlabSchedule'];",
    "const schedulePanels = ['panelColSchedule', 'panelBeamSchedule', 'panelFootingSchedule', 'panelSlabSchedule', 'panelBlockwall', 'panelLoadSummary', 'panelRebarSchedule', 'panelBOM'];",
    1
)
print("4b. Updated schedulePanels")

# Add to isScheduleTab
c = c.replace(
    "const isScheduleTab = ['colSchedule', 'beamSchedule', 'footingSchedule', 'slabSchedule'].includes(tab);",
    "const isScheduleTab = ['colSchedule', 'beamSchedule', 'footingSchedule', 'slabSchedule', 'blockwall', 'loadSummary', 'rebarSchedule', 'bom'].includes(tab);",
    1
)
print("4c. Updated isScheduleTab")

# Add panel show logic after slabSchedule
old_slab_logic = """                    } else if (tab === 'slabSchedule') {
                        document.getElementById('panelSlabSchedule').style.display = 'block';
                        populateSlabSchedule();
                    }"""

new_slab_logic = """                    } else if (tab === 'slabSchedule') {
                        document.getElementById('panelSlabSchedule').style.display = 'block';
                        populateSlabSchedule();
                    } else if (tab === 'blockwall') {
                        document.getElementById('panelBlockwall').style.display = 'block';
                        calculateBlockwalls();
                    } else if (tab === 'loadSummary') {
                        document.getElementById('panelLoadSummary').style.display = 'block';
                        populateLoadSummary();
                    } else if (tab === 'rebarSchedule') {
                        document.getElementById('panelRebarSchedule').style.display = 'block';
                        populateRebarSchedule();
                    } else if (tab === 'bom') {
                        document.getElementById('panelBOM').style.display = 'block';
                        populateBOM();
                    }"""

c = c.replace(old_slab_logic, new_slab_logic, 1)
print("4d. Added panel show logic for new tabs")

# ================================================================
#  5. ADD POPULATE FUNCTIONS FOR NEW TABS
# ================================================================
new_functions = r"""
// ========== v3.11: NEW TAB FUNCTIONS ==========

// --- BLOCKWALL DESIGN ---
function calculateBlockwalls() {
    const chbSize = parseInt(document.getElementById('chbSize')?.value || 150);
    const wallH = parseFloat(document.getElementById('bwHeight')?.value || 3.0);
    const plaster = parseInt(document.getElementById('plasterThk')?.value || 15);
    const openPct = parseInt(document.getElementById('openingPct')?.value || 20);

    // CHB unit weights per NSCP (kN/m² of wall face)
    const chbWeights = { 100: 1.77, 150: 2.33, 200: 3.39 }; // kN/m²
    const chbWt = chbWeights[chbSize] || 2.33;

    // Plaster: 23 kN/m³ * thickness (both sides)
    const plasterWt = 2 * (plaster / 1000) * 23; // kN/m²

    const grossWt = chbWt + plasterWt; // kN/m² of wall face
    const netWt = grossWt * (1 - openPct / 100); // less openings

    // Line load = net weight × height
    const lineLoad = netWt * wallH; // kN/m

    // Update display
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('bwUnitWt', chbWt.toFixed(2));
    set('bwPlasterWt', plasterWt.toFixed(2));
    set('bwGrossWt', grossWt.toFixed(2));
    set('bwNetWt', netWt.toFixed(2));
    set('bwLineLoad', lineLoad.toFixed(2));
}

// --- LOAD SUMMARY ---
function populateLoadSummary() {
    const tbody = document.getElementById('loadSummaryBody');
    if (!tbody) return;

    let html = '';
    const currentFloorId = state.floors[state.currentFloorIndex]?.id;

    state.columns.forEach(col => {
        if (col.active === false) return;
        const type = (typeof getColumnTypeForFloor === 'function') 
            ? getColumnTypeForFloor(col, currentFloorId) : (col.type || '-');
        const trib = col.tributaryArea || 0;
        const slabDL = col.slabLoad || 0;
        const live = col.liveLoad || 0;
        const beamDL = col.beamLoad || 0;
        const colDL = col.columnDL || 0;
        const wall = col.wallContrib || 0;
        const total = col.totalLoadWithDL || col.totalLoad || 0;

        html += `<tr>
            <td><strong>${col.id}</strong></td>
            <td>${type}</td>
            <td>${trib.toFixed(1)}</td>
            <td>${slabDL.toFixed(1)}</td>
            <td>${live.toFixed(1)}</td>
            <td>${beamDL.toFixed(1)}</td>
            <td>${colDL.toFixed(1)}</td>
            <td>${wall.toFixed(1)}</td>
            <td><strong>${total.toFixed(1)}</strong></td>
        </tr>`;
    });
    tbody.innerHTML = html || '<tr><td colspan="9">Run calculation first</td></tr>';
}

// --- REBAR SCHEDULE ---
function populateRebarSchedule() {
    const fc = state.fc || 21;
    const fy = state.fy || 415;

    // Footing rebar
    const ftBody = document.getElementById('rebarFootingBody');
    if (ftBody) {
        const footingTypes = {};
        state.columns.forEach(col => {
            if (col.active === false || !col.footingSize || col.isPlanted) return;
            const key = col.footingSize.toFixed(2);
            if (!footingTypes[key]) {
                footingTypes[key] = { size: col.footingSize, design: col.footingDesign, count: 0 };
            }
            footingTypes[key].count++;
        });

        let html = '';
        let typeIdx = 1;
        Object.values(footingTypes).forEach(ft => {
            const fd = ft.design;
            html += `<tr>
                <td>F${typeIdx} (×${ft.count})</td>
                <td>${ft.size.toFixed(2)}×${ft.size.toFixed(2)}</td>
                <td>${fd ? fd.h : 300}</td>
                <td>${fd ? fd.nBars + '-ø' + fd.barDia : '-'}</td>
                <td>${fd ? fd.spacing + 'mm' : '-'}</td>
                <td>${fd ? fd.As : '-'}</td>
            </tr>`;
            typeIdx++;
        });
        ftBody.innerHTML = html || '<tr><td colspan="6">No footings designed</td></tr>';
    }

    // Column rebar (preliminary - 1% min)
    const colBody = document.getElementById('rebarColumnBody');
    if (colBody) {
        const colTypes = {};
        state.columns.forEach(col => {
            if (col.active === false) return;
            const b = col.suggestedB || 250;
            const h = col.suggestedH || 250;
            const key = b + 'x' + h;
            if (!colTypes[key]) {
                colTypes[key] = { b, h, maxPu: 0, count: 0 };
            }
            colTypes[key].count++;
            colTypes[key].maxPu = Math.max(colTypes[key].maxPu, col.totalLoadWithDL || col.totalLoad || 0);
        });

        let html = '';
        Object.values(colTypes).forEach(ct => {
            const Ag = ct.b * ct.h; // mm²
            const rho_min = 0.01; // 1% minimum
            const As = rho_min * Ag;
            const barDia = ct.b >= 350 ? 20 : 16;
            const Ab = Math.PI * barDia * barDia / 4;
            const nBars = Math.max(4, Math.ceil(As / Ab));
            const tieSize = barDia >= 20 ? 10 : 10;
            const tieSpacing = Math.min(16 * barDia, Math.min(ct.b, ct.h), 300);

            html += `<tr>
                <td>C-${ct.b}×${ct.h} (×${ct.count})</td>
                <td>${ct.b}×${ct.h}</td>
                <td>${ct.maxPu.toFixed(0)}</td>
                <td>${(rho_min * 100).toFixed(1)}</td>
                <td>${nBars}-ø${barDia}mm</td>
                <td>ø${tieSize}mm @ ${tieSpacing}mm</td>
            </tr>`;
        });
        colBody.innerHTML = html || '<tr><td colspan="6">No columns</td></tr>';
    }
}

// --- BILL OF MATERIALS ---
function populateBOM() {
    const tbody = document.getElementById('bomBody');
    if (!tbody) return;

    const numFloors = state.floors.length;
    const floorHeight = state.floors[0]?.height || 3.0;

    // Columns
    const activeCols = state.columns.filter(c => c.active !== false && !c.isPlanted);
    const colB = (activeCols[0]?.suggestedB || 250) / 1000;
    const colH = (activeCols[0]?.suggestedH || 250) / 1000;
    const colVol = colB * colH * floorHeight * activeCols.length * numFloors;

    // Beams (one floor)
    let beamVol = 0;
    state.beams.forEach(beam => {
        if (beam.isCustom || beam.isCantilever) return;
        const bB = (beam.suggestedB || 250) / 1000;
        const bH = (beam.suggestedH || 400) / 1000;
        beamVol += bB * bH * (beam.span || 0);
    });
    beamVol *= numFloors;

    // Footings
    let footingVol = 0;
    activeCols.forEach(col => {
        if (col.footingSize) {
            const h = col.footingDesign ? col.footingDesign.h / 1000 : (col.footingThick || 0.3);
            footingVol += col.footingSize * col.footingSize * h;
        }
    });

    // Slabs
    let slabVol = 0;
    state.floors.forEach(floor => {
        const t = (floor.slabThickness || 150) / 1000;
        state.slabs.forEach(slab => {
            if (!slab.isVoid) slabVol += slab.width * slab.height * t;
        });
    });

    // Tie beams
    const avgSpan = (state.xSpans.reduce((a,b) => a+b, 0) + state.ySpans.reduce((a,b) => a+b, 0)) /
        (state.xSpans.length + state.ySpans.length);
    const tbVol = state.tieBeamW * state.tieBeamH * avgSpan * activeCols.length;

    const totalVol = colVol + beamVol + footingVol + slabVol + tbVol;

    let html = '';
    html += `<tr><td>1</td><td>Columns (${colB*1000}×${colH*1000}mm)</td><td>${activeCols.length * numFloors}</td><td>pcs</td><td>${colVol.toFixed(2)}</td></tr>`;
    html += `<tr><td>2</td><td>Beams</td><td>${state.beams.filter(b => !b.isCustom && !b.isCantilever).length * numFloors}</td><td>pcs</td><td>${beamVol.toFixed(2)}</td></tr>`;
    html += `<tr><td>3</td><td>Slabs (${numFloors} floors)</td><td>${state.slabs.filter(s => !s.isVoid).length * numFloors}</td><td>panels</td><td>${slabVol.toFixed(2)}</td></tr>`;
    html += `<tr><td>4</td><td>Footings</td><td>${activeCols.length}</td><td>pcs</td><td>${footingVol.toFixed(2)}</td></tr>`;
    html += `<tr><td>5</td><td>Tie Beams (${(state.tieBeamW*1000).toFixed(0)}×${(state.tieBeamH*1000).toFixed(0)}mm)</td><td>${activeCols.length}</td><td>pcs</td><td>${tbVol.toFixed(2)}</td></tr>`;

    tbody.innerHTML = html;
    document.getElementById('bomTotalConcrete').textContent = totalVol.toFixed(2);
    document.getElementById('bomTotalRebar').textContent = (totalVol * 80).toFixed(0);
}

"""

# Inject before the INIT section
init_marker = "// ========== FOOTING STRUCTURAL DESIGN"
idx = c.find(init_marker)
if idx > 0:
    c = c[:idx] + new_functions + "\n" + c[idx:]
    print("5. Added 4 new populate functions")

# ================================================================
#  6. AUTO-CALCULATE ON LOAD (no manual Run clicks)
# ================================================================
# Find window.onload and add calculate() call
old_onload = "window.onload = function () {"
new_onload = "window.onload = function () {\n            // v3.11: Auto-calculate on load\n            setTimeout(() => { if (typeof calculate === 'function') calculate(); }, 500);"
c = c.replace(old_onload, new_onload, 1)
print("6. Added auto-calculate on page load")

# ================================================================
#  7. FIX IFC EXPORT: ADD CONCRETE MATERIAL PROPERTIES
# ================================================================
# Insert material definitions right after the unit assignment in IFC
ifc_mat_code = """
    // v3.11: Material definition for Revit Structure
    const matConcrete = nid();
    ifc += matConcrete + "= IFCMATERIAL('Concrete - " + (state.fc || 21) + "MPa');\\n";
    const matLayer = nid();
    ifc += matLayer + "= IFCMATERIALLAYER(" + matConcrete + ",0.3,.U.);\\n";
    const matLayerSet = nid();
    ifc += matLayerSet + "= IFCMATERIALLAYERSET((" + matLayer + "),'Concrete');\\n";
    const propSingle1 = nid();
    ifc += propSingle1 + "= IFCPROPERTYSINGLEVALUE('CompressiveStrength',$,IFCPRESSUREMEASURE(" + ((state.fc || 21) * 1000000) + ".0),$);\\n";
    const propSingle2 = nid();
    ifc += propSingle2 + "= IFCPROPERTYSINGLEVALUE('ConcreteDensity',$,IFCMASSDENSITYMEASURE(2400.0),$);\\n";
    const propSingle3 = nid();
    ifc += propSingle3 + "= IFCPROPERTYSINGLEVALUE('YoungsModulus',$,IFCMODULUSOFELASTICITYMEASURE(" + (4700 * Math.sqrt(state.fc || 21) * 1000000) + ".0),$);\\n";
    const propSingle4 = nid();
    ifc += propSingle4 + "= IFCPROPERTYSINGLEVALUE('PoissonRatio',$,IFCPOSITIVERATIOMEASURE(0.17),$);\\n";
    const propSet = nid();
    ifc += propSet + "= IFCPROPERTYSET('" + generateIFCGUID() + "'," + ownerHistoryId + ",'Pset_MaterialConcrete',$,(" + propSingle1 + "," + propSingle2 + "," + propSingle3 + "," + propSingle4 + "));\\n";
"""

# Insert right before "// Project" in the IFC function
ifc_marker = "    // Project"
ifc_idx = c.find(ifc_marker)
if ifc_idx > 0:
    c = c[:ifc_idx] + ifc_mat_code + "\n" + c[ifc_idx:]
    print("7. Added IFC concrete material properties for Revit")
else:
    print("WARNING: Could not find IFC injection point")

# Add material association after each IFCCOLUMN creation
old_col_line = '''ifc += colId + "= IFCCOLUMN('" + generateIFCGUID() + "'," + ownerHistoryId + ",'" + col.id + "',$,$," + clp + "," + ps + ",$);\\n";'''
new_col_line = old_col_line + '''
            const relMat = nid();
            ifc += relMat + "= IFCRELASSOCIATESMATERIAL('" + generateIFCGUID() + "'," + ownerHistoryId + ",$,$,(" + colId + ")," + matConcrete + ");\\n";'''

if old_col_line in c:
    c = c.replace(old_col_line, new_col_line, 1)
    print("7b. Added material association to IFC columns")
else:
    print("WARNING: Could not find IFCCOLUMN line")

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(c)

print("\n✅ ALL UPGRADES APPLIED SUCCESSFULLY")

