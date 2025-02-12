from rough import canvas, Options, RoughCanvas

# embedded text comparison
c: RoughCanvas = canvas(600, 150)

palette = ["#E63946", "#F4A261", "#2A9D8F", "#264653"]

# referenced text (font not embedded into SVG)
opts = Options()
opts.fontFamily = "Cooper Black, Impact, Verdana, Helvetica"
opts.fontSize = 32
opts.fill = palette[0]
c.text(50, 0, "Text using browser/OS fonts", options=opts)

opts.fontFamily = "Cooper Black, Impact, Verdana, Helvetica"
opts.fontSize = 32
opts.fill = palette[0:4]
c.text(50, 50, "...not roughenable, but legible and efficient", options=opts)

# text converted to outlines and stored in the SVG
opts = Options()
opts.fontSize = 50
# note the required use of 'fontPath' when embed_outline=True
opts.fontPath = "resources/fonts/Roboto/static/Roboto_Condensed-Black.ttf"
opts.fill = [palette[0], palette[1]]
opts.fillStyle = "hachure"
opts.hachureGap = 2.0
opts.roughness = 1.0
opts.bowing = 1.0
opts.strokeWidth = 0
c.text(
    50,
    120,
    "Text as polygons... ROUGHable, but big files!",
    options=opts,
    embed_outline=True,
)

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 110, auto_fit_margin=20)

# write SVG text to a file
with open("examples/example27.svg", "w") as f:
    f.write(svg_data)
