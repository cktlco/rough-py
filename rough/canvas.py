"""
This module provides the RoughCanvas class, which manages drawing operations
with rough, hand-drawn styling, along with a FakeCanvasContext for transformations.
"""

from __future__ import annotations
from typing import Optional, List, Tuple
import math

from .core import Config, Options, ResolvedOptions, Drawable
from .generator import RoughGenerator
from .geometry import Point
from .math import Random


class FakeCanvasContext:
    """
    Maintains and applies a simple 3×3 transformation matrix for scaling, rotating,
    and translating drawn shapes. This class is used to transform shapes on the
    RoughCanvas before they are rendered or exported.
    """

    def __init__(self) -> None:
        # Initialize with the identity matrix.
        self._matrix: List[float] = [1, 0, 0, 0, 1, 0, 0, 0, 1]

    def translate(self, dx: float, dy: float) -> None:
        """
        Applies a translation by (dx, dy) to the current transformation matrix.
        """
        tm = [1, 0, dx, 0, 1, dy, 0, 0, 1]
        self._matrix = _matrixMultiply(self._matrix, tm)

    def scale(self, sx: float, sy: float) -> None:
        """
        Applies a scaling by factors (sx, sy) to the current transformation matrix.
        """
        sm = [sx, 0, 0, 0, sy, 0, 0, 0, 1]
        self._matrix = _matrixMultiply(self._matrix, sm)

    def rotate(self, angle_radians: float) -> None:
        """
        Applies a rotation by angle_radians to the current transformation matrix.
        """
        c = math.cos(angle_radians)
        s = math.sin(angle_radians)
        rm = [c, -s, 0, s, c, 0, 0, 0, 1]
        self._matrix = _matrixMultiply(self._matrix, rm)

    def resetTransform(self) -> None:
        """
        Resets the current transformation matrix to the identity.
        """
        self._matrix = [1, 0, 0, 0, 1, 0, 0, 0, 1]

    def currentTransform(self) -> List[float]:
        """
        Returns a copy of the current 3×3 transformation matrix in row-major form.
        """
        return list(self._matrix)


def _matrixMultiply(m1: List[float], m2: List[float]) -> List[float]:
    """
    Multiplies two 3×3 matrices (in row-major form): result = m1 × m2.
    Returns the resulting 3×3 matrix in row-major form.
    """
    return [
        m1[0] * m2[0] + m1[1] * m2[3] + m1[2] * m2[6],
        m1[0] * m2[1] + m1[1] * m2[4] + m1[2] * m2[7],
        m1[0] * m2[2] + m1[1] * m2[5] + m1[2] * m2[8],
        m1[3] * m2[0] + m1[4] * m2[3] + m1[5] * m2[6],
        m1[3] * m2[1] + m1[4] * m2[4] + m1[5] * m2[7],
        m1[3] * m2[2] + m1[4] * m2[5] + m1[5] * m2[8],
        m1[6] * m2[0] + m1[7] * m2[3] + m1[8] * m2[6],
        m1[6] * m2[1] + m1[7] * m2[4] + m1[8] * m2[7],
        m1[6] * m2[2] + m1[7] * m2[5] + m1[8] * m2[8],
    ]


def _transformXY(x: float, y: float, mat: List[float]) -> Tuple[float, float]:
    """
    Applies the 3×3 matrix 'mat' to the point (x, y). The point is assumed
    to be (x, y, 1) in homogeneous coordinates.
    """
    x2 = x * mat[0] + y * mat[1] + mat[2]
    y2 = x * mat[3] + y * mat[4] + mat[5]
    return (x2, y2)


def _matrixAsSvgTransform(m: List[float]) -> str:
    """
    Converts a 3×3 matrix [a,b,c, d,e,f, g,h,i] in row-major order into
    an SVG transform string of the form 'matrix(a d b e c f)' for 2D usage.
    """
    a = m[0]
    b = m[1]
    c = m[2]
    d = m[3]
    e = m[4]
    f = m[5]
    return f"matrix({a} {d} {b} {e} {c} {f})"


