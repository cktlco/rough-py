"""
Module defining the core classes and default configuration for rough-py, including
options, a drawing surface, and the primary data structures for commands and sets.
"""

from __future__ import annotations
from typing import Optional, List, Tuple

SVGNS = "http://www.w3.org/2000/svg"


class Config:
    """
    Holds global configuration for the library, wrapping user-provided options if present.
    """

    def __init__(self, options: Optional[Options] = None) -> None:
        self.options = options


class DrawingSurface:
    """
    Encapsulates a simple drawing surface with a defined width and height.
    """

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height


class Options:
    """
    Defines user-configurable drawing options, with all constructor arguments defaulting
    to None. Any non-None fields override the library defaults when creating shapes.
    """

    def __init__(
        self,
        maxRandomnessOffset: float | None = None,
        roughness: float | None = None,
        bowing: float | None = None,
        stroke: str | None = None,
        strokeWidth: float | None = None,
        curveFitting: float | None = None,
        curveTightness: float | None = None,
        curveStepCount: int | None = None,
        fill: str | None = None,
        fillStyle: str | None = None,
        fillWeight: float | None = None,
        hachureAngle: float | None = None,
        hachureGap: float | None = None,
        dashOffset: float | None = None,
        dashGap: float | None = None,
        zigzagOffset: float | None = None,
        fontFamily: str | None = None,
        fontSize: float | None = None,
        fontPath: str | None = None,
        fontWeight: str | None = None,
        gradientAngle: float | None = None,
        gradientSmoothness: float | None = None,
        seed: int | None = None,
        strokeLineDash: List[float] | None = None,
        strokeLineDashOffset: float | None = None,
        fillLineDash: List[float] | None = None,
        fillLineDashOffset: float | None = None,
        disableMultiStroke: bool | None = None,
        disableMultiStrokeFill: bool | None = None,
        preserveVertices: bool | None = None,
        fixedDecimalPlaceDigits: int | None = None,
        fillShapeRoughnessGain: float | None = None,
    ) -> None:
        self.maxRandomnessOffset = maxRandomnessOffset
        self.roughness = roughness
        self.bowing = bowing
        self.stroke = stroke
        self.strokeWidth = strokeWidth
        self.curveFitting = curveFitting
        self.curveTightness = curveTightness
        self.curveStepCount = curveStepCount
        self.fill = fill
        self.fillStyle = fillStyle
        self.fillWeight = fillWeight
        self.hachureAngle = hachureAngle
        self.hachureGap = hachureGap
        self.dashOffset = dashOffset
        self.dashGap = dashGap
        self.zigzagOffset = zigzagOffset
        self.fontFamily = fontFamily
        self.fontSize = fontSize
        self.fontPath = fontPath
        self.fontWeight = fontWeight
        self.gradientAngle = gradientAngle
        self.gradentSmoothness = gradientSmoothness
        self.seed = seed if seed is not None else 0
        self.strokeLineDash = strokeLineDash
        self.strokeLineDashOffset = strokeLineDashOffset
        self.fillLineDash = fillLineDash
        self.fillLineDashOffset = fillLineDashOffset
        self.disableMultiStroke = disableMultiStroke
        self.disableMultiStrokeFill = disableMultiStrokeFill
        self.preserveVertices = preserveVertices
        self.fixedDecimalPlaceDigits = fixedDecimalPlaceDigits
        self.fillShapeRoughnessGain = fillShapeRoughnessGain


