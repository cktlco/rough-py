from rough import canvas, Options, RoughCanvas

# demonstration of multiple seed usage, extreme bounding, and auto_fit
c: RoughCanvas = canvas(600, 150)

# shapes placed at negative coordinates to push bounding beyond normal view
c.rectangle(-300, -100, 200, 150, Options(fill="#ccf", roughness=3, seed=42))
c.circle(
    -50, -50, 80, Options(stroke="orange", fill="pink", fillStyle="solid", seed=999)
)

# large polygon straddling origin
pts = [(150, -100), (300, -50), (250, 50), (120, 60)]
c.polygon(pts, Options(fill="lightgreen", fillStyle="hachure", roughness=2, seed=123))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150, auto_fit=False)

# write SVG text to a file
with open("examples/example23.svg", "w") as f:
    f.write(svg_data)

# create another version with auto_fit to compare the difference.
# auto_fit ensures entire scene fits in final 600x200
# note that auto_fit is True by default, so you don't have to specify
# unless you want to disable it
svg_data: str = c.as_svg(600, 150, auto_fit=True, auto_fit_margin=10)

# write SVG text to a file
with open("examples/example23-autofit.svg", "w") as f:
    f.write(svg_data)
