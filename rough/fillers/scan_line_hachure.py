# rough/fillers/scan_line_hachure.py
from __future__ import annotations
from typing import List, Optional
import math
from ..geometry import Point, Line
from ..core import ResolvedOptions
from ..math import Random


def polygon_hachure_lines(
    polygonList: List[List[Point]], o: ResolvedOptions
) -> List[Line]:
    """
    Produce hachure lines for each polygon in polygonList, using a NON-ZERO
    winding approach.
    """
    angle_base = o.hachureAngle if o.hachureAngle is not None else -41.0
    angle_deg = angle_base + 90.0

    if o.hachureGap is not None and o.hachureGap >= 0:
        gap = float(o.hachureGap)
    else:
        sw = o.strokeWidth if (o.strokeWidth is not None) else 2.0
        gap = sw * 4.0
    gap = max(gap, 0.1)

    angle_rad = math.radians(-angle_deg)

    all_lines: List[Line] = []

    for poly in polygonList:
        if len(poly) < 3:
            continue

        rpoly = [_rotatePoint(p, -angle_rad) for p in poly]
        minY = min(p[1] for p in rpoly)
        maxY = max(p[1] for p in rpoly)
        y: float = float(minY)

        while y <= maxY:
            crossing_data = _horizontalIntersectionsNonZero(rpoly, y)
            if not crossing_data:
                y += gap
                continue

            segments = []
            running_winding: float = 0
            prev_x: Optional[float] = None
            for cx, dW in crossing_data:
                inside_now = running_winding != 0
                if inside_now and prev_x is not None:
                    if cx > prev_x:
                        segments.append((prev_x, cx))
                running_winding += dW
                prev_x = cx

            for xstart, xend in segments:
                p1 = _rotatePoint((xstart, y), angle_rad)
                p2 = _rotatePoint((xend, y), angle_rad)
                all_lines.append((p1, p2))

            y += gap

    return all_lines


def _horizontalIntersectionsNonZero(
    rpoly: List[Point], scanY: float
) -> List[tuple[float, float]]:
    crossing_list: List[tuple[float, float]] = []
    length = len(rpoly)
    if length < 2:
        return crossing_list

    for i in range(length):
        p1 = rpoly[i]
        p2 = rpoly[(i + 1) % length]
        if _edge_intersects_scanline(p1, p2, scanY):
            xint = _xIntersect(p1, p2, scanY)
            if xint is not None:
                sign = +1 if (p2[1] > p1[1]) else -1
                crossing_list.append((xint, sign))

    crossing_list.sort(key=lambda c: c[0])
    return crossing_list


def _edge_intersects_scanline(p1: Point, p2: Point, scanY: float) -> bool:
    y1, y2 = p1[1], p2[1]
    if abs(y1 - y2) < 1e-14 and abs(y1 - scanY) < 1e-14:
        return False
    mn = min(y1, y2)
    mx = max(y1, y2)
    if scanY <= mn or scanY >= mx:
        return False
    return True


def _xIntersect(p1: Point, p2: Point, y: float) -> float | None:
    x1, y1 = p1
    x2, y2 = p2
    dy = y2 - y1
    if abs(dy) < 1e-14:
        return None
    t = (y - y1) / dy
    return x1 + t * (x2 - x1)


def _rotatePoint(p: Point, theta: float) -> Point:
    cosA = math.cos(theta)
    sinA = math.sin(theta)
    rx = p[0] * cosA - p[1] * sinA
    ry = p[0] * sinA + p[1] * cosA
    return (rx, ry)


def _getRandom(o: ResolvedOptions) -> float:
    if not hasattr(o, "_randHachureGen"):
        setattr(o, "_randHachureGen", Random(o.seed + 12345))
    randg = getattr(o, "_randHachureGen")
    return randg.next()
