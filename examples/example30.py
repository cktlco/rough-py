from rough import canvas, Options, RoughCanvas

# comparing random seeds for rough shapes
c: RoughCanvas = canvas(600, 200)

# supply multiple colors in a list for fill
rect_with_gradient = c.rectangle(
    10,
    10,
    200,
    120,
    Options(
        fill=["#FFA500", "#FF0000"],  # from orange to red
        gradientAngle=45.0,  # angle in degrees
        gradientSmoothness=2,  # how many intermediate stops to generate
    ),
)

# similarly for stroke, you can do:
circle_with_gradient_stroke = c.circle(
    280,
    70,
    60,
    Options(
        stroke=["#00F", "#0FF"],  # from blue to cyan
        strokeWidth=3,
        gradientAngle=90.0,
        gradientSmoothness=3,
    ),
)

svg_data: str = c.as_svg(600, 200)
with open("examples/example30.svg", "w", encoding="utf-8") as f:
    f.write(svg_data)
