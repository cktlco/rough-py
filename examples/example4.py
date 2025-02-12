# showcase multiple arcs and elliptical shapes
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# big ellipse, hatch fill
c.ellipse(80, 60, 120, 80, Options(fill="#ffcc99", fillStyle="hachure", stroke="#333"))

# partial arc
c.arc(200, 100, 60, 80, 0, 1.57, False, Options(stroke="red", strokeWidth=2.5))

# arc with fill, closed
c.arc(300, 80, 70, 70, 3.14, 4.71, True, Options(fill="lightgreen", stroke="#666"))

# circle with no stroke, just fill
c.circle(420, 60, 50, Options(stroke="none", fill="#ff66cc", fillStyle="solid"))

# rectangle with dotted fill
c.rectangle(500, 30, 80, 100, Options(fill="#ddd", fillStyle="dots", stroke="#999"))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example4.svg", "w") as f:
    f.write(svg_data)
