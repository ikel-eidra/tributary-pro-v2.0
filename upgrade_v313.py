"""
v3.13: Add RCDC-Style Advanced Design Features
9 new tabs: BBS, Crack Width, Slenderness, Ductile Detailing,
Deflection, Load Combos, Development Length, Foundation Stability, PDF Report
"""

FILE = r"d:\projects\tributary-pro-v2.0-LIVE\v3\index.html"

with open(FILE, 'r', encoding='utf-8') as f:
    c = f.read()

# ================================================================
#  1. ADD 9 NEW TAB BUTTONS
# ================================================================
old_water = """<button class="plan-tab" id="tabWaterTank" onclick="setPlanTab('waterTank')">Water Tank</button>"""
new_tabs = old_water + """
                    <button class="plan-tab" id="tabBBS" onclick="setPlanTab('bbs')">Bar Bending</button>
                    <button class="plan-tab" id="tabCrackWidth" onclick="setPlanTab('crackWidth')">Crack Width</button>
                    <button class="plan-tab" id="tabSlenderness" onclick="setPlanTab('slenderness')">Slenderness</button>
                    <button class="plan-tab" id="tabDuctile" onclick="setPlanTab('ductile')">Ductile Detail</button>
                    <button class="plan-tab" id="tabDeflection" onclick="setPlanTab('deflection')">Deflection</button>
                    <button class="plan-tab" id="tabLoadCombos" onclick="setPlanTab('loadCombos')">Load Combos</button>
                    <button class="plan-tab" id="tabDevLength" onclick="setPlanTab('devLength')">Dev. Length</button>
                    <button class="plan-tab" id="tabFdnStability" onclick="setPlanTab('fdnStability')">Fdn Stability</button>
                    <button class="plan-tab" id="tabPDFReport" onclick="setPlanTab('pdfReport')">PDF Report</button>"""

c = c.replace(old_water, new_tabs, 1)
print("1. Added 9 new tab buttons")

# ================================================================
#  2. ADD 9 NEW PANEL HTML BLOCKS
# ================================================================
new_panels = """
                <!-- v3.13: Bar Bending Schedule -->
                <div id="panelBBS" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Bar Bending Schedule</h3></div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;">
                            <thead><tr><th>Member</th><th>Bar Mark</th><th>Dia (mm)</th><th>No.</th><th>Cut Length (m)</th><th>Total (m)</th><th>Weight (kg)</th></tr></thead>
                            <tbody id="bbsBody"></tbody>
                            <tfoot><tr style="font-weight:bold; border-top:2px solid #000;"><td colspan="5">TOTAL REBAR</td><td id="bbsTotalLength">-</td><td id="bbsTotalWeight">-</td></tr></tfoot>
                        </table>
                    </div>
                </div>

                <!-- v3.13: Crack Width Check -->
                <div id="panelCrackWidth" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Crack Width Check (ACI 318 S24.3)</h3></div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;">
                            <thead><tr><th>Beam</th><th>Size</th><th>fs (MPa)</th><th>dc (mm)</th><th>s (mm)</th><th>s,max (mm)</th><th>Status</th></tr></thead>
                            <tbody id="crackWidthBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.13: Column Slenderness -->
                <div id="panelSlenderness" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Column Slenderness (ACI 318 S6.2)</h3></div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;">
                            <thead><tr><th>Column</th><th>Size</th><th>lu (m)</th><th>r (mm)</th><th>klu/r</th><th>Limit</th><th>Class</th><th>dns</th><th>Status</th></tr></thead>
                            <tbody id="slendernessBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.13: Ductile Detailing -->
                <div id="panelDuctile" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Ductile Detailing (NSCP/ACI 318 Ch.18)</h3></div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <h4 style="margin:0 0 8px; font-size:0.75rem; text-transform:uppercase;">Column Confinement</h4>
                        <table class="schedule-table" style="width:100%;">
                            <thead><tr><th>Column</th><th>Size</th><th>lo (mm)</th><th>Conf. Tie Dia</th><th>Conf. Spacing</th><th>Mid Spacing</th></tr></thead>
                            <tbody id="ductileColBody"></tbody>
                        </table>
                        <h4 style="margin:12px 0 8px; font-size:0.75rem; text-transform:uppercase;">Beam Confinement</h4>
                        <table class="schedule-table" style="width:100%;">
                            <thead><tr><th>Beam</th><th>Size</th><th>Zone (2h)</th><th>Hoop Spacing</th><th>Mid Spacing</th></tr></thead>
                            <tbody id="ductileBeamBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.13: Deflection Check -->
                <div id="panelDeflection" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Deflection Check (ACI 318 Table 24.2)</h3></div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;">
                            <thead><tr><th>Beam</th><th>Span (m)</th><th>Ig (mm4)</th><th>Mcr (kN.m)</th><th>Ma (kN.m)</th><th>Ie (mm4)</th><th>di (mm)</th><th>Limit</th><th>Status</th></tr></thead>
                            <tbody id="deflectionBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.13: Load Combinations -->
                <div id="panelLoadCombos" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Load Combinations (NSCP 2015 S203)</h3></div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;" id="loadComboTable">
                            <thead><tr><th>#</th><th>Combination</th><th>Formula</th><th>Pu (kN) Max Col</th></tr></thead>
                            <tbody id="loadComboBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.13: Development Length -->
                <div id="panelDevLength" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Development Length (ACI 318 S25.4)</h3></div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;">
                            <thead><tr><th>Bar Size</th><th>db (mm)</th><th>Ab (mm2)</th><th>ld,tension (mm)</th><th>ld,comp (mm)</th><th>Lap (Class B)</th></tr></thead>
                            <tbody id="devLengthBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.13: Foundation Stability -->
                <div id="panelFdnStability" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Foundation Stability Check</h3></div>
                    <div style="padding:12px; max-height:70vh; overflow:auto;">
                        <table class="schedule-table" style="width:100%;">
                            <thead><tr><th>Check</th><th>Resisting</th><th>Overturning</th><th>FS</th><th>Required</th><th>Status</th></tr></thead>
                            <tbody id="fdnStabilityBody"></tbody>
                        </table>
                    </div>
                </div>

                <!-- v3.13: PDF Report -->
                <div id="panelPDFReport" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>Structural Computation Report</h3></div>
                    <div style="padding:12px; text-align:center;">
                        <p style="margin:20px 0; font-size:0.85rem;">Generate a complete structural computation report including all schedules, design checks, and load analysis.</p>
                        <button onclick="generatePDFReport()" style="padding:12px 32px; font-size:1rem; font-weight:bold; background:#2563eb; color:#fff; border:none; border-radius:6px; cursor:pointer;">Download PDF Report</button>
                        <div id="pdfReportStatus" style="margin-top:12px; font-size:0.75rem;"></div>
                    </div>
                </div>
"""

