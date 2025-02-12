from rough import canvas, Config, Options, RoughCanvas

# show different fill styles on overlapping rectangles

# set some defaults
my_defaults = Config(Options(fillWeight=2.0, hachureGap=20.0))
c: RoughCanvas = canvas(600, 150, my_defaults)

# solid fill
c.rectangle(20, 20, 300, 300, Options(fill="#ff7777", fillStyle="solid", strokeWidth=2))

# cross-hatch fill
c.rectangle(
    220, 40, 300, 300, Options(fill="orange", fillStyle="cross-hatch", stroke="#333")
)

# hachure fill
c.rectangle(
    470, 60, 300, 300, Options(fill="#77ff77", fillStyle="hachure", fillWeight=1.0)
)

# dots fill (gold-color rect at the end)
c.rectangle(
    970, 100, 300, 300, Options(fill="#ffff99", fillStyle="dots", stroke="#999")
)

# zigzag fill (second to last, grey fill)
c.rectangle(720, 80, 300, 300, Options(fill="lightblue", fillStyle="zigzag"))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example7.svg", "w") as f:
    f.write(svg_data)
