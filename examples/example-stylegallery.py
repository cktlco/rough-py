from rough import canvas, Options, RoughCanvas
from rough.core import Config
import math

# This script showcases a broad style gallery:
#
# 1) A grid of rectangles demonstrating permutations of fillStyle, hachureAngle,
#    fillWeight, and hachureGap (for patterns like hachure or cross-hatch).
#
# 2) A second grid focusing on stroke permutations over strokeWidth, roughness,
#    preserveVertices, and disableMultiStroke — applying them to a star-shaped
#    polygon. The star is closed so its outline is visible.

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 3400

# Two sections: The first half for fills, the second for strokes
FILL_SECTION_TOP = 75
STROKE_SECTION_TOP = 2500

########################################################################
# SECTION 1: Fill Patterns Gallery
########################################################################

NUM_COLS_FILL = 4
NUM_ROWS_FILL = 24
CELL_W = 200
CELL_H = 100

FILL_STYLES = ["hachure", "zigzag", "cross-hatch", "dots"]
HACHURE_ANGLES = [-45, -30, -15, 0, 15, 30, 45, 60]
FILL_WEIGHTS = [0.5, 2, 4]
HACHURE_GAPS = range(5, 25, 5)
PALETTE_DARK = ["#D32F2F", "#FBC02D", "#388E3C", "#8E44AD", "#2980B9"]

########################################################################
# SECTION 2: Stroke Patterns on a Star Polygon
########################################################################

# Now define strokeWidth, roughness, preserveVertices, disableMultiStroke permutations
STROKE_WEIGHTS = [1, 2, 3, 5, 10, 20]
STROKE_ROUGHNESS = [0.5, 1.0, 2.0, 6.0]
PRESERVE_VERTICES = [False, True]
DISABLE_MULTI_STROKE = [False]

# Arrange 36 combos in a 6×6 grid:
STAR_NUM_COLS = 6
STAR_NUM_ROWS = 12
STAR_CELL_W = 120
STAR_CELL_H = 120

########################################################################
# Misc Setup
########################################################################

default_config = Config(options=Options(strokeWidth=2, roughness=2.0, bowing=1.0))
c: RoughCanvas = canvas(CANVAS_WIDTH, CANVAS_HEIGHT, config=default_config)

########################################################################
# Fill Patterns Grid
########################################################################

# Fill intro text
label_str = "FILL OPTIONS: fill style, fill weight, hachure gap, hachure angle"
c.text(
    60,
    FILL_SECTION_TOP - 10,
    label_str,
    Options(fontSize=18, stroke="none", fill="#333"),
    embed_outline=False,
    align="left",
    valign="bottom",
)

col_count_fill = min(NUM_COLS_FILL, len(FILL_STYLES))
row_count_fill = NUM_ROWS_FILL

for row_idx in range(row_count_fill):
    for col_idx in range(col_count_fill):
        fs = FILL_STYLES[col_idx]
        ang = HACHURE_ANGLES[row_idx % len(HACHURE_ANGLES)]
        fw = FILL_WEIGHTS[row_idx % len(FILL_WEIGHTS)]
        hg = list(HACHURE_GAPS)[(row_idx + col_idx) % len(HACHURE_GAPS)]
        color = PALETTE_DARK[col_idx % len(PALETTE_DARK)]

        x = col_idx * CELL_W + 50
        y = FILL_SECTION_TOP + row_idx * CELL_H

        shape_opts = Options(
            fill=color,
            fillStyle=fs,
            hachureAngle=ang,
            fillWeight=fw,
            hachureGap=hg,
            stroke="#333333",
        )

        c.rectangle(x, y, CELL_W - 40, CELL_H - 20, shape_opts)

        # White background rect behind label text
        c.rectangle(
            x + 15, y + 28, 135, 25,
            Options(fill="white", fillStyle="solid", strokeWidth=0, roughness=0)
        )

        label_str = f"{fs} {ang}° wt={fw} gap={hg}"
        c.text(
            x + CELL_W / 2,
            y + CELL_H / 2,
            label_str,
            Options(fontSize=10, stroke="none", fill="#333"),
            embed_outline=False,
            align="center",
            valign="middle",
        )

########################################################################
# Stroke Patterns on a Star Polygon
########################################################################

def make_star(cx, cy, outer_r, inner_r, n=5):
    points = []
    angle_step = math.pi / n
    for i in range(2 * n):
        r = outer_r if i % 2 == 0 else inner_r
        angle = i * angle_step - (math.pi / 2)
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        points.append((px, py))
    return points

STAR_OUTER_R = 40
STAR_INNER_R = 18

# Build all stroke combos
all_combos = []
for sw in STROKE_WEIGHTS:
    for rv in STROKE_ROUGHNESS:
        for pv in PRESERVE_VERTICES:
            for dm in DISABLE_MULTI_STROKE:
                all_combos.append((sw, rv, pv, dm))

# Stroke intro text
label_str = "STROKE OPTIONS: stroke width, roughness, preserveVertices"
c.text(
    60,
    STROKE_SECTION_TOP + 50,
    label_str,
    Options(fontSize=18, stroke="none", fill="#333"),
    embed_outline=False,
    align="left",
    valign="bottom",
)

col_count_stroke = STAR_NUM_COLS
row_count_stroke = STAR_NUM_ROWS

for row_idx in range(row_count_stroke):
    for col_idx in range(col_count_stroke):
        idx = row_idx * STAR_NUM_COLS + col_idx
        if idx >= len(all_combos):
            break  # safety check in case we exceed combos

        sw, rv, pv, dm = all_combos[idx]

        x = col_idx * STAR_CELL_W + 50
        y = STROKE_SECTION_TOP + row_idx * STAR_CELL_H + 40

        # Generate star points
        star_pts = make_star(x + 60, y + 50, STAR_OUTER_R, STAR_INNER_R, n=5)

        star_opts = Options(
            stroke="#2C3E50",
            strokeWidth=sw,
            roughness=rv,
            fill="none",
            preserveVertices=pv,
            disableMultiStroke=dm,
        )

        c.polygon(star_pts, star_opts)

        # label to describe stroke
        label_str = f'w={sw} rough={rv}\n {"pv" if pv else ""} {"single" if dm else ""}'
        c.text(
            x + 10,
            y + STAR_CELL_H - 10,
            label_str,
            Options(fontSize=9, stroke="none", fill="#333"),
            embed_outline=False,
            align="left",
            valign="bottom",
        )

########################################################################
# Export
########################################################################

# draw white background
c.rectangle(
    30, 20, CANVAS_WIDTH, CANVAS_HEIGHT + 100,
    Options(fill="white", fillStyle="solid", stroke="none"),
    z_index=-999  # ensure it's drawn behind everything else
)

svg_data = c.as_svg(CANVAS_WIDTH, CANVAS_HEIGHT, auto_fit=True)
with open("examples/example-stylegallery.svg", "w", encoding="utf-8") as f:
    f.write(svg_data)
