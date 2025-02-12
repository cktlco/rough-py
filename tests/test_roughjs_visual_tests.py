"""
A single Python test file (not a pytest test) that replicates each of the
Rough.js "visual-tests" snippets in Python.

1) Each test function corresponds to one of the HTML demos from the Rough.js repo.
2) The code draws shapes onto an in-memory rough.canvas() of the specified size.
3) Each shape uses an Options(...) object for overrides (stroke, fill, dash, etc.).
4) After drawing, it calls canvas.as_svg(...) to create an SVG version
   in the "tests/test_roughjs_visual_tests/" subdirectory, e.g. "tests/test_roughjs_visual_tests/svg_line.svg".
5) Finally, main() runs all tests and produces test_index.html listing them.

To run:
    python test_roughjs_visual_tests.py
"""

import os
import rough
from rough import RoughCanvas
from rough.core import Config, Options


def xxbuild_canvas_as_svg(rc: RoughCanvas, width, height, outname):
    """
    Exports all draw_calls in rc (which is a RoughCanvas) to a single <svg> file.
    Respects strokeLineDash / strokeLineDashOffset (for normal strokes)
    and fillLineDash / fillLineDashOffset (for 'fillSketch' strokes).
    """
    svg_lines = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    ]

    rc.auto_fit(margin=20)

    for drawable in rc.draw_calls:
        path_infos = rc.gen.toPaths(drawable)  # Convert geometry to PathInfo
        o = drawable.options  # original shape options

        for pinfo in path_infos:
            stroke_val = pinfo.stroke if pinfo.stroke else "none"
            fill_val = pinfo.fill if pinfo.fill else "none"
            swidth = pinfo.strokeWidth

            # Detect whether this path is a 'fillSketch'
            is_fillSketch = (
                pinfo.stroke != "none"
                and pinfo.stroke == (o.fill or "none")
                and pinfo.strokeWidth
                == (o.fillWeight if o.fillWeight >= 0 else o.strokeWidth * 0.5)
            )

            # Decide which dash array/offset to use
            dasharray = ""
            dashoffset = 0.0

            if is_fillSketch:
                if o.fillLineDash and len(o.fillLineDash) > 0:
                    dash_vals = " ".join(str(v) for v in o.fillLineDash)
                    dasharray = dash_vals
                dashoffset = o.fillLineDashOffset
            else:
                if o.strokeLineDash and len(o.strokeLineDash) > 0:
                    dash_vals = " ".join(str(v) for v in o.strokeLineDash)
                    dasharray = dash_vals
                dashoffset = o.strokeLineDashOffset

            path_attrs = [
                f'd="{pinfo.d}"',
                f'stroke="{stroke_val}"',
                f'stroke-width="{swidth}"',
                f'fill="{fill_val}"',
            ]
            if dasharray:
                path_attrs.append(f'stroke-dasharray="{dasharray}"')
            if dashoffset and dashoffset != 0:
                path_attrs.append(f'stroke-dashoffset="{dashoffset}"')

            svg_lines.append(f'  <path {" ".join(path_attrs)} />')

    svg_lines.append("</svg>")

    with open(outname, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
    print(f"Wrote {outname}")


##############################################################################
# SVG-Based Tests (favored over duplicates)
##############################################################################


def test_svg_line():
    # matches visual-tests/svg/line.html
    rc = rough.canvas(800, 800)
    rc.line(10, 10, 100, 10)
    rc.line(10, 210, 500, 210)
    rc.line(10, 20, 10, 110, Options(stroke="red"))
    rc.line(10, 10, 100, 10)
    rc.line(50, 30, 200, 100, Options(stroke="blue", strokeWidth=5))

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/svg_line.svg")


def test_svg_dashed_line():
    # visual-tests/svg/dashed/line.html
    rc = rough.canvas(800, 800)

    dash_opts = Options(strokeLineDash=[15, 5], strokeLineDashOffset=10)
    dash_red = Options(stroke="red", strokeLineDash=[15, 5], strokeLineDashOffset=10)
    dash_blue5 = Options(
        stroke="blue", strokeWidth=5, strokeLineDash=[15, 5], strokeLineDashOffset=10
    )

    rc.line(10, 10, 100, 10, dash_opts)
    rc.line(10, 210, 500, 210, dash_opts)
    rc.line(10, 20, 10, 110, dash_red)
    rc.line(10, 10, 100, 10, dash_opts)
    rc.line(50, 30, 200, 100, dash_blue5)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/svg_dashed_line.svg")


def test_svg_dashed_polygon():
    # visual-tests/svg/dashed/polygon.html
    rc = rough.canvas(800, 800)
    poly_opts = Options(
        stroke="black",
        strokeWidth=2,
        fill="red",
        hachureAngle=90,
        strokeLineDash=[15, 5],
        strokeLineDashOffset=10,
    )
    points = [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]]
    rc.polygon(points, poly_opts)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/svg_dashed_polygon.svg")


def test_svg_dashed_ellipse():
    # visual-tests/svg/dashed/ellipse.html
    rc = rough.canvas(800, 800)
    base_dash = Options(strokeLineDash=[15, 5], strokeLineDashOffset=10)
    red_fill = Options(fill="red", strokeLineDash=[15, 5], strokeLineDashOffset=10)
    pink_sol = Options(
        fill="pink", fillStyle="solid", strokeLineDash=[15, 5], strokeLineDashOffset=10
    )
    red_ch = Options(
        fill="red",
        fillStyle="cross-hatch",
        strokeLineDash=[15, 5],
        strokeLineDashOffset=10,
    )
    red_zz = Options(
        fill="red",
        fillStyle="zigzag",
        hachureGap=8,
        strokeLineDash=[15, 5],
        strokeLineDashOffset=10,
    )
    red_dots = Options(
        fill="red", fillStyle="dots", strokeLineDash=[15, 5], strokeLineDashOffset=10
    )

    rc.ellipse(50, 50, 80, 80, base_dash)
    rc.ellipse(150, 50, 80, 80, red_fill)
    rc.ellipse(250, 50, 80, 80, pink_sol)
    rc.ellipse(350, 50, 80, 80, red_ch)
    rc.ellipse(450, 50, 80, 80, red_zz)
    rc.ellipse(550, 50, 80, 80, red_dots)

    # circle versions
    rough2 = Options(roughness=2)
    redblue = Options(
        fill="red",
        stroke="blue",
        hachureAngle=0,
        strokeWidth=3,
        strokeLineDash=[15, 5],
        strokeLineDashOffset=10,
    )
    pinkw3 = Options(
        fill="pink",
        fillWeight=3,
        hachureGap=8,
        hachureAngle=45,
        strokeLineDash=[15, 5],
        strokeLineDashOffset=10,
    )

    rc.circle(50, 150, 80, rough2)
    rc.circle(150, 150, 80, redblue)
    rc.circle(250, 150, 80, pinkw3)

    bigdots = Options(
        fill="red", fillStyle="dots", hachureGap=20, hachureAngle=0, fillWeight=2
    )
    rc.ellipse(300, 350, 480, 280, bigdots)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/svg_dashed_ellipse.svg")


