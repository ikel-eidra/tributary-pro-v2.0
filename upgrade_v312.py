"""
v3.12: Add ALL engineering features as tabs + UI cleanup
Features: Seismic, Wind, Beam Design, Column Check, Slab Design, Staircase, Water Tank
UI: Clean toolbar, remove clutter
"""

FILE = r"d:\projects\tributary-pro-v2.0-LIVE\v3\index.html"

with open(FILE, 'r', encoding='utf-8') as f:
    c = f.read()

# ================================================================
#  1. ADD 7 NEW TAB BUTTONS
# ================================================================
old_bom_tab = '<button class="plan-tab" id="tabBOM" onclick="setPlanTab(\'bom\')">Bill of Materials</button>'
new_tabs = old_bom_tab + """
                    <button class="plan-tab" id="tabSeismic" onclick="setPlanTab('seismic')">Seismic</button>
                    <button class="plan-tab" id="tabWind" onclick="setPlanTab('wind')">Wind</button>
                    <button class="plan-tab" id="tabBeamDesign" onclick="setPlanTab('beamDesign')">Beam Design</button>
                    <button class="plan-tab" id="tabColDesign" onclick="setPlanTab('colDesign')">Column Check</button>
                    <button class="plan-tab" id="tabSlabDesign" onclick="setPlanTab('slabDesign')">Slab Design</button>
                    <button class="plan-tab" id="tabStaircase" onclick="setPlanTab('staircase')">Staircase</button>
                    <button class="plan-tab" id="tabWaterTank" onclick="setPlanTab('waterTank')">Water Tank</button>"""

c = c.replace(old_bom_tab, new_tabs, 1)
print("1. Added 7 new tab buttons")

# ================================================================
#  2. CLEAN UP TOOLBAR - Remove clutter, keep essentials
# ================================================================
# Remove layer toggle buttons (they clutter the toolbar)
old_layers = """                <!-- 2. Layer Toggles -->
                <div class="layer-toggles">
                    <button class="layer-btn active" id="layerGrid" onclick="toggleLayer('grid')">GRID</button>
                    <button class="layer-btn active" id="layerAreas" onclick="toggleLayer('areas')">Areas</button>
                    <button class="layer-btn active" id="layerBeams" onclick="toggleLayer('beams')">Beams</button>
                    <button class="layer-btn active" id="layerCols" onclick="toggleLayer('cols')">Cols</button>
                </div>"""

c = c.replace(old_layers, "<!-- Layer toggles moved to settings -->", 1)
print("2a. Removed layer toggle clutter from toolbar")

# Simplify modeling buttons - remove Stair Beam and Col Align (niche)
old_modeling = """                <!-- 3. Action Buttons (Modeling Tools) -->
                <button class="tool-btn" id="addBeamBtn" onclick="toggleBeamMode()"
                    title="Click to add framing beam, then click-drag on canvas">Add Beam</button>
                <button class="tool-btn" id="addCustomBeamBtn" onclick="showCustomBeamDialog()"
                    title="Add framing beam via dialog (gridline-based)">Stair Beam</button>
                <button class="tool-btn" id="addPlantedColBtn" onclick="togglePlantedColumnMode(event)"
                    title="Click to select beam for planted column. Shift+Click for grid/custom placement.">
                    Planted Col</button>
                <button class="tool-btn" id="colAlignBtn" onclick="toggleColumnAlignment()"
                    title="Toggle edge column alignment (Centered / Flush to Grid)">Col: Center</button>"""

new_modeling = """                <!-- 3. Quick Modeling -->
                <button class="tool-btn" id="addBeamBtn" onclick="toggleBeamMode()" title="Add framing beam">+ Beam</button>
                <button class="tool-btn" id="addPlantedColBtn" onclick="togglePlantedColumnMode(event)" title="Add planted column">+ Column</button>"""

c = c.replace(old_modeling, new_modeling, 1)
print("2b. Simplified modeling buttons")

