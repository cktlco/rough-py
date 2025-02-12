# rough/fillers/dashed_filler.py
from __future__ import annotations
from typing import List
import math
from ..core import ResolvedOptions, OpSet, Op
from ..geometry import Point, line_length
from .filler_interface import PatternFiller, RenderHelper
from .scan_line_hachure import polygon_hachure_lines


class DashedFiller(PatternFiller):
    def __init__(self, helper: RenderHelper) -> None:
        self.helper = helper

    def fillPolygons(self, polygonList: List[List[Point]], o: ResolvedOptions) -> OpSet:
        lines = polygon_hachure_lines(polygonList, o)
        return OpSet("fillSketch", self._dashedLine(lines, o))

    def _dashedLine(
        self, lines: List[tuple[Point, Point]], o: ResolvedOptions
    ) -> List[Op]:
        if o.dashOffset is not None and o.dashOffset >= 0:
            offset = float(o.dashOffset)
        else:
            # fallback to hachureGap or strokeWidth*4
            if o.hachureGap is not None and o.hachureGap >= 0:
                offset = float(o.hachureGap)
            else:
                sw = o.strokeWidth if o.strokeWidth is not None else 2.0
                offset = sw * 4.0

        if o.dashGap is not None and o.dashGap >= 0:
            gap = float(o.dashGap)
        else:
            if o.hachureGap is not None and o.hachureGap >= 0:
                gap = float(o.hachureGap)
            else:
                sw = o.strokeWidth if o.strokeWidth is not None else 2.0
                gap = sw * 4.0

        ops = []
        for ln in lines:
            length = line_length(ln)
            # avoid division by zero
            denom = (offset + gap) if (offset + gap) != 0 else 0.00001
            count = int(math.floor(length / denom))
            startOffset = (length + gap - (count * (offset + gap))) * 0.5
            p1, p2 = ln
            if p1[0] > p2[0]:
                p1, p2 = p2, p1
            alpha = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
            for i in range(count):
                lstart = i * (offset + gap)
                lend = lstart + offset
                sx = (
                    p1[0] + (lstart * math.cos(alpha)) + (startOffset * math.cos(alpha))
                )
                sy = (
                    p1[1] + (lstart * math.sin(alpha)) + (startOffset * math.sin(alpha))
                )
                ex = p1[0] + (lend * math.cos(alpha)) + (startOffset * math.cos(alpha))
                ey = p1[1] + (lend * math.sin(alpha)) + (startOffset * math.sin(alpha))
                ops.extend(self.helper.doubleLineOps(sx, sy, ex, ey, o))
        return ops
