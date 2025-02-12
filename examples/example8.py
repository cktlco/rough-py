# arcs and polygons with different roughness
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# very rough arc
c.arc(60, 60, 60, 40, 0, 3.14, False, Options(stroke="purple", roughness=4))

# polygon with moderate roughness
pts = [(130, 40), (170, 20), (190, 60), (150, 80)]
c.polygon(pts, Options(stroke="teal", fill="pink", roughness=2))

# circle with minimal roughness
c.circle(260, 60, 50, Options(fill="#ccddff", stroke="#444", roughness=0.5))

# ellipse with high roughness
c.ellipse(360, 60, 90, 50, Options(fill="lime", roughness=3))

# line with moderate roughness
c.line(450, 20, 550, 100, Options(stroke="red", roughness=2))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example8.svg", "w") as f:
    f.write(svg_data)
