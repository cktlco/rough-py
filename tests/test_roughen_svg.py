"""
This script is kept in the tests folder but is designed for standalone execution.
It processes one or more .svg files, "roughens" them, and writes the output to a
test_svg_roughen subdirectory with a configurable random subset selection.

Example usage:
    poetry run python tests/test_svg_roughen.py --input-svg ./path/to/svgfilesdir --sample-count 2
    poetry run python tests/test_svg_roughen.py --input-svg ./path/to/single.svg
    poetry run python tests/test_svg_roughen.py -h  (for help)
"""

import argparse
import math
import re
import os
import random
from pathlib import Path

import rough

# note that this is the local 'svgelements' in the repo root, not the PiPy package
from external.svgelements import (
    SVG,
    Shape,
    Path as SPath,
    Matrix,
    SVGText,
    SVGImage,
    Circle,
    Ellipse,
    Rect,
    Polygon,
    Polyline,
    Line,
)


######################################################################
# Internal caching for shape-segment sampling
######################################################################
class _SegmentCache:
    __slots__ = ("length", "sample_dict")

    def __init__(self):
        self.length = None  # float length, once computed
        self.sample_dict = {}  # maps stepcount -> list_of_points


_segment_cache = {}
_rx_strip_nonfloat = re.compile(r"[^\d.\-+eE]")


def main():
    parser = argparse.ArgumentParser(
        description="Parse & roughen SVG(s), then output new roughened version(s)."
    )
    parser.add_argument(
        "--input-svg",
        help="Path to a single SVG file or a directory of .svg files to process.",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output-svg",
        help="Output SVG filename (only if processing a single input file).",
    )
    parser.add_argument(
        "--roughness", type=float, default=1.0, help="Roughness factor."
    )
    parser.add_argument(
        "--default-fillstyle",
        default="hachure",
        help="Fill style if shape has fill color (e.g. 'hachure', 'solid', etc.).",
    )
    parser.add_argument(
        "--hachure-gap",
        type=float,
        default=1.0,
        help="Hachure gap spacing (only relevant if fillStyle != 'solid').",
    )
    parser.add_argument(
        "--sample-count",
        type=int,
        default=1,
        help="Number of .svg files to randomly pick from a directory; ignored if input is a single file.",
    )
    args = parser.parse_args()

    in_path = Path(args.input_svg).resolve()
    out_dir = Path(__file__).parent / "test_svg_roughen"
    out_dir.mkdir(parents=True, exist_ok=True)

    if in_path.is_file():
        # process single file
        process_one_file(args, in_path, out_dir)
    elif in_path.is_dir():
        # gather .svg files
        svg_files = list(in_path.glob("*.svg"))
        if not svg_files:
            print(f"No .svg files found in {in_path}")
            return
        if args.sample_count < 1:
            args.sample_count = 1

        chosen = random.sample(svg_files, min(args.sample_count, len(svg_files)))
        print(f"Picked {len(chosen)} .svg file(s) from directory '{in_path}'")
        for sf in chosen:
            process_one_file(args, sf, out_dir)
    else:
        print(f"ERROR: input path {in_path} is neither a file nor a directory.")


