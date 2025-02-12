from rough import canvas, Options, RoughCanvas

# demonstration of separate fill vs stroke dash and offset variations
c: RoughCanvas = canvas(600, 150)

# polygon with custom stroke dash
poly_pts = [(20, 20), (80, 20), (60, 80)]
c.polygon(
    poly_pts, Options(strokeLineDash=[4, 4], strokeLineDashOffset=2, stroke="brown")
)

# arc with fill line dash
c.arc(
    160,
    60,
    80,
    60,
    0,
    3.14,
    True,
    Options(fill="pink", fillStyle="hachure", fillLineDash=[2, 6]),
)

# rectangle with different dash for stroke vs fill
c.rectangle(
    240,
    30,
    100,
    80,
    Options(
        stroke="blue",
        strokeLineDash=[6, 2],
        fill="lightgreen",
        fillStyle="cross-hatch",
        fillLineDash=[1, 4],
    ),
)

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example21.svg", "w") as f:
    f.write(svg_data)
