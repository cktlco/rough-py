# fill shape roughness gain experimentation
from rough import canvas, Config, Options, RoughCanvas

c: RoughCanvas = canvas(
    600,
    600,
    config=Config(
        Options(
            fillStyle="hachure",
            hachureGap=1.0,
            fillWeight=3.0,
            fontSize=10,
            bowing=1.0,
            fontFamily="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif",
            fontWeight="bold",
        )
    ),
)

box_width = 125
box_height = 25
box_h_center = box_height / 2 + 7.5
box_w_center = box_width / 2 + 10


# use simple functions to make reusable components
def box(text: str, color: str):
    options = Options(fill=color, stroke="#E63946")
    c.rectangle(0, 0, box_width, box_height, options)
    c.text(
        box_w_center + 0.2,
        box_h_center + 0.2,
        text,
        Options(fill="#F0F0F0"),
        align="center",
        valign="middle",
    )  # drop shadow
    c.text(
        box_w_center + 0.1,
        box_h_center + 0.1,
        text,
        Options(fill="#AAA"),
        align="center",
        valign="middle",
    )  # drop shadow
    c.text(
        box_w_center,
        box_h_center,
        text,
        Options(fill="#101010"),
        align="center",
        valign="middle",
    )


def arrow():
    x_adj = box_w_center - 8
    y_adj = 20
    c.ctx.translate(x_adj, y_adj)
    c.ctx.scale(0.5, 0.5)  # scaling just to make the arrow shape smaller
    c.polygon(
        [(0, 0), (20, 0), (20, 20), (30, 20), (10, 50), (-10, 20), (0, 20)],
        Options(
            stroke="#E63946",
            fill="#FCA4AB",
            fillStyle="zigzag",
            fillWeight=3.0,
            hachureGap=3.0,
            hachureAngle=23,
        ),
        z_index=10,  # highest z-index is drawn on top
    )
    c.ctx.scale(2.0, 2.0)
    c.ctx.translate(-x_adj + 10, y_adj)


# draw diagram
box("1. Install rough-py", "#87CEEB")
arrow()
box("2. Draw some shapes", "#00CED1")
arrow()
box("3. Output SVG image", "#40E0D0")


# render the canvas as SVG (Scalable Vector Graphics) code
svg_data: str = c.as_svg(600, 480)

# write SVG text to a file
with open("examples/example-quickstart.svg", "w") as f:
    f.write(svg_data)
