# rough/fillers/filler_interface.py
from __future__ import annotations
from typing import List
from ..core import ResolvedOptions, OpSet, Op
from ..geometry import Point


class PatternFiller:
    def fillPolygons(self, polygonList: List[List[Point]], o: ResolvedOptions) -> OpSet:
        raise NotImplementedError()


class RenderHelper:
    def randOffset(self, x: float, o: ResolvedOptions) -> float:
        raise NotImplementedError()

    def randOffsetWithRange(
        self, min_val: float, max_val: float, o: ResolvedOptions
    ) -> float:
        raise NotImplementedError()

    def ellipse(
        self, x: float, y: float, width: float, height: float, o: ResolvedOptions
    ) -> OpSet:
        raise NotImplementedError()

    def doubleLineOps(
        self, x1: float, y1: float, x2: float, y2: float, o: ResolvedOptions
    ) -> List[Op]:
        raise NotImplementedError()
