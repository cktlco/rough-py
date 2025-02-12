# arcs with assorted fill and stroke details
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# large arc half circle
c.arc(60, 100, 100, 100, 0, 3.14, False, Options(stroke="#dd4444", strokeWidth=3))

# closed arc
c.arc(180, 80, 100, 80, 1.57, 2.8, True, Options(fill="#ffaaaa", fillStyle="zigzag"))

# small arcs repeated
c.arc(300, 60, 40, 40, 0, 1.0, False, Options(stroke="#666"))
c.arc(360, 60, 40, 40, 1.0, 2.0, False, Options(stroke="#666"))
c.arc(420, 60, 40, 40, 2.0, 3.14, False, Options(stroke="#666"))

# final arc closed with fill
c.arc(520, 80, 60, 60, 3.14, 4.71, True, Options(fill="#ccffcc", stroke="gray"))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example11.svg", "w") as f:
    f.write(svg_data)