def process_one_file(args, in_file: Path, out_dir: Path):
    """
    Reads one SVG file, roughens it, and writes it into out_dir.
    If args.output_svg is given and only one file is processed, that is used as output.
    """
    print(f"\nProcessing {in_file} ...")
    doc_in = SVG.parse(in_file, reify=False)

    raw_w = doc_in.values.get("width", "800")
    raw_h = doc_in.values.get("height", "600")
    out_w = _tryf_dim(raw_w, 800)
    out_h = _tryf_dim(raw_h, 600)

    rc = rough.canvas(out_w, out_h)

    # iterate shapes
    for elem in doc_in.elements():
        if not getattr(elem, "visible", True):
            continue
        if isinstance(elem, (SVG, SVGText, SVGImage)):
            continue
        if not isinstance(elem, Shape):
            continue

        # gather style
        stroke_val = elem.values.get("stroke", "none")
        stroke_width_val = elem.values.get("stroke-width", "1")
        fill_val = elem.values.get("fill", "none")
        dash_str = elem.values.get("stroke-dasharray", "none")
        dash_off_str = elem.values.get("stroke-dashoffset", "0")

        sw = _tryf(stroke_width_val, 1)
        dash_list = None
        if dash_str and dash_str.lower() != "none":
            dash_list = []
            for part in dash_str.split(","):
                dash_list.append(_tryf(part, 0))
        dash_off = _tryf(dash_off_str, 0)

        ropts = rough.Options()
        ropts.roughness = args.roughness
        ropts.maxRandomnessOffset = 2.0
        ropts.stroke = "none" if stroke_val.lower() == "none" else stroke_val
        ropts.strokeWidth = sw
        if dash_list:
            ropts.strokeLineDash = dash_list
        ropts.strokeLineDashOffset = dash_off

        if fill_val.lower() == "none":
            ropts.fill = None
            ropts.fillStyle = "solid"
        else:
            ropts.fill = fill_val
            ropts.fillStyle = args.default_fillstyle

        ropts.hachureGap = args.hachure_gap
        ropts.preserveVertices = True

        transform = Matrix(elem.transform) if hasattr(elem, "transform") else Matrix()

        # handle shapes
        if isinstance(elem, Circle):
            cx, cy = elem.cx, elem.cy
            r = elem.rx
            if r <= 0:
                continue
            steps = 64
            circ_pts = []
            for i in range(steps + 1):
                t = 2 * math.pi * (i / steps)
                lx = cx + r * math.cos(t)
                ly = cy + r * math.sin(t)
                circ_pts.append(_xform(transform, lx, ly))
            rc.polygon(circ_pts, ropts)

        elif isinstance(elem, Ellipse):
            cx, cy = elem.cx, elem.cy
            rx, ry = elem.rx, elem.ry
            if rx <= 0 or ry <= 0:
                continue
            steps = 64
            ell_pts = []
            for i in range(steps + 1):
                t = 2 * math.pi * (i / steps)
                lx = cx + rx * math.cos(t)
                ly = cy + ry * math.sin(t)
                ell_pts.append(_xform(transform, lx, ly))
            rc.polygon(ell_pts, ropts)

        else:
            points, closed = shape_to_polygon(elem, transform)
            if not points:
                continue
            if closed:
                rc.polygon(points, ropts)
            else:
                rc.linearPath(points, ropts)

    out_svg = build_svg_output(rc, doc_in, out_w, out_h)

    # determine output name
    if args.output_svg and args.input_svg and Path(args.input_svg).is_file():
        # user-specified name for single file mode
        out_file = Path(args.output_svg).resolve()
    else:
        # place in out_dir
        base_name = in_file.stem + "_roughened.svg"
        out_file = out_dir / base_name

    out_file.write_text(out_svg, encoding="utf-8")
    # printing an absolute path so you can open it in a browser
    # if you need a custom prefix, adapt below
    print(f"Wrote file:///X:{str(out_file.resolve()).replace('dev_local/', '')}")


def shape_to_polygon(shape: Shape, transform: Matrix, line_steps=16, curve_steps=64):
    """
    Param-sample shape => polygon in local coords, apply transform => final points
    """
    sp = SPath(shape)
    sp.validate_connections()
    segs = sp.segments()
    closed = sp.closed

    out_pts = []
    last_end = None
    for seg in segs:
        cn = seg.__class__.__name__
        if cn in ("Move", "Close"):
            continue
        nsteps = line_steps if cn == "Line" else curve_steps
        local_samps = param_sample(seg, nsteps)
        xformed = [_xform(transform, pt[0], pt[1]) for pt in local_samps]

        if not out_pts:
            out_pts.extend(xformed)
            last_end = xformed[-1]
        else:
            if last_end != xformed[0]:
                out_pts.append(xformed[0])
            out_pts.extend(xformed[1:])
            last_end = xformed[-1]

    if closed and len(out_pts) > 2:
        if out_pts[0] != out_pts[-1]:
            out_pts.append(out_pts[0])
    return (out_pts, closed)


