import math
from rough import canvas, Options, RoughCanvas

# demonstration of building a star shape from math, preserveVertices,
# and varied stroke/fill styling


def star_points(cx: float, cy: float, spikes: int, outer_r: float, inner_r: float):
    pts = []
    step = math.pi / spikes
    angle = 0.0
    for i in range(spikes * 2):
        r = outer_r if i % 2 == 0 else inner_r
        sx = cx + r * math.cos(angle)
        sy = cy + r * math.sin(angle)
        pts.append((sx, sy))
        angle += step
    return pts


c: RoughCanvas = canvas(600, 150)

# star shape with preserveVertices
pts = star_points(80, 80, spikes=5, outer_r=60, inner_r=25)
c.polygon(
    pts,
    Options(stroke="blue", fill="#fdd", fillStyle="zigzag-line", preserveVertices=True),
)

# smaller star with dashed stroke
pts2 = star_points(220, 80, spikes=7, outer_r=40, inner_r=15)
c.polygon(
    pts2,
    Options(
        stroke="green",
        strokeLineDash=[3, 3],
        fill="yellow",
        fillStyle="dots",
        roughness=1.5,
    ),
)

# line connecting the stars, using multi-stroke
c.line(80, 80, 220, 80, Options(stroke="black", roughness=2))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example22.svg", "w") as f:
    f.write(svg_data)
