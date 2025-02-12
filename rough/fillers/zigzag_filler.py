# rough/fillers/zigzag_filler.py
from __future__ import annotations
from typing import List
import math
from ..core import ResolvedOptions, OpSet
from ..geometry import Point, line_length
from .hachure_filler import HachureFiller
from .scan_line_hachure import polygon_hachure_lines


class ZigZagFiller(HachureFiller):
    def fillPolygons(self, polygonList: List[List[Point]], o: ResolvedOptions) -> OpSet:
        if o.hachureGap is not None and o.hachureGap >= 0:
            gap = float(o.hachureGap)
        else:
            sw = o.strokeWidth if o.strokeWidth is not None else 2.0
            gap = sw * 4.0
        gap = max(gap, 0.1)

        o2 = ResolvedOptions()
        for k, v in o.__dict__.items():
            setattr(o2, k, v)
        o2.hachureGap = gap

        lines = polygon_hachure_lines(polygonList, o2)

        # ensure hachureAngle is float
        base_ang = o2.hachureAngle if o2.hachureAngle is not None else -41.0
        zigzagAngle = (math.pi / 180.0) * base_ang

        zigzagLines = []
        dgx = gap * 0.5 * math.cos(zigzagAngle)
        dgy = gap * 0.5 * math.sin(zigzagAngle)

        for p1, p2 in lines:
            if line_length((p1, p2)) > 0:
                zigzagLines.append(((p1[0] - dgx, p1[1] + dgy), p2))
                zigzagLines.append(((p1[0] + dgx, p1[1] - dgy), p2))
        ops = self.renderLines(zigzagLines, o2)
        return OpSet("fillSketch", ops)
