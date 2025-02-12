from rough import canvas, Options, RoughCanvas

# demonstration of shape size extremes, toggling multi-stroke selectively,
# partial auto_fit usage, and mindful fillLineDash vs strokeLineDash tips

c: RoughCanvas = canvas(600, 150)

# extremely large rectangle, partially off-canvas
# note: auto_fit defaults to True, so it will scale unless we pass auto_fit=False below
c.rectangle(
    -500, -100, 1000, 400, Options(fill="lightblue", stroke="black", strokeWidth=1.5)
)

# a very small circle with multi-stroke disabled to preserve a crisp shape
c.circle(300, 60, 0.5, Options(stroke="red", disableMultiStroke=True, roughness=2))

# an ellipse that uses fillLineDash separately from stroke dash
c.ellipse(
    450,
    60,
    100,
    60,
    Options(
        strokeLineDash=[6, 3],
        fillLineDash=[2, 2],
        fill="lightgreen",
        fillStyle="hachure",
    ),
)

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150, auto_fit=True)

# write SVG text to a file
with open("examples/example25.svg", "w") as f:
    f.write(svg_data)