def test_svg_config_defaults():
    # unaffiliated with the base tests
    config_defaults = Options(
        fill="green", strokeLineDash=[15, 5], strokeLineDashOffset=10
    )
    rc = rough.canvas(800, 800, config=Config(config_defaults))
    red_fill = Options(fill="red", strokeLineDash=[15, 5], strokeLineDashOffset=10)
    pink_sol = Options(
        fill="pink", fillStyle="solid", strokeLineDash=[15, 5], strokeLineDashOffset=10
    )
    red_dots = Options(
        fill="red", fillStyle="dots", strokeLineDash=[15, 5], strokeLineDashOffset=10
    )
    green_zz = Options(
        fillStyle="zigzag",
        hachureGap=8,
        strokeLineDash=[15, 5],
        strokeLineDashOffset=10,
    )

    # note setting to [] instead of None to override inheritance
    purple_ch = Options(
        fill="purple",
        fillStyle="cross-hatch",
        strokeLineDash=[],
        strokeLineDashOffset=None,
    )

    rc.ellipse(50, 50, 80, 80)
    rc.ellipse(150, 50, 80, 80, red_fill)
    rc.ellipse(250, 50, 80, 80, pink_sol)
    rc.ellipse(550, 50, 80, 80, red_dots)

    # should be solid line, not dashed
    rc.ellipse(350, 50, 80, 80, purple_ch)

    # should be green from inherited canvas config
    rc.ellipse(450, 50, 80, 80, green_zz)
    rc.ellipse(50, 250, 80, 80, Options(fillStyle="solid"))

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/svg_config_defaults.svg")


def test_svg_dashed_rectangle():
    # visual-tests/svg/dashed/rectangle.html
    rc = rough.canvas(800, 800)
    dash = Options(strokeLineDash=[15, 5], strokeLineDashOffset=10)
    red_fill = Options(fill="red", strokeLineDash=[15, 5], strokeLineDashOffset=10)
    pink_sol = Options(
        fill="pink", fillStyle="solid", strokeLineDash=[15, 5], strokeLineDashOffset=10
    )
    ch_fill = Options(
        fill="red",
        fillStyle="cross-hatch",
        strokeLineDash=[15, 5],
        strokeLineDashOffset=10,
    )
    zz_fill = Options(
        fill="red",
        fillStyle="zigzag",
        hachureGap=8,
        strokeLineDash=[15, 5],
        strokeLineDashOffset=10,
    )
    dots_fill = Options(
        fill="red", fillStyle="dots", strokeLineDash=[15, 5], strokeLineDashOffset=10
    )

    rc.rectangle(10, 10, 80, 80, dash)
    rc.rectangle(110, 10, 80, 80, red_fill)
    rc.rectangle(210, 10, 80, 80, pink_sol)
    rc.rectangle(310, 10, 80, 80, ch_fill)
    rc.rectangle(410, 10, 80, 80, zz_fill)
    rc.rectangle(510, 10, 80, 80, dots_fill)

    # second row
    row2a = Options(roughness=2, strokeLineDash=[15, 5], strokeLineDashOffset=10)
    row2b = Options(
        fill="red",
        stroke="blue",
        hachureAngle=0,
        strokeWidth=3,
        strokeLineDash=[15, 5],
        strokeLineDashOffset=10,
    )
    row2c = Options(
        fill="pink",
        fillWeight=5,
        hachureGap=10,
        hachureAngle=90,
        strokeLineDash=[15, 5],
        strokeLineDashOffset=10,
    )

    rc.rectangle(10, 110, 80, 80, row2a)
    rc.rectangle(110, 110, 80, 80, row2b)
    rc.rectangle(210, 110, 80, 80, row2c)

    bigdots = Options(fill="red", fillStyle="dots", hachureGap=20, fillWeight=2)
    rc.rectangle(10, 210, 480, 280, bigdots)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/svg_dashed_rectangle.svg")


def test_svg_polygon():
    # visual-tests/svg/polygon.html
    rc = rough.canvas(800, 800)
    opts = Options(
        fillStyle="solid", stroke="black", strokeWidth=2, fill="red", hachureAngle=90
    )
    pts = [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]]
    rc.polygon(pts, opts)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/svg_polygon.svg")


def test_svg_rectangle2():
    # visual-tests/svg/rectangle2.html
    rc = rough.canvas(800, 800)
    r2 = Options(fill="red", hachureGap=1.7)
    rc.rectangle(10, 10, 280, 280, r2)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/svg_rectangle2.svg")


def test_svg_ellipse():
    # visual-tests/svg/ellipse.html
    rc = rough.canvas(800, 800)

    rc.ellipse(50, 50, 80, 80)
    rc.ellipse(150, 50, 80, 80, Options(fill="red"))
    rc.ellipse(250, 50, 80, 80, Options(fill="pink", fillStyle="solid"))
    rc.ellipse(350, 50, 80, 80, Options(fill="red", fillStyle="cross-hatch"))
    rc.ellipse(450, 50, 80, 80, Options(fill="red", fillStyle="zigzag", hachureGap=8))
    rc.ellipse(550, 50, 80, 80, Options(fill="red", fillStyle="dots"))

    rc.circle(50, 150, 80, Options(roughness=2))
    rc.circle(
        150, 150, 80, Options(fill="red", stroke="blue", hachureAngle=0, strokeWidth=3)
    )
    rc.circle(
        250, 150, 80, Options(fill="pink", fillWeight=3, hachureGap=8, hachureAngle=45)
    )

    bigdots = Options(
        fill="red", fillStyle="dots", hachureGap=20, hachureAngle=0, fillWeight=2
    )
    rc.ellipse(300, 350, 480, 280, bigdots)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/svg_ellipse.svg")


def test_svg_rectangle():
    # visual-tests/svg/rectangle.html
    rc = rough.canvas(800, 800)
    rc.rectangle(10, 10, 80, 80)
    rc.rectangle(110, 10, 80, 80, Options(fill="red"))
    rc.rectangle(210, 10, 80, 80, Options(fill="pink", fillStyle="solid"))
    rc.rectangle(310, 10, 80, 80, Options(fill="red", fillStyle="cross-hatch"))
    rc.rectangle(410, 10, 80, 80, Options(fill="red", fillStyle="zigzag", hachureGap=8))
    rc.rectangle(510, 10, 80, 80, Options(fill="red", fillStyle="dots"))

    rc.rectangle(10, 110, 80, 80, Options(roughness=2))
    rc.rectangle(
        110,
        110,
        80,
        80,
        Options(fill="red", stroke="blue", hachureAngle=0, strokeWidth=3),
    )
    rc.rectangle(
        210,
        110,
        80,
        80,
        Options(fill="pink", fillWeight=5, hachureGap=10, hachureAngle=90),
    )

    bigdots = Options(fill="red", fillStyle="dots", hachureGap=20, fillWeight=2)
    rc.rectangle(10, 210, 480, 280, bigdots)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/svg_rectangle.svg")


