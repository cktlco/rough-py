# mix of shapes, lines, fill styles, and seeds
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# specify seed for consistent random style
seeded_opts: Options = Options(stroke="#00a", roughness=1, seed=1234)
c.line(20, 20, 100, 100, seeded_opts)

# rectangle with a different seed
c.rectangle(120, 30, 100, 80, Options(fill="#ffa", fillStyle="dots", seed=5678))

# polygon with no stroke, only fill
pts = [(260, 20), (300, 50), (280, 90), (250, 80)]
c.polygon(pts, Options(stroke="none", fill="#ccffcc", fillStyle="solid"))

# ellipse with cross-hatch
c.ellipse(380, 60, 100, 50, Options(fill="#ddf", fillStyle="cross-hatch"))

# arcs with different seeds
c.arc(500, 60, 70, 70, 0, 3.14, False, Options(stroke="magenta", seed=999))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example16.svg", "w") as f:
    f.write(svg_data)
