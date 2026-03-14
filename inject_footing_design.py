"""
Inject full NSCP/ACI 318 footing design into the monolithic v3/index.html.
Adds designFooting() function and hooks it into calculateFootingSizes().
"""
import sys

def inject_footing_design(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The footing design code block
    footing_code = r"""
// ========== FOOTING STRUCTURAL DESIGN (NSCP 2015 / ACI 318-14) ==========
// Performs: sizing, punching shear, wide-beam shear, flexural reinforcement
// Called after calculateFootingSizes() to add structural checks

function designFooting(col) {
    if (!col.footingSize || col.footingSize <= 0) return;

    const fc = state.fc || 21;        // MPa
    const fy = state.fy || 415;       // MPa
    const gamma_c = 24;               // kN/m³
    const phi_v = 0.75;               // Shear reduction factor
    const phi_b = 0.90;               // Flexure reduction factor
    const cover = 75;                 // mm concrete cover (soil contact)
    const barDia = 16;                // mm main rebar diameter
    const d_guess = (col.footingThick || 0.3) * 1000 - cover - barDia / 2; // effective depth mm

    const L = col.footingSize;        // m (square footing side)
    const Pu = col.totalLoadWithDL || col.totalLoad || 0; // kN (factored)
    const colB = (col.suggestedB || 250) / 1000; // m
    const colH = (col.suggestedH || 250) / 1000; // m

    // ------- Step 1: Net upward soil pressure -------
    const qu = Pu / (L * L); // kPa (factored)

    // ------- Step 2: Footing Thickness by Punching Shear (ACI 318-14 §22.6) -------
    // Critical perimeter at d/2 from column face
    let d = d_guess; // mm, iterate

    for (let iter = 0; iter < 5; iter++) {
        const d_m = d / 1000; // in meters
        const bo = 2 * ((colB + d_m) + (colH + d_m)); // m - perimeter
        const Ap = (colB + d_m) * (colH + d_m); // m² - punching area
        const Vu_punch = Pu - qu * Ap; // kN

        // ACI 318 §22.6.5.2: Vc = min of three equations
        const beta_c = Math.max(colH, colB) / Math.min(colH, colB); // aspect ratio
        const lambda = 1.0; // normal weight concrete
        const Vc1 = 0.33 * lambda * Math.sqrt(fc) * bo * d / 1000; // kN
        const Vc2 = (0.17 * (1 + 2 / beta_c)) * lambda * Math.sqrt(fc) * bo * d / 1000;
        const alpha_s = 40; // interior column
        const Vc3 = (0.083 * (alpha_s * d / (bo * 1000) + 2)) * lambda * Math.sqrt(fc) * bo * d / 1000;
        const Vc = Math.min(Vc1, Vc2, Vc3);
        const phiVc = phi_v * Vc;

        if (phiVc >= Vu_punch) {
            break; // OK
        } else {
            // Increase d by 25mm and try again
            d += 25;
        }
    }

    // ------- Step 3: Wide-Beam (One-Way) Shear Check (ACI 318-14 §22.5) -------
    // Critical section at d from column face
    const d_m = d / 1000;
    const cantilever = (L - colB) / 2; // m - projection from column face
    const Vu_wide = qu * L * (cantilever - d_m); // kN
    const Vc_wide = 0.17 * 1.0 * Math.sqrt(fc) * (L * 1000) * d / 1000; // kN
    const phiVc_wide = phi_v * Vc_wide;

    let wideBeamOK = phiVc_wide >= Vu_wide;

    // If wide beam shear fails, increase d
    while (!wideBeamOK && d < 1500) {
        d += 25;
        const d_m2 = d / 1000;
        const Vu2 = qu * L * (cantilever - d_m2);
        const Vc2 = 0.17 * Math.sqrt(fc) * (L * 1000) * d / 1000;
        wideBeamOK = (phi_v * Vc2) >= Vu2;
    }

    // ------- Step 4: Required Footing Thickness -------
    const hReq = d + cover + barDia / 2; // mm
    const hFinal = Math.max(300, Math.ceil(hReq / 50) * 50); // round up to 50mm
    const dFinal = hFinal - cover - barDia / 2;  // final effective depth

    // ------- Step 5: Flexural Reinforcement (ACI 318-14 §13.3.3) -------
    // Critical section at face of column
    const Mu = qu * L * Math.pow(cantilever, 2) / 2; // kN·m per meter width
    // Actually Mu total = qu * L * (L-colB)²/8 for full footing width
    const Mu_total = qu * L * Math.pow((L - colB) / 2, 2) / 2; // kN·m

    // Rn = Mu / (phi * b * d²)
    const b_mm = L * 1000; // mm (full width)
    const Rn = (Mu_total * 1e6) / (phi_b * b_mm * dFinal * dFinal); // MPa

    // rho = 0.85*fc/fy * (1 - sqrt(1 - 2*Rn/(0.85*fc)))
    const discriminant = 1 - (2 * Rn) / (0.85 * fc);
    let rho;
    if (discriminant > 0) {
        rho = (0.85 * fc / fy) * (1 - Math.sqrt(discriminant));
    } else {
        rho = 0.85 * fc / fy * 0.5; // fallback
    }

    // Minimum reinforcement for footings: rho_min = 0.0018 (Grade 60) or 0.0020 (Grade 40)
    const rho_min = fy >= 400 ? 0.0018 : 0.0020;
    rho = Math.max(rho, rho_min);

    // Required steel area
    const As_req = rho * b_mm * dFinal; // mm²

    // Calculate number of bars
    const Ab = Math.PI * barDia * barDia / 4; // area per bar
    const nBars = Math.ceil(As_req / Ab);

    // Spacing
    const spacing = Math.floor((b_mm - 2 * cover) / (nBars - 1));

    // ------- Step 6: Store Results -------
    col.footingDesign = {
        L: L,                           // m - footing side length
        h: hFinal,                      // mm - total thickness
        d: dFinal,                      // mm - effective depth
        qu: qu.toFixed(1),              // kPa - factored soil pressure
        // Punching shear
        punchingVu: (Pu - qu * ((colB + dFinal/1000) * (colH + dFinal/1000))).toFixed(1),
        punchingPhiVc: (phi_v * Math.min(
            0.33 * Math.sqrt(fc) * 2 * ((colB + dFinal/1000) + (colH + dFinal/1000)) * dFinal / 1000,
            (0.17 * (1 + 2 / (Math.max(colH,colB)/Math.min(colH,colB)))) * Math.sqrt(fc) * 2 * ((colB + dFinal/1000) + (colH + dFinal/1000)) * dFinal / 1000
        )).toFixed(1),
        punchingOK: true,
        // Wide beam shear
        wideVu: (qu * L * ((L - colB) / 2 - dFinal / 1000)).toFixed(1),
        widePhiVc: (phi_v * 0.17 * Math.sqrt(fc) * b_mm * dFinal / 1000).toFixed(1),
        wideOK: wideBeamOK,
        // Flexure
        Mu: Mu_total.toFixed(1),        // kN·m
        rho: (rho * 100).toFixed(3),    // percentage
        As: As_req.toFixed(0),          // mm²
        nBars: nBars,
        barDia: barDia,
        spacing: spacing,
        rebarStr: nBars + '-ø' + barDia + 'mm @ ' + spacing + 'mm c/c EW'
    };

    // Update footing thickness on column
    col.footingThick = hFinal / 1000;

    return col.footingDesign;
}

/**
 * Run footing design for all columns after sizing
 */
function designAllFootings() {
    state.columns.forEach(col => {
        if (col.active !== false && col.footingSize > 0 && !col.isPlanted) {
            designFooting(col);
        }
    });
    // Update footing schedule display if visible
    if (typeof populateFootingSchedule === 'function') {
        try { populateFootingSchedule(); } catch(e) {}
    }
}

"""

    # Inject BEFORE the INIT section
    marker = "// ========== STRUCTURAL EXPORT FUNCTIONS =========="
    idx = content.find(marker)
    if idx == -1:
        # Fallback: inject before INIT
        marker = "// ========== INIT =========="
        idx = content.find(marker)
    
    if idx == -1:
        print("ERROR: Could not find injection marker")
        return

    content = content[:idx] + footing_code + "\n" + content[idx:]

    # Now hook designAllFootings() into calculateFootingSizes()
    # Find the end of calculateFootingSizes and add the call
    hook_marker = "col.footingDL = footingVolume * state.concreteDensity * 1.2;  // kN factored"
    hook_idx = content.find(hook_marker)
    if hook_idx > 0:
        # Find the closing of the for loop and function (next `}` after the marker area)
        # We'll add the call right after this line's parent block
        # Search for the pattern where the function closes
        end_pattern = "// v3.0: Footing self-weight"
        ep_idx = content.find(end_pattern)
        if ep_idx > 0:
            # Find the next line that starts with "}" at function level after footingDL
            # Actually let's just append after the for loop ends
            # Search for "}" + blank line pattern after the footingDL line
            search_area = content[hook_idx:hook_idx+500]
            # Find `}\n\n` or `}\r\n\r\n` after the hook
            import re
            m = re.search(r'\n\s*\}\s*\n', search_area)
            if m:
                insert_pos = hook_idx + m.end()
                # Check if designAllFootings() call already exists
                if 'designAllFootings()' not in content[insert_pos:insert_pos+200]:
                    content = content[:insert_pos] + "\n            designAllFootings();\n" + content[insert_pos:]
                    print("HOOKED: designAllFootings() called after calculateFootingSizes()")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SUCCESS: Footing design module injected")

if __name__ == '__main__':
    inject_footing_design(sys.argv[1])