##############################################################################
# Unique Canvas Tests (no SVG duplicates)
##############################################################################


def test_canvas_curve_seed():
    rc = rough.canvas(800, 800)
    seed = 232
    roughness = 1.5

    rc.curve(
        [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]],
        Options(roughness=roughness, seed=seed),
    )
    rc.ctx.translate(0, 210)
    rc.curve(
        [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100]],
        Options(roughness=roughness, seed=seed),
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_curve_seed.svg")


def test_canvas_path7():
    rc = rough.canvas(800, 800)
    path = (
        "M 32 0 L 153.96380615234375 0 Q 185.96380615234375 0, 185.96380615234375 32 "
        "L 185.96380615234375 157.74319458007812 Q 185.96380615234375 189.74319458007812, "
        "153.96380615234375 189.74319458007812 L 32 189.74319458007812 Q 0 189.74319458007812, "
        "0 157.74319458007812 L 0 32 Q 0 0, 32 0"
    )
    ops = Options(
        preserveVertices=True,
        fill="red",
        fillStyle="hachure",
        hachureGap=6,
        roughness=1,
    )

    rc.ctx.translate(0, 50)
    rc.path(path, ops)
    rc.ctx.translate(200, 0)
    rc.path(path, ops)
    rc.ctx.translate(200, 0)
    rc.path(path, ops)
    rc.ctx.translate(200, 0)
    rc.path(path, ops)

    rc.ctx.resetTransform()
    rc.ctx.translate(0, 250)
    rc.path(path, ops)
    rc.ctx.translate(200, 0)
    rc.path(path, ops)
    rc.ctx.translate(200, 0)
    rc.path(path, ops)
    rc.ctx.translate(200, 0)
    rc.path(path, ops)

    rc.ctx.resetTransform()
    rc.ctx.translate(0, 450)
    rc.path(path, ops)
    rc.ctx.translate(200, 0)
    rc.path(path, ops)
    rc.ctx.translate(200, 0)
    rc.path(path, ops)
    rc.ctx.translate(200, 0)
    rc.path(path, ops)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_path7.svg")


def test_canvas_path4():
    rc = rough.canvas(1000, 1000)

    # Simple "rings" shape example
    def rings(xpos):
        return [
            [[100, 300], [800, 300], [800, 0], [100, 0]],
            [[200, 250], [200, 50], [600, 50], [600, 250]],
            [[400, 200], [550, 200], [550, 100], [400, 100]],
            [[xpos + 25, 175], [xpos + 25, 125], [xpos + 75, 125], [xpos + 75, 175]],
        ]

    xPos = 100
    path_segs = []
    for poly in rings(xPos):
        seg = "M" + "L".join(f"{p[0]} {p[1]}" for p in poly) + "Z"
        path_segs.append(seg)
    path_segs.append("M 650, 150 a 50,50 0 1,0 100,0 a 50,50 0 1,0 -100,0")
    final_path = " ".join(path_segs)
    rc.path(final_path, Options(seed=2142156371, fill="orange", fillWeight=2))

    rc.as_svg(1000, 1000, "tests/test_roughjs_visual_tests/canvas_path4.svg")


def test_canvas_arc():
    rc = rough.canvas(800, 800)
    rc.arc(350, 200, 200, 180, 3.14159, 3.14159 * 1.6)
    rc.arc(350, 300, 200, 180, 3.14159, 3.14159 * 1.6, True)
    rc.arc(
        350,
        300,
        200,
        180,
        0,
        3.14159 / 2,
        True,
        Options(
            stroke="red", strokeWidth=4, fill="rgba(255,255,0,0.4)", fillStyle="solid"
        ),
    )
    rc.arc(
        350,
        300,
        200,
        180,
        3.14159 / 2,
        3.14159,
        True,
        Options(stroke="blue", strokeWidth=2, fill="rgba(255,0,255,0.4)"),
    )

    rc.ctx.translate(-210, 0)
    rc.arc(
        350,
        300,
        200,
        180,
        3.14159,
        3.14159 * 1.6,
        True,
        Options(fill="red", fillStyle="zigzag", hachureGap=10),
    )
    rc.arc(
        350,
        300,
        200,
        180,
        0,
        3.14159 / 2,
        True,
        Options(stroke="red", strokeWidth=4, fill="orange", fillStyle="dots"),
    )
    rc.arc(
        350,
        300,
        200,
        180,
        3.14159 / 2,
        3.14159,
        True,
        Options(stroke="blue", strokeWidth=2, fill="red", fillStyle="cross-hatch"),
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_arc.svg")


def test_canvas_path_with_transform():
    rc = rough.canvas(800, 800)
    rc.ctx.translate(150, 150)
    rc.ctx.scale(1, -1)
    rc.path("M-100, 0L0 100L100 100Z", Options(fill="red"))

    rc.as_svg(
        800, 800, "tests/test_roughjs_visual_tests/canvas_path_with_transform.svg"
    )


def test_canvas_ellipse2():
    rc = rough.canvas(800, 800)
    rc.ellipse(300, 350, 380, 280, Options(roughness=2))
    rc.ellipse(200, 150, 380, 280, Options(roughness=1))
    rc.ellipse(400, 150, 380, 280, Options(roughness=0, fill="red", hachureGap=10))
    rc.ellipse(400, 150, 100.65800865800863, 17.70129870129859, Options(roughness=0))
    rc.ellipse(200, 150, 100, 17, Options(roughness=0, fill="red"))
    rc.ellipse(200, 50, 100, 17, Options(roughness=0, fill="pink", fillStyle="solid"))

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_ellipse2.svg")


def test_canvas_linearpath():
    rc = rough.canvas(800, 800)
    pts = [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]]
    rc.linearPath(pts, Options(stroke="orange", strokeWidth=4))

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_linearpath.svg")