# ================================================================
#  3. ADD 7 NEW PANEL HTML BLOCKS
# ================================================================
new_panels = """
                <!-- v3.12: Seismic Analysis Panel -->
                <div id="panelSeismic" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Seismic Analysis (NSCP 2015)</h3></div>
                    <div style="padding:12px;">
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;">
                            <label style="font-size:0.75rem;">Seismic Zone:
                                <select id="seismicZone" onchange="calculateSeismic()" style="width:100%; padding:4px; margin-top:4px;">
                                    <option value="4">Zone 4 (0.40g)</option>
                                    <option value="2">Zone 2 (0.20g)</option>
                                </select>
                            </label>
                            <label style="font-size:0.75rem;">Soil Profile:
                                <select id="soilProfile" onchange="calculateSeismic()" style="width:100%; padding:4px; margin-top:4px;">
                                    <option value="SD">SD - Stiff Soil</option>
                                    <option value="SC">SC - Very Dense Soil</option>
                                    <option value="SE">SE - Soft Soil</option>
                                </select>
                            </label>
                            <label style="font-size:0.75rem;">Importance Factor (I):
                                <select id="importFactor" onchange="calculateSeismic()" style="width:100%; padding:4px; margin-top:4px;">
                                    <option value="1.0" selected>1.00 - Standard</option>
                                    <option value="1.25">1.25 - Essential</option>
                                    <option value="1.50">1.50 - Hazardous</option>
                                </select>
                            </label>
                            <label style="font-size:0.75rem;">R (Response Modification):
                                <select id="rFactor" onchange="calculateSeismic()" style="width:100%; padding:4px; margin-top:4px;">
                                    <option value="8.5" selected>8.5 - SMRF</option>
                                    <option value="5.5">5.5 - IMRF</option>
                                    <option value="3.5">3.5 - OMRF</option>
                                </select>
                            </label>
                        </div>
                        <table class="schedule-table" style="width:100%;" id="seismicTable">
                            <tbody id="seismicBody"></tbody>
                        </table>
                        <h4 style="margin:12px 0 4px; font-size:0.75rem; text-transform:uppercase;">Story Forces</h4>
                        <table class="schedule-table" style="width:100%;">
                            <thead><tr><th>Story</th><th>hi (m)</th><th>Wi (kN)</th><th>Wi*hi</th><th>Fi (kN)</th></tr></thead>
                            <tbody id="storyForceBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.12: Wind Analysis Panel -->
                <div id="panelWind" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Wind Load Analysis (NSCP 2015)</h3></div>
                    <div style="padding:12px;">
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;">
                            <label style="font-size:0.75rem;">Basic Wind Speed V (m/s):
                                <input type="number" id="windSpeed" value="200" min="150" max="350" step="10" onchange="calculateWind()" style="width:100%; padding:4px; margin-top:4px;">
                            </label>
                            <label style="font-size:0.75rem;">Exposure Category:
                                <select id="windExposure" onchange="calculateWind()" style="width:100%; padding:4px; margin-top:4px;">
                                    <option value="B">B - Urban/Suburban</option>
                                    <option value="C" selected>C - Open Terrain</option>
                                    <option value="D">D - Flat/Unobstructed</option>
                                </select>
                            </label>
                        </div>
                        <table class="schedule-table" style="width:100%;">
                            <tbody id="windBody"></tbody>
                        </table>
                        <h4 style="margin:12px 0 4px; font-size:0.75rem; text-transform:uppercase;">Wind Pressure per Story</h4>
                        <table class="schedule-table" style="width:100%;">
                            <thead><tr><th>Story</th><th>h (m)</th><th>Kz</th><th>qz (kPa)</th><th>Force (kN)</th></tr></thead>
                            <tbody id="windStoryBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.12: Beam Design Panel -->
                <div id="panelBeamDesign" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Beam Design (ACI 318-14)</h3></div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;">
                            <thead>
                                <tr><th>Beam</th><th>b x h (mm)</th><th>Span (m)</th><th>wu (kN/m)</th><th>Mu (kN.m)</th><th>As,req (mm2)</th><th>Bars</th><th>Vu (kN)</th><th>Stirrups</th></tr>
                            </thead>
                            <tbody id="beamDesignBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.12: Column Check Panel -->
                <div id="panelColDesign" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Column Check (ACI 318-14)</h3></div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;">
                            <thead>
                                <tr><th>Column</th><th>Size (mm)</th><th>Pu (kN)</th><th>phi*Pn (kN)</th><th>Ratio</th><th>rho (%)</th><th>Main Bars</th><th>Ties</th><th>Status</th></tr>
                            </thead>
                            <tbody id="colDesignBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.12: Slab Design Panel -->
                <div id="panelSlabDesign" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Slab Design (ACI 318-14)</h3></div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;">
                            <thead>
                                <tr><th>Slab</th><th>Type</th><th>Lx (m)</th><th>Ly (m)</th><th>t (mm)</th><th>t,min (mm)</th><th>Mu (kN.m/m)</th><th>As (mm2/m)</th><th>Bars</th></tr>
                            </thead>
                            <tbody id="slabDesignBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.12: Staircase Panel -->
                <div id="panelStaircase" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Staircase Loading</h3></div>
                    <div style="padding:12px;">
                        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-bottom:12px;">
                            <label style="font-size:0.75rem;">Rise (mm):
                                <input type="number" id="stairRise" value="175" min="150" max="200" step="5" onchange="calculateStaircase()" style="width:100%; padding:4px; margin-top:4px;">
                            </label>
                            <label style="font-size:0.75rem;">Tread (mm):
                                <input type="number" id="stairTread" value="275" min="250" max="300" step="5" onchange="calculateStaircase()" style="width:100%; padding:4px; margin-top:4px;">
                            </label>
                            <label style="font-size:0.75rem;">Waist (mm):
                                <input type="number" id="stairWaist" value="150" min="100" max="250" step="10" onchange="calculateStaircase()" style="width:100%; padding:4px; margin-top:4px;">
                            </label>
                        </div>
                        <table class="schedule-table" style="width:100%;">
                            <tbody id="staircaseBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.12: Water Tank Panel -->
                <div id="panelWaterTank" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Water Tank Loading</h3></div>
                    <div style="padding:12px;">
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;">
                            <label style="font-size:0.75rem;">Capacity (liters):
                                <input type="number" id="tankCapacity" value="1000" min="500" max="10000" step="500" onchange="calculateWaterTank()" style="width:100%; padding:4px; margin-top:4px;">
                            </label>
                            <label style="font-size:0.75rem;">Location:
                                <select id="tankLocation" onchange="calculateWaterTank()" style="width:100%; padding:4px; margin-top:4px;">
                                    <option value="roof">Roof (Elevated)</option>
                                    <option value="ground">Ground Level</option>
                                </select>
                            </label>
                        </div>
                        <table class="schedule-table" style="width:100%;">
                            <tbody id="waterTankBody"></tbody>
                        </table>
                    </div>
                </div>
"""

