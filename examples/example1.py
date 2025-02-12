from rough import canvas, Options, RoughCanvas

# create a canvas of 600x200
c: RoughCanvas = canvas(600, 150)

# draw a few lines with default options
c.line(10, 10, 200, 40)
c.line(200, 40, 300, 70, Options(stroke="red", strokeWidth=3.0, roughness=2))

# draw a rectangle with blue stroke
c.rectangle(320, 20, 80, 100, Options(stroke="blue", strokeWidth=3.0))

# draw a circle with solid fill
c.circle(450, 60, 50, Options(fill="green", fillStyle="solid", stroke="#999"))

# draw a small polygon
points = [(510, 30), (560, 40), (550, 90), (520, 75)]
c.polygon(points, Options(stroke="purple", fill="#ffc0cb", fillStyle="hachure"))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example1.svg", "w") as f:
    f.write(svg_data)