def _applyMatrixToDrawable(drawable: Drawable, matrix: List[float]) -> None:
    """
    Applies the given transformation matrix to the coordinates of the Drawable in-place.
    For text (fallback text shapes), the matrix is stored as an SVG transform rather
    than directly applied to the numeric x,y coordinates.
    """
    for opset in drawable.sets:
        if opset.type == "text":
            # For fallback text, store the transform matrix instead of rewriting x,y
            if opset.size:
                if not hasattr(opset, "extras") or opset.extras is None:
                    opset.extras = {}
                opset.extras["transform"] = _matrixAsSvgTransform(matrix)
            continue

        if opset.type in ("textPath", "path", "fillPath", "fillSketch", "textOutline"):
            for op in opset.ops:
                if not op.data:
                    continue
                if op.op in ("move", "lineTo"):
                    x, y = op.data
                    nx, ny = _transformXY(x, y, matrix)
                    op.data = [nx, ny]
                elif op.op == "bcurveTo":
                    cx1, cy1, cx2, cy2, ex, ey = op.data
                    cx1n, cy1n = _transformXY(cx1, cy1, matrix)
                    cx2n, cy2n = _transformXY(cx2, cy2, matrix)
                    exn, eyn = _transformXY(ex, ey, matrix)
                    op.data = [cx1n, cy1n, cx2n, cy2n, exn, eyn]


