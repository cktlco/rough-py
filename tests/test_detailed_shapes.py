import math
import pytest
from pathlib import Path
from rough import canvas, Options


def test_render_detailed_canvas_shapes():
    rc = canvas(800, 600)
    rc.rectangle(10, 10, 100, 100)
    rc.rectangle(
        140,
        10,
        100,
        100,
        Options(fill="rgba(255,0,0,0.2)", fillStyle="solid", roughness=2),
    )
    rc.rectangle(
        10,
        130,
        100,
        100,
        Options(
            fill="red",
            stroke="blue",
            hachureAngle=60,
            hachureGap=10,
            fillWeight=5,
            strokeWidth=5,
        ),
    )
    rc.ellipse(350, 50, 150, 80)
    rc.ellipse(610, 50, 150, 80, Options(fill="blue"))
    rc.circle(
        480,
        50,
        80,
        Options(
            stroke="red", strokeWidth=2, fill="rgba(0,255,0,0.3)", fillStyle="solid"
        ),
    )
    rc.circle(
        480,
        150,
        80,
        Options(
            stroke="red",
            strokeWidth=4,
            fill="rgba(0,255,0,1)",
            fillWeight=4,
            hachureGap=6,
        ),
    )
    rc.circle(
        530,
        150,
        80,
        Options(
            stroke="blue",
            strokeWidth=4,
            fill="rgba(255,255,0,1)",
            fillWeight=4,
            hachureGap=6,
        ),
    )
    rc.linearPath(
        [[690, 10], [790, 20], [750, 120], [690, 100]],
        Options(roughness=0.7, stroke="red", strokeWidth=4),
    )
    rc.polygon([[690, 130], [790, 140], [750, 240], [690, 220]])
    rc.polygon(
        [[690, 250], [790, 260], [750, 360], [690, 340]],
        Options(
            stroke="red", strokeWidth=4, fill="rgba(0,0,255,0.2)", fillStyle="solid"
        ),
    )
    rc.polygon(
        [[690, 370], [790, 385], [750, 480], [690, 460]],
        Options(stroke="red", hachureAngle=65, fill="rgba(0,0,255,0.6)"),
    )
    rc.arc(350, 200, 200, 180, math.pi, math.pi * 1.6)
    rc.arc(350, 300, 200, 180, math.pi, math.pi * 1.6, True)
    rc.arc(
        350,
        300,
        200,
        180,
        0,
        math.pi / 2,
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
        math.pi / 2,
        math.pi,
        True,
        Options(stroke="blue", strokeWidth=2, fill="rgba(255,0,255,0.4)"),
    )

    points = []
    for i in range(20):
        x = (400 / 20) * i + 10
        xdeg = (math.pi / 100) * x
        y = round(math.sin(xdeg) * 90) + 500
        points.append([x, y])
    rc.curve(points, Options(roughness=1.2, stroke="red", strokeWidth=3))

    svg_data = rc.as_svg(800, 600)

    out_dir = Path(__file__).parent / "test_detailed_canvas_shapes"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "roughend_shapes.svg"
    out_file.write_text(svg_data, encoding="utf-8")

    print(f"\nWrote file:///X:{str(out_file.resolve()).replace('dev_local/', '')}")
    assert out_file.stat().st_size > 0
