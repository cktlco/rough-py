from rough import canvas, Options, RoughCanvas

# text example -- README header logo

palette = [
    "#00FFFF",
    "#00FFFF",
    "#00FFFF",
    "#00FFFF",
    "#FF00FF",
    "#FF00FF",
    "#FF00FF",
    "#FFFF00",
    "#FFFF00",
]

c: RoughCanvas = canvas(500, 200)

# white text "ROUGH"
# using embed_outlines to store text as polygon path
opts = Options()
opts.fontFamily = "Impact"
opts.fontSize = 150
opts.fontPath = "resources/fonts/Roboto/static/Roboto_Condensed-Black.ttf"
opts.fill = "white"
opts.fillStyle = "hachure"
opts.strokeWidth = 0
opts.hachureGap = 5.0
opts.roughness = 2.0
c.text(45, 95, "rough-py", options=opts, embed_outline=True)

# black text "ROUGH"
opts = Options()
opts.fontFamily = "Impact"
opts.fontSize = 150
opts.fontPath = "resources/fonts/Roboto/static/Roboto_Condensed-Black.ttf"
opts.fill = "black"
opts.fillStyle = "hachure"
opts.fillWeight = 2.0
opts.strokeWidth = 0
opts.hachureGap = 5.0
opts.roughness = 2.0
c.text(50, 100, "rough-py", options=opts, embed_outline=True)

# CMYK gradient text "ROUGH"
opts = Options()
opts.fontSize = 150
opts.fontPath = "resources/fonts/Roboto/static/Roboto_Condensed-Black.ttf"
opts.fill = palette
opts.fillWeight = 1.0
opts.fillStyle = "zigzag"
opts.gradientAngle = 35.0
opts.hachureGap = 5.0
opts.strokeWidth = 0
opts.roughness = 1.0
c.text(60, 105, "rough-py", options=opts, embed_outline=True)

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(500, 155, auto_fit_margin=10)

# write SVG text to a file
with open("examples/example26.svg", "w") as f:
    f.write(svg_data)
