from rough import canvas, Options, RoughCanvas

# WIP testing
c: RoughCanvas = canvas(600, 150)

rect = c.gen.rectangle(
    0, 0, 200, 50, options=Options(fill="rgba(100, 100, 230, 0.5)", fillStyle="solid")
)
c.draw(rect)

c.ctx.translate(20, 20)
c.draw(rect)


# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example28.svg", "w") as f:
    f.write(svg_data)
