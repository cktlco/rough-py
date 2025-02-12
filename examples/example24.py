from rough import canvas, Options, RoughCanvas
import math

# demonstration of using line transformations vs path transformations
# (rotate after drawing vs rotate before drawing)

c: RoughCanvas = canvas(600, 150)

# draw a rectangle normally
c.rectangle(20, 20, 80, 60, Options(fill="#ffc", stroke="brown"))

# rotate the context, then draw a similar rectangle
c.ctx.rotate(math.pi / 6.0)  # rotate 30 degrees
c.rectangle(20, 20, 80, 60, Options(fill="#cfc", stroke="purple"))

# reset transform and rotate the rectangle data "manually" by using path string
c.ctx.resetTransform()
path_rect = "M 200 20 L 280 20 L 280 80 L 200 80 Z"  # unrotated

# rotate around center ~ (240,50)
rotation_angle = 45.0
c.path(path_rect, Options(stroke="blue", roughness=1))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example24.svg", "w") as f:
    f.write(svg_data)
