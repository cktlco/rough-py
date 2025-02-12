# fill shape roughness gain experimentation
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# rectangle with normal fill shape roughness gain
c.rectangle(20, 30, 80, 80, Options(fill="lightblue", fillStyle="hachure"))

# rectangle with higher fill shape roughness gain
c.rectangle(
    120,
    30,
    80,
    80,
    Options(fill="lightgreen", fillStyle="hachure", fillShapeRoughnessGain=2.5),
)

# ellipse with fill shape roughness
c.ellipse(240, 70, 100, 60, Options(fill="pink", fillShapeRoughnessGain=1.5))

# circle with fill shape roughness
c.circle(380, 70, 60, Options(fill="orange", fillShapeRoughnessGain=3.0))

# polygon with lower fill shape roughness
pts = [(480, 30), (530, 20), (560, 60), (500, 100)]
c.polygon(pts, Options(fill="#fffccc", fillShapeRoughnessGain=0.3))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example13.svg", "w") as f:
    f.write(svg_data)
