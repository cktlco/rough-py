# variety of polygons and lines
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# triangle
tri_pts = [(20, 120), (100, 20), (180, 120)]
c.polygon(tri_pts, Options(stroke="blue", fill="#ffff66", fillStyle="hachure"))

# pentagon
pent_pts = [
    (220, 40),
    (260, 20),
    (300, 40),
    (290, 80),
    (230, 80),
]
c.polygon(pent_pts, Options(stroke="brown", fill="#ccffcc", fillStyle="solid"))

# random lines
c.line(330, 30, 360, 90, Options(strokeWidth=3, stroke="gray"))
c.line(340, 20, 370, 100, Options(strokeWidth=1, stroke="gray", roughness=3))

# ellipse with cross-hatch
c.ellipse(450, 60, 100, 60, Options(fill="#66bbff", fillStyle="cross-hatch"))

# closed arc in dotted fill
c.arc(550, 70, 50, 50, 0, 3.14, True, Options(fill="#ff9999", fillStyle="dots"))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example5.svg", "w") as f:
    f.write(svg_data)
