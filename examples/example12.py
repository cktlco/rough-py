# different strokes on lines, arcs, and circles
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# thick line
c.line(20, 30, 120, 120, Options(stroke="black", strokeWidth=5))

# thin line
c.line(140, 30, 240, 120, Options(stroke="blue", strokeWidth=0.5))

# arc with moderate stroke
c.arc(340, 80, 60, 60, 0, 3.14, False, Options(stroke="red", strokeWidth=2))

# circle with wide stroke
c.circle(440, 70, 60, Options(stroke="green", strokeWidth=4))

# ellipse with extremely thin stroke
c.ellipse(540, 80, 80, 60, Options(stroke="#999", strokeWidth=0.2))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example12.svg", "w") as f:
    f.write(svg_data)
