# explore different fill styles and line transformations
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# dashed rectangle
c.rectangle(
    20, 30, 100, 60, Options(stroke="black", fill="lightblue", fillStyle="dashed")
)

# filled ellipse in cross-hatch
c.ellipse(200, 60, 100, 60, Options(fill="#88cc88", fillStyle="cross-hatch"))

# polygon with zigzag fill
pts = [(320, 20), (390, 30), (380, 90), (310, 80)]
c.polygon(pts, Options(stroke="navy", fill="#cccc00", fillStyle="zigzag"))

# arc with no fill, thick stroke
c.arc(460, 60, 80, 80, 0, 2.14, False, Options(stroke="magenta", strokeWidth=4))

# line path with preserve vertices
line_points = [(540, 20), (570, 40), (560, 80), (530, 60)]
c.linearPath(line_points, Options(stroke="brown", preserveVertices=True))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example3.svg", "w") as f:
    f.write(svg_data)
