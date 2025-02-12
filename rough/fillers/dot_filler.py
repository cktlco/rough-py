# rough/fillers/dot_filler.py
from __future__ import annotations
from typing import List
import math, random
from ..core import ResolvedOptions, OpSet, Op
from ..geometry import Point, line_length
from .filler_interface import PatternFiller, RenderHelper
from .scan_line_hachure import polygon_hachure_lines


class DotFiller(PatternFiller):
    def __init__(self, helper: RenderHelper) -> None:
        self.helper = helper

    def fillPolygons(self, polygonList: List[List[Point]], o: ResolvedOptions) -> OpSet:
        temp = ResolvedOptions()
        for k, v in o.__dict__.items():
            setattr(temp, k, v)
        temp.hachureAngle = 0
        lines = polygon_hachure_lines(polygonList, temp)
        return self._dotsOnLines(lines, o)

    def _dotsOnLines(
        self, lines: List[tuple[Point, Point]], o: ResolvedOptions
    ) -> OpSet:
        ops = []
        if o.hachureGap is not None and o.hachureGap >= 0:
            gap = o.hachureGap
        else:
            sw = o.strokeWidth if o.strokeWidth is not None else 2.0
            gap = sw * 4.0
        gap = float(gap)
        gap = max(gap, 0.1)

        if o.fillWeight is not None and o.fillWeight >= 0:
            fweight = float(o.fillWeight)
        else:
            sw2 = o.strokeWidth if o.strokeWidth is not None else 2.0
            fweight = sw2 * 0.5

        ro = gap / 4.0
        for ln in lines:
            length = line_length(ln)
            # if length < gap, count might be 0 => that's fine
            count = int(math.ceil(length / gap)) - 1
            if count < 0:
                count = 0
            offset = length - (count * gap)

            # we treat x as a float
            x = ((ln[0][0] + ln[1][0]) * 0.5) - (gap * 0.25)
            minY = min(ln[0][1], ln[1][1])
            for i in range(count):
                y = minY + offset + (i * gap)
                cx = (x - ro) + random.random() * (2.0 * ro)
                cy = (y - ro) + random.random() * (2.0 * ro)
                # ellipse requires float
                el = self.helper.ellipse(cx, cy, fweight, fweight, o)
                ops.extend(el.ops)
        return OpSet("fillSketch", ops)
