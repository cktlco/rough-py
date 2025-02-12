# The Rough-Py API

- [Primary Classes](#primary-classes)
  - [RoughGenerator](#roughgenerator)
  - [RoughCanvas](#roughcanvas)
  - [Drawable](#drawable)
  - [OpSet and Op](#opset-and-op)
  - [Options and ResolvedOptions](#options-and-resolvedoptions)
- [Supporting Structures](#supporting-structures)
  - [geometry.py](#geometrypy)
  - [math.py](#mathpy)
- [Helper Functions](#helper-functions)
  - [canvas()](#canvas)
  - [generator()](#generator)
  - [new_seed()](#new_seed)
- [Shape Drawing Methods](#shape-drawing-methods)
  - [Line](#line)
  - [Rectangle](#rectangle)
  - [Ellipse and Circle](#ellipse-and-circle)
  - [Arc](#arc)
  - [Linear Path](#linear-path)
  - [Curve](#curve)
  - [Polygon](#polygon)
  - [Path](#path)
  - [Text](#text)
- [Filling and Patterns](#filling-and-patterns)
- [Exporting and Serialization](#exporting-and-serialization)
- [Examples for Complex Usage](#examples-for-complex-usage)

---

## Core Concepts

*Note: most of these terms are a direct port of concepts designed and implemented by the author of [Rough.js](https://github.com/rough-stuff/rough)*

- **Sketchy behavior**: Shapes are rendered with random offsets, multiple strokes, and various filler patterns to imitate a hand-drawn aesthetic.
- **Drawable objects**: Each shape (line, rectangle, circle, polygon, text) is generated as a `Drawable` holding one or more `OpSet` groups. These operations (ops) describe how to render or export the shape.
- **Config Options**: Shape and behavior options can be set at the Canvas level so all shapes inherit it, then optionally override at the shape level.
- **Seeded randomness**: A deterministic pseudo-random generator ensures reproducible roughness when the same seed is supplied.

---

## Primary Classes

### RoughGenerator

Use `RoughGenerator` when you want to produce shapes as standalone `Drawable` objects. Each `Drawable` can later be rendered in different contexts or manipulated directly. By contrast, `RoughCanvas` is more convenient if you want to build up a set of shapes and export them all at once.

```python
from rough.generator import RoughGenerator
from rough.core import Config, Options

# Create with optional config
my_config = Config(options=Options(seed=12345))
generator = RoughGenerator(my_config)

# Generate a shape and inspect it
line_drawable = generator.line(10, 10, 100, 100)
print(line_drawable.shape)  # "line"
print(len(line_drawable.sets))
```

You might choose `RoughGenerator` if you want maximum flexibility — for instance, to store the shape data and later embed it in multiple canvases.

**Key methods** (each returns a `Drawable`):
- `line(x1, y1, x2, y2, options=None)`
- `rectangle(x, y, width, height, options=None)`
- `ellipse(x, y, width, height, options=None)`
- `circle(x, y, diameter, options=None)`
- `linearPath(points, options=None)`
- `arc(x, y, width, height, start, stop, closed=False, options=None)`
- `curve(points, options=None)`  
- `polygon(points, options=None)`
- `path(d_str, options=None)`
- `text(x, y, textStr, options=None, doOutline=False, align="left", valign="baseline")`

Additionally, you have utilities like:
- `opsToPath(opset, fixedDecimals=None)` to convert an `OpSet` to an SVG path string  
- `toPaths(drawable)` to convert an entire `Drawable` into path data  
- `new_seed()` (static) for generating fresh random seeds

### RoughCanvas

A `RoughCanvas` creates and *immediately* retains shapes. Think of it as a container that maintains all of your drawn objects in a stack. In the end, you typically call `as_svg()` to export everything as an SVG string.

```python
from rough.canvas import RoughCanvas

canvas = RoughCanvas(400, 300)
canvas.line(10, 10, 200, 100, options=None, z_index=1)
canvas.rectangle(50, 50, 200, 120, options=None, z_index=0)
svg_str = canvas.as_svg(400, 300)
print(svg_str)
```

Use `RoughCanvas` if your workflow is straightforward: you create shapes, they’re all stored on this single canvas, and you export them at the end.

**Key aspects**:
- Normally `z_index` is based on the natural order in which the shapes are created by your script. However, if desired, you may optionally specify the `z_index` for each shape to control drawing order: shapes with higher `z_index` appear on top in the final SVG.
- Once done, call `canvas.as_svg(...)` to get a single `<svg>` string that contains all shapes.

Some methods provided:
- `draw(drawable, z_index=0)` — directly add a `Drawable`
- `line(x1, y1, x2, y2, options=None, z_index=0)` — creates and stores a line
- `rectangle(...)`, `ellipse(...)`, `circle(...)`, etc. — same shape calls as on `RoughGenerator`, but returned shapes are also tracked
- `link(drawable, href, z_index=0)` — wraps a shape in an `<a>` tag to make it clickable
- `as_svg(width, height, auto_fit=True, auto_fit_margin=20)` — exports all shapes in an SVG document
- `auto_fit(margin=0.0)` — attempts to scale/translate all shapes so they fit in the canvas dimension

### Drawable

Represents a single shape or text element. Typically, you don’t instantiate `Drawable` yourself; it’s what you get from a generator or a canvas method. You can introspect it or pass it around. It has:

- `shape` (string like `"line"` or `"circle"`)
- `options` (the `ResolvedOptions` that were used)
- `sets` (list of `OpSet` describing geometry)
- `href` (optional link if made clickable)

### OpSet and Op

*Advanced usage only.*  
- **Op**: A low-level command such as `"move"`, `"lineTo"`, or `"bcurveTo"`, plus numeric data to define control points.
- **OpSet**: A collection of Ops that define a sub-path. For instance, the rough outline of a rectangle might be one OpSet.

You generally don’t need to build these manually unless you want total control of the geometry.

### Options and ResolvedOptions

`Options` is where you specify how you want your shape to appear: color, fill style, random roughness, etc. If a field is `None`, it falls back to a default. Internally, `Options` is converted to `ResolvedOptions` where all defaults are filled in.

Key fields (with simplified explanations):
- **stroke**: a color string (e.g. `"black"` or `"#FF0000"`). `"none"` to have no stroke.
- **strokeWidth**: how thick the outline is.
- **fill**: fill color, or `"none"` to skip filling.
- **fillStyle**: pattern for the fill, e.g. `"hachure"`, `"solid"`, `"zigzag"`, etc.
- **maxRandomnessOffset**: controls how far lines deviate from the perfect geometry.
- **roughness**: general factor for how “loose” or “jittery” the lines should be. Larger = more chaotic.
- **bowing**: how lines arc slightly. Low values mean straighter lines.
- **disableMultiStroke**: if `True`, shapes draw fewer layered strokes, appearing less scribbled.
- **seed**: an integer seed for reproducible randomness.
- **fontFamily**, **fontSize**, **fontPath**: control text rendering. If `fontPath` is present, you can outline text as polygons.
  
Here’s a simple example:

```python
from rough.core import Options

# This shape will have a red stroke, blue fill, more randomness, and a fixed seed
my_opts = Options(
    stroke="red",
    fill="blue",
    fillStyle="solid",
    roughness=2.0,
    seed=999
)
```

You can mix & match more advanced fields, but these are the main ones. The library will guess defaults for anything unset.

---

## Supporting Structures

### geometry.py

- **Point**: A `tuple` `(x, y)`.
- **Line**: A `tuple` of two Points: `( (x1, y1), (x2, y2) )`.
- `line_length(line)`: returns the distance between the endpoints.

```python
from rough.geometry import Point, Line, line_length

p1 = (0, 0)
p2 = (3, 4)
print(line_length((p1, p2)))  # 5.0
```

### math.py

- `random_seed()`: returns an integer in `[0, 2^31)`.  
- `Random(seed)`: a custom linear generator for float values in `[0,1)` used internally.

```python
from rough.math import random_seed, Random

seed_val = random_seed()
rng = Random(seed_val)
print(rng.next())
```

---

## Helper Functions

### canvas()

Creates a `RoughCanvas`. Think of `(width, height)` as your intended SVG dimensions, though you can override them in `as_svg()` if you like. The coordinate system for shapes is standard Cartesian: `(0,0)` is top-left, `x` extends to the right, and `y` extends downward. By default, there’s no built-in “origin shift” unless you apply transformations.

A `RoughCanvas` also provides `ctx` as a transformation context. You can do:
```python
canvas.ctx.translate(50, 30)  # shift future shapes by (50,30)
canvas.ctx.rotate(0.3)        # rotate future shapes by 0.3 radians
canvas.ctx.scale(2, 2)        # scale everything
canvas.ctx.resetTransform()   # back to identity matrix
```
Shapes you create after transformations will be placed differently when exported.

```python
from rough import canvas
c = canvas(600, 400)
```
Parameters:
- `width`, `height` (the nominal dimensions)
- `config` (optional global config)

### generator()

Creates a `RoughGenerator` you can call to get `Drawable`s. Same config structure as the Canvas. Usually you either use a generator or a canvas, but not both.

```python
from rough import generator, Config, Options
gen = generator(Config(options=Options(seed=42)))
```

### new_seed()

Generates a random integer seed.

```python
from rough import new_seed
s = new_seed()
```

---

## Shape Drawing Methods

Below methods are identical on both `RoughGenerator` and `RoughCanvas`. On a generator, they return a `Drawable`. On a canvas, they return the `Drawable` *and* store it internally.

**Browse the gallery of [official examples](examples/examples.md)** to see the API in action.

### Line

Draw a rough line between `(x1, y1)` and `(x2, y2)`:

```python
# using generator
d = generator.line(10, 10, 200, 80, Options(stroke="orange"))

# using canvas
canvas.line(10, 10, 200, 80, Options(stroke="orange"))
```

### Rectangle

A rectangle at `(x, y)` with specified width and height. By default, if you set a `fill` color in `Options`, the rectangle interior is filled with that color/pattern.

```python
rect1 = generator.rectangle(50, 50, 120, 80, Options(fill="green"))
canvas.rectangle(50, 50, 120, 80, Options(fill="green"))
```

### Ellipse and Circle

`ellipse(x, y, width, height)` draws a shape whose full bounding box is `width` by `height`, centered at `(x, y)`.  
`circle(x, y, diameter)` is just `ellipse(...)` with the same width and height.

```python
ell = generator.ellipse(100, 100, 80, 50, Options(fill="none", stroke="black"))
circ = generator.circle(200, 200, 60, Options(fill="pink"))
```

### Arc

Draw an ellipse-like arc from `start` angle to `stop` angle (radians). If you set `closed=True`, it forms a wedge or pie-slice shape.

```python
ar = generator.arc(100, 100, 80, 80, 0.0, 3.14, closed=True, options=Options(fill="yellow"))
```

### Linear Path

Make a simple polyline through a list of `(x, y)` points. Optionally can set stroke color.

```python
pts = [(10, 10), (50, 20), (80, 60)]
p = generator.linearPath(pts, Options(stroke="blue"))
```

### Curve

Same as `linearPath`, except it smooths the shape. You can pass one list of points or multiple lists for multiple segments.

```python
# single curve
c1 = generator.curve([(10, 10), (60, 20), (90, 80)])

# multiple segments
c2 = generator.curve([
  [(10, 10), (40, 50), (80, 20)],
  [(80, 20), (100, 60), (120, 40)]
])
```

### Polygon

Creates a closed polygon from your list of points. If `fill` is set, it’s filled with that color/pattern.

```python
polygon_points = [(0, 0), (100, 0), (80, 80), (30, 50)]
poly = generator.polygon(polygon_points, Options(fill="red"))
```

### Path

Allows you to specify a standard SVG path string. Use this if you already have an SVG path definition. For example, you might parse or import it from another library, then “roughify” it. Note this won't work on "an entire SVG file", only a single Path element like `<path d="M25.1 71.6 C26.0 ...>`.

```python
d_str = "M10,10 C20,20 40,20 50,10"
svg_path = generator.path(d_str, Options(stroke="blue"))
```

### Text

By default, text is just an SVG `<text>` node referencing your chosen font. If you set `embed_outline=True` and provide `fontPath` in `Options`, the library will attempt to convert the text into polygon outlines — letting you apply advanced “rough” shapes or filler patterns to the text. That requires `fonttools` installed and can produce large geometry for big strings.

**Alignments**:
- `align="left" | "center" | "right"`  
- `valign="baseline" | "top" | "middle" | "bottom"`

These control how `(x, y)` is interpreted for text layout. With `align="center"`, the text is centered horizontally at `(x, y)`. With `valign="middle"`, it’s centered vertically, etc.

```python
text_shape = generator.text(
  100, 100, "Hello World",
  options=Options(fontSize=20, fill="blue"),
  doOutline=False,
  align="center",
  valign="bottom"
)
```

---

## Filling and Patterns

When `fill` is not `"none"`, the library attempts to fill shapes. By default, the fill “style” is `"hachure"` which looks like diagonal shading lines. However, you can pick from several styles:
- **hachure** – repeating diagonal lines (default)
- **solid** – a solid fill with possibly a rough outline
- **zigzag** – lines drawn back and forth in a zigzag pattern
- **cross-hatch** – two sets of hachure lines at right angles
- **dots** – fill with randomly placed dots
- **dashed** – fill with repeated dashed lines
- **zigzag-line** – a zigzag variant with lines offset from each other

Each style has its own unique “hand-drawn” look. You can combine these with your `fill` color. For example, `"zigzag"` with a red fill might produce squiggly red diagonal strokes that fill the shape.

```python
filled_poly = generator.polygon(
    [(10, 10), (120, 10), (120, 100), (10, 100)],
    Options(fill="red", fillStyle="zigzag")
)
```

To get deeper, you can investigate `rough.fillers`, which houses classes like `HachureFiller`, `ZigZagFiller`, etc. But usually you just specify `fillStyle` and let the library decide how to do the pattern.


## Gradient Fills and Strokes

Bored of using just a static single color? Try filling with a gradient which smoothly transitions between your chosen colors.

You can provide a list of color strings (instead of a single color) to `fill` or `stroke` and the library will automatically generate a simple linear gradient.

![](examples/example30.svg)

```python
# supply multiple colors in a list for fill
rect_with_gradient = canvas.rectangle(
    10, 10, 200, 120,
    Options(
        fill=["#FFA500", "#FF0000"],  # from orange to red
        gradientAngle=45.0,           # angle in degrees
        gradientSmoothness=2          # how many intermediate stops to generate
    )
)

# similarly for stroke, you can do:
circle_with_gradient_stroke = canvas.circle(
    280, 70, 60,
    Options(
        stroke=["#00F", "#0FF"],      # from blue to cyan
        strokeWidth=3,
        gradientAngle=90.0,
        gradientSmoothness=3
    )
)
```

The gradient is defined in “user space” coordinates. The library calculates each shape’s bounding box and attempts to fit the gradient within that box.
The gradientAngle (in degrees) sets the direction of the color transition (0 = left-to-right, 90 = top-to-bottom, etc.).

`gradientSmoothness` controls how many intermediate stops are generated between each pair of colors. A higher number yields a smoother blend.

You can provide more than two colors if you want a more complex rainbow effect.
Whether it’s fill or stroke, if `rough` sees that it’s a list of color strings, it creates a gradient. If you provide a normal single color (like "#FF0000"), it behaves as before with a solid color.

Explore mixing multiple colors, angles, or even combining gradient fills with one of the pattern styles (fillStyle), for interesting layered effects.

---

## Exporting and Serialization

`canvas.as_svg(width, height)` returns a full `<svg>` document with all shapes included. You can save that string to a file:

```python
svg_data = canvas.as_svg(600, 400)
with open("output.svg", "w", encoding="utf-8") as f:
    f.write(svg_data)
```

If you only have a single `Drawable` (from `RoughGenerator`), you could do:

```python
paths = generator.toPaths(line_drawable)
# each path has stroke/fill data that you can embed manually in your own SVG logic
```

---

## Examples for Complex Usage

### Linked Shapes

If you want a shape in the output SVG that functions as a hyperlink, you can create the shape using either the generator or the canvas, then call `canvas.link()`, providing the URL and `z_index`:

```python
# Suppose we have a rectangle shape
some_rect = generator.rectangle(10, 10, 100, 50, Options(fill="#AAF"))
# Link it and place it on canvas with z_index=1
canvas.link(some_rect, href="https://example.com", z_index=1)
```
Under the hood, the library will wrap that shape’s `<path>` (or `<polygon>`, etc.) in an `<a>` element with `xlink:href` so it becomes clickable.

### Automatic Fit

If you’ve drawn shapes that might extend beyond your chosen canvas size, you can ask the library to auto-rescale them before exporting:

```python
# after you have drawn multiple shapes in the canvas:
canvas.auto_fit(margin=20.0)
final_svg = canvas.as_svg(width=300, height=200)
```

`auto_fit` scans all the geometry, figures out a bounding box, and scales/translates them so they fit nicely within the specified dimension (minus margin). This is particularly handy if you don’t know in advance how large your shapes will be.

Note that the default behavior of `as_svg()` includes `auto_fit = True`, so you only need to specify if you want to disable it.


*That's it, you know it all!*