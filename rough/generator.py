"""
Provides a generator that approximates the multi-subpath fill behavior of Rough.js.

This module contains the RoughGenerator class, which merges global configuration
and local Options to produce Drawable objects for various shapes, arcs, paths, and text
elements. The shapes drawn by this generator have a "rough" or hand-sketched style.
"""

from __future__ import annotations
from typing import List, Optional, Union
import math

from .core import Config, Options, ResolvedOptions, Drawable, OpSet, Op, PathInfo
from .geometry import Point
from .math import random_seed
from .renderer import (
    line,
    rectangle,
    ellipseWithParams,
    generateEllipseParams,
    linearPath,
    arc,
    curve,
    polygon,
    svgPath,
    solidFillPolygon,
    patternFillPolygons,
    patternFillArc,
)

# ------------------------------------------------------------------------
# Check if fontTools is installed, so text outlines can be drawn if doOutline=True
# ------------------------------------------------------------------------
HAS_FONTTOOLS = False
try:
    from fontTools.ttLib import TTFont
    from fontTools.pens.basePen import BasePen

    HAS_FONTTOOLS = True
except ImportError:
    pass
# ------------------------------------------------------------------------


class RoughGenerator:
    """
    Provides shape-drawing methods returning Drawable objects with approximate
    hand-sketched styling. This class merges global configuration with local Options,
    ensuring shape settings like stroke, fill, and roughness have default values
    when not explicitly provided.

    :param config: An optional Config that may include global drawing Options.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config if config else Config()
        # Create a ResolvedOptions object with library defaults
        self.defaultOptions = ResolvedOptions()
        # If the config has user-provided options, merge those in
        if self.config.options:
            self._merge_options(self.config.options)

    @staticmethod
    def new_seed() -> int:
        """
        Returns a new random seed based on the library's math module.

        :return: An integer seed (pseudo-random).
        """
        return random_seed()

    def _merge_options(self, user_options: Options) -> None:
        """
        Copies any non-None fields from user_options onto self.defaultOptions.
        """
        for k, v in user_options.__dict__.items():
            if v is not None:
                setattr(self.defaultOptions, k, v)

    def _o(self, options: Optional[Options]) -> ResolvedOptions:
        """
        Merges defaultOptions with optionally provided Options, ensuring
        that shapes are not rendered invisible.
        """
        ro = ResolvedOptions()
        # Copy default options first
        for k, v in self.defaultOptions.__dict__.items():
            if v is not None:
                setattr(ro, k, v)
        # Then override with local Options
        if options:
            for k, v in options.__dict__.items():
                if v is not None:
                    setattr(ro, k, v)

        # Minimal check to avoid invisible shapes:
        if ro.strokeWidth == 0:
            ro.stroke = "none"
        if (ro.stroke is None or ro.stroke == "none") and (
            ro.fill in [None, "", "none"]
        ):
            ro.stroke = "#000"
        if (ro.fill is None or ro.fill in ["none", ""]) and (
            ro.stroke in [None, "", "none"]
        ):
            ro.fill = "#0f0"

        return ro

    def line(
        self, x1: float, y1: float, x2: float, y2: float, options: Options | None = None
    ) -> Drawable:
        """
        Creates a rough-styled line from (x1, y1) to (x2, y2).

        :param x1: The start point x-coordinate.
        :param y1: The start point y-coordinate.
        :param x2: The end point x-coordinate.
        :param y2: The end point y-coordinate.
        :param options: Optional drawing Options for this shape.
        :return: A Drawable containing the line data.
        """
        o = self._o(options)
        opset = line(x1, y1, x2, y2, o)
        return Drawable("line", o, [opset])

    def rectangle(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        options: Options | None = None,
    ) -> Drawable:
        """
        Creates a rough rectangle at (x, y) with dimensions width × height.

        :param x: The top-left x-coordinate of the rectangle.
        :param y: The top-left y-coordinate of the rectangle.
        :param width: The rectangle's width.
        :param height: The rectangle's height.
        :param options: Optional drawing Options for this shape.
        :return: A Drawable representing the rectangle.
        """
        o = self._o(options)
        sets: List[OpSet] = []
        outline = rectangle(x, y, width, height, o)
        # Decide whether to fill the rectangle
        if o.fill:
            pts = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
            if o.fillStyle == "solid":
                sets.append(solidFillPolygon([pts], o))
            else:
                sets.append(patternFillPolygons([pts], o))
        # If stroke is not 'none', add the outline opset
        if o.stroke != "none":
            sets.append(outline)
        return Drawable("rectangle", o, sets)

    def ellipse(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        options: Options | None = None,
    ) -> Drawable:
        """
        Creates a rough ellipse centered at (x, y) with total width and height.

        :param x: The center x-coordinate.
        :param y: The center y-coordinate.
        :param width: The total horizontal diameter of the ellipse.
        :param height: The total vertical diameter of the ellipse.
        :param options: Optional drawing Options for this shape.
        :return: A Drawable for the ellipse.
        """
        o = self._o(options)
        sets: List[OpSet] = []
        params = generateEllipseParams(width, height, o)
        e_ops, e_points = ellipseWithParams(x, y, o, params)

        if o.fill:
            if o.fillStyle == "solid":
                fill_op = ellipseWithParams(x, y, o, params)[0]
                fill_op.type = "fillPath"
                sets.append(fill_op)
            else:
                sets.append(patternFillPolygons([e_points], o))

        if o.stroke != "none":
            sets.append(e_ops)
        return Drawable("ellipse", o, sets)

    def circle(
        self, x: float, y: float, diameter: float, options: Options | None = None
    ) -> Drawable:
        """
        Creates a rough circle centered at (x, y) with the given diameter.

        :param x: The center x-coordinate of the circle.
        :param y: The center y-coordinate of the circle.
        :param diameter: The circle's diameter.
        :param options: Optional drawing Options for this shape.
        :return: A Drawable for the circle.
        """
        d = self.ellipse(x, y, diameter, diameter, options)
        d.shape = "circle"
        return d

    def linearPath(
        self, points: List[Point], options: Options | None = None
    ) -> Drawable:
        """
        Creates a linear path (polyline) through the given list of points.

        :param points: A list of (x, y) coordinates.
        :param options: Optional drawing Options for this shape.
        :return: A Drawable for the linear path.
        """
        o = self._o(options)
        opset = linearPath(points, False, o)
        return Drawable("linearPath", o, [opset])

    def arc(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        start: float,
        stop: float,
        closed: bool = False,
        options: Options | None = None,
    ) -> Drawable:
        """
        Creates a rough arc or ellipse segment. The ellipse is centered at (x, y)
        with total width and height. The arc goes from angle `start` to `stop` (radians).

        :param x: Center x-coordinate.
        :param y: Center y-coordinate.
        :param width: The total width of the ellipse for the arc.
        :param height: The total height of the ellipse for the arc.
        :param start: Start angle in radians.
        :param stop: Stop angle in radians.
        :param closed: If True, closes the arc back to the center for a pie-slice shape.
        :param options: Optional drawing Options for this shape.
        :return: A Drawable representing the arc.
        """
        o = self._o(options)
        sets: List[OpSet] = []
        outline = arc(x, y, width, height, start, stop, closed, True, o)

        # If closed and fill is set, add the fill ops
        if closed and o.fill:
            if o.fillStyle == "solid":
                fill_o = ResolvedOptions()
                for k, v in o.__dict__.items():
                    setattr(fill_o, k, v)
                fill_o.disableMultiStroke = True
                shape = arc(x, y, width, height, start, stop, True, False, fill_o)
                shape.type = "fillPath"
                sets.append(shape)
            else:
                sets.append(patternFillArc(x, y, width, height, start, stop, o))

        if o.stroke != "none":
            sets.append(outline)
        return Drawable("arc", o, sets)

    def curve(
        self,
        points: Union[List[Point], List[List[Point]]],
        options: Options | None = None,
    ) -> Drawable:
        """
        Creates one or more rough curves through the specified points. If the input
        is a list of (x,y) points, it creates a single curve. If it is a list of list
        of points, it creates multiple curve segments.

        :param points: A list of points or a list of lists of points.
        :param options: Optional drawing Options for the curve.
        :return: A Drawable for the curve.
        """
        o = self._o(options)
        sets: List[OpSet] = []
        outline = curve(points, o)

        # If there's a fill, handle it (solid or pattern).
        if o.fill and o.fill != "none":
            if o.fillStyle == "solid":
                fill_ops = curve(points, self._solidFillHelper(o))
                fill_ops.type = "fillPath"
                sets.append(fill_ops)
            else:
                poly_points = self._approxCurveAsPoints(points, o)
                if poly_points:
                    sets.append(patternFillPolygons([poly_points], o))
        if o.stroke != "none":
            sets.append(outline)
        return Drawable("curve", o, sets)

    def polygon(self, points: List[Point], options: Options | None = None) -> Drawable:
        """
        Creates a rough polygon through the list of points, automatically
        closing the shape.

        :param points: A list of (x, y) coordinates for the polygon.
        :param options: Optional drawing Options for this shape.
        :return: A Drawable representing the polygon.
        """
        o = self._o(options)
        sets: List[OpSet] = []
        outline = polygon(points, o)

        if o.fill:
            if o.fillStyle == "solid":
                sets.append(solidFillPolygon([points], o))
            else:
                sets.append(patternFillPolygons([points], o))

        if o.stroke != "none":
            sets.append(outline)
        return Drawable("polygon", o, sets)

    def path(self, d: str, options: Options | None = None) -> Drawable:
        """
        Creates a rough path from an SVG path string.

        :param d: The SVG path string (e.g. "M10 10 H 90 V 90 H 10 Z").
        :param options: Optional drawing Options for the path.
        :return: A Drawable for the path.
        """
        o = self._o(options)
        sets: List[OpSet] = []

        # Return early if the path string is empty
        if not d.strip():
            return Drawable("path", o, sets)

        # Compute stroke and fill opsets
        has_stroke = o.stroke != "none"
        stroke_opset = svgPath(d, o)

        has_fill = o.fill and o.fill not in ["none", "transparent"]
        if has_fill:
            fill_o = ResolvedOptions()
            for k, v in o.__dict__.items():
                setattr(fill_o, k, v)
            fill_o.disableMultiStroke = True
            fill_o.roughness = (o.roughness or 1.0) + (o.fillShapeRoughnessGain or 0.8)

            fill_ops_raw = svgPath(d, fill_o).ops
            if o.fillStyle == "solid":
                fill_set = OpSet("fillPath", fill_ops_raw)
                sets.append(fill_set)
            else:
                poly = self._approxPathSingle(d, fill_o)
                if len(poly) > 2:
                    sets.append(patternFillPolygons([poly], fill_o))

        if has_stroke:
            sets.append(stroke_opset)
        return Drawable("path", o, sets)

    def opsToPath(self, drawing: OpSet, fixedDecimals: int | None = None) -> str:
        """
        Converts an OpSet to an SVG path data string.

        :param drawing: The OpSet containing line/bcurve operations.
        :param fixedDecimals: If set, numeric coordinates are rounded to this many decimals.
        :return: The SVG path data string.
        """
        path: List[str] = []
        for op in drawing.ops:
            data = op.data
            # Optionally round the coordinates for a cleaner path string
            if fixedDecimals is not None and fixedDecimals >= 0:
                data = [round(x, fixedDecimals) for x in data]
            if op.op == "move":
                path.append(f"M{data[0]} {data[1]}")
            elif op.op == "bcurveTo":
                path.append(
                    f"C{data[0]} {data[1]}, {data[2]} {data[3]}, {data[4]} {data[5]}"
                )
            elif op.op == "lineTo":
                path.append(f"L{data[0]} {data[1]}")
        return " ".join(path).strip()

    def toPaths(self, drawable: Drawable) -> List[PathInfo]:
        """
        Converts a Drawable into a list of PathInfo objects suitable for SVG rendering.

        :param drawable: The Drawable to convert.
        :return: A list of PathInfo objects containing path data, stroke/fill info, etc.
        """
        sets = drawable.sets
        o = drawable.options
        result: List[PathInfo] = []

        for drawing in sets:
            path_info = None
            if drawing.type == "path":
                p = self.opsToPath(drawing, o.fixedDecimalPlaceDigits)
                stroke_val = o.stroke if o.stroke is not None else "none"
                sw_val = o.strokeWidth if o.strokeWidth is not None else 2.0
                path_info = PathInfo(p, stroke_val, sw_val, "")
            elif drawing.type == "fillPath":
                p = self.opsToPath(drawing, o.fixedDecimalPlaceDigits)
                fill_color = o.fill if (o.fill is not None and o.fill != "") else "none"
                path_info = PathInfo(p, "none", 0.0, fill_color)
            elif drawing.type == "fillSketch":
                path_info = self._fillSketchPath(drawing, o)
            elif drawing.type in ["textPath", "textOutline"]:
                # Outlined text is treated like a path
                p = self.opsToPath(drawing, o.fixedDecimalPlaceDigits)
                stroke_val = o.stroke if o.stroke else "none"
                sw_val = o.strokeWidth if o.strokeWidth else 1.0
                fill_val = o.fill if o.fill else "none"
                path_info = PathInfo(p, stroke_val, sw_val, fill_val)
                path_info.tag = "path"
            elif drawing.type == "text":
                # Fallback text is rendered differently
                pinfo = PathInfo("", "none", 0.0, "none")
                pinfo.tag = "text"
                if hasattr(drawing, "size") and drawing.size:
                    pinfo.x = drawing.size[0]
                    pinfo.y = drawing.size[1]
                else:
                    pinfo.x = 0
                    pinfo.y = 0
                if hasattr(drawing, "path"):
                    pinfo.text = drawing.path or ""
                else:
                    pinfo.text = ""
                pinfo.stroke = o.stroke if o.stroke else "none"
                pinfo.fill = o.fill if o.fill else "none"
                pinfo.strokeWidth = o.strokeWidth if o.strokeWidth else 1.0
                if hasattr(drawing, "extras") and drawing.extras:
                    pinfo.extras = dict(drawing.extras)
                result.append(pinfo)
                continue

            if path_info:
                result.append(path_info)

        return result

    def _fillSketchPath(self, drawing: OpSet, o: ResolvedOptions) -> PathInfo:
        """
        Converts a 'fillSketch' OpSet into a PathInfo object.
        """
        fweight = o.fillWeight if o.fillWeight is not None else 1.0
        if fweight < 0.0:
            fweight = (o.strokeWidth if o.strokeWidth else 2.0) * 0.5
        d_str = self.opsToPath(drawing, o.fixedDecimalPlaceDigits)
        fill_col = o.fill if o.fill else "none"
        return PathInfo(d_str, fill_col, fweight, "none")

    def _solidFillHelper(self, o: ResolvedOptions) -> ResolvedOptions:
        """
        Clones the given ResolvedOptions and adjusts them for a solid fill.
        This is used internally to create a filled path for the shapes that
        use 'solid' fill styling.
        """
        fill_o = ResolvedOptions()
        for k, v in o.__dict__.items():
            setattr(fill_o, k, v)
        fill_o.disableMultiStroke = True
        fill_o.roughness = (o.roughness or 1.0) + (o.fillShapeRoughnessGain or 0.8)
        return fill_o

    def _approxCurveAsPoints(
        self, points: Union[List[Point], List[List[Point]]], o: ResolvedOptions
    ) -> List[Point]:
        """
        Approximates a set of curves as a flattened list of points,
        for use in pattern-filling the shape.
        """
        if not points:
            return []
        # If the first element is a float, assume it's a single list of (x,y).
        if isinstance(points[0][0], float):
            return points  # type: ignore
        # If it's a list of lists, flatten them
        out: List[Point] = []
        for seg in points:  # type: ignore
            if isinstance(seg, tuple):
                out.append(seg)
            else:
                out.extend(seg)
        return out

    def _approxPathSingle(
        self, d: str, o: ResolvedOptions
    ) -> List[tuple[float, float]]:
        """
        Approximates a single path definition into a list of points for pattern fill.
        """
        if not d.strip():
            return []
        fill_o = ResolvedOptions()
        for k, v in o.__dict__.items():
            setattr(fill_o, k, v)
        fill_o.disableMultiStroke = True

        # Re-use the same svgPath from renderer
        opset = svgPath(d, fill_o).ops
        poly = self._sampleSubpathAll(opset)
        return poly

    def _sampleSubpathAll(self, ops: List[Op]) -> List[tuple[float, float]]:
        """
        Converts a sequence of ops (move, lineTo, bcurveTo) into a list of points
        that approximate the shape's outline, for pattern or fill usage.
        """
        pts: List[tuple[float, float]] = []
        if not ops:
            return pts

        # Start from the first move op
        cx, cy = ops[0].data[0], ops[0].data[1]
        pts.append((cx, cy))

        for op in ops[1:]:
            if op.op == "move":
                nx, ny = op.data
                pts.append((nx, ny))
                cx, cy = nx, ny
            elif op.op == "lineTo":
                x, y = op.data
                seg_len = math.hypot(x - cx, y - cy)
                steps = max(2, int(seg_len / 4))
                # Linear interpolation along the line segment
                for s in range(1, steps + 1):
                    t = s / float(steps)
                    xx = cx + t * (x - cx)
                    yy = cy + t * (y - cy)
                    pts.append((xx, yy))
                cx, cy = x, y
            elif op.op == "bcurveTo":
                x1, y1, x2, y2, x3, y3 = op.data
                steps = 20  # fixed approximation steps for cubic
                for s in range(1, steps + 1):
                    t = s / float(steps)
                    xx, yy = self._pointOnCubic(cx, cy, x1, y1, x2, y2, x3, y3, t)
                    pts.append((xx, yy))
                cx, cy = x3, y3
        return pts

    def _pointOnCubic(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        t: float,
    ) -> tuple[float, float]:
        """
        Returns the point on the cubic Bezier defined by (x0,y0), (x1,y1), (x2,y2), (x3,y3)
        at the parameter t, where 0 <= t <= 1.
        """
        mt = 1.0 - t
        mt2 = mt * mt
        t2 = t * t
        a = mt * mt2
        b = 3.0 * mt2 * t
        c = 3.0 * mt * t2
        d = t * t2
        bx = (a * x0) + (b * x1) + (c * x2) + (d * x3)
        by = (a * y0) + (b * y1) + (c * y2) + (d * y3)
        return (bx, by)

    def text(
        self,
        x: float,
        y: float,
        textStr: str,
        options: Options | None = None,
        embed_outline: bool = False,
        align: str = "left",
        valign: str = "baseline",
    ) -> Drawable:
        """
        Draws text at (x, y). If embed_outline=True and fontTools is available along
        with a valid TTF font path in options.fontPath, the text is approximated
        by polygons for each glyph. Otherwise, fallback to <text> rendering.

        :param x: The anchor x-position for text alignment.
        :param y: The anchor y-position for text alignment.
        :param textStr: The text content to render.
        :param options: Optional drawing Options (e.g. fontSize, fontPath).
        :param embed_outline: Whether to render text by polygon outlines (requires fontTools).
        :param align: Horizontal alignment: "left", "center", or "right".
        :param valign: Vertical alignment: "baseline", "top", "middle", or "bottom".
        :return: A Drawable representing the text or text outline geometry.
        """
        o = self._o(options)
        # If no fontTools or user didn't request outlines => fallback
        if not embed_outline or not HAS_FONTTOOLS:
            return self._makeSimpleTextDrawable(x, y, textStr, o, align, valign)

        # Outline-based approach
        try:
            font_file = getattr(o, "fontPath", None)
            if not font_file:
                return self._makeSimpleTextDrawable(x, y, textStr, o, align, valign)

            font = TTFont(font_file)
            if "glyf" not in font or "cmap" not in font:
                return self._makeSimpleTextDrawable(x, y, textStr, o, align, valign)

            glyf = font["glyf"]
            cmap = font.getBestCmap()
            head = font["head"]
            unitsPerEm = head.unitsPerEm
            asc = 0
            desc = 0
            if "OS/2" in font:
                os2 = font["OS/2"]
                asc = os2.sTypoAscender
                desc = os2.sTypoDescender
            textHeight = asc - desc if asc > 0 else unitsPerEm
            if textHeight <= 0:
                textHeight = unitsPerEm

            scale = (o.fontSize or 16.0) / float(textHeight)
            hmtx = font["hmtx"]

            class ApproxPen(BasePen):
                """
                A simple pen that approximates curves with small line segments,
                storing the resulting polygonal contours in self.contours.
                """

                def __init__(self, glyphSet):
                    super().__init__(glyphSet)
                    self.contours: List[List[Point]] = []
                    self.current: List[Point] = []

                def _moveTo(self, pt) -> None:
                    if self.current:
                        self.contours.append(self.current)
                    self.current = [pt]

                def _lineTo(self, pt) -> None:
                    self.current.append(pt)

                def _curveToOne(self, p1, p2, p3) -> None:
                    segs = 10
                    cpts = self._cubicApprox(self._currentPoint, p1, p2, p3, segs)
                    self.current.extend(cpts[1:])

                def _qCurveToOne(self, p1, p2) -> None:
                    segs = 10
                    qpts = self._quadApprox(self._currentPoint, p1, p2, segs)
                    self.current.extend(qpts[1:])

                def _closePath(self) -> None:
                    if self.current:
                        self.contours.append(self.current)
                    self.current = []

                @property
                def _currentPoint(self) -> Point:
                    if self.current:
                        return self.current[-1]
                    return (0, 0)

                def _cubicApprox(self, s, c1, c2, e, segments) -> List[Point]:
                    pts = []
                    for i in range(segments + 1):
                        t = i / segments
                        mt = 1.0 - t
                        a_ = mt * mt * mt
                        b_ = 3 * mt * mt * t
                        c_ = 3 * mt * t * t
                        d_ = t * t * t
                        x = a_ * s[0] + b_ * c1[0] + c_ * c2[0] + d_ * e[0]
                        y = a_ * s[1] + b_ * c1[1] + c_ * c2[1] + d_ * e[1]
                        pts.append((x, y))
                    return pts

                def _quadApprox(self, s, c, e, segments) -> List[Point]:
                    pts = []
                    for i in range(segments + 1):
                        t = i / segments
                        mt = 1.0 - t
                        x = mt * mt * s[0] + 2 * mt * t * c[0] + t * t * e[0]
                        y = mt * mt * s[1] + 2 * mt * t * c[1] + t * t * e[1]
                        pts.append((x, y))
                    return pts

            finalSets: List[OpSet] = []
            base_x = x
            base_y = y
            cursor_x = 0.0

            # Track bounding box for final alignment
            min_x = math.inf
            max_x = -math.inf
            min_y = math.inf
            max_y = -math.inf

            # Generate polygons for each glyph in the text
            for ch in textStr:
                if ch == " ":
                    space_advance = 0.35 * (o.fontSize or 16.0)
                    cursor_x += space_advance
                    continue
                cc = ord(ch)
                if cc not in cmap:
                    continue
                glyphName = cmap[cc]
                if glyphName not in glyf:
                    continue

                pen = ApproxPen(glyf)
                glyf[glyphName].draw(pen, glyf)
                aw, _lsb = hmtx[glyphName]

                allContours: List[List[Point]] = []
                # Convert pen.contours into actual x,y points
                for cont in pen.contours:
                    if len(cont) < 2:
                        continue
                    newC = []
                    for ox, oy in cont:
                        nx = base_x + cursor_x + (ox * scale)
                        ny = base_y - (oy * scale)
                        newC.append((nx, ny))
                    # Ensure the polygon is closed if not already
                    if len(newC) > 1 and newC[0] != newC[-1]:
                        newC.append(newC[0])
                    allContours.append(newC)

                # Update bounding box
                for cpoly in allContours:
                    for px, py in cpoly:
                        if px < min_x:
                            min_x = px
                        if px > max_x:
                            max_x = px
                        if py < min_y:
                            min_y = py
                        if py > max_y:
                            max_y = py

                # Fill and stroke for this glyph
                fillOps: List[OpSet] = []
                strokeOps: List[OpSet] = []

                # Fill polygons if fill is specified
                if o.fill and o.fill != "none":
                    if o.fillStyle == "solid":
                        fillOps.append(solidFillPolygon(allContours, o))
                    else:
                        fillOps.append(patternFillPolygons(allContours, o))

                # Draw stroke if stroke is not 'none'
                if o.stroke and o.stroke != "none":
                    for poly in allContours:
                        if len(poly) > 1:
                            polyN = poly[:]
                            # Remove last point if it's a repeat of the first
                            if polyN[0] == polyN[-1]:
                                polyN = polyN[:-1]
                            polyDraw = self.polygon(polyN, o)
                            strokeOps.extend(polyDraw.sets)

                finalSets.extend(fillOps)
                finalSets.extend(strokeOps)
                # Advance cursor by glyph's advance width
                cursor_x += aw * scale

            # If there were no valid glyphs found, fallback to simple text
            if min_x == math.inf or max_x == -math.inf:
                return self._makeSimpleTextDrawable(x, y, textStr, o, align, valign)

            text_width = max_x - min_x
            text_height = max_y - min_y

            # Shift geometry to implement alignment
            shift_x = 0.0
            shift_y = 0.0
            if align == "center":
                shift_x = -text_width / 2.0
            elif align == "right":
                shift_x = -text_width
            if valign == "middle":
                shift_y = -text_height / 2.0
            elif valign == "bottom":
                shift_y = -text_height

            if abs(shift_x) > 1e-9 or abs(shift_y) > 1e-9:
                for opset in finalSets:
                    for op in opset.ops:
                        if not op.data:
                            continue
                        if op.op in ("move", "lineTo"):
                            op.data[0] += shift_x
                            op.data[1] += shift_y
                        elif op.op == "bcurveTo":
                            op.data[0] += shift_x
                            op.data[1] += shift_y
                            op.data[2] += shift_x
                            op.data[3] += shift_y
                            op.data[4] += shift_x
                            op.data[5] += shift_y

            # Set the first OpSet's size to store the text bounding box for future references
            if finalSets:
                finalSets[0].size = (min_x + shift_x, min_y + shift_y)
                finalSets[0].width = text_width
                finalSets[0].height = text_height

            return Drawable("textOutline", o, finalSets)

        except Exception:
            # On any error, fallback to a simple <text> rendering
            return self._makeSimpleTextDrawable(x, y, textStr, o, align, valign)

    def _makeSimpleTextDrawable(
        self,
        x: float,
        y: float,
        textStr: str,
        o: ResolvedOptions,
        align: str,
        valign: str,
    ) -> Drawable:
        """
        Fallback text => uses a simple <text> element at (x, y).
        The alignment offsets x,y as needed to match 'align'/'valign'.
        """
        approx_width = len(textStr) * (o.fontSize * 0.6)  # naive estimate
        approx_height = float(o.fontSize)

        # Adjust (x,y) based on horizontal and vertical alignment
        shift_x = 0.0
        shift_y = 0.0
        if align == "center":
            shift_x = -approx_width / 2.0
        elif align == "right":
            shift_x = -approx_width
        if valign == "middle":
            shift_y = -approx_height / 2.0
        elif valign == "bottom":
            shift_y = -approx_height

        final_x = x + shift_x
        final_y = y + shift_y

        # Create an OpSet of type 'text' to store the fallback text data
        text_opset = OpSet("text", [])
        text_opset.size = (final_x, final_y)
        text_opset.path = textStr  # The text string is stored in .path for rendering
        text_opset.width = approx_width
        text_opset.height = approx_height

        return Drawable("text", o, [text_opset])
