"""
Provides path generation and filler logic for the rough drawing library.

This module contains helper functions for drawing rough lines, arcs, polygons, ellipses,
and interpreting SVG path commands. It also manages multi-stroke illusions by overlaying
multiple approximations of the same shape for a hand-drawn effect.
"""

from __future__ import annotations
import math
import re
from typing import List, Any, Tuple, Optional, Union

from .core import Op, OpSet, ResolvedOptions
from .geometry import Point
from .fillers.filler import getFiller
from .fillers.filler_interface import RenderHelper
from .math import Random


def randOffset(x: float, o: ResolvedOptions) -> float:
    """
    Returns a pseudo-random offset for a single dimension x, scaled
    by roughness from the provided ResolvedOptions.
    """
    return offsetOpt(x, o)


def randOffsetWithRange(min_val: float, max_val: float, o: ResolvedOptions) -> float:
    """
    Returns a pseudo-random offset within [min_val, max_val], adjusted by roughness.
    """
    return offsetRange(min_val, max_val, o)


def doubleLineFillOps(
    x1: float, y1: float, x2: float, y2: float, o: ResolvedOptions
) -> List[Op]:
    """
    Generates one or two passes of line operations (depending on the fill settings),
    specifically for fill use-cases where multiStroke might be disabled.
    """
    return doubleLine(x1, y1, x2, y2, o, filling=True)


class RenderHelperImpl(RenderHelper):
    """
    Implements the RenderHelper interface by calling local functions in this module.
    This helper is passed into filler objects for generating the line/ellipse ops.
    """

    def randOffset(self, x: float, o: ResolvedOptions) -> float:
        return randOffset(x, o)

    def randOffsetWithRange(
        self, min_val: float, max_val: float, o: ResolvedOptions
    ) -> float:
        return randOffsetWithRange(min_val, max_val, o)

    def ellipse(
        self, x: float, y: float, width: float, height: float, o: ResolvedOptions
    ) -> OpSet:
        return ellipse(x, y, width, height, o)

    def doubleLineOps(
        self, x1: float, y1: float, x2: float, y2: float, o: ResolvedOptions
    ) -> List[Op]:
        return doubleLineFillOps(x1, y1, x2, y2, o)


# A single instance of RenderHelperImpl for pattern filling
helper = RenderHelperImpl()


def line(x1: float, y1: float, x2: float, y2: float, o: ResolvedOptions) -> OpSet:
    """
    Creates a rough line from (x1, y1) to (x2, y2) using one or two passes
    of bcurveTo operations (depending on multiStroke settings).
    """
    ops = doubleLine(x1, y1, x2, y2, o)
    return OpSet("path", ops)


def linearPath(points: List[Point], close: bool, o: ResolvedOptions) -> OpSet:
    """
    Creates a rough polyline (or closed polygon if close=True) from a list of Points.
    Each adjacent pair of points is drawn with line operations.
    """
    ops: List[Op] = []
    if len(points) > 2:
        # Build lines between consecutive points
        for i in range(len(points) - 1):
            ops.extend(
                doubleLine(
                    points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], o
                )
            )
        # If closing, connect last back to first
        if close:
            ops.extend(
                doubleLine(points[-1][0], points[-1][1], points[0][0], points[0][1], o)
            )
    elif len(points) == 2:
        # Just a single line
        ops = doubleLine(points[0][0], points[0][1], points[1][0], points[1][1], o)
    return OpSet("path", ops)


def polygon(points: List[Point], o: ResolvedOptions) -> OpSet:
    """
    Creates a closed polygon from the provided list of Points.
    """
    return linearPath(points, True, o)


def rectangle(
    x: float, y: float, width: float, height: float, o: ResolvedOptions
) -> OpSet:
    """
    Creates a rough rectangle with top-left corner (x, y),
    and the specified width and height.
    """
    pts = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
    return polygon(pts, o)


def generateEllipseParams(width: float, height: float, o: ResolvedOptions) -> dict:
    """
    Calculates the parameters (radius, increment step, etc.) needed
    for drawing a rough ellipse. It also introduces random offsets
    for more natural, hand-drawn imperfections.
    """
    cstep = o.curveStepCount if o.curveStepCount is not None else 9
    cfitting = o.curveFitting if o.curveFitting is not None else 0.95
    # Approximate perimeter for ellipse-like shapes
    psq = math.sqrt(math.pi * 2 * math.sqrt(((width / 2) ** 2 + (height / 2) ** 2) / 2))
    stepCount = max(cstep, int((cstep / math.sqrt(200)) * psq))
    inc = (math.pi * 2) / stepCount
    rx = abs(width / 2)
    ry = abs(height / 2)
    curveFit = 1.0 - cfitting
    rx += offsetOpt(rx * curveFit, o)
    ry += offsetOpt(ry * curveFit, o)
    return {"rx": rx, "ry": ry, "increment": inc}


