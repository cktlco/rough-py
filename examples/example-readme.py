from rough import canvas, Options

c = canvas(600, 200)

# purple arc using an SVG-style path
swirl_path = "M 30 150 C 80 30, 220 30, 270 150 S 370 270, 420 150"
c.path(swirl_path, Options(stroke="#8a2be2", strokeWidth=4, roughness=2.5))

# transparent rectangle
c.rectangle(x=112, y=20, w=80, h=100, options=Options(fill="rgba(230, 250, 255, 0.3)"))

# arc in bright magenta
c.arc(360, 80, 80, 80, 0, 3.14, False, Options(stroke="#ff66cc", strokeWidth=3))

# circle with pink fill
c.circle(
    100, 80, 60, Options(fill="pink", fillStyle="solid", stroke="#444", strokeWidth=3)
)

# green filled polygon
points = [(150, 30), (270, 70), (250, 90), (210, 100)]
c.polygon(
    points,
    Options(
        stroke="teal", fill="#a3ffa3", fillStyle="hachure", strokeWidth=2, roughness=1
    ),
)

# broad orange stroke
c.line(420, 20, 580, 100, Options(stroke="orange", strokeWidth=20, roughness=2))

# write to a SVG file
svg_data: str = c.as_svg(600, 150)
with open("examples/example-readme.svg", "w") as f:
    f.write(svg_data)