class ResolvedOptions(Options):
    """
    Resolves and applies default values for any None fields in Options, ensuring
    the resulting configuration is fully specified.
    """

    def __init__(self) -> None:
        super().__init__(
            maxRandomnessOffset=None,
            roughness=None,
            bowing=None,
            stroke=None,
            strokeWidth=None,
            curveFitting=None,
            curveTightness=None,
            curveStepCount=None,
            fill=None,
            fillStyle=None,
            fillWeight=None,
            hachureAngle=None,
            hachureGap=None,
            dashOffset=None,
            dashGap=None,
            zigzagOffset=None,
            fontFamily=None,
            fontSize=None,
            fontPath=None,
            fontWeight=None,
            gradientAngle=None,
            gradientSmoothness=None,
            seed=0,
            strokeLineDash=None,
            strokeLineDashOffset=None,
            fillLineDash=None,
            fillLineDashOffset=None,
            disableMultiStroke=None,
            disableMultiStrokeFill=None,
            preserveVertices=None,
            fixedDecimalPlaceDigits=None,
            fillShapeRoughnessGain=None,
        )

        # Ensure gradientAngle and gradientSmoothness are set
        if not hasattr(self, "gradientAngle"):
            self.gradientAngle = 0.0
        if not hasattr(self, "gradientSmoothness"):
            self.gradientSmoothness = 1

        if self.maxRandomnessOffset is None:
            self.maxRandomnessOffset = 2
        if self.roughness is None:
            self.roughness = 1
        if self.bowing is None:
            self.bowing = 2

        # If stroke is None, default to "none" instead of black
        if self.stroke is None:
            self.stroke = "none"
        else:
            self.stroke = self.stroke or "#000"

        if self.strokeWidth is None:
            self.strokeWidth = 2.0
        if self.curveFitting is None:
            self.curveFitting = 0.95
        if self.curveTightness is None:
            self.curveTightness = 0.1
        if self.curveStepCount is None:
            self.curveStepCount = 9
        if self.fill is None:
            self.fill = None
        if self.fillStyle is None:
            self.fillStyle = "hachure"
        if self.fillWeight is None:
            self.fillWeight = 1.0
        if self.hachureAngle is None:
            self.hachureAngle = -41
        if self.hachureGap is None:
            self.hachureGap = 3.5
        if self.dashOffset is None:
            self.dashOffset = -1
        if self.dashGap is None:
            self.dashGap = -1
        if self.zigzagOffset is None:
            self.zigzagOffset = -1
        if self.fontFamily is None:
            self.fontFamily = "sans-serif"
        if self.fontSize is None:
            self.fontSize = 25
        if self.fontWeight is None:
            self.fontWeight = "normal"
        if self.gradientAngle is None:
            self.gradientAngle = 0
        if self.gradientSmoothness is None:
            self.gradentSmoothness = 1
        if self.strokeLineDash is None:
            self.strokeLineDash = []
        if self.strokeLineDashOffset is None:
            self.strokeLineDashOffset = 0
        if self.fillLineDash is None:
            self.fillLineDash = []
        if self.fillLineDashOffset is None:
            self.fillLineDashOffset = 0
        if self.disableMultiStroke is None:
            self.disableMultiStroke = False
        if self.disableMultiStrokeFill is None:
            self.disableMultiStrokeFill = False
        if self.preserveVertices is None:
            self.preserveVertices = False
        if self.fixedDecimalPlaceDigits is None:
            self.fixedDecimalPlaceDigits = None
        if self.fillShapeRoughnessGain is None:
            self.fillShapeRoughnessGain = 0.8

        # 1) If strokeWidth is 0 => hide stroke
        if self.strokeWidth == 0:
            self.stroke = "none"

        # 2) If stroke is 'none' and fill is None or 'none', provide a default stroke to ensure visibility
        if (self.stroke is None or self.stroke == "none") and (
            self.fill in [None, "", "none"]
        ):
            self.stroke = "#000"

        # 3) If fill is None or 'none' and stroke is also 'none', provide a default fill color
        if (self.fill is None or self.fill in ["none", ""]) and (
            self.stroke in [None, "", "none"]
        ):
            self.fill = "#0f0"


class Op:
    """
    Represents a drawing operation such as move, lineTo, or bcurveTo, along with its numeric data.
    """

    def __init__(self, op: str, data: List[float]) -> None:
        self.op = op
        self.data = data


class OpSet:
    """
    Groups a list of Op objects under a certain type, possibly including path or size info.
    """

    def __init__(self, type_: str, ops: List[Op]) -> None:
        self.type = type_
        self.ops = ops
        self.size: Tuple[float, float] | None = None
        self.path: str | None = None
        self.width: float | None = None
        self.height: float | None = None
        self.extras: dict = {}


class Drawable:
    """
    Encapsulates a shape name, the ResolvedOptions used for drawing, and
    the collection of operation sets needed to render the shape.

    The 'href' attribute can optionally hold a hyperlink reference if the shape
    is intended to be clickable in an exported SVG.
    """

    def __init__(self, shape: str, options: ResolvedOptions, sets: List[OpSet]) -> None:
        self.shape = shape
        self.options = options
        self.sets = sets
        self.href: Optional[str] = None  # used for linking shapes in SVG


class PathInfo:
    """
    Provides data for rendering a shape as an SVG path, including the path data string,
    stroke/fill colors, and any text content if the shape is textual.
    """

    def __init__(self, d: str, stroke: str, strokeWidth: float, fill: str = "") -> None:
        self.d = d
        self.stroke = stroke
        self.strokeWidth = strokeWidth
        self.fill = fill
        self.tag: str = "path"
        self.x: float = 0
        self.y: float = 0
        self.text: str = ""
        # extras is a dictionary for additional attributes like transforms, etc.
        self.extras: dict[str, str] = {}