def ellipseWithParams(
    x: float, y: float, o: ResolvedOptions, ep: dict
) -> Tuple[OpSet, List[Point]]:
    """
    Creates an ellipse using the given ellipse parameter dict (ep), returning both
    an OpSet for the shape and a list of the 'core' ellipse points used.
    """
    ap1, cp1 = computeEllipsePoints(
        ep["increment"],
        x,
        y,
        ep["rx"],
        ep["ry"],
        offset=1.0,
        overlap=ep["increment"] * offsetRange(0.1, offsetRange(0.4, 1.0, o), o),
        o=o,
    )
    c_ops = curveOps(ap1, None, o)
    # If multiple strokes are allowed and roughness is non-zero, add a second pass
    if (not o.disableMultiStroke) and (o.roughness != 0):
        ap2, _ = computeEllipsePoints(
            ep["increment"], x, y, ep["rx"], ep["ry"], offset=1.5, overlap=0, o=o
        )
        c_ops2 = curveOps(ap2, None, o)
        c_ops.extend(c_ops2)
    return (OpSet("path", c_ops), cp1)


def ellipse(
    x: float, y: float, width: float, height: float, o: ResolvedOptions
) -> OpSet:
    """
    Creates a rough ellipse with the center at (x, y) and the given width and height.
    """
    ep = generateEllipseParams(width, height, o)
    e_ops, _ = ellipseWithParams(x, y, o, ep)
    return e_ops


def computeEllipsePoints(
    increment: float,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    offset: float,
    overlap: float,
    o: ResolvedOptions,
) -> Tuple[List[Point], List[Point]]:
    """
    Generates two lists of Points: one for all computed ellipse perimeter points,
    and one for the 'core' points. The offset and overlap parameters control how
    'rough' or overlapped the ellipse edges become.
    """
    coreOnly = o.roughness == 0
    allPoints: List[Point] = []
    corePoints: List[Point] = []
    if coreOnly:
        # If roughness is zero, use fewer steps for a simpler ellipse
        inc = increment / 4.0
        allPoints.append((cx + rx * math.cos(-inc), cy + ry * math.sin(-inc)))
        angle = 0.0
        while angle <= (math.pi * 2):
            px = cx + rx * math.cos(angle)
            py = cy + ry * math.sin(angle)
            corePoints.append((px, py))
            allPoints.append((px, py))
            angle += inc
        allPoints.append((cx + rx * math.cos(0), cy + ry * math.sin(0)))
        allPoints.append((cx + rx * math.cos(inc), cy + ry * math.sin(inc)))
    else:
        # More hand-drawn approach with random offsets
        radOffset = offsetOpt(0.5, o) - (math.pi / 2.0)
        allPoints.append(
            (
                offsetOpt(offset, o) + cx + 0.9 * rx * math.cos(radOffset - increment),
                offsetOpt(offset, o) + cy + 0.9 * ry * math.sin(radOffset - increment),
            )
        )
        endAngle = (math.pi * 2) + radOffset - 0.01
        angle = radOffset
        while angle < endAngle:
            px = offsetOpt(offset, o) + cx + rx * math.cos(angle)
            py = offsetOpt(offset, o) + cy + ry * math.sin(angle)
            corePoints.append((px, py))
            allPoints.append((px, py))
            angle += increment
        allPoints.append(
            (
                offsetOpt(offset, o)
                + cx
                + rx * math.cos(radOffset + math.pi * 2 + overlap * 0.5),
                offsetOpt(offset, o)
                + cy
                + ry * math.sin(radOffset + math.pi * 2 + overlap * 0.5),
            )
        )
        allPoints.append(
            (
                offsetOpt(offset, o) + cx + 0.98 * rx * math.cos(radOffset + overlap),
                offsetOpt(offset, o) + cy + 0.98 * ry * math.sin(radOffset + overlap),
            )
        )
        allPoints.append(
            (
                offsetOpt(offset, o)
                + cx
                + 0.9 * rx * math.cos(radOffset + overlap * 0.5),
                offsetOpt(offset, o)
                + cy
                + 0.9 * ry * math.sin(radOffset + overlap * 0.5),
            )
        )
    return (allPoints, corePoints)


def arc(
    x: float,
    y: float,
    width: float,
    height: float,
    start: float,
    stop: float,
    closed: bool,
    roughClosure: bool,
    o: ResolvedOptions,
) -> OpSet:
    """
    Creates a rough arc (portion of an ellipse) from angle start to angle stop,
    optionally closed at the center. The roughClosure flag uses lines that
    preserve the same rough style, while a standard closure is simpler.
    """
    rx = abs(width / 2.0)
    ry = abs(height / 2.0)
    rx += offsetOpt(rx * 0.01, o)
    ry += offsetOpt(ry * 0.01, o)
    strt = start
    stp = stop
    # Normalize angles so they stay within [0, 2π) range
    while strt < 0:
        strt += math.pi * 2
        stp += math.pi * 2
    if (stp - strt) > (math.pi * 2):
        strt = 0
        stp = math.pi * 2

    cstep = o.curveStepCount if o.curveStepCount is not None else 9
    ellipseInc = (math.pi * 2) / cstep
    arcInc = min(ellipseInc / 2.0, (stp - strt) / 2.0)

    # First pass
    ops = arcOps(arcInc, x, y, rx, ry, strt, stp, 1.0, o)
    # If multi-stroke is allowed, a second pass is made
    if not o.disableMultiStroke:
        ops2 = arcOps(arcInc, x, y, rx, ry, strt, stp, 1.5, o)
        ops.extend(ops2)
    if closed:
        # Optionally close at the center
        cx, cy = x, y
        if roughClosure:
            ops.extend(
                doubleLine(
                    cx, cy, cx + rx * math.cos(strt), cy + ry * math.sin(strt), o
                )
            )
            ops.extend(
                doubleLine(cx, cy, cx + rx * math.cos(stp), cy + ry * math.sin(stp), o)
            )
        else:
            ops.append(Op("lineTo", [cx, cy]))
            ops.append(
                Op("lineTo", [cx + rx * math.cos(strt), cy + ry * math.sin(strt)])
            )
    return OpSet("path", ops)


