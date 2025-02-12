# rough/fillers/filler.py
from __future__ import annotations
from ..core import ResolvedOptions
from .filler_interface import PatternFiller, RenderHelper
from .hachure_filler import HachureFiller
from .zigzag_filler import ZigZagFiller
from .hatch_filler import HatchFiller
from .dot_filler import DotFiller
from .dashed_filler import DashedFiller
from .zigzag_line_filler import ZigZagLineFiller

_fillers_cache: dict[str, PatternFiller] = {}


def getFiller(o: ResolvedOptions, helper: RenderHelper) -> PatternFiller:
    fillerName = o.fillStyle or "hachure"
    if fillerName not in _fillers_cache:
        if fillerName == "zigzag":
            _fillers_cache[fillerName] = ZigZagFiller(helper)
        elif fillerName == "cross-hatch":
            _fillers_cache[fillerName] = HatchFiller(helper)
        elif fillerName == "dots":
            _fillers_cache[fillerName] = DotFiller(helper)
        elif fillerName == "dashed":
            _fillers_cache[fillerName] = DashedFiller(helper)
        elif fillerName == "zigzag-line":
            _fillers_cache[fillerName] = ZigZagLineFiller(helper)
        else:
            # default
            fillerName = "hachure"
            _fillers_cache[fillerName] = HachureFiller(helper)
    return _fillers_cache[fillerName]