class RoughCanvas:
    """
    A canvas-like class for drawing rough, hand-sketched styled shapes. Holds
    a transformation context (ctx) and a list of draw calls that can be rendered
    to an SVG.

    :param width: The logical width of the canvas.
    :param height: The logical height of the canvas.
    :param config: Optional configuration for rough drawing.
    """

    def __init__(self, width: int, height: int, config: Config | None = None) -> None:
        self.width: int = width
        self.height: int = height
        self.gen: RoughGenerator = RoughGenerator(config)
        # Stores (z_index, Drawable) so shapes can be sorted by z-index on export:
        self.draw_calls: List[Tuple[int, Drawable]] = []
        self.ctx: FakeCanvasContext = FakeCanvasContext()

    def getDefaultOptions(self) -> ResolvedOptions:
        """
        Retrieves the default ResolvedOptions used by the underlying RoughGenerator.
        """
        return self.gen.defaultOptions

    def draw(self, drawable: Drawable, z_index: int = 0) -> None:
        """
        Appends a Drawable to the list of shapes to be drawn on this canvas,
        along with its specified z-index (drawing order).
        """
        self.draw_calls.append((z_index, drawable))

    def link(self, drawable: Drawable, href: str, z_index: int = 0) -> Drawable:
        """
        Wraps the given drawable in an <a> tag with 'href', making the shape clickable
        in the final SVG. The shape is then drawn with the specified z-index.
        """
        drawable.href = href
        _applyMatrixToDrawable(drawable, self.ctx.currentTransform())
        self.draw(drawable, z_index)
        return drawable

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        options: Options | None = None,
        z_index: int = 0,
    ) -> Drawable:
        """
        Draws a rough line between the points (x1, y1) and (x2, y2).
        """
        d = self.gen.line(x1, y1, x2, y2, options)
        _applyMatrixToDrawable(d, self.ctx.currentTransform())
        self.draw(d, z_index)
        return d

    def rectangle(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        options: Options | None = None,
        z_index: int = 0,
    ) -> Drawable:
        """
        Draws a rough rectangle at (x, y) with width w and height h.
        """
        d = self.gen.rectangle(x, y, w, h, options)
        _applyMatrixToDrawable(d, self.ctx.currentTransform())
        self.draw(d, z_index)
        return d

    def ellipse(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        options: Options | None = None,
        z_index: int = 0,
    ) -> Drawable:
        """
        Draws a rough ellipse centered at (x, y) with total width w and height h.
        """
        d = self.gen.ellipse(x, y, w, h, options)
        _applyMatrixToDrawable(d, self.ctx.currentTransform())
        self.draw(d, z_index)
        return d

    def circle(
        self,
        x: float,
        y: float,
        diameter: float,
        options: Options | None = None,
        z_index: int = 0,
    ) -> Drawable:
        """
        Draws a rough circle centered at (x, y) with the specified diameter.
        """
        d = self.gen.circle(x, y, diameter, options)
        _applyMatrixToDrawable(d, self.ctx.currentTransform())
        self.draw(d, z_index)
        return d

    def linearPath(
        self,
        points: List[Tuple[float, float]],
        options: Options | None = None,
        z_index: int = 0,
    ) -> Drawable:
        """
        Draws a rough polyline (or open path) through a list of points.
        """
        d = self.gen.linearPath(points, options)
        _applyMatrixToDrawable(d, self.ctx.currentTransform())
        self.draw(d, z_index)
        return d

    def polygon(
        self,
        points: List[Tuple[float, float]],
        options: Options | None = None,
        z_index: int = 0,
    ) -> Drawable:
        """
        Draws a rough polygon through the provided list of points,
        automatically closing the shape.
        """
        d = self.gen.polygon(points, options)
        _applyMatrixToDrawable(d, self.ctx.currentTransform())
        self.draw(d, z_index)
        return d

    def arc(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        start: float,
        stop: float,
        closed: bool = False,
        options: Options | None = None,
        z_index: int = 0,
    ) -> Drawable:
        """
        Draws a rough arc or ellipse segment from angle start to angle stop, with optional closure.
        The arc is centered at (x, y), with total width w, height h.
        """
        d = self.gen.arc(x, y, w, h, start, stop, closed, options)
        _applyMatrixToDrawable(d, self.ctx.currentTransform())
        self.draw(d, z_index)
        return d

    def curve(
        self,
        points: List[Tuple[float, float]],
        options: Options | None = None,
        z_index: int = 0,
    ) -> Drawable:
        """
        Draws a rough curve through the list of points. The curve can consist of multiple
        segments if the points array contains sub-arrays (though typically just one list).
        """
        d = self.gen.curve(points, options)
        _applyMatrixToDrawable(d, self.ctx.currentTransform())
        self.draw(d, z_index)
        return d

    def path(
        self,
        d_str: str,
        options: Options | None = None,
        z_index: int = 0,
    ) -> Drawable:
        """
        Draws a rough shape from an SVG path string (d_str).
        """
        d = self.gen.path(d_str, options)
        _applyMatrixToDrawable(d, self.ctx.currentTransform())
        self.draw(d, z_index)
        return d

    def text(
        self,
        x: float,
        y: float,
        textStr: str,
        options: Options | None = None,
        embed_outline: bool = False,
        align: str = "left",
        valign: str = "baseline",
        z_index: int = 0,
    ) -> Drawable:
        """
        Draws text at position (x, y). By default, it uses a fallback <text> element,
        unless embed_outline=True and a valid TTF font is provided via fontPath in the
        options, in which case it outlines the text geometry directly.
        """
        d = self.gen.text(
            x,
            y,
            textStr,
            options,
            embed_outline=embed_outline,
            align=align,
            valign=valign,
        )
        _applyMatrixToDrawable(d, self.ctx.currentTransform())
        self.draw(d, z_index)
        return d

    def as_svg(
        self,
        width: int,
        height: int,
        auto_fit: bool = True,
        auto_fit_margin: float = 20,
    ) -> str:
        """
        Exports the current list of Drawables to an SVG string.
        The shapes are sorted by z_index ascending, so higher z_index shapes
        are output later and appear above others.

        :param width: The output SVG width attribute.
        :param height: The output SVG height attribute.
        :param auto_fit: If True, attempts to auto-scale and fit all drawn shapes
                         within the SVG, leaving a margin.
        :param auto_fit_margin: Margin used for auto-fit calculations.
        :return: A string containing an <svg> element with the rendered shapes.
        """
        svg_lines: List[str] = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        ]

        if auto_fit:
            self.auto_fit(margin=auto_fit_margin)

        # Sort by z_index ascending so shapes with higher z_index come last.
        sorted_calls = sorted(self.draw_calls, key=lambda pair: pair[0])

        gradient_defs: List[str] = []
        shapeGradCount: int = 0

        for z_i, drawable in sorted_calls:
            o = drawable.options

            # Check if fill or stroke is a list => treat as gradient stops.
            fill_is_gradient = isinstance(o.fill, list) and len(o.fill) > 0
            stroke_is_gradient = isinstance(o.stroke, list) and len(o.stroke) > 0

            if fill_is_gradient or stroke_is_gradient:
                shapeGradCount += 1
                gradID = f"roughGradient{shapeGradCount}"

                # Compute bounding box of shape to place gradient effectively.
                min_x, min_y, max_x, max_y = self._computeDrawableBounds(drawable)
                bw = max_x - min_x
                bh = max_y - min_y
                if bw < 1e-9:
                    bw = 1.0
                if bh < 1e-9:
                    bh = 1.0

                colorList: str | list = (o.fill if fill_is_gradient else o.stroke) or ""

                angleDeg = getattr(o, "gradientAngle", 0.0)
                aRad = math.radians(angleDeg)
                x2Abs = math.cos(aRad) * bw
                y2Abs = math.sin(aRad) * bh

                gradSmooth = int(getattr(o, "gradientSmoothness", 1))
                if gradSmooth < 1:
                    gradSmooth = 1

                finalStops: List[Tuple[float, str]] = []
                totalSegments = (len(colorList) - 1) * gradSmooth
                if totalSegments < 1:
                    totalSegments = 1
                stepEach = 100.0 / float(totalSegments)
                accum = 0.0
                for segI in range(len(colorList) - 1):
                    cA = colorList[segI]
                    cB = colorList[segI + 1]
                    for s in range(gradSmooth):
                        t = s / float(gradSmooth)
                        offset = accum + t * stepEach
                        if t < 1:
                            finalStops.append((offset, cA))
                        else:
                            finalStops.append((offset, cB))
                    accum += stepEach
                finalStops.append((100.0, colorList[-1]))

                stopsXML: List[str] = []
                usedOffsets = set()
                for off, col in finalStops:
                    if off not in usedOffsets:
                        usedOffsets.add(off)
                        stopsXML.append(
                            f'    <stop offset="{off:.1f}%" stop-color="{col}" />'
                        )

                gradientXML = f"""
  <linearGradient id="{gradID}" gradientUnits="userSpaceOnUse"
                  x1="0" y1="0" x2="{x2Abs:.6f}" y2="{y2Abs:.6f}"
                  gradientTransform="translate({min_x:.6f},{min_y:.6f})">
{chr(10).join(stopsXML)}
  </linearGradient>
"""
                gradient_defs.append(gradientXML)
                if fill_is_gradient:
                    o.fill = f"url(#{gradID})"
                if stroke_is_gradient:
                    o.stroke = f"url(#{gradID})"

            # If the drawable has an href, wrap <a> around it in SVG.
            if drawable.href:
                svg_lines.append(f'  <a href="{drawable.href}">')

            path_infos = self.gen.toPaths(drawable)

            for pinfo in path_infos:
                stroke_val = pinfo.stroke if pinfo.stroke else "none"
                fill_val = pinfo.fill if pinfo.fill else "none"
                swidth = pinfo.strokeWidth
                dpath = pinfo.d if pinfo.d else ""

                if pinfo.tag == "text":
                    # Rendering text as <text> in the SVG.
                    textColor = fill_val if fill_val != "none" else "#000"
                    fontSize = getattr(o, "fontSize", 16) or 16
                    fontFamily = getattr(o, "fontFamily", "sans-serif")
                    fontWeight = getattr(o, "fontWeight", "normal")

                    transform_attr = ""
                    if getattr(pinfo, "extras", None):
                        if "transform" in pinfo.extras:
                            transform_attr = f' transform="{pinfo.extras["transform"]}"'

                    extra2 = ""
                    if getattr(pinfo, "extras", None):
                        for kk, vv in pinfo.extras.items():
                            if kk == "transform":
                                continue
                            extra2 += f' {kk}="{vv}"'

                    fontWeight_str = (
                        "" if fontWeight == "normal" else f' font-weight="{fontWeight}"'
                    )

                    # If shape is linked, do not suppress pointer events.
                    if drawable.href:
                        style_str = 'style="user-select: none;"'
                    else:
                        style_str = 'style="pointer-events: none; user-select: none;"'

                    svg_lines.append(
                        f'  <text x="{pinfo.x}" y="{pinfo.y}" fill="{textColor}" '
                        f'font-size="{fontSize}" font-family="{fontFamily}"{fontWeight_str}'
                        f"{transform_attr}{extra2} {style_str}>"
                        f"{pinfo.text}</text>"
                    )
                else:
                    # Rendering shapes as <path>
                    path_attrs = [
                        f'd="{dpath}"',
                        f'stroke="{stroke_val}"',
                        f'stroke-width="{swidth}"',
                        f'fill="{fill_val}"',
                    ]
                    extra_attrs = ""
                    if getattr(pinfo, "extras", None):
                        for kex, vex in pinfo.extras.items():
                            if kex == "transform":
                                continue
                            extra_attrs += f' {kex}="{vex}"'

                    is_fillSketch = (
                        stroke_val != "none"
                        and stroke_val == (o.fill or "none")
                        and swidth
                        == (
                            o.fillWeight
                            if (o.fillWeight is not None and o.fillWeight >= 0)
                            else (o.strokeWidth or 2.0) * 0.5
                        )
                    )

                    dasharray = ""
                    dashoffset = 0.0
                    if is_fillSketch:
                        if o.fillLineDash and len(o.fillLineDash) > 0:
                            dash_vals = " ".join(str(v) for v in o.fillLineDash)
                            dasharray = dash_vals
                        dashoffset = o.fillLineDashOffset or 0.0
                    else:
                        if o.strokeLineDash and len(o.strokeLineDash) > 0:
                            dash_vals = " ".join(str(v) for v in o.strokeLineDash)
                            dasharray = dash_vals
                        dashoffset = o.strokeLineDashOffset or 0.0

                    if dasharray:
                        path_attrs.append(f'stroke-dasharray="{dasharray}"')
                    if dashoffset != 0.0:
                        path_attrs.append(f'stroke-dashoffset="{dashoffset}"')

                    svg_lines.append(f'  <path {" ".join(path_attrs)}{extra_attrs} />')

            if drawable.href:
                svg_lines.append("  </a>")

        if gradient_defs:
            svg_lines.insert(1, "  <defs>\n" + "".join(gradient_defs) + "  </defs>\n")

        svg_lines.append("</svg>")
        return "\n".join(svg_lines)

    def auto_fit(self, margin: float = 0.0) -> None:
        """
        Attempts to scale and translate all geometry so that the entire bounding box
        of drawn shapes fits within the canvas dimensions, leaving the specified margin.
        """
        if not self.draw_calls:
            return

        min_x = math.inf
        max_x = -math.inf
        min_y = math.inf
        max_y = -math.inf

        # Scan all shapes to find the overall bounding box.
        for _, drawable in self.draw_calls:
            for opset in drawable.sets:
                if opset.type == "text":
                    # For fallback text, use size + transform.
                    if opset.size:
                        tx, ty = opset.size
                        transform_str = ""
                        if hasattr(opset, "extras") and opset.extras:
                            transform_str = opset.extras.get("transform", "")
                        # If transform is a matrix(...), parse it.
                        if transform_str.startswith("matrix("):
                            nums = transform_str[7:-1].split()
                            if len(nums) == 6:
                                a = float(nums[0])
                                d_ = float(nums[1])
                                b = float(nums[2])
                                e_ = float(nums[3])
                                c_ = float(nums[4])
                                f_ = float(nums[5])
                                px = a * tx + b * ty + c_
                                py = d_ * tx + e_ * ty + f_
                                if px < min_x:
                                    min_x = px
                                if px > max_x:
                                    max_x = px
                                if py < min_y:
                                    min_y = py
                                if py > max_y:
                                    max_y = py
                                if opset.width and opset.height:
                                    bx = tx + opset.width
                                    by = ty + opset.height
                                    px2 = a * bx + b * by + c_
                                    py2 = d_ * bx + e_ * by + f_
                                    if px2 < min_x:
                                        min_x = px2
                                    if px2 > max_x:
                                        max_x = px2
                                    if py2 < min_y:
                                        min_y = py2
                                    if py2 > max_y:
                                        max_y = py2
                            else:
                                # If matrix parse fails, just use tx,ty bounding box approach.
                                if tx < min_x:
                                    min_x = tx
                                if tx > max_x:
                                    max_x = tx
                                if ty < min_y:
                                    min_y = ty
                                if ty > max_y:
                                    max_y = ty
                                if opset.width and opset.height:
                                    bx = tx + opset.width
                                    by = ty + opset.height
                                    if bx < min_x:
                                        min_x = bx
                                    if bx > max_x:
                                        max_x = bx
                                    if by < min_y:
                                        min_y = by
                                    if by > max_y:
                                        max_y = by
                        else:
                            # No transform => bounding box is at (tx,ty).
                            if tx < min_x:
                                min_x = tx
                            if tx > max_x:
                                max_x = tx
                            if ty < min_y:
                                min_y = ty
                            if ty > max_y:
                                max_y = ty
                            if opset.width and opset.height:
                                bx = tx + opset.width
                                by = ty + opset.height
                                if bx < min_x:
                                    min_x = bx
                                if bx > max_x:
                                    max_x = bx
                                if by < min_y:
                                    min_y = by
                                if by > max_y:
                                    max_y = by
                    continue

                # For regular path/bcurve ops, collect min/max points.
                for op in opset.ops:
                    data = op.data
                    if not data:
                        continue
                    if op.op in ("move", "lineTo"):
                        x, y = data
                        if x < min_x:
                            min_x = x
                        if x > max_x:
                            max_x = x
                        if y < min_y:
                            min_y = y
                        if y > max_y:
                            max_y = y
                    elif op.op == "bcurveTo":
                        x1, y1, x2, y2, x3, y3 = data
                        for xx, yy in [(x1, y1), (x2, y2), (x3, y3)]:
                            if xx < min_x:
                                min_x = xx
                            if xx > max_x:
                                max_x = xx
                            if yy < min_y:
                                min_y = yy
                            if yy > max_y:
                                max_y = yy

        if math.isinf(min_x) or math.isinf(min_y):
            return

        bbox_width = max_x - min_x
        bbox_height = max_y - min_y
        if bbox_width < 1e-9 and bbox_height < 1e-9:
            return

        w = self.width
        h = self.height
        sx = (w - 2 * margin) / bbox_width
        sy = (h - 2 * margin) / bbox_height
        scale = min(sx, sy)
        offset_x = margin - scale * min_x
        offset_y = margin - scale * min_y

        # Apply scale/translate to the shapes in-place.
        for _, drawable in self.draw_calls:
            for opset in drawable.sets:
                if opset.type == "text":
                    # Adjust fallback text with a transform matrix if possible.
                    if opset.size:
                        transform_str = ""
                        if hasattr(opset, "extras") and opset.extras:
                            transform_str = opset.extras.get("transform", "")
                        if transform_str.startswith("matrix("):
                            nums = transform_str[7:-1].split()
                            if len(nums) == 6:
                                a = float(nums[0])
                                d_ = float(nums[1])
                                b = float(nums[2])
                                e_ = float(nums[3])
                                c_ = float(nums[4])
                                f_ = float(nums[5])
                                T = [1, 0, offset_x, 0, 1, offset_y, 0, 0, 1]
                                S = [scale, 0, 0, 0, scale, 0, 0, 0, 1]
                                TS = _matrixMultiply(T, S)
                                Mcur = [a, b, c_, d_, e_, f_, 0, 0, 1]
                                Mfinal = _matrixMultiply(TS, Mcur)
                                opset.extras["transform"] = _matrixAsSvgTransform(
                                    Mfinal
                                )
                    continue

                for op in opset.ops:
                    data = op.data
                    if not data:
                        continue
                    if op.op in ("move", "lineTo"):
                        x, y = data
                        x1 = scale * x + offset_x
                        y1 = scale * y + offset_y
                        op.data = [x1, y1]
                    elif op.op == "bcurveTo":
                        x1, y1, x2, y2, x3, y3 = data
                        x1n = scale * x1 + offset_x
                        y1n = scale * y1 + offset_y
                        x2n = scale * x2 + offset_x
                        y2n = scale * y2 + offset_y
                        x3n = scale * x3 + offset_x
                        y3n = scale * y3 + offset_y
                        op.data = [x1n, y1n, x2n, y2n, x3n, y3n]

    def _computeDrawableBounds(
        self, drawable: Drawable
    ) -> Tuple[float, float, float, float]:
        """
        Computes the bounding box of a single Drawable, returning (min_x, min_y, max_x, max_y).
        """
        min_x = math.inf
        max_x = -math.inf
        min_y = math.inf
        max_y = -math.inf

        for opset in drawable.sets:
            if opset.type == "text":
                # For fallback text, use size + transform.
                if opset.size:
                    tx, ty = opset.size
                    transform_str = ""
                    if hasattr(opset, "extras") and opset.extras:
                        transform_str = opset.extras.get("transform", "")
                    if transform_str.startswith("matrix("):
                        nums = transform_str[7:-1].split()
                        if len(nums) == 6:
                            a = float(nums[0])
                            d_ = float(nums[1])
                            b = float(nums[2])
                            e_ = float(nums[3])
                            c_ = float(nums[4])
                            f_ = float(nums[5])
                            px = a * tx + b * ty + c_
                            py = d_ * tx + e_ * ty + f_
                            if px < min_x:
                                min_x = px
                            if px > max_x:
                                max_x = px
                            if py < min_y:
                                min_y = py
                            if py > max_y:
                                max_y = py
                            if opset.width and opset.height:
                                bx = tx + opset.width
                                by = ty + opset.height
                                px2 = a * bx + b * by + c_
                                py2 = d_ * bx + e_ * by + f_
                                if px2 < min_x:
                                    min_x = px2
                                if px2 > max_x:
                                    max_x = px2
                                if py2 < min_y:
                                    min_y = py2
                                if py2 > max_y:
                                    max_y = py2
                        else:
                            # If the matrix parse fails, just handle tx, ty
                            if tx < min_x:
                                min_x = tx
                            if tx > max_x:
                                max_x = tx
                            if ty < min_y:
                                min_y = ty
                            if ty > max_y:
                                max_y = ty
                            if opset.width and opset.height:
                                bx = tx + opset.width
                                by = ty + opset.height
                                if bx < min_x:
                                    min_x = bx
                                if bx > max_x:
                                    max_x = bx
                                if by < min_y:
                                    min_y = by
                                if by > max_y:
                                    max_y = by
                    else:
                        # No transform => bounding box is simply (tx, ty).
                        if tx < min_x:
                            min_x = tx
                        if tx > max_x:
                            max_x = tx
                        if ty < min_y:
                            min_y = ty
                        if ty > max_y:
                            max_y = ty
                        if opset.width and opset.height:
                            bx = tx + opset.width
                            by = ty + opset.height
                            if bx < min_x:
                                min_x = bx
                            if bx > max_x:
                                max_x = bx
                            if by < min_y:
                                min_y = by
                            if by > max_y:
                                max_y = by
                continue

            # For standard move/line/bcurve ops, gather min/max among all control points.
            for op in opset.ops:
                data = op.data
                if not data:
                    continue
                if op.op in ("move", "lineTo"):
                    x, y = data
                    if x < min_x:
                        min_x = x
                    if x > max_x:
                        max_x = x
                    if y < min_y:
                        min_y = y
                    if y > max_y:
                        max_y = y
                elif op.op == "bcurveTo":
                    x1, y1, x2, y2, x3, y3 = data
                    for xx, yy in [(x1, y1), (x2, y2), (x3, y3)]:
                        if xx < min_x:
                            min_x = xx
                        if xx > max_x:
                            max_x = xx
                        if yy < min_y:
                            min_y = yy
                        if yy > max_y:
                            max_y = yy

        # If still infinite, this means there's no valid geometry (no move/line data).
        if math.isinf(min_x) or math.isinf(min_y):
            min_x = 0
            min_y = 0
            max_x = 0
            max_y = 0

        return (min_x, min_y, max_x, max_y)