def curve(points: Union[List[Point], List[List[Point]]], o: ResolvedOptions) -> OpSet:
    """
    Creates a rough multi-segment curve through the given points.
    The 'points' parameter may be a single list of (x,y) tuples or
    a list of multiple such lists, indicating multiple segments.
    """
    if not points:
        return OpSet("path", [])

    # If the first element is a single coordinate pair, interpret points as a single path
    if isinstance(points[0][0], (float, int)):
        amt1 = 1.0 * (1.0 + (o.roughness if o.roughness is not None else 1.0) * 0.2)
        amt2 = 0.0
        if not o.disableMultiStroke:
            amt2 = 1.5 * (
                1.0 + (o.roughness if o.roughness is not None else 1.0) * 0.22
            )
        # If 'points' is just one tuple, wrap it into a list
        if isinstance(points, tuple):
            # Convert single tuple into a single-element list
            points_list: List[Point] = [points]
            under = curveWithOffset(points_list, amt1, o)
            over: List[Op] = []
            if not o.disableMultiStroke:
                over = curveWithOffset(points_list, amt2, cloneOptionsSeed(o))
        else:
            # Otherwise, cast the existing iterable of points
            points_list = list(points)  # type: ignore[arg-type]
            under = curveWithOffset(points_list, amt1, o)
            over = []
            if not o.disableMultiStroke:
                over = curveWithOffset(points_list, amt2, cloneOptionsSeed(o))
        return OpSet("path", under + over)
    else:
        # Here, points is a list of multiple sub-lists of points
        all_ops: List[Op] = []
        first_segment = True
        for pset in points:  # each pset is a List[Point]
            amt1 = 1.0 * (1.0 + (o.roughness if o.roughness is not None else 1.0) * 0.2)
            amt2 = 0.0
            if not o.disableMultiStroke:
                amt2 = 1.5 * (
                    1.0 + (o.roughness if o.roughness is not None else 1.0) * 0.22
                )
            under = curveWithOffset(pset, amt1, o)
            if not o.disableMultiStroke:
                over2 = curveWithOffset(pset, amt2, cloneOptionsSeed(o))
            else:
                over2 = []
            # Merge the ops, skipping the move operation on subsequent segments
            if first_segment:
                all_ops.extend(under + over2)
                first_segment = False
            else:
                for i, op in enumerate(under):
                    if i == 0 and op.op == "move":
                        continue
                    all_ops.append(op)
                for i, op in enumerate(over2):
                    if i == 0 and op.op == "move":
                        continue
                    all_ops.append(op)
        return OpSet("path", all_ops)


def svgPath(path: str, o: ResolvedOptions) -> OpSet:
    """
    Parses an SVG path string into absolute segments, then converts them
    into a rough path using line, bezier, or arc approximations.
    """
    p = path.strip()
    if not p:
        return OpSet("path", [])

    segs = parsePathCommands(p)
    abs_segs = toAbsolute(segs)
    ops: List[Op] = []
    current: Point = (0.0, 0.0)
    first: Point = (0.0, 0.0)

    for seg in abs_segs:
        cmd = seg[0]
        vals = seg[1]
        if cmd == "M":
            x, y = vals[0], vals[1]
            current = (x, y)
            first = (x, y)
            ops.append(Op("move", [x, y]))
        elif cmd == "L":
            x, y = vals[0], vals[1]
            # If multi-stroke is disabled, just do one line
            if o.disableMultiStroke:
                ops.append(Op("lineTo", [x, y]))
            else:
                ops.extend(doubleLine(current[0], current[1], x, y, o))
            current = (x, y)
        elif cmd == "H":
            vx = vals[0]
            if o.disableMultiStroke:
                ops.append(Op("lineTo", [vx, current[1]]))
            else:
                ops.extend(doubleLine(current[0], current[1], vx, current[1], o))
            current = (vx, current[1])
        elif cmd == "V":
            vy = vals[0]
            if o.disableMultiStroke:
                ops.append(Op("lineTo", [current[0], vy]))
            else:
                ops.extend(doubleLine(current[0], current[1], current[0], vy, o))
            current = (current[0], vy)
        elif cmd == "C":
            cx1, cy1, cx2, cy2, x3, y3 = vals
            if o.disableMultiStroke:
                ops.extend(singleCubic(current, cx1, cy1, cx2, cy2, x3, y3))
            else:
                ops.extend(cubicBezierOps(cx1, cy1, cx2, cy2, x3, y3, current, o))
            current = (x3, y3)
        elif cmd == "Q":
            qx, qy, x3, y3 = vals
            if o.disableMultiStroke:
                ops.extend(singleQuadratic(current, qx, qy, x3, y3))
            else:
                ops.extend(quadToCubic(qx, qy, x3, y3, current, o))
            current = (x3, y3)
        elif cmd == "A":
            rx, ry, xrot, laf, swf, ex, ey = vals
            if o.disableMultiStroke:
                arcops, newp = singleArc(current, rx, ry, xrot, laf, swf, ex, ey)
                ops.extend(arcops)
                current = newp
            else:
                arcops, newp = arcToCubics(current, rx, ry, xrot, laf, swf, ex, ey, o)
                ops.extend(arcops)
                current = newp
        elif cmd == "Z":
            if o.disableMultiStroke:
                ops.append(Op("lineTo", [first[0], first[1]]))
            else:
                ops.extend(doubleLine(current[0], current[1], first[0], first[1], o))
            current = first

    return OpSet("path", ops)


