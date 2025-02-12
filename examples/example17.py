from rough import canvas, Options, RoughCanvas

# demonstration of canvas transformations
# (scale, rotate, translate) and then drawing
c: RoughCanvas = canvas(600, 150)

palette = [
    "rgba(248,181,0,0.8)",
    "rgba(31,138,112,0.8)",
    "rgba(232,116,161,0.8)",
    "rgba(79,124,189,0.8)",
    "rgba(252,89,94,0.8)",
    "rgba(125,206,130,0.8)",
    "rgba(180,122,234,0.8)",
    "rgba(163,211,156,0.8)",
]

# draw a series of overlapping rectangles
for angle in range(0, 360, 45):
    # rotate the canvas before drawing the next shape
    angle_radians = angle * 3.14159 / 180
    c.ctx.rotate(angle_radians)

    # choose a stylish fill color
    stroke_color = palette[angle // 45 % len(palette)]

    c.rectangle(
        50,
        0,
        90,
        180,
        Options(stroke=stroke_color, fillStyle="hachure", roughness=3.0, bowing=2.0),
    )


# translate the drawing origin
c.ctx.translate(450, 100)

# draw a series of overlapping circles
for x in range(8):
    # scale down the canvas
    c.ctx.scale(0.9, 0.9)

    # fancify
    fill_color = palette[x % len(palette)]
    stroke_color = palette[(x + 1) % len(palette)]

    c.circle(
        0,
        0,
        300,
        Options(
            roughness=6.0,
            fill=fill_color,
            stroke=stroke_color,
            hachureGap=35,
            fillStyle="zigzag",
        ),
    )


# reset scale and translate the drawing origin
c.ctx.resetTransform()
c.ctx.translate(440, -100)

# draw a series of rotated text elements
for angle in range(0, 360, 45):
    angle_radians = angle * 3.14159 / 180
    c.ctx.rotate(angle_radians)

    c.ctx.translate(-10, -20)

    fill_color = palette[angle // 45 % len(palette)]

    c.text(
        0,
        0,
        "-=1234567890=-",
        Options(fill=fill_color, fillStyle="hachure", fontFamily="Impact", fontSize=40),
        embed_outline=True,
    )


svg_data: str = c.as_svg(600, 150, auto_fit_margin=10)
with open("examples/example17.svg", "w") as f:
    f.write(svg_data)
