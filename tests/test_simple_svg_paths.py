"""
Creates multiple rough paths on a pseudo-canvas, including arcs and nested SVG paths.
Exports as an SVG for visual verification.
Run with 'pytest -s' to see printed file location.
"""

import pytest
from pathlib import Path
import rough
from rough import Options


def test_simple_svg_paths():
    rc = rough.canvas(600, 400)

    rc.path(
        "M400 100 h 90 v 90 h -90z",
        Options(
            stroke="red", strokeWidth=3, fill="rgba(0,0,255,0.2)", fillStyle="solid"
        ),
    )
    rc.path(
        "M400 250 h 90 v 90 h -90z",
        Options(fill="rgba(0,0,255,0.6)", fillWeight=4, hachureGap=8),
    )
    rc.path(
        "M37,17v15H14V17z M50,5H5v50h45z",
        Options(stroke="red", strokeWidth=1, fill="blue"),
    )
    rc.path(
        "M80 80 A 45 45, 0, 0, 0, 125 125 L 125 80 Z",
        Options(fill="green"),
    )
    rc.path(
        "M230 80 A 45 45, 0, 1, 0, 275 125 L 275 80 Z",
        Options(fill="purple", hachureAngle=60, hachureGap=5),
    )
    rc.path(
        "M80 230 A 45 45, 0, 0, 1, 125 275 L 125 230 Z",
        Options(fill="red"),
    )
    rc.path(
        "M230 230 A 45 45, 0, 1, 1, 275 275 L 275 230 Z",
        Options(fill="blue"),
    )

    svg_data = rc.as_svg(width=600, height=400)
    out_dir = Path(__file__).parent / "test_simple_svg_paths"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "roughened_output.svg"
    out_file.write_text(svg_data, encoding="utf-8")

    print(f"\nWrote file:///X:{str(out_file.resolve()).replace('dev_local/', '')}")
    assert out_file.stat().st_size > 0