def parsePathCommands(d: str) -> List[List[Any]]:
    """
    Splits an SVG path string into tokens, grouping commands (like 'M', 'L', etc.)
    with the appropriate numeric arguments following them.
    """
    d = d.replace(",", " ")
    d = re.sub(r"([aAcChHlLmMqQsStTvVzZ])", r" \1 ", d)
    d = re.sub(r"\s+", " ", d).strip()
    tokens = d.split(" ")
    segs: List[List[Union[str, float]]] = []
    idx = 0

    def is_cmd(x: str) -> bool:
        return bool(re.match(r"^[aAcChHlLmMqQsStTvVzZ]$", x))

    while idx < len(tokens):
        t: str = tokens[idx]
        if is_cmd(t):
            segs.append([t])
            idx += 1
        else:
            try:
                val: float = float(t)
                segs[-1].append(val)
            except ValueError:
                pass
            idx += 1
    return segs


def toAbsolute(segments: List[List[Any]]) -> List[List[Any]]:
    """
    Converts relative SVG path commands in 'segments' to absolute equivalents.
    Each segment is of the form [command, ...numbers].
    """
    result: List[List[Any]] = []
    current = (0.0, 0.0)
    first = (0.0, 0.0)
    for seg in segments:
        cmd = seg[0]
        nums = seg[1:]
        isLower = cmd == cmd.lower()
        upcmd = cmd.upper()

        if upcmd == "M":
            i = 0
            while i + 1 < len(nums):
                x, y = nums[i], nums[i + 1]
                i += 2
                if isLower:
                    x += current[0]
                    y += current[1]
                current = (x, y)
                if not result:
                    first = current
                result.append(["M", [x, y]])
            first = current
        elif upcmd == "L":
            i = 0
            while i + 1 < len(nums):
                x, y = nums[i], nums[i + 1]
                i += 2
                if isLower:
                    x += current[0]
                    y += current[1]
                result.append(["L", [x, y]])
                current = (x, y)
        elif upcmd == "H":
            i = 0
            while i < len(nums):
                vx = nums[i]
                i += 1
                if isLower:
                    vx += current[0]
                result.append(["H", [vx]])
                current = (vx, current[1])
        elif upcmd == "V":
            i = 0
            while i < len(nums):
                vy = nums[i]
                i += 1
                if isLower:
                    vy += current[1]
                result.append(["V", [vy]])
                current = (current[0], vy)
        elif upcmd == "C":
            i = 0
            while i + 5 < len(nums):
                cx1, cy1, cx2, cy2, x3, y3 = nums[i : i + 6]
                i += 6
                if isLower:
                    cx1 += current[0]
                    cy1 += current[1]
                    cx2 += current[0]
                    cy2 += current[1]
                    x3 += current[0]
                    y3 += current[1]
                result.append(["C", [cx1, cy1, cx2, cy2, x3, y3]])
                current = (x3, y3)
        elif upcmd == "Q":
            i = 0
            while i + 3 < len(nums):
                qx, qy, x3, y3 = nums[i : i + 4]
                i += 4
                if isLower:
                    qx += current[0]
                    qy += current[1]
                    x3 += current[0]
                    y3 += current[1]
                result.append(["Q", [qx, qy, x3, y3]])
                current = (x3, y3)
        elif upcmd == "A":
            i = 0
            while i + 6 < len(nums):
                rx, ry, xrot, laf, swf, ex, ey = nums[i : i + 7]
                i += 7
                if isLower:
                    ex += current[0]
                    ey += current[1]
                result.append(["A", [rx, ry, xrot, laf, swf, ex, ey]])
                current = (ex, ey)
        elif upcmd == "Z":
            result.append(["Z", []])
            current = first
        else:
            # Unrecognized command, skip
            pass
    return result


def arcToCubics(
    current: Point,
    rx: float,
    ry: float,
    xrot: float,
    laf: float,
    swf: float,
    ex: float,
    ey: float,
    o: ResolvedOptions,
) -> Tuple[List[Op], Point]:
    """
    Converts a single elliptical arc command into one or more cubic Bezier segments,
    returning the resulting ops and the new end point.
    """
    beziers = ellipticalArcToBezier(
        current[0], current[1], ex, ey, rx, ry, math.radians(xrot % 360), laf, swf
    )
    ops: List[Op] = []
    last = current
    for c in beziers:
        cx1, cy1, cx2, cy2, x3, y3 = c
        ops.extend(cubicBezierOps(cx1, cy1, cx2, cy2, x3, y3, last, o))
        last = (x3, y3)
    return (ops, (ex, ey))


