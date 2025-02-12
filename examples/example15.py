# large swirl path plus arcs
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# swirl-like path
swirl: str = "M 20 100 C 50 20, 100 20, 130 100 S 180 180, 210 100 S 260 20, 290 100"
c.path(swirl, Options(stroke="purple", strokeWidth=2))

# arcs with random angles
c.arc(340, 60, 60, 60, 0.2, 2.6, False, Options(stroke="green"))
c.arc(420, 70, 80, 80, 1.8, 3.14, True, Options(fill="#ffdddd", stroke="red"))
c.arc(500, 80, 60, 60, 0, 1.0, False, Options(stroke="blue"))

# circle with zigzag-line fill
c.circle(560, 70, 40, Options(fillStyle="zigzag-line", fill="#ccc"))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example15.svg", "w") as f:
    f.write(svg_data)
