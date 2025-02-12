# demonstration of preserveVertices for sharper corners
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# polygon with normal corners
pts1 = [(20, 20), (80, 40), (60, 80), (20, 100)]
c.polygon(pts1, Options(fill="lime"))

# polygon with preserve vertices
pts2 = [(120, 20), (180, 40), (160, 80), (120, 100)]
c.polygon(pts2, Options(fill="#ccf", stroke="blue", preserveVertices=True))

# circle normal
c.circle(280, 60, 50, Options(fill="yellow"))

# circle preserve vertices (less visible effect on circles, but shown anyway)
c.circle(380, 60, 50, Options(fill="gold", preserveVertices=True))

# line path preserve vertices
line_pts = [(480, 30), (520, 40), (510, 90), (470, 80)]
c.linearPath(line_pts, Options(stroke="red", preserveVertices=True))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example14.svg", "w") as f:
    f.write(svg_data)