def test_canvas_path3():
    rc = rough.canvas(800, 800)
    roughness = 2
    path_data = (
        "M 37.1484375 0 L 112.11328125 0 Q 149.26171875 0, 149.26171875 37.1484375 "
        "L 149.26171875 111.4453125 Q 149.26171875 148.59375, 112.11328125 148.59375 "
        "L 37.1484375 148.59375 Q 0 148.59375, 0 111.4453125 L 0 37.1484375 "
        "Q 0 0, 37.1484375 0"
    )
    shape = rc.path(
        path_data,
        Options(
            disableMultiStroke=False,
            fill=None,
            fillStyle="hachure",
            fillWeight=0.5,
            hachureGap=4,
            roughness=roughness,
            seed=2142156371,
            stroke="#000000",
            strokeWidth=1,
        ),
    )
    print(shape)

    rc.ctx.translate(250, 0)
    rc.path(
        path_data,
        Options(
            disableMultiStroke=False,
            fill=None,
            fillStyle="hachure",
            fillWeight=0.5,
            hachureGap=4,
            roughness=roughness,
            seed=2142156371,
            stroke="#000000",
            strokeWidth=1,
            preserveVertices=True,
        ),
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_path3.svg")


def test_canvas_curve4():
    rc = rough.canvas(800, 800)
    ctx = rc.ctx
    ops = Options(roughness=1, fill="red")

    ctx.translate(20, 20)
    rc.curve(
        [
            [
                [0, 0],
                [107.03890991210938, 324.7185974121094],
                [297.3592224121094, 186.47903442382812],
                [356.3987731933594, -5.518890380859375],
                [490.5584411621094, 216.71908569335938],
            ],
            [
                [490.5584411621094, 216.71908569335938],
                [645.1175231933594, 47.040374755859375],
            ],
        ],
        ops,
    )

    ctx.translate(0, 210)
    # Additional transforms if needed, but we’ll just leave the example
    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_curve4.svg")


def test_canvas_polygon2():
    rc = rough.canvas(800, 800)
    pts = [[10, 300], [150, 200], [310, 300], [200, 50], [100, 50]]
    rc.polygon(
        pts, Options(fill="red", fillStyle="zigzag", hachureGap=20, hachureAngle=85)
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_polygon2.svg")


def test_canvas_dashed_arc():
    rc = rough.canvas(800, 800)
    base = Options(stroke="red", strokeLineDash=[15, 5], strokeLineDashOffset=10)
    rc.arc(350, 200, 200, 180, 3.14159, 3.14159 * 1.6, options=base)
    rc.arc(350, 300, 200, 180, 3.14159, 3.14159 * 1.6, True, base)
    rc.arc(
        350,
        300,
        200,
        180,
        0,
        3.14159 / 2,
        True,
        Options(
            stroke="red",
            strokeWidth=4,
            fill="rgba(255,255,0,0.4)",
            fillStyle="solid",
            strokeLineDash=[15, 5],
            strokeLineDashOffset=10,
        ),
    )
    rc.arc(
        350,
        300,
        200,
        180,
        3.14159 / 2,
        3.14159,
        True,
        Options(
            stroke="blue",
            strokeWidth=2,
            fill="rgba(255,0,255,0.4)",
            fillLineDash=[15, 5],
            fillLineDashOffset=10,
        ),
    )

    rc.ctx.translate(-210, 0)
    rc.arc(
        350,
        300,
        200,
        180,
        3.14159,
        3.14159 * 1.6,
        True,
        Options(fill="red", fillStyle="zigzag", hachureGap=10),
    )
    rc.arc(
        350,
        300,
        200,
        180,
        0,
        3.14159 / 2,
        True,
        Options(stroke="red", strokeWidth=4, fill="orange", fillStyle="dots"),
    )
    rc.arc(
        350,
        300,
        200,
        180,
        3.14159 / 2,
        3.14159,
        True,
        Options(stroke="blue", strokeWidth=2, fill="red", fillStyle="cross-hatch"),
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_dashed_arc.svg")


def test_canvas_dashed_path_with_transform():
    rc = rough.canvas(800, 800)
    ctx = rc.ctx
    ctx.translate(150, 150)
    ctx.scale(1, -1)
    dash = Options(fill="red", strokeLineDash=[15, 5], strokeLineDashOffset=10)
    rc.path("M-100, 0L0 100L100 100Z", dash)

    rc.as_svg(
        800,
        800,
        "tests/test_roughjs_visual_tests/canvas_dashed_path_with_transform.svg",
    )


def test_canvas_dashed_linearpath():
    rc = rough.canvas(800, 800)
    rp = Options(
        stroke="orange", strokeWidth=4, strokeLineDash=[15, 5], strokeLineDashOffset=10
    )
    pts = [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]]
    rc.linearPath(pts, rp)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_dashed_linearpath.svg")


def test_canvas_dashed_curve():
    rc = rough.canvas(800, 800)
    base_opts = Options(stroke="red", strokeLineDash=[15, 5], strokeLineDashOffset=10)
    shape1 = Options(
        stroke="black",
        strokeWidth=2,
        fill="red",
        hachureAngle=90,
        fillLineDash=[15, 5],
        fillLineDashOffset=10,
        strokeLineDash=[15, 5],
        strokeLineDashOffset=10,
    )
    pts = [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]]
    rc.curve(pts, shape1)

    rc.ctx.translate(0, 210)
    rc.curve(pts, Options(fill="red", fillStyle="solid"))
    rc.ctx.translate(0, 210)
    rc.curve(pts, Options(fill="red", fillStyle="dots", hachureGap=16, fillWeight=2))
    rc.ctx.translate(300, 0)
    rc.curve(pts, Options(fill="red", fillStyle="cross-hatch", hachureGap=8))
    rc.ctx.translate(0, -210)
    rc.curve(pts, Options(fill="red", fillStyle="zigzag", hachureGap=8))
    rc.ctx.translate(0, -210)
    rc.curve(pts, Options(stroke="orange", strokeWidth=5))

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_dashed_curve.svg")


def test_canvas_dashed_path():
    rc = rough.canvas(800, 800)
    base = Options(simplification=None, strokeLineDash=[15, 5], strokeLineDashOffset=10)

    rc.path(
        "M400 100 h 90 v 90 h -90z",
        Options(
            stroke="red",
            strokeWidth=3,
            fill="rgba(0,0,255,0.2)",
            fillStyle="solid",
            strokeLineDash=[15, 5],
            strokeLineDashOffset=10,
        ),
    )
    rc.path(
        "M400 250 h 90 v 90 h -90z",
        Options(
            fill="rgba(0,0,255,0.6)", strokeLineDash=[15, 5], strokeLineDashOffset=10
        ),
    )
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(
            stroke="red",
            strokeWidth=1,
            fill="blue",
            strokeLineDash=[15, 5],
            strokeLineDashOffset=10,
        ),
    )
    rc.path(
        "M80 80 A 45 45, 0, 0, 0, 125 125 L 125 80 Z",
        Options(fill="green", strokeLineDash=[15, 5], strokeLineDashOffset=10),
    )
    rc.path(
        "M230 80 A 45 45, 0, 1, 0, 275 125 L 275 80 Z",
        Options(
            fill="purple",
            hachureAngle=60,
            hachureGap=5,
            fillLineDash=[15, 5],
            fillLineDashOffset=10,
            strokeLineDash=[15, 5],
            strokeLineDashOffset=10,
        ),
    )
    rc.path(
        "M80 230 A 45 45, 0, 0, 1, 125 275 L 125 230 Z",
        Options(fill="red", strokeLineDash=[15, 5], strokeLineDashOffset=10),
    )
    rc.path(
        "M230 230 A 45 45, 0, 1, 1, 275 275 L 275 230 Z",
        Options(fill="blue", strokeLineDash=[15, 5], strokeLineDashOffset=10),
    )

    rc.ctx.translate(0, 70)
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(
            fill="blue",
            fillStyle="dots",
            strokeLineDash=[15, 5],
            strokeLineDashOffset=10,
        ),
    )
    rc.ctx.translate(0, 70)
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(
            fill="blue",
            fillStyle="cross-hatch",
            strokeLineDash=[15, 5],
            strokeLineDashOffset=10,
        ),
    )
    rc.ctx.translate(0, 70)
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(
            fill="blue",
            fillStyle="solid",
            strokeLineDash=[15, 5],
            strokeLineDashOffset=10,
        ),
    )
    rc.ctx.translate(0, 70)
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(
            fill="blue",
            fillStyle="zigzag",
            strokeLineDash=[15, 5],
            strokeLineDashOffset=10,
        ),
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_dashed_path.svg")