def ellipticalArcToBezier(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    rx: float,
    ry: float,
    phi: float,
    fa: float,
    fs: float,
) -> List[List[float]]:
    """
    Converts an elliptical arc defined by start (x1,y1), end (x2,y2),
    radii rx,ry, rotation angle phi, large-arc-flag fa, and sweep-flag fs
    into a series of cubic bezier segments for easier approximation.
    """
    if abs(x1 - x2) < 1e-9 and abs(y1 - y2) < 1e-9:
        return []
    if rx == 0 or ry == 0:
        return [[x1, y1, x2, y2, x2, y2]]

    # Transform to ellipse space
    x1p = math.cos(phi) * (x1 - x2) / 2.0 + math.sin(phi) * (y1 - y2) / 2.0
    y1p = -math.sin(phi) * (x1 - x2) / 2.0 + math.cos(phi) * (y1 - y2) / 2.0
    if abs(x1p) < 1e-9 and abs(y1p) < 1e-9:
        return []

    rx2 = rx * rx
    ry2 = ry * ry
    x1p2 = x1p * x1p
    y1p2 = y1p * y1p
    lam = (x1p2 / rx2) + (y1p2 / ry2)
    if lam > 1:
        # Scale radii if the start and end points cannot fit in a single arc
        scale = math.sqrt(lam)
        rx *= scale
        ry *= scale
        rx2 = rx * rx
        ry2 = ry * ry

    sign = 1 if fa != fs else -1
    num = rx2 * ry2 - rx2 * y1p2 - ry2 * x1p2
    den = rx2 * y1p2 + ry2 * x1p2
    num = max(num, 0.0)
    if abs(den) < 1e-12:
        return []

    c = sign * math.sqrt(num / den)
    cxp = c * (rx * y1p / ry)
    cyp = c * (-ry * x1p / rx)
    # Center in global coords
    cx = math.cos(phi) * cxp - math.sin(phi) * cyp + (x1 + x2) / 2.0
    cy = math.sin(phi) * cxp + math.cos(phi) * cyp + (y1 + y2) / 2.0

    def angle(u: Tuple[float, float], v: Tuple[float, float]) -> float:
        dot = u[0] * v[0] + u[1] * v[1]
        mag = math.sqrt((u[0] ** 2 + u[1] ** 2) * (v[0] ** 2 + v[1] ** 2))
        if mag < 1e-12:
            return 0.0
        sign2 = 1.0
        if (u[0] * v[1] - u[1] * v[0]) < 0:
            sign2 = -1.0
        val = dot / mag
        val = max(-1.0, min(1.0, val))
        return sign2 * math.acos(val)

    # Compute angles for arcs
    ux = (x1p - cxp) / rx
    uy = (y1p - cyp) / ry
    vx = (-x1p - cxp) / rx
    vy = (-y1p - cyp) / ry
    start_ang = angle((1.0, 0.0), (ux, uy))
    sweep_ang = angle((ux, uy), (vx, vy))

    if not fs and sweep_ang > 0:
        sweep_ang -= 2.0 * math.pi
    elif fs and sweep_ang < 0:
        sweep_ang += 2.0 * math.pi
    sweep_ang = math.fmod(sweep_ang, 2.0 * math.pi)

    seg_count = int(math.ceil(abs(sweep_ang) / (math.pi / 2.0)))
    seg_sweep = sweep_ang / seg_count
    out: List[List[float]] = []
    for i in range(seg_count):
        st = start_ang + i * seg_sweep
        en = st + seg_sweep
        out.append(arcSegmentToCubic(cx, cy, rx, ry, phi, st, en))
    return out


def arcSegmentToCubic(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    phi: float,
    start_ang: float,
    end_ang: float,
) -> List[float]:
    """
    Approximates an arc segment [start_ang..end_ang] of an ellipse
    with center (cx, cy), radii (rx, ry), and rotation phi, using a
    cubic bezier curve representation.
    """
    alpha = (end_ang - start_ang) / 2.0
    if abs(alpha) < 1e-9:
        # Degenerate arc => approximate as a single point repeated
        mid = (start_ang + end_ang) * 0.5
        x3 = (
            cx + rx * math.cos(mid) * math.cos(phi) - ry * math.sin(mid) * math.sin(phi)
        )
        y3 = (
            cy + rx * math.cos(mid) * math.sin(phi) + ry * math.sin(mid) * math.cos(phi)
        )
        return [x3, y3, x3, y3, x3, y3]

    x1 = rx * math.cos(start_ang)
    y1 = ry * math.sin(start_ang)
    x2 = rx * math.cos(end_ang)
    y2 = ry * math.sin(end_ang)

    sin_a = math.sin(alpha)
    if abs(sin_a) < 1e-9:
        l = 0.0
    else:
        l = (4.0 / 3.0) * math.tan(alpha / 2.0)

    c1x = x1 - l * rx * math.sin(start_ang)
    c1y = y1 + l * ry * math.cos(start_ang)
    c2x = x2 + l * rx * math.sin(end_ang)
    c2y = y2 - l * ry * math.cos(end_ang)

    def rot(px: float, py: float) -> Tuple[float, float]:
        xr = px * math.cos(phi) - py * math.sin(phi)
        yr = px * math.sin(phi) + py * math.cos(phi)
        return (xr + cx, yr + cy)

    sAbs = rot(x1, y1)
    c1Abs = rot(c1x, c1y)
    c2Abs = rot(c2x, c2y)
    eAbs = rot(x2, y2)
    return [c1Abs[0], c1Abs[1], c2Abs[0], c2Abs[1], eAbs[0], eAbs[1]]