panel_marker = "<!-- Column Results Table"
idx = c.find(panel_marker)
if idx > 0:
    c = c[:idx] + new_panels + "\n" + c[idx:]
    print("2. Added 9 new HTML panels")

# ================================================================
#  3. UPDATE setPlanTab() MAPPINGS
# ================================================================
c = c.replace(
    "'waterTank': 'tabWaterTank'\n            };",
    "'waterTank': 'tabWaterTank',\n                'bbs': 'tabBBS',\n                'crackWidth': 'tabCrackWidth',\n                'slenderness': 'tabSlenderness',\n                'ductile': 'tabDuctile',\n                'deflection': 'tabDeflection',\n                'loadCombos': 'tabLoadCombos',\n                'devLength': 'tabDevLength',\n                'fdnStability': 'tabFdnStability',\n                'pdfReport': 'tabPDFReport'\n            };",
    1
)
print("3a. Updated tabBtnMap")

c = c.replace(
    "'panelStaircase', 'panelWaterTank'",
    "'panelStaircase', 'panelWaterTank', 'panelBBS', 'panelCrackWidth', 'panelSlenderness', 'panelDuctile', 'panelDeflection', 'panelLoadCombos', 'panelDevLength', 'panelFdnStability', 'panelPDFReport'",
    1
)
print("3b. Updated schedulePanels")

c = c.replace(
    "'staircase', 'waterTank'",
    "'staircase', 'waterTank', 'bbs', 'crackWidth', 'slenderness', 'ductile', 'deflection', 'loadCombos', 'devLength', 'fdnStability', 'pdfReport'",
    1
)
print("3c. Updated isScheduleTab")

# Panel show logic
old_wt_logic = """                    } else if (tab === 'waterTank') {
                        document.getElementById('panelWaterTank').style.display = 'block';
                        calculateWaterTank();
                    }"""

new_wt_logic = """                    } else if (tab === 'waterTank') {
                        document.getElementById('panelWaterTank').style.display = 'block';
                        calculateWaterTank();
                    } else if (tab === 'bbs') {
                        document.getElementById('panelBBS').style.display = 'block';
                        populateBBS();
                    } else if (tab === 'crackWidth') {
                        document.getElementById('panelCrackWidth').style.display = 'block';
                        checkCrackWidth();
                    } else if (tab === 'slenderness') {
                        document.getElementById('panelSlenderness').style.display = 'block';
                        checkSlenderness();
                    } else if (tab === 'ductile') {
                        document.getElementById('panelDuctile').style.display = 'block';
                        populateDuctileDetailing();
                    } else if (tab === 'deflection') {
                        document.getElementById('panelDeflection').style.display = 'block';
                        checkDeflection();
                    } else if (tab === 'loadCombos') {
                        document.getElementById('panelLoadCombos').style.display = 'block';
                        populateLoadCombos();
                    } else if (tab === 'devLength') {
                        document.getElementById('panelDevLength').style.display = 'block';
                        populateDevLength();
                    } else if (tab === 'fdnStability') {
                        document.getElementById('panelFdnStability').style.display = 'block';
                        checkFdnStability();
                    } else if (tab === 'pdfReport') {
                        document.getElementById('panelPDFReport').style.display = 'block';
                    }"""

