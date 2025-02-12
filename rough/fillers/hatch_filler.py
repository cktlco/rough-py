# rough/fillers/hatch_filler.py
from __future__ import annotations
from typing import List
from ..core import ResolvedOptions, OpSet
from ..geometry import Point
from .hachure_filler import HachureFiller


class HatchFiller(HachureFiller):
    def fillPolygons(self, polygonList: List[List[Point]], o: ResolvedOptions) -> OpSet:
        set1 = self._fillPolygons(polygonList, o)
        o2 = ResolvedOptions()
        for k, v in o.__dict__.items():
            setattr(o2, k, v)
        base_ang = o.hachureAngle if o.hachureAngle is not None else -41.0
        o2.hachureAngle = base_ang + 90.0
        set2 = self._fillPolygons(polygonList, o2)
        set1.ops.extend(set2.ops)
        return set1