# Insert before Column Results Table
panel_marker = "<!-- Column Results Table"
idx = c.find(panel_marker)
if idx > 0:
    c = c[:idx] + new_panels + "\n" + c[idx:]
    print("3. Added 7 new HTML panels")

# ================================================================
#  4. UPDATE setPlanTab() TO HANDLE NEW TABS
# ================================================================
# tabBtnMap
c = c.replace(
    "'bom': 'tabBOM'\n            };",
    "'bom': 'tabBOM',\n                'seismic': 'tabSeismic',\n                'wind': 'tabWind',\n                'beamDesign': 'tabBeamDesign',\n                'colDesign': 'tabColDesign',\n                'slabDesign': 'tabSlabDesign',\n                'staircase': 'tabStaircase',\n                'waterTank': 'tabWaterTank'\n            };",
    1
)
print("4a. Updated tabBtnMap")

# schedulePanels
c = c.replace(
    "'panelBlockwall', 'panelLoadSummary', 'panelRebarSchedule', 'panelBOM'",
    "'panelBlockwall', 'panelLoadSummary', 'panelRebarSchedule', 'panelBOM', 'panelSeismic', 'panelWind', 'panelBeamDesign', 'panelColDesign', 'panelSlabDesign', 'panelStaircase', 'panelWaterTank'",
    1
)
print("4b. Updated schedulePanels")

# isScheduleTab
c = c.replace(
    "'blockwall', 'loadSummary', 'rebarSchedule', 'bom'",
    "'blockwall', 'loadSummary', 'rebarSchedule', 'bom', 'seismic', 'wind', 'beamDesign', 'colDesign', 'slabDesign', 'staircase', 'waterTank'",
    1
)
print("4c. Updated isScheduleTab")

# Panel show logic
old_bom_logic = """                    } else if (tab === 'bom') {
                        document.getElementById('panelBOM').style.display = 'block';
                        populateBOM();
                    }"""