c = c.replace(old_wt_logic, new_wt_logic, 1)
print("3d. Added panel show logic for 9 new tabs")

# ================================================================
#  4. ADD ALL 9 ENGINEERING FUNCTIONS
# ================================================================
rcdc_functions = r"""
// ========== v3.13: RCDC-STYLE ADVANCED DESIGN FUNCTIONS ==========

// --- BAR BENDING SCHEDULE ---
function populateBBS() {
    const fc = state.fc || 21, fy = state.fy || 415;
    const tbody = document.getElementById('bbsBody');
    if (!tbody) return;

    // Unit weights (kg/m) for common bar diameters
    const barWt = {10: 0.617, 12: 0.888, 16: 1.578, 20: 2.466, 25: 3.853, 28: 4.834, 32: 6.313};
    let html = '', totalLen = 0, totalWt = 0, markIdx = 1;

    // Footing bars
    const footingTypes = {};
    state.columns.forEach(col => {
        if (col.active === false || !col.footingSize || col.isPlanted) return;
        const key = col.footingSize.toFixed(2);
        if (!footingTypes[key]) footingTypes[key] = { size: col.footingSize, design: col.footingDesign, count: 0 };
        footingTypes[key].count++;
    });
    Object.values(footingTypes).forEach(ft => {
        const fd = ft.design;
        if (!fd) return;
        const dia = fd.barDia || 16;
        const nBarsPerFtg = fd.nBars * 2; // each way
        const cover = 75;
        const cutLen = (ft.size * 1000 - 2 * cover + 2 * 12 * dia) / 1000; // with hooks
        const totalN = nBarsPerFtg * ft.count;
        const len = cutLen * totalN;
        const wt = len * (barWt[dia] || 1.578);
        totalLen += len; totalWt += wt;
        html += '<tr><td>Footing (x' + ft.count + ')</td><td>FM' + markIdx + '</td><td>' + dia + '</td><td>' + totalN + '</td><td>' + cutLen.toFixed(2) + '</td><td>' + len.toFixed(1) + '</td><td>' + wt.toFixed(1) + '</td></tr>';
        markIdx++;
    });

    // Column bars (main + ties)
    const colGroups = {};
    state.columns.forEach(col => {
        if (col.active === false) return;
        const b = col.suggestedB || 250, h = col.suggestedH || 250;
        const key = b + 'x' + h;
        if (!colGroups[key]) colGroups[key] = { b, h, count: 0 };
        colGroups[key].count++;
    });
    const numFloors = state.floors.length;
    const floorH = state.floors[0]?.height || 3.0;
    Object.values(colGroups).forEach(g => {
        const mainDia = g.b >= 350 ? 20 : 16;
        const nMain = g.b >= 350 ? 8 : 4;
        const lapLen = 40 * mainDia / 1000; // m
        const cutLen = floorH + lapLen;
        const totalN = nMain * g.count * numFloors;
        const len = cutLen * totalN;
        const wt = len * (barWt[mainDia] || 1.578);
        totalLen += len; totalWt += wt;
        html += '<tr><td>Col ' + g.b + 'x' + g.h + ' (x' + g.count + ')</td><td>CM' + markIdx + '</td><td>' + mainDia + '</td><td>' + totalN + '</td><td>' + cutLen.toFixed(2) + '</td><td>' + len.toFixed(1) + '</td><td>' + wt.toFixed(1) + '</td></tr>';
        markIdx++;

        // Ties
        const tieDia = 10;
        const tieSpacing = 200; // mm
        const tiesPerCol = Math.ceil((floorH * 1000) / tieSpacing);
        const tiePerimeter = 2 * ((g.b - 80) + (g.h - 80)) + 2 * 135; // hooks
        const tieCutLen = tiePerimeter / 1000;
        const totalTies = tiesPerCol * g.count * numFloors;
        const tieLen = tieCutLen * totalTies;
        const tieWt = tieLen * (barWt[tieDia] || 0.617);
        totalLen += tieLen; totalWt += tieWt;
        html += '<tr><td>Col Ties ' + g.b + 'x' + g.h + '</td><td>CT' + markIdx + '</td><td>' + tieDia + '</td><td>' + totalTies + '</td><td>' + tieCutLen.toFixed(2) + '</td><td>' + tieLen.toFixed(1) + '</td><td>' + tieWt.toFixed(1) + '</td></tr>';
        markIdx++;
    });

    // Beam bars
    state.beams.forEach(beam => {
        if (beam.isCustom || beam.isCantilever) return;
        const bw = beam.suggestedB || 250, bh = beam.suggestedH || 400;
        const span = beam.span || 4.0;
        const mainDia = bh >= 500 ? 20 : 16;
        const nBot = 3, nTop = 2;
        const lapLen = 40 * mainDia / 1000;
        const botLen = span + 2 * lapLen;
        const topLen = span * 0.3 + lapLen; // top bars at supports
        const totalBot = nBot * numFloors;
        const totalTop = nTop * 2 * numFloors; // both ends
        const lenBot = botLen * totalBot, lenTop = topLen * totalTop;
        const wtBot = lenBot * (barWt[mainDia] || 1.578);
        const wtTop = lenTop * (barWt[mainDia] || 1.578);
        totalLen += lenBot + lenTop; totalWt += wtBot + wtTop;
        html += '<tr><td>Beam ' + (beam.id || '-') + ' Bot</td><td>BM' + markIdx + '</td><td>' + mainDia + '</td><td>' + totalBot + '</td><td>' + botLen.toFixed(2) + '</td><td>' + lenBot.toFixed(1) + '</td><td>' + wtBot.toFixed(1) + '</td></tr>';
        markIdx++;
    });

    tbody.innerHTML = html || '<tr><td colspan="7">No data</td></tr>';
    document.getElementById('bbsTotalLength').textContent = totalLen.toFixed(1);
    document.getElementById('bbsTotalWeight').textContent = totalWt.toFixed(0);
}

// --- CRACK WIDTH CHECK (ACI 318 S24.3) ---
function checkCrackWidth() {
    const fy = state.fy || 415;
    const tbody = document.getElementById('crackWidthBody');
    if (!tbody) return;
    let html = '';
    state.beams.forEach(beam => {
        if (beam.isCustom || beam.isCantilever) return;
        const b = beam.suggestedB || 250, h = beam.suggestedH || 400;
        const cover = 40;
        const barDia = h >= 500 ? 20 : 16;
        const dc = cover + barDia / 2; // mm
        const fs = 0.6 * fy; // service stress ~ 0.6fy
        const nBars = 3; // assumed
        const s = (b - 2 * cover) / (nBars - 1); // bar spacing

        // ACI 318-14 Eq. 24.3.2: s_max = 380(280/fs) - 2.5*cc
        const cc = cover;
        const s_max_1 = 380 * (280 / fs) - 2.5 * cc;
        const s_max_2 = 300 * (280 / fs);
        const s_max = Math.min(s_max_1, s_max_2);
        const ok = s <= s_max;

        html += '<tr>' +
            '<td>' + (beam.id || '-') + '</td>' +
            '<td>' + b + 'x' + h + '</td>' +
            '<td>' + fs.toFixed(0) + '</td>' +
            '<td>' + dc.toFixed(0) + '</td>' +
            '<td>' + s.toFixed(0) + '</td>' +
            '<td>' + s_max.toFixed(0) + '</td>' +
            '<td style="font-weight:bold;' + (ok ? 'color:green;' : 'color:red;') + '">' + (ok ? 'OK' : 'NG') + '</td>' +
            '</tr>';
    });
    tbody.innerHTML = html || '<tr><td colspan="7">No beams</td></tr>';
}

// --- COLUMN SLENDERNESS (ACI 318 S6.2) ---
function checkSlenderness() {
    const fc = state.fc || 21, fy = state.fy || 415;
    const tbody = document.getElementById('slendernessBody');
    if (!tbody) return;
    const lu = (state.floors[0]?.height || 3.0) - 0.4; // clear height
    const k = 1.0; // braced frame, conservative
    let html = '';

    state.columns.forEach(col => {
        if (col.active === false) return;
        const b = col.suggestedB || 250, h = col.suggestedH || 250;
        const r = 0.3 * Math.min(b, h); // radius of gyration (rectangular)
        const kluR = (k * lu * 1000) / r;
        const limit = 22; // ACI non-sway limit (34-12*M1/M2 simplified)
        const isSlender = kluR > limit;
        const classification = isSlender ? 'Slender' : 'Short';

        // Moment magnifier for slender columns
        let dns = 1.0;
        if (isSlender) {
            const Ec = 4700 * Math.sqrt(fc);
            const Ig = (b * Math.pow(h, 3)) / 12; // mm4
            const EI = (0.4 * Ec * Ig) / 1.0; // simplified
            const Pcr = (Math.PI * Math.PI * EI) / Math.pow(k * lu * 1000, 2) / 1000; // kN
            const Pu = col.totalLoadWithDL || col.totalLoad || 0;
            const Cm = 1.0; // conservative
            dns = Math.max(1.0, Cm / (1 - Pu / (0.75 * Pcr)));
            dns = Math.min(dns, 3.0); // cap
        }

        html += '<tr>' +
            '<td>' + col.id + '</td>' +
            '<td>' + b + 'x' + h + '</td>' +
            '<td>' + lu.toFixed(2) + '</td>' +
            '<td>' + r.toFixed(0) + '</td>' +
            '<td>' + kluR.toFixed(1) + '</td>' +
            '<td>' + limit + '</td>' +
            '<td>' + classification + '</td>' +
            '<td>' + dns.toFixed(2) + '</td>' +
            '<td style="font-weight:bold;' + (!isSlender ? 'color:green;' : 'color:#d97706;') + '">' + (!isSlender ? 'OK' : 'Magnify') + '</td>' +
            '</tr>';
    });
    tbody.innerHTML = html || '<tr><td colspan="9">No columns</td></tr>';
}

// --- DUCTILE DETAILING (ACI 318-14 Ch.18 / NSCP) ---
function populateDuctileDetailing() {
    const numFloors = state.floors.length;
    const floorH = state.floors[0]?.height || 3.0;

    // Column confinement
    const colBody = document.getElementById('ductileColBody');
    if (colBody) {
        const colGroups = {};
        state.columns.forEach(col => {
            if (col.active === false) return;
            const b = col.suggestedB || 250, h = col.suggestedH || 250;
            const key = b + 'x' + h;
            if (!colGroups[key]) colGroups[key] = { b, h, count: 0 };
            colGroups[key].count++;
        });

        let html = '';
        Object.values(colGroups).forEach(g => {
            // Confinement length lo = max(h, lu/6, 450)
            const lu = floorH * 1000;
            const lo = Math.max(g.h, lu / 6, 450);
            const mainDia = g.b >= 350 ? 20 : 16;
            const tieDia = 10;
            // Confinement spacing: s <= min(b/4, 6*db, 100+(350-hx)/3) capped 150mm
            const hx = g.b - 2 * 40; // core dimension
            const so = Math.min(Math.floor(g.b / 4), 6 * mainDia, Math.floor(100 + (350 - hx) / 3));
            const sConf = Math.max(75, Math.min(so, 150));
            const sMid = Math.min(16 * mainDia, Math.min(g.b, g.h), 300);

            html += '<tr>' +
                '<td>C-' + g.b + 'x' + g.h + ' (x' + g.count + ')</td>' +
                '<td>' + g.b + 'x' + g.h + '</td>' +
                '<td>' + lo.toFixed(0) + '</td>' +
                '<td>D' + tieDia + '</td>' +
                '<td>' + sConf + 'mm</td>' +
                '<td>' + sMid + 'mm</td>' +
                '</tr>';
        });
        colBody.innerHTML = html || '<tr><td colspan="6">No columns</td></tr>';
    }

    // Beam confinement
    const beamBody = document.getElementById('ductileBeamBody');
    if (beamBody) {
        let html = '';
        const beamGroups = {};
        state.beams.forEach(beam => {
            if (beam.isCustom || beam.isCantilever) return;
            const b = beam.suggestedB || 250, h = beam.suggestedH || 400;
            const key = b + 'x' + h;
            if (!beamGroups[key]) beamGroups[key] = { b, h, count: 0 };
            beamGroups[key].count++;
        });

        Object.values(beamGroups).forEach(g => {
            const zone = 2 * g.h; // confinement zone = 2h from face
            const mainDia = g.h >= 500 ? 20 : 16;
            const sConf = Math.min(Math.floor(g.h / 4), 8 * mainDia, 24 * 10, 200);
            const sMid = Math.min(Math.floor(g.h / 2), 200);

            html += '<tr>' +
                '<td>B-' + g.b + 'x' + g.h + ' (x' + g.count + ')</td>' +
                '<td>' + g.b + 'x' + g.h + '</td>' +
                '<td>' + zone + 'mm</td>' +
                '<td>' + sConf + 'mm</td>' +
                '<td>' + sMid + 'mm</td>' +
                '</tr>';
        });
        beamBody.innerHTML = html || '<tr><td colspan="5">No beams</td></tr>';
    }
}

// --- DEFLECTION CHECK (ACI 318 Table 24.2) ---
function checkDeflection() {
    const fc = state.fc || 21;
    const Ec = 4700 * Math.sqrt(fc); // MPa
    const fr = 0.62 * Math.sqrt(fc); // modulus of rupture
    const tbody = document.getElementById('deflectionBody');
    if (!tbody) return;
    let html = '';

    state.beams.forEach(beam => {
        if (beam.isCustom || beam.isCantilever) return;
        const b = beam.suggestedB || 250, h = beam.suggestedH || 400;
        const d = h - 50;
        const L = (beam.span || 4.0) * 1000; // mm
        const wu = beam.uniformLoad || beam.totalDistributed || 15; // kN/m service
        const ws = wu / 1.4; // approximate service load

        // Gross moment of inertia
        const Ig = (b * Math.pow(h, 3)) / 12; // mm4
        // Cracking moment
        const yt = h / 2;
        const Mcr = fr * Ig / yt / 1e6; // kN.m
        // Service moment
        const Ma = (ws * Math.pow(L / 1000, 2)) / 8; // kN.m

        // Effective Ie (Branson)
        let Ie;
        if (Ma <= Mcr) {
            Ie = Ig;
        } else {
            const ratio = Math.pow(Mcr / Ma, 3);
            // Approximate Icr ~ 0.35*Ig for T-section behavior
            const Icr = 0.35 * Ig;
            Ie = ratio * Ig + (1 - ratio) * Icr;
            Ie = Math.min(Ie, Ig);
        }

        // Immediate deflection
        const di = (5 * ws * Math.pow(L, 4)) / (384 * Ec * Ie) * 1e3; // mm (uniform load)
        // Limit: L/240 for floors (attached nonstructural)
        const limit = L / 240;
        const ok = di <= limit;

        html += '<tr>' +
            '<td>' + (beam.id || '-') + '</td>' +
            '<td>' + (L / 1000).toFixed(1) + '</td>' +
            '<td>' + (Ig / 1e6).toFixed(0) + 'e6</td>' +
            '<td>' + Mcr.toFixed(1) + '</td>' +
            '<td>' + Ma.toFixed(1) + '</td>' +
            '<td>' + (Ie / 1e6).toFixed(0) + 'e6</td>' +
            '<td>' + di.toFixed(1) + '</td>' +
            '<td>' + limit.toFixed(1) + '</td>' +
            '<td style="font-weight:bold;' + (ok ? 'color:green;' : 'color:red;') + '">' + (ok ? 'OK' : 'NG') + '</td>' +
            '</tr>';
    });
    tbody.innerHTML = html || '<tr><td colspan="9">No beams</td></tr>';
}

// --- LOAD COMBINATIONS (NSCP 2015 S203) ---
function populateLoadCombos() {
    const tbody = document.getElementById('loadComboBody');
    if (!tbody) return;

    // Get max column load for reference
    let maxDL = 0, maxLL = 0;
    state.columns.forEach(col => {
        if (col.active === false) return;
        const total = col.totalLoadWithDL || col.totalLoad || 0;
        const dl = total * 0.7; // approx DL portion
        const ll = total * 0.3; // approx LL portion
        maxDL = Math.max(maxDL, dl);
        maxLL = Math.max(maxLL, ll);
    });

    const E = maxDL * 0.15; // seismic ~ 15% of DL (approximate)
    const W = maxDL * 0.10; // wind ~ 10% of DL (approximate)

    const combos = [
        { id: 1, name: '1.4D', formula: '1.4D', val: 1.4 * maxDL },
        { id: 2, name: '1.2D + 1.6L', formula: '1.2D + 1.6L', val: 1.2 * maxDL + 1.6 * maxLL },
        { id: 3, name: '1.2D + 1.0E + 1.0L', formula: '1.2D + 1.0E + 1.0L', val: 1.2 * maxDL + E + maxLL },
        { id: 4, name: '1.2D + 1.0W + 1.0L', formula: '1.2D + 1.0W + 1.0L', val: 1.2 * maxDL + W + maxLL },
        { id: 5, name: '0.9D + 1.0E', formula: '0.9D + 1.0E', val: 0.9 * maxDL + E },
        { id: 6, name: '0.9D + 1.0W', formula: '0.9D + 1.0W', val: 0.9 * maxDL + W },
        { id: 7, name: '1.2D + 1.6L + 0.5W', formula: '1.2D + 1.6L + 0.5W', val: 1.2 * maxDL + 1.6 * maxLL + 0.5 * W },
    ];

    // Find governing
    let maxVal = 0, govIdx = 0;
    combos.forEach((c, i) => { if (c.val > maxVal) { maxVal = c.val; govIdx = i; } });

    let html = '';
    combos.forEach((c, i) => {
        const isGov = i === govIdx;
        html += '<tr style="' + (isGov ? 'background:rgba(37,99,235,0.1); font-weight:bold;' : '') + '">' +
            '<td>' + c.id + '</td>' +
            '<td>' + c.name + (isGov ? ' *GOV' : '') + '</td>' +
            '<td>' + c.formula + '</td>' +
            '<td>' + c.val.toFixed(1) + '</td>' +
            '</tr>';
    });
    tbody.innerHTML = html;
}

// --- DEVELOPMENT LENGTH (ACI 318 S25.4) ---
function populateDevLength() {
    const fc = state.fc || 21, fy = state.fy || 415;
    const tbody = document.getElementById('devLengthBody');
    if (!tbody) return;

    const bars = [
        { name: 'D10', db: 10 },
        { name: 'D12', db: 12 },
        { name: 'D16', db: 16 },
        { name: 'D20', db: 20 },
        { name: 'D25', db: 25 },
        { name: 'D28', db: 28 },
        { name: 'D32', db: 32 },
    ];

    let html = '';
    bars.forEach(bar => {
        const Ab = Math.PI * bar.db * bar.db / 4;
        // Tension: ld = (fy * psi_t * psi_e * psi_s) / (1.1 * lambda * sqrt(fc)) * db
        // Simplified for bottom bars, uncoated, normal weight
        const psi_t = 1.0, psi_e = 1.0, psi_s = bar.db <= 20 ? 0.8 : 1.0, lambda = 1.0;
        const ld_t = Math.max(
            (fy * psi_t * psi_e * psi_s) / (1.1 * lambda * Math.sqrt(fc)) * bar.db,
            300
        );
        // Compression: ld = max(0.24*fy*db/sqrt(fc), 0.043*fy*db, 200)
        const ld_c = Math.max(0.24 * fy * bar.db / Math.sqrt(fc), 0.043 * fy * bar.db, 200);
        // Lap splice Class B = 1.3 * ld
        const lap = 1.3 * ld_t;

        html += '<tr>' +
            '<td>' + bar.name + '</td>' +
            '<td>' + bar.db + '</td>' +
            '<td>' + Ab.toFixed(0) + '</td>' +
            '<td>' + ld_t.toFixed(0) + '</td>' +
            '<td>' + ld_c.toFixed(0) + '</td>' +
            '<td>' + lap.toFixed(0) + '</td>' +
            '</tr>';
    });
    tbody.innerHTML = html;
}

// --- FOUNDATION STABILITY ---
function checkFdnStability() {
    const tbody = document.getElementById('fdnStabilityBody');
    if (!tbody) return;

    const numFloors = state.floors.length;
    const floorH = state.floors[0]?.height || 3.0;
    const totalH = numFloors * floorH;
    const buildingW = state.xSpans.reduce((a, b) => a + b, 0);
    const buildingD = state.ySpans.reduce((a, b) => a + b, 0);

    // Total building weight
    let W = 0;
    state.columns.forEach(col => {
        if (col.active === false) return;
        W += col.totalLoadWithDL || col.totalLoad || 0;
    });

    // Lateral force (approximate: 10% of W for seismic)
    const H = 0.10 * W;

    // Overturning moment
    const OTM = H * totalH * 0.67; // at 2/3 height

    // Resisting moment
    const RM_x = W * buildingW / 2;
    const RM_y = W * buildingD / 2;

    // Factor of safety
    const FS_x = RM_x / OTM;
    const FS_y = RM_y / OTM;

    // Sliding
    const mu = 0.5; // friction coefficient
    const Fr = mu * W;
    const FS_slide = Fr / H;

    // Eccentricity
    const e_x = OTM / W;
    const e_limit_x = buildingW / 6;
    const e_limit_y = buildingD / 6;

    let html = '';
    html += '<tr><td>Overturning X-dir</td><td>' + RM_x.toFixed(0) + ' kN.m</td><td>' + OTM.toFixed(0) + ' kN.m</td><td>' + FS_x.toFixed(2) + '</td><td>1.50</td><td style="font-weight:bold;' + (FS_x >= 1.5 ? 'color:green;' : 'color:red;') + '">' + (FS_x >= 1.5 ? 'OK' : 'NG') + '</td></tr>';
    html += '<tr><td>Overturning Y-dir</td><td>' + RM_y.toFixed(0) + ' kN.m</td><td>' + OTM.toFixed(0) + ' kN.m</td><td>' + FS_y.toFixed(2) + '</td><td>1.50</td><td style="font-weight:bold;' + (FS_y >= 1.5 ? 'color:green;' : 'color:red;') + '">' + (FS_y >= 1.5 ? 'OK' : 'NG') + '</td></tr>';
    html += '<tr><td>Sliding</td><td>' + Fr.toFixed(0) + ' kN</td><td>' + H.toFixed(0) + ' kN</td><td>' + FS_slide.toFixed(2) + '</td><td>1.50</td><td style="font-weight:bold;' + (FS_slide >= 1.5 ? 'color:green;' : 'color:red;') + '">' + (FS_slide >= 1.5 ? 'OK' : 'NG') + '</td></tr>';
    html += '<tr><td>Eccentricity X</td><td>B/6 = ' + e_limit_x.toFixed(2) + ' m</td><td>e = ' + e_x.toFixed(2) + ' m</td><td>-</td><td>e < B/6</td><td style="font-weight:bold;' + (e_x < e_limit_x ? 'color:green;' : 'color:red;') + '">' + (e_x < e_limit_x ? 'OK' : 'NG') + '</td></tr>';

    tbody.innerHTML = html;
}

// --- PDF REPORT GENERATOR ---
function generatePDFReport() {
    const status = document.getElementById('pdfReportStatus');
    if (status) status.textContent = 'Generating report...';

    // Build HTML report content
    let report = '<!DOCTYPE html><html><head><meta charset="utf-8">';
    report += '<title>Structural Computation Report - FutolStructure</title>';
    report += '<style>';
    report += 'body { font-family: "Courier New", monospace; font-size: 11px; margin: 20mm; line-height: 1.4; }';
    report += 'h1 { font-size: 16px; text-align: center; border-bottom: 2px solid #000; padding-bottom: 8px; }';
    report += 'h2 { font-size: 13px; margin-top: 20px; border-bottom: 1px solid #000; }';
    report += 'h3 { font-size: 11px; margin-top: 12px; }';
    report += 'table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 10px; }';
    report += 'th, td { border: 1px solid #333; padding: 3px 6px; text-align: left; }';
    report += 'th { background: #f0f0f0; font-weight: bold; }';
    report += '.page-break { page-break-before: always; }';
    report += '@media print { body { margin: 15mm; } }';
    report += '</style></head><body>';

    // Title
    report += '<h1>STRUCTURAL COMPUTATION REPORT</h1>';
    report += '<table><tr><td>Project:</td><td>FutolStructure Analysis</td></tr>';
    report += '<tr><td>Date:</td><td>' + new Date().toLocaleDateString() + '</td></tr>';
    report += '<tr><td>Software:</td><td>Tributary Pro v3.x</td></tr>';
    report += '<tr><td>Code:</td><td>NSCP 2015 / ACI 318-14</td></tr></table>';

    // Building Parameters
    report += '<h2>1. BUILDING PARAMETERS</h2>';
    report += '<table>';
    report += '<tr><td>X-Spans:</td><td>' + state.xSpans.join(', ') + ' m</td></tr>';
    report += '<tr><td>Y-Spans:</td><td>' + state.ySpans.join(', ') + ' m</td></tr>';
    report += '<tr><td>No. of Floors:</td><td>' + state.floors.length + '</td></tr>';
    report += '<tr><td>Floor Height:</td><td>' + (state.floors[0]?.height || 3.0) + ' m</td></tr>';
    report += '<tr><td>fc\':</td><td>' + (state.fc || 21) + ' MPa</td></tr>';
    report += '<tr><td>fy:</td><td>' + (state.fy || 415) + ' MPa</td></tr>';
    report += '<tr><td>Soil Bearing:</td><td>' + (state.soilBearing || 100) + ' kPa</td></tr>';
    report += '</table>';

    // Column Schedule
    report += '<h2>2. COLUMN SCHEDULE</h2><table>';
    report += '<tr><th>ID</th><th>Type</th><th>B (mm)</th><th>H (mm)</th><th>Pu (kN)</th></tr>';
    state.columns.forEach(col => {
        if (col.active === false) return;
        report += '<tr><td>' + col.id + '</td><td>' + (col.type || '-') + '</td><td>' + (col.suggestedB || 250) + '</td><td>' + (col.suggestedH || 250) + '</td><td>' + (col.totalLoadWithDL || col.totalLoad || 0).toFixed(1) + '</td></tr>';
    });
    report += '</table>';

    // Footing Schedule
    report += '<h2>3. FOOTING SCHEDULE</h2><table>';
    report += '<tr><th>Column</th><th>Size (m)</th><th>h (mm)</th><th>Reinforcement</th></tr>';
    state.columns.forEach(col => {
        if (col.active === false || !col.footingSize || col.isPlanted) return;
        const fd = col.footingDesign;
        report += '<tr><td>' + col.id + '</td><td>' + col.footingSize.toFixed(2) + 'x' + col.footingSize.toFixed(2) + '</td><td>' + (fd ? fd.h : 300) + '</td><td>' + (fd ? fd.rebarStr : '-') + '</td></tr>';
    });
    report += '</table>';

    // Beam Schedule
    report += '<h2>4. BEAM SCHEDULE</h2><table>';
    report += '<tr><th>Beam</th><th>b x h (mm)</th><th>Span (m)</th></tr>';
    state.beams.forEach(beam => {
        if (beam.isCustom || beam.isCantilever) return;
        report += '<tr><td>' + (beam.id || '-') + '</td><td>' + (beam.suggestedB || 250) + 'x' + (beam.suggestedH || 400) + '</td><td>' + (beam.span || 0).toFixed(1) + '</td></tr>';
    });
    report += '</table>';

    report += '</body></html>';

    // Open in new window for printing
    const win = window.open('', '_blank');
    win.document.write(report);
    win.document.close();
    win.print();

    if (status) status.textContent = 'Report opened in new window. Use Ctrl+P to save as PDF.';
}

"""

# Inject before v3.12 functions
eng_marker = "// ========== v3.12: ENGINEERING ANALYSIS FUNCTIONS =========="
idx = c.find(eng_marker)
if idx > 0:
    c = c[:idx] + rcdc_functions + "\n" + c[idx:]
    print("4. Added 9 RCDC-style functions")

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(c)

print("\nDONE: All 9 RCDC-style features added")
