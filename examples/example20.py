from rough import canvas, Options, RoughCanvas

# demonstration of arcs and paths
c: RoughCanvas = canvas(600, 150)

# big arc
c.arc(100, 100, 200, 180, 0, 3.14, False, Options(stroke="purple", strokeWidth=2))

# second overlapping arc
c.arc(150, 100, 220, 180, 1.57, 4.71, False, Options(stroke="orange"))

# another path
d_str: str = "M 220 50 L 300 50 C 320 80, 360 80, 380 50 Z"
c.path(d_str, Options(fill="#ccf"))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example20.svg", "w") as f:
    f.write(svg_data)