def test_canvas_poly_seed():
    rc = rough.canvas(800, 800)
    seed = 232
    roughness = 1.5
    rc.linearPath(
        [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]],
        Options(roughness=roughness, seed=seed),
    )
    rc.ctx.translate(0, 210)
    rc.linearPath(
        [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100]],
        Options(roughness=roughness, seed=seed),
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_poly_seed.svg")


def test_canvas_ellipse3():
    rc = rough.canvas(800, 800)
    ops = Options(fill="red", fillStyle="solid", roughness=2, stroke="none")

    # 6 small circles/ellipses
    rc.ellipse(50, 50, 80, 80, ops)
    rc.ellipse(150, 50, 80, 80, ops)
    rc.ellipse(250, 50, 80, 80, ops)
    rc.ellipse(350, 50, 80, 80, ops)
    rc.ellipse(450, 50, 80, 80, ops)
    rc.ellipse(550, 50, 80, 80, ops)

    rc.circle(50, 150, 80, ops)
    rc.circle(150, 150, 80, ops)
    rc.circle(250, 150, 80, ops)

    rc.ellipse(300, 350, 480, 280, ops)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_ellipse3.svg")


def test_canvas_curve():
    rc = rough.canvas(800, 800)
    pts = [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]]
    rc.curve(pts, Options(stroke="black", strokeWidth=2, fill="red", hachureAngle=90))
    rc.ctx.translate(0, 210)
    rc.curve(pts, Options(fill="red", fillStyle="solid"))
    rc.ctx.translate(0, 210)
    rc.curve(pts, Options(fill="red", fillStyle="dots", hachureGap=16, fillWeight=2))
    rc.ctx.translate(300, 0)
    rc.curve(pts, Options(fill="red", fillStyle="cross-hatch", hachureGap=8))
    rc.ctx.translate(0, -210)
    rc.curve(pts, Options(fill="red", fillStyle="zigzag", hachureGap=8))
    rc.ctx.translate(0, -210)
    rc.curve(pts, Options(stroke="orange", strokeWidth=5))

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_curve.svg")


