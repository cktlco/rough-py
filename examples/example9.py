# combining linear paths and arcs
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# linear path
points = [(10, 20), (60, 40), (40, 80), (20, 100)]
c.linearPath(points, Options(stroke="#666", strokeWidth=2))

# second linear path with fill
points2 = [(100, 30), (140, 20), (160, 60), (120, 90)]
c.linearPath(points2, Options(stroke="blue", fill="#cff", fillStyle="dashed"))

# closed arc with dotted fill
c.arc(250, 80, 70, 50, 0, 1.57, True, Options(fill="pink", fillStyle="dots"))

# open arc
c.arc(350, 60, 100, 100, 3.14, 5.0, False, Options(stroke="orange"))

# random line
c.line(480, 30, 580, 100, Options(stroke="brown", strokeWidth=3))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example9.svg", "w") as f:
    f.write(svg_data)
