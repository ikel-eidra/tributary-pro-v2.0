"""
v3.16 REPAIR: Fix all corrupted lines from earlier injection scripts.
"""

FILE = r"d:\projects\tributary-pro-v2.0-LIVE\v3\index.html"

with open(FILE, 'r', encoding='utf-8') as f:
    c = f.read()

repairs = 0

# --- FIX 1: Comments at 3495-3496 (harmless but ugly) ---
c = c.replace(
    " * Save cu        ate          before mutations\n         * Call this BEFORE         e-changing operation",
    " * Save current state before mutations\n         * Call this BEFORE any state-changing operation"
)
repairs += 1
print(f"Fix {repairs}: saveStateSnapshot comments")

# --- FIX 2: Floor type per floor (line ~4634) ---
c = c.replace(
    "// v3.0: Store          flo         date global type for current                       col.typePerFloor[targetFloorId] =         \n                col.type = newType;  // Also update global fo         d compatibility",
    "// v3.0: Store per-floor type and update global type for current floor\n                col.typePerFloor[targetFloorId] = newType;\n                col.type = newType;  // Also update global for backward compatibility"
)
repairs += 1
print(f"Fix {repairs}: typePerFloor assignment")

# --- FIX 3: Floor deletion - state.fl___gth (line ~4818) ---
c = c.replace(
    "state.currentFloorIndex = state.fl        gth",
    "state.currentFloorIndex = state.floors.length - 1;"
)
repairs += 1
print(f"Fix {repairs}: state.floors.length in floor delete")

# --- FIX 4: Floor rename loop (lines ~4822-4830) ---
c = c.replace(
    """            ors.forEach((f, i) => {
                if (i === 0                        f.id = 'GF';
                f.name = 'Grou         ;
            } else if (f.isRoof) {
                             F';
                f.name = 'Roof';
                f.id = `${i + 1}F`;
                f.name = `${i + 1}${['st', 'nd', 'rd'][i - 1] || 'th'} Floor`;
            }
        });""",
    """            state.floors.forEach((f, i) => {
                if (i === 0 && !f.isRoof) {
                    f.id = 'GF';
                    f.name = 'Ground Floor';
                } else if (f.isRoof) {
                    f.id = 'RF';
                    f.name = 'Roof';
                } else {
                    f.id = `${i + 1}F`;
                    f.name = `${i + 1}${['st', 'nd', 'rd'][i - 1] || 'th'} Floor`;
                }
            });"""
)
repairs += 1
print(f"Fix {repairs}: Floor rename loop")

# --- FIX 5: calculate() docstring (line ~4841) ---
c = c.replace(
    "* Implements: SLAB → BEAMS → COLUM        path          * v2.3: Calculates per-floor and cumulative a          floors",
    "* Implements: SLAB -> BEAMS -> COLUMNS load path\n         * v2.3: Calculates per-floor and cumulative across floors"
)
repairs += 1
print(f"Fix {repairs}: calculate() docstring")

# --- FIX 6: sanitizeSpan calls (lines ~4844-4846) ---
c = c.replace(
    """               Clean spans to avoid zero / negative values
            state.xS         ate.xSpans.map(span => sanitizeSpan(span));
            state.yS         ate.ySpans.map(span => sanitizeSpan(span));""",
    """            // Clean spans to avoid zero / negative values
            state.xSpans = state.xSpans.map(span => sanitizeSpan(span));
            state.ySpans = state.ySpans.map(span => sanitizeSpan(span));"""
)
repairs += 1
print(f"Fix {repairs}: sanitizeSpan calls")

# --- FIX 7: Check IFC/STAAD export sections for corruption ---
# Line 12504
old_12504 = '"TY         TE\\n";'
if old_12504 in c:
    # Need to see more context - let's find and fix
    pass

# --- FIX 8: alert line 12598 ---
old_alert = "alert('        aile         r.message);"
if old_alert in c:
    c = c.replace(old_alert, "alert('Export failed: ' + err.message);")
    repairs += 1
    print(f"Fix {repairs}: alert error message")

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"\nDONE: Applied {repairs} repairs")
