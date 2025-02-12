# demonstration of bounding box scaling with auto_fit
# note that auto_fit=True is the default behavior
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# draw shapes that go beyond normal 600x200 range
c.ellipse(50, 50, 300, 300, Options(stroke="green"))
c.rectangle(-100, 100, 200, 200, Options(fill="pink"))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150, auto_fit=True, auto_fit_margin=10)

# write SVG text to a file
with open("examples/example18.svg", "w") as f:
    f.write(svg_data)
