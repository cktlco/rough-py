# demonstrate arcs, paths, and multiple fill styles
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

# draw an arc (open)
c.arc(50, 100, 80, 80, 0, 3.14, False, Options(stroke="blue", roughness=1))

# draw a closed arc with solid fill
c.arc(150, 100, 60, 60, 1.57, 4.71, True, Options(fill="orange", fillStyle="solid"))

# freeform path to create a small wave
path_str: str = "M 220 80 C 240 20, 300 20, 320 80 S 380 140, 400 80"
c.path(path_str, Options(stroke="purple", strokeWidth=2.5))

# second path with fill
path_str2: str = "M 450 50 L 500 50 L 500 90 L 450 90 Z"
c.path(path_str2, Options(fill="yellow", fillStyle="hachure", strokeWidth=1.5))

# draw a circle with dashed stroke
c.circle(550, 80, 40, Options(stroke="red", strokeLineDash=[4, 2]))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example2.svg", "w") as f:
    f.write(svg_data)
