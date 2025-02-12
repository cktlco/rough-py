# rough/fillers/zigzag_line_filler.py
from __future__ import annotations
from typing import List
import math
from ..core import ResolvedOptions, OpSet, Op
from ..geometry import Point, line_length
from .filler_interface import PatternFiller, RenderHelper
from .scan_line_hachure import polygon_hachure_lines


class ZigZagLineFiller(PatternFiller):
    def __init__(self, helper: RenderHelper) -> None:
        self.helper = helper

    def fillPolygons(self, polygonList: List[List[Point]], o: ResolvedOptions) -> OpSet:
        if o.hachureGap is not None and o.hachureGap >= 0:
            gap = o.hachureGap
        else:
            sw = o.strokeWidth if (o.strokeWidth is not None) else 2.0
            gap = sw * 4.0
        gap = float(gap)

        if o.zigzagOffset is not None and o.zigzagOffset >= 0:
            zo = o.zigzagOffset
        else:
            zo = gap
        zo = float(zo)

        temp = ResolvedOptions()
        for k, v in o.__dict__.items():
            setattr(temp, k, v)

        temp.hachureGap = gap + zo  # now both guaranteed float
        lines = polygon_hachure_lines(polygonList, temp)
        return OpSet("fillSketch", self._zigzagLines(lines, zo, temp))

    def _zigzagLines(
        self, lines: List[tuple[Point, Point]], zo: float, o: ResolvedOptions
    ) -> List[Op]:
        ops = []
        for ln in lines:
            length = line_length(ln)
            # no need to floor if we used round
            count = int(round(length / (2.0 * zo)))
            p1, p2 = ln
            if p1[0] > p2[0]:
                p1, p2 = p2, p1
            alpha = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
            for i in range(count):
                lstart = i * (2.0 * zo)
                lend = (i + 1) * (2.0 * zo)
                dz = math.sqrt(2.0 * (zo**2))
                sx = p1[0] + (lstart * math.cos(alpha))
                sy = p1[1] + (lstart * math.sin(alpha))
                ex = p1[0] + (lend * math.cos(alpha))
                ey = p1[1] + (lend * math.sin(alpha))
                mx = sx + dz * math.cos(alpha + math.pi / 4.0)
                my = sy + dz * math.sin(alpha + math.pi / 4.0)
                ops.extend(self.helper.doubleLineOps(sx, sy, mx, my, o))
                ops.extend(self.helper.doubleLineOps(mx, my, ex, ey, o))
        return ops
