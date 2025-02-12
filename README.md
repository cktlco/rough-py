
<picture>
    <img src="https://raw.githubusercontent.com/cktlco/rough-py/main/resources/images/rough-py.svg" 
        alt="rough-py"
        width="500px" />
</picture>


> Python port of Rough.js 

### Create useful graphics with a "hand drawn" visual style

 You'll use `rough-py` to **programmatically generate graphics** for documentation or data visualization.

<picture>
    <img src="https://raw.githubusercontent.com/cktlco/rough-py/main/examples/example-quickstart.svg"
        alt="1. Install rough-py, 2. Draw some shapes, 3. Output SVG image" 
        width="800px" />
</picture>

## 🖌️ Install
```bash
pip install rough
```

No other python packages or third-party dependencies needed. Optionally, you can `pip install fonttools` to enable embedding font outlines into your SVG output.

## 🖍️ Use
<picture>
    <img src="https://raw.githubusercontent.com/cktlco/rough-py/main/examples/example-readme.svg" 
        alt="rough-py API code usage example" 
        width="800px" />
</picture>

```python
from rough import canvas, Options

c = canvas(600, 200)  # arbitrary units

# purple arc using an SVG-style path
swirl_path = "M 30 150 C 80 30, 220 30, 270 150 S 370 270, 420 150"
c.path(swirl_path, Options(stroke="#8a2be2", strokeWidth=4, roughness=2.5))

# transparent rectangle
c.rectangle(x=112, y=20, w=80, h=100, options=Options(fill="rgba(230, 250, 255, 0.3)"))

# arc in bright magenta
c.arc(360, 80, 80, 80, 0, 3.14, False, Options(stroke="#ff66cc", strokeWidth=3))

# circle with pink fill
c.circle(100, 80, 60, Options(fill="pink", fillStyle="solid", stroke="#444", strokeWidth=3))

# green filled polygon
points = [(150, 30), (270, 70), (250, 90), (210, 100)]
c.polygon(points, Options(stroke="teal", fill="#a3ffa3", fillStyle="hachure", strokeWidth=2, roughness=1))

# broad orange stroke
c.line(420, 20, 580, 100, Options(stroke="orange", strokeWidth=4, roughness=1.2))

# write to a SVG file
svg_data: str = c.as_svg(600, 150)
with open("/tmp/rough-example.svg", "w") as f:
    f.write(svg_data)
```


## Use the full API
🚀 [API Documentation](https://github.com/cktlco/rough-py/blob/main/API.md)

📚 [Examples Gallery](https://github.com/cktlco/rough-py/examples/examples.md)

🎨 [Fill and Stroke Style Gallery](https://github.com/cktlco/rough-py/examples/example-stylegallery.md)

Still desperate? There are even more examples ([1](https://github.com/cktlco/rough-py/tests/test_roughjs_visual_tests.py), [2](https://github.com/cktlco/rough-py/tests/test_detailed_shapes.py), [3](https://github.com/cktlco/rough-py/tests/test_simple_svg_paths.py)) in the `tests/` directory.

## Limitations

🚫  **No JavaScript-style Interactivity**

🚧  **Will not roughen existing SVG files**. For those too proud to accept that, review [`tests/test_roughen_svg.py`](https://github.com/cktlco/rough-py/tests/test_roughen_svg.py) which implements a functional but work-in-progress SVG file "roughener".


## Questions or Issues?
🔍 See the [FAQ page](/FAQ.md).

Freely use the **Discussions** tab above for general questions, or use the **Issues** tab to report a problem.


## All glory to:
- Rough.js - https://github.com/rough-stuff/rough
- svgelements SVG Path parser - https://github.com/meerk40t/svgelements



<br/><br/>
*Happy Roughening!*