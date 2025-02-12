# using custom dash patterns for strokes
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# line with dash pattern
c.line(20, 20, 100, 80, Options(stroke="darkred", strokeWidth=3, strokeLineDash=[6, 4]))

# rectangle with dash offset
c.rectangle(
    120,
    30,
    80,
    100,
    Options(strokeLineDash=[8, 3], strokeLineDashOffset=4, fill="#ffeecc"),
)

# polygon with fill dash
poly_pts = [(240, 20), (280, 40), (270, 80), (230, 70)]
c.polygon(poly_pts, Options(fill="lightblue", fillStyle="hachure", fillLineDash=[3, 2]))

# ellipse with custom stroke dash
c.ellipse(360, 60, 80, 60, Options(strokeLineDash=[1, 2, 6, 2], stroke="#666"))

# arc with no fill
c.arc(500, 80, 80, 60, 0.7, 3.14, False, Options(stroke="darkgreen", strokeWidth=2))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example6.svg", "w") as f:
    f.write(svg_data)
