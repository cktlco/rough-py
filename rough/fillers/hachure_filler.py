# rough/fillers/hachure_filler.py
from __future__ import annotations
from typing import List
from ..core import ResolvedOptions, OpSet, Op
from ..geometry import Point
from .filler_interface import PatternFiller, RenderHelper
from .scan_line_hachure import polygon_hachure_lines


class HachureFiller(PatternFiller):
    def __init__(self, helper: RenderHelper) -> None:
        self.helper = helper

    def fillPolygons(self, polygonList: List[List[Point]], o: ResolvedOptions) -> OpSet:
        return self._fillPolygons(polygonList, o)

    def _fillPolygons(
        self, polygonList: List[List[Point]], o: ResolvedOptions
    ) -> OpSet:
        lines = polygon_hachure_lines(polygonList, o)
        ops = self.renderLines(lines, o)
        return OpSet("fillSketch", ops)

    def renderLines(
        self, lines: List[tuple[Point, Point]], o: ResolvedOptions
    ) -> List[Op]:
        ops = []
        for p1, p2 in lines:
            ops.extend(self.helper.doubleLineOps(p1[0], p1[1], p2[0], p2[1], o))
        return ops
