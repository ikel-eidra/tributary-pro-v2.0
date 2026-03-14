"""
v3.15: Kimi Code AI Assistant integration
- AI Assistant tab with chat interface
- Structural context injection (grounded, no hallucination)
- Kimi API via moonshot.cn
"""

FILE = r"d:\projects\tributary-pro-v2.0-LIVE\v3\index.html"

with open(FILE, 'r', encoding='utf-8') as f:
    c = f.read()

# ================================================================
#  1. ADD AI ASSISTANT TAB BUTTON (first position for prominence)
# ================================================================
old_mix = """<button class="plan-tab" id="tabMixDesign" onclick="setPlanTab('mixDesign')">Mix Design</button>"""
new_ai = old_mix + """
                    <button class="plan-tab" id="tabAIAssistant" onclick="setPlanTab('aiAssistant')" style="background:#7c3aed; color:#fff;">AI Assistant</button>"""

c = c.replace(old_mix, new_ai, 1)
print("1. Added AI Assistant tab button")

# ================================================================
#  2. ADD AI ASSISTANT PANEL
# ================================================================
ai_panel = """
                <!-- v3.15: AI Assistant Panel (Kimi Code) -->
                <div id="panelAIAssistant" class="schedule-panel" style="display:none;">
                    <div class="schedule-header"><h3>AI Structural Assistant (Kimi)</h3></div>
                    <div style="padding:8px;">
                        <div style="display:flex; gap:6px; margin-bottom:8px; align-items:center;">
                            <label style="font-size:0.7rem; white-space:nowrap;">API Key:</label>
                            <input type="password" id="kimiApiKey" placeholder="sk-kimi-..." style="flex:1; padding:4px 8px; font-size:0.75rem; border:1px solid #ccc; border-radius:4px;">
                            <select id="kimiModel" style="padding:4px; font-size:0.7rem; border:1px solid #ccc; border-radius:4px;">
                                <option value="moonshot-v1-32k">moonshot-v1-32k</option>
                                <option value="kimi-k2.5">kimi-k2.5</option>
                                <option value="moonshot-v1-128k">moonshot-v1-128k</option>
                            </select>
                        </div>
                        <div id="aiChatMessages" style="height:50vh; overflow-y:auto; border:1px solid #e2e8f0; border-radius:6px; padding:8px; margin-bottom:8px; background:#fafafa; font-size:0.8rem; line-height:1.5;">
                            <div style="color:#64748b; font-style:italic;">Ask anything about your structural design. The AI sees your project data (spans, loads, member sizes, design results). Try:<br>
                            - "Review my column sizes, are they adequate?"<br>
                            - "What's the most critical member?"<br>
                            - "Suggest improvements for my footing layout"<br>
                            - "Write a structural narrative for my report"</div>
                        </div>
                        <div style="display:flex; gap:6px;">
                            <input type="text" id="aiUserInput" placeholder="Ask about your structural design..." style="flex:1; padding:8px 12px; border:1px solid #ccc; border-radius:6px; font-size:0.8rem;" onkeydown="if(event.key==='Enter')sendToKimi()">
                            <button onclick="sendToKimi()" style="padding:8px 16px; background:#7c3aed; color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:bold; font-size:0.8rem;">Send</button>
                            <button onclick="clearAIChat()" style="padding:8px 12px; background:#94a3b8; color:#fff; border:none; border-radius:6px; cursor:pointer; font-size:0.75rem;">Clear</button>
                        </div>
                    </div>
                </div>
"""

panel_marker = "<!-- Column Results Table"
idx = c.find(panel_marker)
if idx > 0:
    c = c[:idx] + ai_panel + "\n" + c[idx:]
    print("2. Added AI Assistant panel")

# ================================================================
#  3. UPDATE setPlanTab() FOR AI TAB
# ================================================================
c = c.replace(
    "'mixDesign': 'tabMixDesign'\n            };",
    "'mixDesign': 'tabMixDesign',\n                'aiAssistant': 'tabAIAssistant'\n            };",
    1
)
print("3a. tabBtnMap")

c = c.replace(
    "'panelMixDesign'",
    "'panelMixDesign', 'panelAIAssistant'",
    1
)
print("3b. schedulePanels")

c = c.replace(
    "'torsion', 'mixDesign'",
    "'torsion', 'mixDesign', 'aiAssistant'",
    1
)
print("3c. isScheduleTab")

old_mix_logic = """                    } else if (tab === 'mixDesign') {
                        document.getElementById('panelMixDesign').style.display = 'block';
                        calculateMixDesign();
                    }"""

new_mix_logic = """                    } else if (tab === 'mixDesign') {
                        document.getElementById('panelMixDesign').style.display = 'block';
                        calculateMixDesign();
                    } else if (tab === 'aiAssistant') {
                        document.getElementById('panelAIAssistant').style.display = 'block';
                        initAIAssistant();
                    }"""