def cubicBezierOps(
    cx1: float,
    cy1: float,
    cx2: float,
    cy2: float,
    ex: float,
    ey: float,
    current: Point,
    o: ResolvedOptions,
) -> List[Op]:
    """
    Generates one or two passes of cubic Bezier ops, depending on whether
    multi-stroke is disabled, to achieve a rough hand-drawn look.
    """
    ops: List[Op] = []
    sx, sy = current
    passes = 1 if o.disableMultiStroke else 2
    base = o.maxRandomnessOffset if o.maxRandomnessOffset is not None else 2.0

    for i in range(passes):
        ro = base + (0.3 if i > 0 else 0.0)
        if i == 0:
            # First pass always starts with "move"
            ops.append(Op("move", [sx, sy]))
        else:
            # Second pass might offset the start if not preserving vertices
            ops.append(
                Op(
                    "move",
                    [
                        sx + (0.0 if o.preserveVertices else offsetOpt(base, o)),
                        sy + (0.0 if o.preserveVertices else offsetOpt(base, o)),
                    ],
                )
            )
        c1x = cx1 + (0.0 if o.preserveVertices else offsetOpt(ro, o))
        c1y = cy1 + (0.0 if o.preserveVertices else offsetOpt(ro, o))
        c2x = cx2 + (0.0 if o.preserveVertices else offsetOpt(ro, o))
        c2y = cy2 + (0.0 if o.preserveVertices else offsetOpt(ro, o))
        fx = ex + (0.0 if o.preserveVertices else offsetOpt(ro, o))
        fy = ey + (0.0 if o.preserveVertices else offsetOpt(ro, o))
        ops.append(Op("bcurveTo", [c1x, c1y, c2x, c2y, fx, fy]))
    return ops


def quadToCubic(
    qx: float, qy: float, x: float, y: float, current: Point, o: ResolvedOptions
) -> List[Op]:
    """
    Converts a single quadratic bezier curve (Q command) into a cubic representation,
    and possibly overlays a second pass if multi-stroke is not disabled.
    """
    sx, sy = current
    c1x = sx + (2.0 / 3.0) * (qx - sx)
    c1y = sy + (2.0 / 3.0) * (qy - sy)
    c2x = x + (2.0 / 3.0) * (qx - x)
    c2y = y + (2.0 / 3.0) * (qy - y)
    return cubicBezierOps(c1x, c1y, c2x, c2y, x, y, (sx, sy), o)


def singleCubic(
    cur: Point, cx1: float, cy1: float, cx2: float, cy2: float, x3: float, y3: float
) -> List[Op]:
    """
    Returns a single set of cubic bezier ops from one segment, without multi-stroke.
    """
    sx, sy = cur
    return [Op("move", [sx, sy]), Op("bcurveTo", [cx1, cy1, cx2, cy2, x3, y3])]


def singleQuadratic(cur: Point, qx: float, qy: float, x3: float, y3: float) -> List[Op]:
    """
    Returns a single set of cubic ops equivalent to a given quadratic segment.
    """
    sx, sy = cur
    c1x = sx + (2.0 / 3.0) * (qx - sx)
    c1y = sy + (2.0 / 3.0) * (qy - sy)
    c2x = x3 + (2.0 / 3.0) * (qx - x3)
    c2y = y3 + (2.0 / 3.0) * (qy - y3)
    return [Op("move", [sx, sy]), Op("bcurveTo", [c1x, c1y, c2x, c2y, x3, y3])]


def singleArc(
    cur: Point,
    rx: float,
    ry: float,
    xrot: float,
    laf: float,
    swf: float,
    ex: float,
    ey: float,
) -> Tuple[List[Op], Point]:
    """
    Returns a single pass of arc->bezier ops, ignoring multi-stroke settings.
    """
    beziers = ellipticalArcToBezier(
        cur[0], cur[1], ex, ey, rx, ry, math.radians(xrot % 360), laf, swf
    )
    ops: List[Op] = []
    last = cur
    for c in beziers:
        cx1, cy1, cx2, cy2, x3, y3 = c
        ops.append(Op("move", [last[0], last[1]]))
        ops.append(Op("bcurveTo", [cx1, cy1, cx2, cy2, x3, y3]))
        last = (x3, y3)
    return (ops, (ex, ey))


def doubleLine(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    o: ResolvedOptions,
    filling: bool = False,
) -> List[Op]:
    """
    Generates either one or two passes of line operations, depending on whether
    multi-stroke is disabled (or if it is a fill context). Provides the main
    line approximation for the library.
    """
    singleStroke = o.disableMultiStrokeFill if filling else o.disableMultiStroke
    first = lineOps(x1, y1, x2, y2, o, move=True, overlay=False)
    if singleStroke:
        return first
    second = lineOps(x1, y1, x2, y2, o, move=True, overlay=True)
    return first + second