def param_sample(seg, steps=10):
    """
    param-sample t=0..1 => steps => list of (x,y). uses a cache for performance
    """
    sid = id(seg)
    cache = _segment_cache.get(sid)
    if cache is None:
        cache = _SegmentCache()
        _segment_cache[sid] = cache

    if cache.length is None:
        try:
            seglen = seg.length(error=1e-12, min_depth=5)
        except:
            seglen = 0
        cache.length = seglen

    sp_dict = cache.sample_dict
    existing = sp_dict.get(steps)
    if existing is not None:
        return existing

    out = []
    dt = 1.0 / steps
    seg_point = seg.point
    for i in range(steps + 1):
        t = i * dt
        p = seg_point(t)
        out.append((p.x, p.y))
    sp_dict[steps] = out
    return out


def _xform(mat: Matrix, x, y):
    return (mat.a * x + mat.c * y + mat.e, mat.b * x + mat.d * y + mat.f)


def build_svg_output(rc: rough.RoughCanvas, doc_in: SVG, out_w, out_h):
    """
    Create final <svg> output from rough drawing calls, copying minimal
    top-level attrs from doc_in if available.
    """
    keep_keys = {
        "id",
        "version",
        "xmlns",
        "xmlns:xlink",
        "xml:space",
        # "viewBox",
        "preserveAspectRatio",
        "x",
        "y",
        "style",
    }
    open_chunks = ["<svg"]
    open_chunks.append(f' width="{out_w}" height="{out_h}"')

    using_viewbox = False
    if (
        doc_in.viewbox
        and doc_in.viewbox.width is not None
        and doc_in.viewbox.height is not None
    ):
        using_viewbox = True
        open_chunks.append(
            f' viewBox="{doc_in.viewbox.x} {doc_in.viewbox.y} '
            f'{doc_in.viewbox.width} {doc_in.viewbox.height}"'
        )

    for k, v in doc_in.values.items():
        if k in keep_keys and v is not None:
            if k.lower() in ("width", "height"):
                continue
            if k == "viewBox":
                continue
            open_chunks.append(f' {k}="{v}"')

    have_xmlns = any("xmlns=" in c for c in open_chunks)
    if not have_xmlns:
        open_chunks.append(' xmlns="http://www.w3.org/2000/svg"')
    open_chunks.append(">")

    if not using_viewbox:
        rc.auto_fit(margin=20)

    lines = ["".join(open_chunks)]
    gen = rc.gen
    for z_index, dcall in rc.draw_calls:
        opts = dcall.options
        sets = dcall.sets
        roundcaps = 'stroke-linecap="round" stroke-linejoin="round"'
        for sset in sets:
            d_str = gen.opsToPath(sset, opts.fixedDecimalPlaceDigits)
            stype = sset.type
            if stype == "fillPath":
                fillcol = opts.fill if opts.fill else "none"
                lines.append(
                    f'<path d="{d_str}" stroke="none" fill="{fillcol}" {roundcaps} />'
                )
            elif stype == "fillSketch":
                fillcol = opts.fill if opts.fill else "none"
                fw = (
                    opts.fillWeight
                    if (opts.fillWeight and opts.fillWeight >= 0)
                    else (opts.strokeWidth or 1) * 0.5
                )
                lines.append(
                    f'<path d="{d_str}" stroke="{fillcol}" stroke-width="{fw}" fill="none" {roundcaps} />'
                )
            else:
                stroke_ = opts.stroke if opts.stroke else "none"
                sw_ = opts.strokeWidth or 1
                dashlist = opts.strokeLineDash
                path_line = f'<path d="{d_str}" stroke="{stroke_}" fill="none" stroke-width="{sw_}" {roundcaps}'
                if dashlist and len(dashlist) > 0:
                    dasharr = ",".join(str(v) for v in dashlist)
                    dashoff = opts.strokeLineDashOffset or 0
                    path_line += (
                        f' stroke-dasharray="{dasharr}" stroke-dashoffset="{dashoff}"'
                    )
                path_line += " />"
                lines.append(path_line)

    lines.append("</svg>")
    return "\n".join(lines)


def _tryf(s, default=0.0):
    s2 = _rx_strip_nonfloat.sub("", str(s if s else ""))
    if not s2.strip():
        return default
    try:
        return float(s2)
    except ValueError:
        return default


def _tryf_dim(s, default=800):
    return _tryf(s, default)


if __name__ == "__main__":
    main()