def test_canvas_path6():
    rc = rough.canvas(800, 800)
    roughness = 2
    path = (
        "M 32 0 L 153.96380615234375 0 Q 185.96380615234375 0, 185.96380615234375 32 "
        "L 185.96380615234375 157.74319458007812 Q 185.96380615234375 189.74319458007812, "
        "153.96380615234375 189.74319458007812 L 32 189.74319458007812 "
        "Q 0 189.74319458007812, 0 157.74319458007812 L 0 32 Q 0 0, 32 0"
    )

    rc.ctx.translate(0, 50)
    rc.path(path, Options(roughness=roughness, seed=2142156371, preserveVertices=True))
    rc.ctx.translate(200, 0)
    rc.path(
        path,
        Options(
            roughness=roughness,
            seed=2142156371,
            preserveVertices=True,
            fill="red",
            hachureGap=15,
        ),
    )
    rc.ctx.translate(200, 0)
    rc.path(
        path,
        Options(
            roughness=roughness,
            seed=2142156371,
            preserveVertices=True,
            fill="purple",
            fillStyle="solid",
        ),
    )
    rc.ctx.translate(200, 0)
    rc.path(
        path,
        Options(
            roughness=roughness,
            seed=2142156371,
            preserveVertices=True,
            fill="purple",
            fillStyle="solid",
            stroke="none",
        ),
    )

    rc.ctx.resetTransform()
    rc.ctx.translate(0, 250)
    rc.ellipse(110, 150, 180, 180, Options(roughness=roughness, seed=2142156371))
    rc.ctx.translate(200, 0)
    rc.ellipse(
        110,
        150,
        180,
        180,
        Options(roughness=roughness, seed=2142156371, fill="red", hachureGap=15),
    )
    rc.ctx.translate(200, 0)
    rc.ellipse(
        110,
        150,
        180,
        180,
        Options(roughness=roughness, seed=2142156371, fill="red", fillStyle="solid"),
    )
    rc.ctx.translate(200, 0)
    rc.ellipse(
        110,
        150,
        180,
        180,
        Options(
            roughness=roughness,
            seed=2142156371,
            fill="red",
            fillStyle="solid",
            stroke="none",
        ),
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_path6.svg")


##############################################################################
# Single-stroke
##############################################################################


def test_canvas_singlestroke_line():
    rc = rough.canvas(800, 800)
    single_opts = Options(disableMultiStroke=True)
    rc.line(10, 10, 100, 10, single_opts)
    rc.line(10, 210, 500, 210, single_opts)
    rc.line(10, 20, 10, 110, Options(stroke="red", disableMultiStroke=True))
    rc.line(
        50, 30, 200, 100, Options(stroke="blue", strokeWidth=5, disableMultiStroke=True)
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_singlestroke_line.svg")


def test_canvas_singlestroke_arc():
    rc = rough.canvas(800, 800)
    base = Options(stroke="red", disableMultiStroke=True, disableMultiStrokeFill=True)
    rc.arc(350, 200, 200, 180, 3.14159, 3.14159 * 1.6, options=base)
    rc.arc(350, 300, 200, 180, 3.14159, 3.14159 * 1.6, True, base)
    rc.arc(
        350,
        300,
        200,
        180,
        0,
        3.14159 / 2,
        True,
        Options(
            stroke="red",
            strokeWidth=4,
            fill="rgba(255,255,0,0.4)",
            fillStyle="solid",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.arc(
        350,
        300,
        200,
        180,
        3.14159 / 2,
        3.14159,
        True,
        Options(
            stroke="blue",
            strokeWidth=2,
            fill="rgba(255,0,255,0.4)",
            fillLineDash=[15, 5],
            fillLineDashOffset=10,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.ctx.translate(-210, 0)
    rc.arc(
        350,
        300,
        200,
        180,
        3.14159,
        3.14159 * 1.6,
        True,
        Options(
            fill="red",
            fillStyle="zigzag",
            hachureGap=10,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.arc(
        350,
        300,
        200,
        180,
        0,
        3.14159 / 2,
        True,
        Options(
            stroke="red",
            strokeWidth=4,
            fill="orange",
            fillStyle="dots",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.arc(
        350,
        300,
        200,
        180,
        3.14159 / 2,
        3.14159,
        True,
        Options(
            stroke="blue",
            strokeWidth=2,
            fill="red",
            fillStyle="cross-hatch",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_singlestroke_arc.svg")


def test_canvas_singlestroke_polygon():
    rc = rough.canvas(800, 800)
    pts = [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]]
    rc.polygon(
        pts,
        Options(
            stroke="black",
            strokeWidth=2,
            fill="red",
            hachureAngle=90,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.ctx.translate(0, 210)
    rc.polygon(
        pts,
        Options(
            fill="red",
            fillStyle="solid",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.ctx.translate(0, 210)
    rc.polygon(
        pts,
        Options(
            fill="red",
            fillStyle="dots",
            hachureGap=16,
            fillWeight=2,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.ctx.translate(300, 0)
    rc.polygon(
        pts,
        Options(
            fill="red",
            fillStyle="cross-hatch",
            hachureGap=8,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.ctx.translate(0, -210)
    rc.polygon(
        pts,
        Options(
            fill="red",
            fillStyle="zigzag",
            hachureGap=8,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.ctx.translate(0, -210)
    rc.polygon(
        pts,
        Options(
            stroke="orange",
            strokeWidth=5,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.as_svg(
        800, 800, "tests/test_roughjs_visual_tests/canvas_singlestroke_polygon.svg"
    )


def test_canvas_singlestroke_curve():
    rc = rough.canvas(800, 800)
    pts = [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]]
    first = Options(
        stroke="black",
        strokeWidth=2,
        fill="red",
        hachureAngle=90,
        fillLineDash=[15, 5],
        fillLineDashOffset=10,
        disableMultiStroke=True,
        disableMultiStrokeFill=True,
    )
    rc.curve(pts, first)
    rc.ctx.translate(0, 210)
    rc.curve(
        pts,
        Options(
            fill="red",
            fillStyle="solid",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.ctx.translate(0, 210)
    rc.curve(
        pts,
        Options(
            fill="red",
            fillStyle="dots",
            hachureGap=16,
            fillWeight=2,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.ctx.translate(300, 0)
    rc.curve(
        pts,
        Options(
            fill="red",
            fillStyle="cross-hatch",
            hachureGap=8,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.ctx.translate(0, -210)
    rc.curve(
        pts,
        Options(
            fill="red",
            fillStyle="zigzag",
            hachureGap=8,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.ctx.translate(0, -210)
    rc.curve(
        pts,
        Options(
            stroke="orange",
            strokeWidth=5,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_singlestroke_curve.svg")


def test_canvas_singlestroke_ellipse():
    rc = rough.canvas(800, 800)
    base = Options(stroke="red", disableMultiStroke=True, disableMultiStrokeFill=True)
    rc.ellipse(50, 50, 80, 80, base)
    rc.ellipse(
        150,
        50,
        80,
        80,
        Options(fill="red", disableMultiStroke=True, disableMultiStrokeFill=True),
    )
    rc.ellipse(
        250,
        50,
        80,
        80,
        Options(
            fill="pink",
            fillStyle="solid",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.ellipse(
        350,
        50,
        80,
        80,
        Options(
            fill="red",
            fillStyle="cross-hatch",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.ellipse(
        450,
        50,
        80,
        80,
        Options(
            fill="red",
            fillStyle="zigzag",
            hachureGap=8,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.ellipse(
        550,
        50,
        80,
        80,
        Options(
            fill="red",
            fillStyle="dots",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.circle(
        50,
        150,
        80,
        Options(roughness=2, disableMultiStroke=True, disableMultiStrokeFill=True),
    )
    rc.circle(
        150,
        150,
        80,
        Options(
            fill="red",
            stroke="blue",
            hachureAngle=0,
            strokeWidth=3,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.circle(
        250,
        150,
        80,
        Options(
            fill="pink",
            fillWeight=3,
            hachureGap=8,
            hachureAngle=45,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.ellipse(
        300,
        350,
        480,
        280,
        Options(
            fill="red",
            fillStyle="dots",
            hachureGap=20,
            hachureAngle=0,
            fillWeight=2,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.as_svg(
        800, 800, "tests/test_roughjs_visual_tests/canvas_singlestroke_ellipse.svg"
    )


def test_canvas_singlestroke_path():
    rc = rough.canvas(800, 800)
    rc.path(
        "M400 100 h 90 v 90 h -90z",
        Options(
            stroke="red",
            strokeWidth=3,
            fill="rgba(0,0,255,0.2)",
            fillStyle="solid",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.path(
        "M400 250 h 90 v 90 h -90z",
        Options(
            fill="rgba(0,0,255,0.6)",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(
            stroke="red",
            strokeWidth=1,
            fill="blue",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.path(
        "M80 80 A 45 45, 0, 0, 0, 125 125 L 125 80 Z",
        Options(fill="green", disableMultiStroke=True, disableMultiStrokeFill=True),
    )
    rc.path(
        "M230 80 A 45 45, 0, 1, 0, 275 125 L 275 80 Z",
        Options(
            fill="purple",
            hachureAngle=60,
            hachureGap=5,
            fillLineDash=[15, 5],
            fillLineDashOffset=10,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.path(
        "M80 230 A 45 45, 0, 0, 1, 125 275 L 125 230 Z",
        Options(fill="red", disableMultiStroke=True, disableMultiStrokeFill=True),
    )
    rc.path(
        "M230 230 A 45 45, 0, 1, 1, 275 275 L 275 230 Z",
        Options(fill="blue", disableMultiStroke=True, disableMultiStrokeFill=True),
    )

    rc.ctx.translate(0, 70)
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(
            fill="blue",
            fillStyle="dots",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.ctx.translate(0, 70)
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(
            fill="blue",
            fillStyle="cross-hatch",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.ctx.translate(0, 70)
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(
            fill="blue",
            fillStyle="solid",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.ctx.translate(0, 70)
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(
            fill="blue",
            fillStyle="zigzag",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_singlestroke_path.svg")


def test_canvas_singlestroke_rectangle():
    rc = rough.canvas(800, 800)
    base = Options(disableMultiStroke=True, disableMultiStrokeFill=True)
    rc.rectangle(10, 10, 80, 80, base)
    rc.rectangle(
        110,
        10,
        80,
        80,
        Options(fill="red", disableMultiStroke=True, disableMultiStrokeFill=True),
    )
    rc.rectangle(
        210,
        10,
        80,
        80,
        Options(
            fill="pink",
            fillStyle="solid",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.rectangle(
        310,
        10,
        80,
        80,
        Options(
            fill="red",
            fillStyle="cross-hatch",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.rectangle(
        410,
        10,
        80,
        80,
        Options(
            fill="red",
            fillStyle="zigzag",
            hachureGap=8,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.rectangle(
        510,
        10,
        80,
        80,
        Options(
            fill="red",
            fillStyle="dots",
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    rc.rectangle(
        10,
        110,
        80,
        80,
        Options(roughness=2, disableMultiStroke=True, disableMultiStrokeFill=True),
    )
    rc.rectangle(
        110,
        110,
        80,
        80,
        Options(
            fill="red",
            stroke="blue",
            hachureAngle=0,
            strokeWidth=3,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )
    rc.rectangle(
        210,
        110,
        80,
        80,
        Options(
            fill="pink",
            fillWeight=5,
            hachureGap=10,
            hachureAngle=90,
            disableMultiStroke=True,
            disableMultiStrokeFill=True,
        ),
    )

    bigdots = Options(
        fill="red",
        fillStyle="dots",
        hachureGap=20,
        fillWeight=2,
        disableMultiStroke=True,
        disableMultiStrokeFill=True,
    )
    rc.rectangle(10, 210, 480, 280, bigdots)

    rc.as_svg(
        800, 800, "tests/test_roughjs_visual_tests/canvas_singlestroke_rectangle.svg"
    )


##############################################################################
# More curves, paths, etc. (unique to canvas)
##############################################################################


def test_canvas_curve2():
    rc = rough.canvas(800, 800)
    ctx = rc.ctx
    pts = [[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]]
    rc.curve(pts, Options(stroke="black", strokeWidth=2, fill="red", hachureGap=10))
    ctx.translate(0, 210)
    rc.curve(pts, Options(fill="red", fillStyle="solid", roughness=3))
    ctx.translate(0, 210)
    rc.curve(pts, Options(fill="red", fillStyle="cross-hatch", hachureGap=8))
    ctx.translate(300, 0)
    ctx.translate(0, -210)
    rc.curve(pts, Options(fill="red", fillStyle="solid", stroke="none", roughness=3))
    ctx.translate(0, -210)
    rc.curve(pts, Options(strokeWidth=2, fill="red", hachureGap=10, stroke="none"))

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_curve2.svg")


def test_canvas_curve3():
    rc = rough.canvas(800, 800)
    ctx = rc.ctx
    ops = Options(fill="red", fillStyle="solid", roughness=1)

    rc.curve([[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]], ops)
    ctx.translate(0, 210)
    rc.curve([[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]], ops)
    ctx.translate(0, 210)
    rc.curve([[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]], ops)
    ctx.translate(300, 0)
    ctx.translate(0, -210)
    rc.curve([[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]], ops)
    ctx.translate(0, -210)
    rc.curve([[10, 10], [200, 10], [100, 100], [100, 50], [300, 100], [60, 200]], ops)

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_curve3.svg")


def test_canvas_path():
    rc = rough.canvas(800, 800)
    rc.path(
        "M400 100 h 90 v 90 h -90z",
        Options(
            stroke="red", strokeWidth=3, fill="rgba(0,0,255,0.2)", fillStyle="solid"
        ),
    )
    rc.path("M400 250 h 90 v 90 h -90z", Options(fill="rgba(0,0,255,0.6)"))
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(stroke="red", strokeWidth=1, fill="blue"),
    )
    rc.path("M80 80 A 45 45, 0, 0, 0, 125 125 L 125 80 Z", Options(fill="green"))
    rc.path(
        "M230 80 A 45 45, 0, 1, 0, 275 125 L 275 80 Z",
        Options(fill="purple", hachureAngle=60, hachureGap=5),
    )
    rc.path("M80 230 A 45 45, 0, 0, 1, 125 275 L 125 230 Z", Options(fill="red"))
    rc.path("M230 230 A 45 45, 0, 1, 1, 275 275 L 275 230 Z", Options(fill="blue"))

    rc.ctx.translate(0, 70)
    rc.path("M37,17v15H14V17z M50,5H5v50h45z", Options(fill="blue", fillStyle="dots"))
    rc.ctx.translate(0, 70)
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z", Options(fill="blue", fillStyle="cross-hatch")
    )
    rc.ctx.translate(0, 70)
    rc.path("M37,17v15H14V17z M50,5H5v50h45z", Options(fill="blue", fillStyle="solid"))
    rc.ctx.translate(0, 70)
    rc.path("M37,17v15H14V17z M50,5H5v50h45z", Options(fill="blue", fillStyle="zigzag"))

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_path.svg")


def test_canvas_path5():
    rc = rough.canvas(1000, 1000)
    rc.path(
        "M400 100 h 90 v 90 h -90z",
        Options(
            fill="orange",
            fillWeight=5,
            hachureAngle=-45,
            hachureGap=20,
            roughness=0.1,
            fillStyle="zigzag",
        ),
    )

    rc.as_svg(1000, 1000, "tests/test_roughjs_visual_tests/canvas_path5.svg")


def test_canvas_path2():
    rc = rough.canvas(800, 800)
    pathA = (
        "M4.5000 150.1500L4.5000 150.1500Q4.5000 144.7500 6 138.1500Q7.5000 131.5500 10.8000 123.6000"
        "L10.8000 123.6000L21.6000 127.8000Q19.2000 134.1000 18 139.3500Q16.8000 144.6000 16.8000 149.1000"
        "L16.8000 149.1000Q16.8000 156.7500 21.1500 162Q25.5000 167.2500 32.9250 169.8750Q40.3500 172.5000 "
        "49.6500 172.5000L49.6500 172.5000Q60.4500 172.5000 68.5500 170.1750Q76.6500 167.8500 82.0500 164.2500"
        "Q87.4500 160.6500 90.0750 156.7500Q92.7000 152.8500 92.7000 149.8500L92.7000 149.8500Q92.7000 147.3000 "
        "89.1000 145.4250Q85.5000 143.5500 80.2500 141.6750Q75 139.8000 69.7500 137.3250Q64.5000 134.8500 60.9000 "
        "131.1750Q57.3000 127.5000 57.3000 121.8000L57.3000 121.8000Q57.3000 115.8000 60.3750 109.6500Q63.4500 "
        "103.5000 68.7750 98.4000Q74.1000 93.3000 80.7000 90.2250Q87.3000 87.1500 94.3500 87.1500L94.3500 87.1500"
        "Q100.6500 87.1500 105.0750 88.8750Q109.5000 90.6000 111.6000 92.1000L111.6000 92.1000L106.6500 102.7500"
        "Q104.1000 101.5500 100.9500 100.5000Q97.8000 99.4500 94.3500 99.4500L94.3500 99.4500Q90 99.4500 85.5750 "
        "101.2500Q81.1500 103.0500 77.4750 106.0500Q73.8000 109.0500 71.5500 112.6500Q69.3000 116.2500 69.3000 "
        "119.8500L69.3000 119.8500Q69.3000 122.4000 71.9250 124.5000Q74.5500 126.6000 78.7500 128.4000Q82.9500 "
        "130.2000 87.6750 132.0750Q92.4000 133.9500 96.6000 136.1250Q100.8000 138.3000 103.4250 141.1500Q106.0500 "
        "144 106.0500 147.9000L106.0500 147.9000Q106.0500 153.6000 102.3000 159.9750Q98.5500 166.3500 91.2000 "
        "171.9750Q83.8500 177.6000 73.2750 181.2000Q62.7000 184.8000 48.9000 184.8000L48.9000 184.8000Q36.3000 "
        "184.8000 26.2500 181.0500Q16.2000 177.3000 10.3500 169.6500Q4.5000 162 4.5000 150.1500Z"
    )
    pathB = (
        "M0.6000 184.5000L0.6000 184.5000L-3.7500 173.1000Q11.4000 168.3000 19.5750 161.7000Q27.7500 "
        "155.1000 30.8250 147.8250Q33.9000 140.5500 33.9000 133.9500L33.9000 133.9500Q33.9000 129.7500 33 "
        "125.8500Q32.1000 121.9500 29.8500 117Q27.6000 112.0500 23.5500 104.7000L23.5500 104.7000L34.5000 "
        "99.1500Q40.2000 108.9000 42.6750 117.6000Q45.1500 126.3000 45.1500 132.9000L45.1500 132.9000Q45.1500 "
        "142.3500 42.0750 150Q39 157.6500 33.9750 163.5750Q28.9500 169.5000 23.0250 173.7000Q17.1000 177.9000 "
        "11.1750 180.6000Q5.2500 183.3000 0.6000 184.5000Z"
    )

    rc.path(pathA, Options(fill="red"))
    rc.ctx.translate(300, 0)
    rc.path(pathB, Options(fill="blue"))

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_path2.svg")


def test_canvas_map():
    rc = rough.canvas(960, 500)
    # Placeholder for a real map drawing; just a background shape here:
    rc.rectangle(0, 0, 960, 500, Options(fill="lightgray"))

    rc.as_svg(960, 500, "tests/test_roughjs_visual_tests/canvas_map.svg")


def test_canvas_arc2():
    rc = rough.canvas(800, 800)
    rc.arc(
        350,
        300,
        200,
        180,
        0,
        3.14159 * 1.6,
        True,
        Options(
            stroke="#1a1f26",
            strokeWidth=1,
            roughness=1,
            fill="rgba(186,186,188,0.5)",
            fillStyle="solid",
        ),
    )

    rc.as_svg(800, 800, "tests/test_roughjs_visual_tests/canvas_arc2.svg")


##############################################################################
# Final list of tests to run
##############################################################################

ALL_TESTS = [
    # SVG tests (kept for duplicates or unique)
    test_svg_line,
    test_svg_dashed_line,
    test_svg_dashed_polygon,
    test_svg_dashed_ellipse,
    test_svg_config_defaults,
    test_svg_dashed_rectangle,
    test_svg_polygon,
    test_svg_rectangle2,
    test_svg_ellipse,
    test_svg_rectangle,
    # Unique Canvas tests
    test_canvas_curve_seed,
    test_canvas_path7,
    test_canvas_path4,
    test_canvas_arc,
    test_canvas_path_with_transform,
    test_canvas_ellipse2,
    test_canvas_linearpath,
    test_canvas_path3,
    test_canvas_curve4,
    test_canvas_polygon2,
    test_canvas_dashed_arc,
    test_canvas_dashed_path_with_transform,
    test_canvas_dashed_linearpath,
    # test_canvas_dashed_curve,
    # test_canvas_dashed_path,
    test_canvas_poly_seed,
    test_canvas_ellipse3,
    # test_canvas_curve,
    test_canvas_path6,
    # single-stroke
    test_canvas_singlestroke_line,
    test_canvas_singlestroke_arc,
    test_canvas_singlestroke_polygon,
    # test_canvas_singlestroke_curve,
    test_canvas_singlestroke_ellipse,
    test_canvas_singlestroke_path,
    test_canvas_singlestroke_rectangle,
    # More unique curves, etc.
    # test_canvas_curve2,
    test_canvas_curve3,
    test_canvas_path,
    test_canvas_path5,
    test_canvas_path2,
    test_canvas_map,
    test_canvas_arc2,
]


def main():
    os.makedirs("tests/test_roughjs_visual_tests", exist_ok=True)
    for fn in ALL_TESTS:
        print(f"Running: {fn.__name__}()")
        fn()
    # Build an index of test SVG outputs
    lines = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'/><title>Rough.js-inspired Visual Test Suite</title>",
        """
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f8f9fa;
            margin: 0.5em;
            padding: 0.5em;
            }
            h1, h2, h3, h4, h5, h6 {
            font-weight: 500;
            }
            h2 { font-size: 1em; color: #A03075; display: inline; }
            div { display:inline; }
            p {
            font-size: 1rem;
            line-height: 1.6;
            }
            .container {
            margin-top: 2rem;
            }
            img {
                width: 49%;
                margin-top: 0.1em;
                margin-bottom: 0.1em;
                border: 5px solid rgba(0,0,0,0.04);
            }
        </style>
        """,
        "</head>",
        "<body><h1>Rough.js-inspired visual test suite</h1>",
    ]
    for f in sorted(os.listdir("tests/test_roughjs_visual_tests")):
        if f.endswith(".svg"):
            lines.append("<div>")
            lines.append(f'<img src="{f}" />')
            lines.append("</div>")
    lines.append("</body></html>")

    with open(
        "tests/test_roughjs_visual_tests/index.html", "w", encoding="utf-8"
    ) as out:
        out.write("\n".join(lines))
    print(
        "Finished. See 'file:///X:/rough-py/tests/test_roughjs_visual_tests/index.html' for .svg outputs."
    )


if __name__ == "__main__":
    main()