def lineOps(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    o: ResolvedOptions,
    move: bool,
    overlay: bool,
) -> List[Op]:
    """
    Constructs a single pass (move + bcurveTo) that approximates a line
    from (x1, y1) to (x2, y2). The 'overlay' flag can introduce slightly
    different offsets for a second stroke in multi-stroke mode.
    """
    lengthSq = (x1 - x2) ** 2 + (y1 - y2) ** 2
    length = math.sqrt(lengthSq)
    roughnessGain = 1.0
    if length > 500.0:
        roughnessGain = 0.4
    elif length >= 200.0:
        roughnessGain = (-0.0016668 * length) + 1.233334
    moff = o.maxRandomnessOffset if o.maxRandomnessOffset is not None else 2.0
    # If shape is very short, reduce the offset so it doesn't overshoot.
    if (moff * moff * 100.0) > lengthSq:
        moff = length / 10.0
    halfOffset = moff / 2.0
    divergePoint = 0.2 + randomFloat(o) * 0.2
    bowv = o.bowing if (o.bowing is not None) else 1.0
    midDispX = bowv * moff * (y2 - y1) / 200.0
    midDispY = bowv * moff * (x1 - x2) / 200.0
    midDispX = offsetOpt(midDispX, o, roughnessGain)
    midDispY = offsetOpt(midDispY, o, roughnessGain)

    ops: List[Op] = []

    def randomHalf() -> float:
        return offsetOpt(halfOffset, o, roughnessGain)

    def randomFull() -> float:
        return offsetOpt(moff, o, roughnessGain)

    if move:
        if overlay:
            ops.append(
                Op(
                    "move",
                    [
                        x1 + (0.0 if o.preserveVertices else randomHalf()),
                        y1 + (0.0 if o.preserveVertices else randomHalf()),
                    ],
                )
            )
        else:
            ops.append(
                Op(
                    "move",
                    [
                        x1 + (0.0 if o.preserveVertices else randomFull()),
                        y1 + (0.0 if o.preserveVertices else randomFull()),
                    ],
                )
            )

    # Calculate the control points for the bcurve
    c1x = midDispX + x1 + (x2 - x1) * divergePoint
    c1y = midDispY + y1 + (y2 - y1) * divergePoint
    c2x = midDispX + x1 + 2.0 * (x2 - x1) * divergePoint
    c2y = midDispY + y1 + 2.0 * (y2 - y1) * divergePoint

    if overlay:
        ops.append(
            Op(
                "bcurveTo",
                [
                    c1x + randomHalf(),
                    c1y + randomHalf(),
                    c2x + randomHalf(),
                    c2y + randomHalf(),
                    x2 + (0.0 if o.preserveVertices else randomHalf()),
                    y2 + (0.0 if o.preserveVertices else randomHalf()),
                ],
            )
        )
    else:
        ops.append(
            Op(
                "bcurveTo",
                [
                    c1x + randomFull(),
                    c1y + randomFull(),
                    c2x + randomFull(),
                    c2y + randomFull(),
                    x2 + (0.0 if o.preserveVertices else randomFull()),
                    y2 + (0.0 if o.preserveVertices else randomFull()),
                ],
            )
        )
    return ops


def curveOps(
    points: List[Point], closePoint: Point | None, o: ResolvedOptions
) -> List[Op]:
    """
    For a sequence of Points, create an approximate multi-point curve using
    bcurveTo. Optionally closes the shape by connecting the last point to closePoint.
    """
    ops: List[Op] = []
    cTight = o.curveTightness if o.curveTightness is not None else 0.0
    if len(points) > 3:
        # Catmull-Rom approach for smoothing
        b: List[Optional[Point]] = [None] * 4
        s = 1.0 - cTight
        ops.append(Op("move", [points[1][0], points[1][1]]))
        for i in range(1, len(points) - 2):
            b[0] = points[i]
            b[1] = (
                points[i][0] + (s * (points[i + 1][0] - points[i - 1][0])) / 6.0,
                points[i][1] + (s * (points[i + 1][1] - points[i - 1][1])) / 6.0,
            )
            b[2] = (
                points[i + 1][0] + (s * (points[i][0] - points[i + 2][0])) / 6.0,
                points[i + 1][1] + (s * (points[i][1] - points[i + 2][1])) / 6.0,
            )
            b[3] = points[i + 1]
            if b[0] and b[1] and b[2] and b[3]:
                ops.append(
                    Op(
                        "bcurveTo",
                        [b[1][0], b[1][1], b[2][0], b[2][1], b[3][0], b[3][1]],
                    )
                )
        if closePoint:
            # Optionally link the last point to the closePoint with a line
            ro = o.maxRandomnessOffset if o.maxRandomnessOffset is not None else 2.0
            ops.append(
                Op(
                    "lineTo",
                    [
                        closePoint[0] + offsetOpt(ro, o),
                        closePoint[1] + offsetOpt(ro, o),
                    ],
                )
            )
    elif len(points) == 3:
        # Simple 3-point approach
        ops.append(Op("move", [points[1][0], points[1][1]]))
        ops.append(
            Op(
                "bcurveTo",
                [
                    points[1][0],
                    points[1][1],
                    points[2][0],
                    points[2][1],
                    points[2][0],
                    points[2][1],
                ],
            )
        )
    elif len(points) == 2:
        # If there are only 2 points, draw them as a line
        ops.extend(
            lineOps(
                points[0][0],
                points[0][1],
                points[1][0],
                points[1][1],
                o,
                move=True,
                overlay=True,
            )
        )
    return ops


def curveWithOffset(points: List[Point], offset: float, o: ResolvedOptions) -> List[Op]:
    """
    Offsets each point in 'points' by a random factor up to 'offset',
    then calls curveOps to produce the final bcurve ops. The offset
    simulates natural variation in the stroke.
    """
    if not points:
        return []
    ps: List[Point] = [
        (
            points[0][0] + offsetOpt(offset, o),
            points[0][1] + offsetOpt(offset, o),
        ),
        (
            points[0][0] + offsetOpt(offset, o),
            points[0][1] + offsetOpt(offset, o),
        ),
    ]
    for i in range(1, len(points)):
        px = points[i][0] + offsetOpt(offset, o)
        py = points[i][1] + offsetOpt(offset, o)
        ps.append((px, py))
        if i == len(points) - 1:
            ps.append((px, py))
    return curveOps(ps, None, o)