new_bom_logic = """                    } else if (tab === 'bom') {
                        document.getElementById('panelBOM').style.display = 'block';
                        populateBOM();
                    } else if (tab === 'seismic') {
                        document.getElementById('panelSeismic').style.display = 'block';
                        calculateSeismic();
                    } else if (tab === 'wind') {
                        document.getElementById('panelWind').style.display = 'block';
                        calculateWind();
                    } else if (tab === 'beamDesign') {
                        document.getElementById('panelBeamDesign').style.display = 'block';
                        designAllBeams();
                    } else if (tab === 'colDesign') {
                        document.getElementById('panelColDesign').style.display = 'block';
                        checkAllColumns();
                    } else if (tab === 'slabDesign') {
                        document.getElementById('panelSlabDesign').style.display = 'block';
                        designAllSlabs();
                    } else if (tab === 'staircase') {
                        document.getElementById('panelStaircase').style.display = 'block';
                        calculateStaircase();
                    } else if (tab === 'waterTank') {
                        document.getElementById('panelWaterTank').style.display = 'block';
                        calculateWaterTank();
                    }"""

c = c.replace(old_bom_logic, new_bom_logic, 1)
print("4d. Added panel show logic for 7 new tabs")

# ================================================================
#  5. ADD ALL ENGINEERING FUNCTIONS
# ================================================================
eng_functions = r"""
// ========== v3.12: ENGINEERING ANALYSIS FUNCTIONS ==========

// --- SEISMIC ANALYSIS (NSCP 2015 / ASCE 7-16) ---
function calculateSeismic() {
    const zone = parseInt(document.getElementById('seismicZone')?.value || 4);
    const soil = document.getElementById('soilProfile')?.value || 'SD';
    const I = parseFloat(document.getElementById('importFactor')?.value || 1.0);
    const R = parseFloat(document.getElementById('rFactor')?.value || 8.5);

    // Zone factors
    const Z = zone === 4 ? 0.40 : 0.20;
    
    // Soil coefficients (NSCP Table 208-7/8)
    const Ca_table = { 'SC': {2: 0.15, 4: 0.40}, 'SD': {2: 0.22, 4: 0.44}, 'SE': {2: 0.28, 4: 0.44} };
    const Cv_table = { 'SC': {2: 0.20, 4: 0.56}, 'SD': {2: 0.32, 4: 0.64}, 'SE': {2: 0.50, 4: 0.96} };
    const Ca = (Ca_table[soil] && Ca_table[soil][zone]) || 0.44;
    const Cv = (Cv_table[soil] && Cv_table[soil][zone]) || 0.64;

    // Building weight
    const numFloors = state.floors.length;
    const totalHeight = state.floors.reduce((sum, f) => sum + (f.height || 3.0), 0);
    
    // Approximate period T = Ct * hn^(3/4) for concrete frame
    const Ct = 0.0731; // NSCP for concrete moment frames
    const T = Ct * Math.pow(totalHeight, 0.75);

    // Seismic coefficients
    const Cs_calc = (Cv * I) / (R * T);
    const Cs_max = (2.5 * Ca * I) / R;
    const Cs_min = 0.11 * Ca * I;
    const Cs = Math.max(Cs_min, Math.min(Cs_calc, Cs_max));

    // Total building weight (approximate)
    let W = 0;
    state.floors.forEach(floor => {
        const slabArea = state.xSpans.reduce((a,b) => a+b, 0) * state.ySpans.reduce((a,b) => a+b, 0);
        const slabWt = slabArea * ((floor.slabThickness || 150) / 1000) * 24;
        const superDL = slabArea * (floor.dlSuper || 2.0);
        const livePartial = slabArea * (floor.liveLoad || 2.0) * 0.25;
        W += slabWt + superDL + livePartial;
    });

    const V = Cs * W; // Base shear

    // Summary
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    let html = '';
    html += '<tr><td>Seismic Zone</td><td>' + zone + '</td><td>Z = ' + Z + '</td></tr>';
    html += '<tr><td>Soil Profile</td><td>' + soil + '</td><td>Ca=' + Ca.toFixed(2) + ' Cv=' + Cv.toFixed(2) + '</td></tr>';
    html += '<tr><td>Building Height</td><td>' + totalHeight.toFixed(1) + ' m</td><td>' + numFloors + ' stories</td></tr>';
    html += '<tr><td>Period T</td><td>' + T.toFixed(3) + ' sec</td><td>Ct=' + Ct + '</td></tr>';
    html += '<tr><td>Cs (calculated)</td><td>' + Cs_calc.toFixed(4) + '</td><td>Cv*I/(R*T)</td></tr>';
    html += '<tr><td>Cs (max)</td><td>' + Cs_max.toFixed(4) + '</td><td>2.5*Ca*I/R</td></tr>';
    html += '<tr><td>Cs (min)</td><td>' + Cs_min.toFixed(4) + '</td><td>0.11*Ca*I</td></tr>';
    html += '<tr style="font-weight:bold; border-top:2px solid #000;"><td>Cs (governing)</td><td>' + Cs.toFixed(4) + '</td><td></td></tr>';
    html += '<tr><td>Building Weight W</td><td>' + W.toFixed(0) + ' kN</td><td></td></tr>';
    html += '<tr style="font-weight:bold; font-size:1.1em; border-top:2px solid #000;"><td>BASE SHEAR V</td><td>' + V.toFixed(1) + ' kN</td><td>Cs x W</td></tr>';
    
    const tbody = document.getElementById('seismicBody');
    if (tbody) tbody.innerHTML = html;

    // Story forces (inverted triangular distribution)
    let cumH = 0;
    const storyData = [];
    let sumWiHi = 0;
    state.floors.forEach(floor => {
        cumH += (floor.height || 3.0);
        const slabArea = state.xSpans.reduce((a,b) => a+b, 0) * state.ySpans.reduce((a,b) => a+b, 0);
        const Wi = slabArea * ((floor.slabThickness || 150) / 1000) * 24 + slabArea * (floor.dlSuper || 2.0);
        sumWiHi += Wi * cumH;
        storyData.push({ name: floor.id, hi: cumH, Wi: Wi, WiHi: Wi * cumH });
    });

    let storyHtml = '';
    storyData.forEach(s => {
        const Fi = (s.WiHi / sumWiHi) * V;
        storyHtml += '<tr><td>' + s.name + '</td><td>' + s.hi.toFixed(1) + '</td><td>' + s.Wi.toFixed(0) + '</td><td>' + s.WiHi.toFixed(0) + '</td><td><strong>' + Fi.toFixed(1) + '</strong></td></tr>';
    });
    const sfBody = document.getElementById('storyForceBody');
    if (sfBody) sfBody.innerHTML = storyHtml;
}

// --- WIND LOAD ANALYSIS (NSCP 2015) ---
function calculateWind() {
    const V = parseInt(document.getElementById('windSpeed')?.value || 200);
    const exposure = document.getElementById('windExposure')?.value || 'C';
    const I_w = 1.0; // Importance factor for wind

    const qh = 0.613 * Math.pow(V / 1000, 2) * 1000; // velocity pressure at height (kPa approx)
    
    const totalHeight = state.floors.reduce((sum, f) => sum + (f.height || 3.0), 0);
    const buildingWidth = state.xSpans.reduce((a,b) => a+b, 0);
    const buildingDepth = state.ySpans.reduce((a,b) => a+b, 0);

    let html = '';
    html += '<tr><td>Wind Speed V</td><td>' + V + ' km/h</td></tr>';
    html += '<tr><td>Exposure Category</td><td>' + exposure + '</td></tr>';
    html += '<tr><td>Building Height</td><td>' + totalHeight.toFixed(1) + ' m</td></tr>';
    html += '<tr><td>Building Width (X)</td><td>' + buildingWidth.toFixed(1) + ' m</td></tr>';
    html += '<tr><td>Building Depth (Y)</td><td>' + buildingDepth.toFixed(1) + ' m</td></tr>';

    const tbody = document.getElementById('windBody');
    if (tbody) tbody.innerHTML = html;

    // Exposure coefficients
    const alphaTable = { 'B': 7.0, 'C': 9.5, 'D': 11.5 };
    const zgTable = { 'B': 365.76, 'C': 274.32, 'D': 213.36 };
    const alpha = alphaTable[exposure] || 9.5;
    const zg = zgTable[exposure] || 274.32;

    let cumH = 0;
    let storyHtml = '';
    state.floors.forEach(floor => {
        cumH += (floor.height || 3.0);
        const Kz = 2.01 * Math.pow(Math.max(cumH, 4.6) / zg, 2 / alpha);
        const qz = 0.613 * Kz * I_w * Math.pow(V * 1000 / 3600, 2) / 1000; // kPa
        const Cp = 0.8; // windward
        const G = 0.85; // gust factor
        const p = qz * G * Cp; // design pressure
        const tributaryH = floor.height || 3.0;
        const F = p * buildingWidth * tributaryH; // force on this story

        storyHtml += '<tr><td>' + floor.id + '</td><td>' + cumH.toFixed(1) + '</td><td>' + Kz.toFixed(3) + '</td><td>' + qz.toFixed(3) + '</td><td><strong>' + F.toFixed(1) + '</strong></td></tr>';
    });

    const wsBody = document.getElementById('windStoryBody');
    if (wsBody) wsBody.innerHTML = storyHtml;
}

// --- BEAM DESIGN (ACI 318-14) ---
function designAllBeams() {
    const fc = state.fc || 21;
    const fy = state.fy || 415;
    const phi = 0.90;
    const coverMm = 40;
    const tbody = document.getElementById('beamDesignBody');
    if (!tbody) return;

    let html = '';
    state.beams.forEach(beam => {
        if (beam.isCustom || beam.isCantilever || beam.deleted) return;
        const b = beam.suggestedB || 250; // mm
        const h = beam.suggestedH || 400; // mm
        const d = h - coverMm - 10; // effective depth
        const L = beam.span || 4.0; // m
        const wu = beam.uniformLoad || beam.totalDistributed || (beam.wallLoad || 0) + 15; // kN/m approx

        // Flexure - simply supported
        const Mu = (wu * L * L) / 8; // kN.m
        const Rn = (Mu * 1e6) / (phi * b * d * d);
        const disc = 1 - (2 * Rn) / (0.85 * fc);
        let rho = disc > 0 ? (0.85 * fc / fy) * (1 - Math.sqrt(disc)) : 0.005;
        const rho_min = Math.max(0.25 * Math.sqrt(fc) / fy, 1.4 / fy);
        rho = Math.max(rho, rho_min);
        const As = rho * b * d;
        const barDia = h >= 500 ? 20 : 16;
        const Ab = Math.PI * barDia * barDia / 4;
        const nBars = Math.max(2, Math.ceil(As / Ab));

        // Shear
        const Vu = wu * L / 2; // kN
        const Vc = 0.17 * Math.sqrt(fc) * b * d / 1000; // kN
        const phiVc = 0.75 * Vc;
        let stirrups = '-';
        if (Vu > phiVc) {
            const Vs = (Vu / 0.75) - Vc;
            const Av = 2 * Math.PI * 5 * 5; // 2 legs of 10mm
            const s = Math.min(Math.floor((Av * fy * d) / (Vs * 1000)), d / 2, 300);
            stirrups = '2L-10mm @ ' + Math.max(s, 75) + 'mm';
        } else {
            stirrups = '2L-10mm @ ' + Math.min(Math.floor(d/2), 200) + 'mm';
        }

        html += '<tr>' +
            '<td>' + (beam.id || '-') + '</td>' +
            '<td>' + b + 'x' + h + '</td>' +
            '<td>' + L.toFixed(1) + '</td>' +
            '<td>' + wu.toFixed(1) + '</td>' +
            '<td>' + Mu.toFixed(1) + '</td>' +
            '<td>' + As.toFixed(0) + '</td>' +
            '<td>' + nBars + '-D' + barDia + '</td>' +
            '<td>' + Vu.toFixed(1) + '</td>' +
            '<td>' + stirrups + '</td>' +
            '</tr>';
    });
    tbody.innerHTML = html || '<tr><td colspan="9">No beams to design</td></tr>';
}

// --- COLUMN CHECK (ACI 318-14) ---
function checkAllColumns() {
    const fc = state.fc || 21;
    const fy = state.fy || 415;
    const phi = 0.65; // tied columns
    const tbody = document.getElementById('colDesignBody');
    if (!tbody) return;

    const colGroups = {};
    state.columns.forEach(col => {
        if (col.active === false) return;
        const b = col.suggestedB || 250;
        const h = col.suggestedH || 250;
        const key = b + 'x' + h;
        if (!colGroups[key]) colGroups[key] = { b, h, cols: [] };
        colGroups[key].cols.push(col);
    });

    let html = '';
    Object.values(colGroups).forEach(grp => {
        const b = grp.b, h = grp.h;
        const Ag = b * h;
        const rho = 0.01; // 1% minimum
        const Ast = rho * Ag;
        const Pn = 0.80 * (0.85 * fc * (Ag - Ast) + fy * Ast) / 1000; // kN
        const phiPn = phi * Pn;

        const barDia = b >= 350 ? 20 : 16;
        const Ab = Math.PI * barDia * barDia / 4;
        const nBars = Math.max(4, Math.ceil(Ast / Ab));
        const tieSize = 10;
        const tieSpacing = Math.min(16 * barDia, Math.min(b, h), 300);

        grp.cols.forEach(col => {
            const Pu = col.totalLoadWithDL || col.totalLoad || 0;
            const ratio = Pu / phiPn;
            const status = ratio <= 1.0 ? 'OK' : 'NG';

            html += '<tr>' +
                '<td>' + col.id + '</td>' +
                '<td>' + b + 'x' + h + '</td>' +
                '<td>' + Pu.toFixed(0) + '</td>' +
                '<td>' + phiPn.toFixed(0) + '</td>' +
                '<td style="' + (ratio > 1 ? 'color:red;font-weight:bold;' : '') + '">' + ratio.toFixed(2) + '</td>' +
                '<td>' + (rho * 100).toFixed(1) + '</td>' +
                '<td>' + nBars + '-D' + barDia + '</td>' +
                '<td>D' + tieSize + '@' + tieSpacing + '</td>' +
                '<td style="font-weight:bold;' + (status === 'OK' ? 'color:green;' : 'color:red;') + '">' + status + '</td>' +
                '</tr>';
        });
    });
    tbody.innerHTML = html || '<tr><td colspan="9">No columns</td></tr>';
}

// --- SLAB DESIGN (ACI 318-14) ---
function designAllSlabs() {
    const fc = state.fc || 21;
    const fy = state.fy || 415;
    const tbody = document.getElementById('slabDesignBody');
    if (!tbody) return;

    let html = '';
    state.slabs.forEach((slab, i) => {
        if (slab.isVoid) return;
        const Lx = Math.min(slab.width, slab.height); // short span
        const Ly = Math.max(slab.width, slab.height); // long span
        const ratio = Ly / Lx;
        const type = ratio >= 2 ? 'One-Way' : 'Two-Way';

        const floor = state.floors[state.currentFloorIndex];
        const t = floor?.slabThickness || 150;

        // Minimum thickness (ACI Table 9.5a)
        let tMin;
        if (type === 'One-Way') {
            tMin = Math.ceil((Lx * 1000) / 24); // simply supported = L/20, continuous = L/24
        } else {
            tMin = Math.ceil((Lx * 1000) / 33); // two-way slab
        }
        tMin = Math.max(tMin, 100); // absolute min

        // Flexure
        const d = t - 25 - 6; // mm effective depth
        const wu = 1.2 * ((t / 1000 * 24) + (floor?.dlSuper || 2.0)) + 1.6 * (floor?.liveLoad || 2.0);
        let Mu;
        if (type === 'One-Way') {
            Mu = (wu * Lx * Lx) / 8; // kN.m/m
        } else {
            Mu = (wu * Lx * Lx) / 10; // approximate for two-way
        }

        const Rn = (Mu * 1e6) / (0.9 * 1000 * d * d);
        const disc = 1 - (2 * Rn) / (0.85 * fc);
        let rho = disc > 0 ? (0.85 * fc / fy) * (1 - Math.sqrt(disc)) : 0.002;
        rho = Math.max(rho, fy >= 400 ? 0.0018 : 0.002);
        const As = rho * 1000 * d; // mm2/m

        const barDia = 12;
        const Ab = Math.PI * barDia * barDia / 4;
        const spacing = Math.min(Math.floor(Ab * 1000 / As), 3 * t, 450);

        html += '<tr>' +
            '<td>S' + (i + 1) + '</td>' +
            '<td>' + type + '</td>' +
            '<td>' + Lx.toFixed(1) + '</td>' +
            '<td>' + Ly.toFixed(1) + '</td>' +
            '<td>' + t + '</td>' +
            '<td style="' + (t < tMin ? 'color:red;font-weight:bold;' : '') + '">' + tMin + '</td>' +
            '<td>' + Mu.toFixed(1) + '</td>' +
            '<td>' + As.toFixed(0) + '</td>' +
            '<td>D' + barDia + '@' + spacing + '</td>' +
            '</tr>';
    });
    tbody.innerHTML = html || '<tr><td colspan="9">No slabs</td></tr>';
}

// --- STAIRCASE LOADING ---
function calculateStaircase() {
    const rise = parseInt(document.getElementById('stairRise')?.value || 175);
    const tread = parseInt(document.getElementById('stairTread')?.value || 275);
    const waist = parseInt(document.getElementById('stairWaist')?.value || 150);

    const theta = Math.atan(rise / tread) * 180 / Math.PI;
    const cosTheta = Math.cos(theta * Math.PI / 180);
    
    // Effective slab thickness
    const hStep = rise / 2; // mm - average step height
    const tEff = waist / cosTheta + hStep; // mm

    // Dead load
    const slabDL = (tEff / 1000) * 24; // kN/m2
    const finishDL = 1.5; // kN/m2 (railing + finish)
    const totalDL = slabDL + finishDL;

    // Live load
    const LL = 4.8; // kN/m2 for stairs (NSCP)

    // Factored
    const wu = 1.2 * totalDL + 1.6 * LL;

    let html = '';
    html += '<tr><td>Rise</td><td>' + rise + ' mm</td><td></td></tr>';
    html += '<tr><td>Tread</td><td>' + tread + ' mm</td><td></td></tr>';
    html += '<tr><td>Waist Thickness</td><td>' + waist + ' mm</td><td></td></tr>';
    html += '<tr><td>Slope Angle</td><td>' + theta.toFixed(1) + '</td><td>degrees</td></tr>';
    html += '<tr><td>Effective Thickness</td><td>' + tEff.toFixed(0) + '</td><td>mm</td></tr>';
    html += '<tr style="border-top:1px solid #ccc;"><td>Slab Dead Load</td><td>' + slabDL.toFixed(2) + '</td><td>kN/m2</td></tr>';
    html += '<tr><td>Finish + Railing</td><td>' + finishDL.toFixed(2) + '</td><td>kN/m2</td></tr>';
    html += '<tr><td>Total DL</td><td>' + totalDL.toFixed(2) + '</td><td>kN/m2</td></tr>';
    html += '<tr><td>Live Load (NSCP)</td><td>' + LL.toFixed(2) + '</td><td>kN/m2</td></tr>';
    html += '<tr style="font-weight:bold; border-top:2px solid #000;"><td>FACTORED wu</td><td>' + wu.toFixed(2) + '</td><td>kN/m2</td></tr>';

    const tbody = document.getElementById('staircaseBody');
    if (tbody) tbody.innerHTML = html;
}

// --- WATER TANK LOADING ---
function calculateWaterTank() {
    const capacity = parseInt(document.getElementById('tankCapacity')?.value || 1000);
    const location = document.getElementById('tankLocation')?.value || 'roof';

    const waterWeight = capacity * 9.81 / 1000; // kN (1 liter = 1 kg)
    const tankSelfWeight = waterWeight * 0.15; // ~15% for tank structure
    const totalWeight = waterWeight + tankSelfWeight;

    // Distribute to nearest columns (assume 4 support points)
    const nSupports = 4;
    const pointLoad = totalWeight / nSupports;

    // If roof, add additional factor for seismic
    const seismicFactor = location === 'roof' ? 1.5 : 1.0;
    const designLoad = pointLoad * seismicFactor;

    let html = '';
    html += '<tr><td>Tank Capacity</td><td>' + capacity + '</td><td>liters</td></tr>';
    html += '<tr><td>Water Weight</td><td>' + waterWeight.toFixed(1) + '</td><td>kN</td></tr>';
    html += '<tr><td>Tank Self-Weight (~15%)</td><td>' + tankSelfWeight.toFixed(1) + '</td><td>kN</td></tr>';
    html += '<tr><td>Total Weight</td><td>' + totalWeight.toFixed(1) + '</td><td>kN</td></tr>';
    html += '<tr style="border-top:1px solid #ccc;"><td>Support Points</td><td>' + nSupports + '</td><td>columns</td></tr>';
    html += '<tr><td>Point Load (service)</td><td>' + pointLoad.toFixed(1) + '</td><td>kN</td></tr>';
    if (location === 'roof') {
        html += '<tr><td>Seismic Factor (Fp)</td><td>' + seismicFactor.toFixed(1) + '</td><td></td></tr>';
    }
    html += '<tr style="font-weight:bold; border-top:2px solid #000;"><td>DESIGN POINT LOAD</td><td>' + designLoad.toFixed(1) + '</td><td>kN per support</td></tr>';

    const tbody = document.getElementById('waterTankBody');
    if (tbody) tbody.innerHTML = html;
}

"""

# Inject before the footing design functions
eng_marker = "// ========== v3.11: NEW TAB FUNCTIONS =========="
idx = c.find(eng_marker)
if idx > 0:
    c = c[:idx] + eng_functions + "\n" + c[idx:]
    print("5. Added 7 engineering analysis functions")

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(c)

print("\nDONE: All 7 engineering features added + UI cleaned up")
