# multiple polygons overlapped
from rough import canvas, Options, RoughCanvas

c: RoughCanvas = canvas(600, 150)

hex_pts = [
    (20, 40),
    (40, 20),
    (60, 20),
    (80, 40),
    (60, 60),
    (40, 60),
]
c.polygon(hex_pts, Options(fill="#ffe0e0", stroke="red", fillStyle="hachure"))

tri_pts = [(100, 20), (140, 20), (120, 60)]
c.polygon(tri_pts, Options(fill="#ccc", strokeWidth=1.5, fillStyle="solid"))

square_pts = [(180, 20), (220, 20), (220, 60), (180, 60)]
c.polygon(square_pts, Options(fill="#ccffcc", stroke="#666"))

oct_pts = [
    (300, 30),
    (320, 20),
    (340, 20),
    (360, 30),
    (360, 50),
    (340, 60),
    (320, 60),
    (300, 50),
]
c.polygon(oct_pts, Options(fill="#ffffcc", stroke="purple", fillStyle="cross-hatch"))

# random polygon
rand_pts = [
    (420, 20),
    (460, 40),
    (440, 60),
    (420, 90),
    (400, 70),
]
c.polygon(rand_pts, Options(fill="lightblue", stroke="blue", fillStyle="dots"))

# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 150)

# write SVG text to a file
with open("examples/example10.svg", "w") as f:
    f.write(svg_data)
