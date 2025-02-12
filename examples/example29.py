from rough import canvas, Options, RoughCanvas

# comparing random seeds for rough shapes
c: RoughCanvas = canvas(600, 200)

# same seed for two circles => identical roughness
c.circle(100, 50, 40, Options(stroke="#333", fill="#ccf", seed=42))
c.circle(100, 130, 40, Options(stroke="#333", fill="#ccf", seed=42))

# no seed => different roughness every time
c.rectangle(200, 30, 80, 80, Options(stroke="red", roughness=2.0))

# a different seed => stable but distinct roughness
c.rectangle(340, 30, 80, 80, Options(stroke="green", roughness=2.0, seed=99))

svg_data: str = c.as_svg(600, 200)
with open("examples/example29.svg", "w", encoding="utf-8") as f:
    f.write(svg_data)
