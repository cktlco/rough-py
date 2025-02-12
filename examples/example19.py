from rough import canvas, Options, RoughCanvas

# demonstration of multi-stroke disabled for fill and stroke, plus zero-size shapes
c: RoughCanvas = canvas(600, 150)

# line with multi-stroke disabled
c.line(20, 20, 120, 20, Options(disableMultiStroke=True, stroke="#333", roughness=3))

# rectangle with no multi-stroke on fill
c.rectangle(20, 40, 100, 80, Options(disableMultiStrokeFill=True, fill="yellow"))

# intentionally zero-size circle
c.circle(200, 60, 0, Options(stroke="blue", fill="#eee"))

# very small ellipse
c.ellipse(240, 60, 1, 1, Options(stroke="red", fill="#fcc"))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example19.svg", "w") as f:
    f.write(svg_data)