c = c.replace(old_mix_logic, new_mix_logic, 1)
print("3d. Panel show logic")

# ================================================================
#  4. ADD KIMI AI FUNCTIONS
# ================================================================
ai_functions = r"""
// ========== v3.15: KIMI CODE AI ASSISTANT ==========

const aiChatHistory = [];

function initAIAssistant() {
    // Load saved API key
    const saved = localStorage.getItem('kimiApiKey');
    if (saved) document.getElementById('kimiApiKey').value = saved;
}

function getStructuralContext() {
    // Build a grounded summary of the ACTUAL project data
    const fc = state.fc || 21, fy = state.fy || 415;
    const numFloors = state.floors.length;
    const floorH = state.floors[0]?.height || 3.0;
    const activeCols = state.columns.filter(c => c.active !== false);
    const activeBeams = state.beams.filter(b => !b.isCustom && !b.isCantilever);

    let ctx = 'PROJECT DATA (actual values from the model):\n';
    ctx += '- Grid: ' + (state.xSpans.length + 1) + 'x' + (state.ySpans.length + 1) + '\n';
    ctx += '- X spans: [' + state.xSpans.join(', ') + '] m\n';
    ctx += '- Y spans: [' + state.ySpans.join(', ') + '] m\n';
    ctx += '- Floors: ' + numFloors + ' @ ' + floorH + 'm height\n';
    ctx += "- f'c = " + fc + ' MPa, fy = ' + fy + ' MPa\n';
    ctx += '- Soil bearing = ' + (state.soilBearing || 100) + ' kPa\n\n';

    // Column summary
    ctx += 'COLUMNS (' + activeCols.length + ' total):\n';
    const colGroups = {};
    activeCols.forEach(col => {
        const b = col.suggestedB || 250, h = col.suggestedH || 250;
        const key = b + 'x' + h;
        if (!colGroups[key]) colGroups[key] = { b, h, count: 0, maxPu: 0, minPu: Infinity };
        colGroups[key].count++;
        const Pu = col.totalLoadWithDL || col.totalLoad || 0;
        colGroups[key].maxPu = Math.max(colGroups[key].maxPu, Pu);
        colGroups[key].minPu = Math.min(colGroups[key].minPu, Pu);
    });
    Object.entries(colGroups).forEach(([key, g]) => {
        const Ag = g.b * g.h;
        const Pn = 0.65 * 0.80 * (0.85 * fc * Ag * 0.99 + fy * 0.01 * Ag) / 1000;
        const ratio = g.maxPu / Pn;
        ctx += '  ' + key + 'mm (x' + g.count + '): Pu=' + g.minPu.toFixed(0) + '-' + g.maxPu.toFixed(0) + 'kN, phiPn=' + Pn.toFixed(0) + 'kN, DCR=' + ratio.toFixed(2) + '\n';
    });

    // Beam summary
    ctx += '\nBEAMS (' + activeBeams.length + ' total):\n';
    const beamGroups = {};
    activeBeams.forEach(beam => {
        const b = beam.suggestedB || 250, h = beam.suggestedH || 400;
        const key = b + 'x' + h;
        if (!beamGroups[key]) beamGroups[key] = { b, h, count: 0, maxSpan: 0 };
        beamGroups[key].count++;
        beamGroups[key].maxSpan = Math.max(beamGroups[key].maxSpan, beam.span || 0);
    });
    Object.entries(beamGroups).forEach(([key, g]) => {
        ctx += '  ' + key + 'mm (x' + g.count + '): max span=' + g.maxSpan.toFixed(1) + 'm\n';
    });

    // Footing summary
    const ftgCols = activeCols.filter(c => c.footingSize && !c.isPlanted);
    if (ftgCols.length > 0) {
        ctx += '\nFOOTINGS (' + ftgCols.length + '):\n';
        const ftgGroups = {};
        ftgCols.forEach(col => {
            const key = col.footingSize.toFixed(2);
            if (!ftgGroups[key]) ftgGroups[key] = { size: col.footingSize, count: 0, design: col.footingDesign };
            ftgGroups[key].count++;
        });
        Object.values(ftgGroups).forEach(g => {
            const fd = g.design;
            ctx += '  ' + g.size.toFixed(2) + 'x' + g.size.toFixed(2) + 'm (x' + g.count + ')';
            if (fd) ctx += ' h=' + fd.h + 'mm, punch=' + (fd.punchOK ? 'OK' : 'NG') + ', shear=' + (fd.shearOK ? 'OK' : 'NG');
            ctx += '\n';
        });
    }

    return ctx;
}

async function sendToKimi() {
    const apiKey = document.getElementById('kimiApiKey')?.value?.trim();
    const model = document.getElementById('kimiModel')?.value || 'moonshot-v1-32k';
    const userInput = document.getElementById('aiUserInput')?.value?.trim();

    if (!apiKey) { alert('Please enter your Kimi API key'); return; }
    if (!userInput) return;

    // Save API key
    localStorage.setItem('kimiApiKey', apiKey);

    // Add user message to chat
    const chatDiv = document.getElementById('aiChatMessages');
    chatDiv.innerHTML += '<div style="margin:8px 0; padding:8px; background:#ede9fe; border-radius:6px;"><strong>You:</strong> ' + userInput.replace(/</g, '&lt;') + '</div>';
    document.getElementById('aiUserInput').value = '';

    // Show loading
    const loadingId = 'loading_' + Date.now();
    chatDiv.innerHTML += '<div id="' + loadingId + '" style="margin:8px 0; color:#7c3aed; font-style:italic;">Thinking...</div>';
    chatDiv.scrollTop = chatDiv.scrollHeight;

    // Build messages
    const structuralContext = getStructuralContext();
    const systemPrompt = `You are a licensed structural engineer assistant integrated into the Tributary Pro structural design software. You are reviewing a REAL project with REAL data.

RULES:
1. ONLY reference data that exists in the PROJECT DATA below. Do NOT invent values.
2. If a value is not available, say "this data is not available in the current model."
3. Be concise and practical. Give specific numbers from the project data.
4. Use NSCP 2015 / ACI 318-14 as the governing code.
5. When suggesting changes, explain WHY with engineering rationale.
6. Always state your assumptions clearly.
7. Do NOT hallucinate member sizes, loads, or results that are not in the data.

${structuralContext}`;

    if (aiChatHistory.length === 0) {
        aiChatHistory.push({ role: 'system', content: systemPrompt });
    }
    aiChatHistory.push({ role: 'user', content: userInput });

    // Keep history manageable (last 10 exchanges)
    while (aiChatHistory.length > 21) aiChatHistory.splice(1, 2);

    try {
        const response = await fetch('https://api.moonshot.cn/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + apiKey
            },
            body: JSON.stringify({
                model: model,
                messages: aiChatHistory,
                temperature: 0.3,
                max_tokens: 2048
            })
        });

        const el = document.getElementById(loadingId);

        if (!response.ok) {
            const errText = await response.text();
            if (el) el.innerHTML = '<div style="color:red;">API Error ' + response.status + ': ' + errText.slice(0, 200) + '</div>';
            return;
        }

        const data = await response.json();
        const reply = data.choices?.[0]?.message?.content || 'No response';
        aiChatHistory.push({ role: 'assistant', content: reply });

        // Format reply (basic markdown)
        let formatted = reply
            .replace(/</g, '&lt;')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>')
            .replace(/`(.*?)`/g, '<code style="background:#f1f5f9; padding:1px 4px; border-radius:2px;">$1</code>');

        if (el) el.innerHTML = '<div style="margin:8px 0; padding:8px; background:#f0fdf4; border-radius:6px; border-left:3px solid #10b981;"><strong>Kimi:</strong><br>' + formatted + '</div>';
        chatDiv.scrollTop = chatDiv.scrollHeight;

    } catch (err) {
        const el = document.getElementById(loadingId);
        if (el) el.innerHTML = '<div style="color:red;">Connection error: ' + err.message + '</div>';
    }
}

function clearAIChat() {
    aiChatHistory.length = 0;
    const chatDiv = document.getElementById('aiChatMessages');
    if (chatDiv) chatDiv.innerHTML = '<div style="color:#64748b; font-style:italic;">Chat cleared. Ask a new question about your structural design.</div>';
}

"""

# Inject before v3.14 functions
marker = "// ========== v3.14: SAVE/LOAD (.tpro) + UNDO + FINAL FEATURES =========="
idx = c.find(marker)
if idx > 0:
    c = c[:idx] + ai_functions + "\n" + c[idx:]
    print("4. Added Kimi AI Assistant functions")

# ================================================================
#  5. PRE-FILL API KEY IN SETTINGS INIT
# ================================================================
# Add default key to localStorage on load
old_init = "// v3.11: Auto-calculate on load"
new_init = """// v3.15: Pre-fill Kimi API key if not set
            if (!localStorage.getItem('kimiApiKey')) localStorage.setItem('kimiApiKey', 'sk-kimi-2nYOAdpc3ZpzZrSJOobdaOmfgrq8AfU2nJ8xex3byDQQwE1XMPzCxpdozzpfwPsS');
            // v3.11: Auto-calculate on load"""
c = c.replace(old_init, new_init, 1)
print("5. Pre-filled API key in localStorage")

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(c)

print("\nDONE: Kimi AI Assistant integrated")