def arcOps(
    arcInc: float,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    strt: float,
    stp: float,
    offset: float,
    o: ResolvedOptions,
) -> List[Op]:
    """
    Approximates an elliptical arc from angle strt to angle stp in increments of arcInc.
    Each point is jittered by offset to create a hand-drawn look.
    """
    radOffset = strt + offsetOpt(0.1, o)
    ops: List[Op] = []
    points: List[Point] = []
    angle = radOffset - arcInc
    # Starting reference point
    px = cx + 0.9 * rx * math.cos(angle)
    py = cy + 0.9 * ry * math.sin(angle)
    points.append((px, py))
    angle = radOffset
    # Sweep the arc
    while angle <= stp:
        xx = offsetOpt(offset, o) + cx + rx * math.cos(angle)
        yy = offsetOpt(offset, o) + cy + ry * math.sin(angle)
        points.append((xx, yy))
        angle += arcInc
    # Ensure the last point is correct
    points.append((cx + rx * math.cos(stp), cy + ry * math.sin(stp)))
    points.append((cx + rx * math.cos(stp), cy + ry * math.sin(stp)))
    ops.extend(curveOps(points, None, o))
    return ops


def randomFloat(o: ResolvedOptions) -> float:
    """
    Provides a random float in [0,1) using a seeded generator
    tied to the ResolvedOptions.
    """
    if not hasattr(o, "_randgen"):
        setattr(o, "_randgen", Random(o.seed))
    randg = getattr(o, "_randgen")
    return randg.next()


def offsetRange(
    minv: float, maxv: float, o: ResolvedOptions, gain: float = 1.0
) -> float:
    """
    Returns a random number in [minv, maxv], scaled by the 'roughness' factor
    and an optional additional gain multiplier.
    """
    r = o.roughness if o.roughness is not None else 1.0
    return r * gain * (randomFloat(o) * (maxv - minv) + minv)


def offsetOpt(x: float, o: ResolvedOptions, gain: float = 1.0) -> float:
    """
    Returns a random offset in the range [-x, x], scaled by the 'roughness' factor
    and an optional gain multiplier.
    """
    return offsetRange(-x, x, o, gain)


def cloneOptionsSeed(o: ResolvedOptions) -> ResolvedOptions:
    """
    Creates a shallow clone of the given ResolvedOptions, incrementing its seed by 1
    to generate a new sequence of random variations. This ensures the second pass
    of a stroke doesn't exactly match the first.
    """
    from .core import ResolvedOptions

    c = ResolvedOptions()
    for k, v in o.__dict__.items():
        setattr(c, k, v)
    c.seed = o.seed + 1
    if hasattr(c, "_randgen"):
        delattr(c, "_randgen")
    return c


def solidFillPolygon(polygonList: List[List[Point]], o: ResolvedOptions) -> OpSet:
    """
    Returns operations to outline polygons, suitable for a solid fill shape.
    This simply moves to the first point and connects subsequent points with lines.
    """
    ops: List[Op] = []
    for pts in polygonList:
        if pts and len(pts) > 2:
            ops.append(Op("move", [pts[0][0], pts[0][1]]))
            for i in range(1, len(pts)):
                ops.append(Op("lineTo", [pts[i][0], pts[i][1]]))
    return OpSet("fillPath", ops)


def patternFillPolygons(polygonList: List[List[Point]], o: ResolvedOptions) -> OpSet:
    """
    Uses a PatternFiller (retrieved from getFiller) to fill the given polygons with a pattern,
    such as hachure, dots, or zigzag lines.
    """
    filler = getFiller(o, helper)
    return filler.fillPolygons(polygonList, o)


def patternFillArc(
    x: float,
    y: float,
    width: float,
    height: float,
    start: float,
    stop: float,
    o: ResolvedOptions,
) -> OpSet:
    """
    Returns an OpSet that, when rendered, fills an arc (or ellipse segment) with a pattern.
    The arc is approximated by subdividing into points along the perimeter, then filled
    via the chosen filler pattern.
    """
    cx = x
    cy = y
    rx = abs(width / 2.0)
    ry = abs(height / 2.0)
    rx += offsetOpt(rx * 0.01, o)
    ry += offsetOpt(ry * 0.01, o)
    strt = start
    stp = stop
    while strt < 0.0:
        strt += math.pi * 2.0
        stp += math.pi * 2.0
    if (stp - strt) > (math.pi * 2.0):
        strt = 0.0
        stp = math.pi * 2.0

    cstep = o.curveStepCount if o.curveStepCount is not None else 9
    inc = (stp - strt) / cstep
    points: List[Point] = []
    angle = strt

    # Build the arc perimeter
    while angle <= stp:
        px = cx + rx * math.cos(angle)
        py = cy + ry * math.sin(angle)
        points.append((px, py))
        angle += inc

    px2 = cx + rx * math.cos(stp)
    py2 = cy + ry * math.sin(stp)
    points.append((px2, py2))
    points.append((cx, cy))
    return patternFillPolygons([points], o)
