import pytest
import rough
import os
from pathlib import Path


def build_svg_from_group(group_dict: dict, width: int, height: int) -> str:
    # converts a nested group structure (RoughSVG draw output) into a minimal svg string
    lines = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    ]
    lines.append(convert_node_to_xml(group_dict))
    lines.append("</svg>")
    return "\n".join(lines)


def convert_node_to_xml(node: dict) -> str:
    # recursively converts a node with 'tag', 'attrs', and optional 'children' into an xml snippet
    tag = node.get("tag", "")
    attrs = node.get("attrs", {})
    children = node.get("children", [])
    attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    child_str = "".join(convert_node_to_xml(c) for c in children)
    if child_str:
        return f"<{tag} {attr_str}>{child_str}</{tag}>"
    return f"<{tag} {attr_str} />"


def test_rough_canvas_export():
    # draws several shapes using RoughCanvas, exports them to an SVG file in this test folder
    rc = rough.canvas(400, 300)
    rc.rectangle(10, 10, 100, 80)
    rc.circle(100, 100, 50)
    rc.line(20, 150, 200, 180)
    rc.arc(250, 80, 80, 80, 0, 3.14, closed=True)

    svg_data = rc.as_svg(width=400, height=300)

    out_dir = Path(__file__).parent / "test_compare_svg_and_canvas_flows"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "test_canvas_export.svg"
    out_file.write_text(svg_data, encoding="utf-8")

    assert out_file.stat().st_size > 0


def test_rough_svg_export():
    # uses RoughSVG, exports a rectangle, saves nested dict as minimal svg
    rsvg = rough.svg()
    group_dict = rsvg.rectangle(10, 10, 150, 100)
    svg_str = build_svg_from_group(group_dict, width=300, height=200)

    out_dir = Path(__file__).parent / "test_compare_svg_and_canvas_flows"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "test_svg_export.svg"
    out_file.write_text(svg_str, encoding="utf-8")

    assert out_file.stat().st_size > 0
