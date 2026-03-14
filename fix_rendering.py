"""
Fix two issues in the monolithic v3/index.html:
1. Add populateFootingSchedule alias for updateFootingSchedule
2. Upgrade beam/column rendering in tributary view from wireframe to scaled rectangles
"""
import re

file_path = r"d:\projects\tributary-pro-v2.0-LIVE\v3\index.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ===== FIX 1: Add populateFootingSchedule alias =====
# Insert right after the closing of updateFootingSchedule function
alias_code = "\n        // Alias for tab switching\n        const populateFootingSchedule = updateFootingSchedule;\n"
marker = "        // v3.0: Set column start floor (for planted columns)"
idx = content.find(marker)
if idx > 0 and 'const populateFootingSchedule' not in content:
    content = content[:idx] + alias_code + "\n" + content[idx:]
    print("FIX 1: Added populateFootingSchedule alias")
    changes += 1
else:
    print("FIX 1: Alias already exists or marker not found")

# ===== FIX 2: Draw columns as scaled rectangles =====
# Replace: const size = 12;
# With: actual dimensions from suggestedB/suggestedH
old_col_size = "            const x = col.x * state.scale + state.offsetX;\n                const y = col.y * state.scale + state.offsetY;\n                const size = 12;"

# Use a regex approach to find and replace the column drawing
old_col_pattern = r"(// Draw columns\s*\n\s*for \(let col of state\.columns\) \{\s*\n\s*)const x = col\.x \* state\.scale \+ state\.offsetX;\s*\n\s*const y = col\.y \* state\.scale \+ state\.offsetY;\s*\n\s*const size = 12;"

new_col_code = r"""\1const x = col.x * state.scale + state.offsetX;
                const y = col.y * state.scale + state.offsetY;
                // v3.10: Scaled column size from actual dimensions
                const colBpx = ((col.suggestedB || 250) / 1000) * state.scale;
                const colHpx = ((col.suggestedH || 250) / 1000) * state.scale;
                const size = Math.max(colBpx, 6); // min 6px for visibility"""

result = re.subn(old_col_pattern, new_col_code, content)
if result[1] > 0:
    content = result[0]
    print("FIX 2a: Column rendering uses scaled dimensions")
    changes += 1

# Now replace the fillRect that uses size/2 to use actual colBpx/colHpx
old_fillrect = "ctx.fillRect(x - size / 2, y - size / 2, size, size);"
new_fillrect = "ctx.fillRect(x - colBpx / 2, y - colHpx / 2, colBpx, colHpx);"
if old_fillrect in content:
    content = content.replace(old_fillrect, new_fillrect, 1)
    print("FIX 2b: Column fillRect uses scaled dimensions")
    changes += 1

# ===== FIX 3: Draw beams as scaled rectangles instead of lines =====
# Find the beam drawing section and replace line drawing with rect drawing
# The beam drawing starts at "ctx.lineWidth = 3;" and draws with ctx.beginPath/lineTo/stroke
# We need to replace it with fillRect using beam width

old_beam_line = """            ctx.lineWidth = 3;
            for (let beam of state.beams) {
                // v3.0 FIX: Skip custom beams - they are drawn separately below
                if (beam.isCustom) continue;

                const x1 = beam.x1 * state.scale + state.offsetX;
                const y1 = beam.y1 * state.scale + state.offsetY;
                const x2 = beam.x2 * state.scale + state.offsetX;
                const y2 = beam.y2 * state.scale + state.offsetY;"""

new_beam_line = """            // v3.10: Draw beams as scaled rectangles (actual beam width)
            for (let beam of state.beams) {
                // v3.0 FIX: Skip custom beams - they are drawn separately below
                if (beam.isCustom) continue;

                const x1 = beam.x1 * state.scale + state.offsetX;
                const y1 = beam.y1 * state.scale + state.offsetY;
                const x2 = beam.x2 * state.scale + state.offsetX;
                const y2 = beam.y2 * state.scale + state.offsetY;
                const beamBpx = ((beam.suggestedB || 250) / 1000) * state.scale; // scaled width"""

if old_beam_line in content:
    content = content.replace(old_beam_line, new_beam_line, 1)
    print("FIX 3a: Beam rendering uses scaled width")
    changes += 1

# Now find where beams are actually drawn with stroke and replace with fillRect
# The pattern: ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
old_beam_draw = """                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();
                ctx.setLineDash([]);"""

new_beam_draw = """                // v3.10: Draw as filled rectangle with actual beam width
                if (beam.direction === 'X') {
                    // Horizontal beam
                    ctx.fillRect(Math.min(x1, x2), y1 - beamBpx / 2, Math.abs(x2 - x1), beamBpx);
                } else {
                    // Vertical beam
                    ctx.fillRect(x1 - beamBpx / 2, Math.min(y1, y2), beamBpx, Math.abs(y2 - y1));
                }
                ctx.setLineDash([]);"""

if old_beam_draw in content:
    content = content.replace(old_beam_draw, new_beam_draw, 1)
    print("FIX 3b: Beam drawing uses fillRect instead of stroke")
    changes += 1

# Also need to change strokeStyle to fillStyle for beams
content = content.replace(
    """                if (isDeleted) {
                    // Draw deleted beam as red dashed
                    ctx.strokeStyle = '#ef4444';  // Red
                    ctx.setLineDash([6, 4]);
                    ctx.lineWidth = 2;
                } else if (isLocked) {
                    // v3.2: Draw locked beam with blue glow effect
                    ctx.strokeStyle = '#3b82f6';  // Blue for locked
                    ctx.setLineDash([]);
                    ctx.lineWidth = 5;  // Thicker line for locked
                } else {
                    ctx.strokeStyle = beam.direction === 'X' ? '#7c3aed' : '#10b981';
                    ctx.setLineDash([]);
                    ctx.lineWidth = 3;""",
    """                if (isDeleted) {
                    // Draw deleted beam as red dashed outline
                    ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';  // Red transparent
                    ctx.strokeStyle = '#ef4444';
                    ctx.setLineDash([6, 4]);
                } else if (isLocked) {
                    // v3.2: Locked beam - blue fill
                    ctx.fillStyle = 'rgba(59, 130, 246, 0.6)';
                    ctx.strokeStyle = '#3b82f6';
                    ctx.setLineDash([]);
                } else {
                    ctx.fillStyle = beam.direction === 'X' ? 'rgba(124, 58, 237, 0.5)' : 'rgba(16, 185, 129, 0.5)';
                    ctx.strokeStyle = beam.direction === 'X' ? '#7c3aed' : '#10b981';
                    ctx.setLineDash([]);""",
    1
)
print("FIX 3c: Beam colors use fillStyle for rectangles")
changes += 1

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nDONE: {changes} fixes applied to index.html")
