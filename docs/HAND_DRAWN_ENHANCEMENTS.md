# Hand-Drawn Style Enhancements

## Overview

Enhanced the hand-drawn aesthetic with more visible sketchy effects, making diagrams look truly hand-drawn instead of just slightly rough.

## What Was Enhanced

### 1. **Multi-Stroke Drawing** ✨ NEW

Shapes are now drawn with multiple overlapping strokes for an authentic sketchy appearance.

```python
# Before: Single stroke per shape
renderer = MermaidRenderer(roughness=1.0)

# After: Multiple overlapping strokes
renderer = MermaidRenderer(
    roughness=1.0,
    multi_stroke=True,  # NEW!
    sketch_style="standard"  # NEW!
)
```

**Effect:**
- Rectangles: 2-3 overlapping outlines
- Circles: 2-3 overlapping ellipses
- Diamonds: 2-3 overlapping paths
- Lines/Arrows: Increased segment density

### 2. **Increased Line Roughness**

Lines now have more visible wobble and imperfection:

**Before:**
- Segments every 40 pixels
- Reduced randomness (0.5x multiplier)
- Minimal deviation

**After:**
- Segments every 20-30 pixels (style-dependent)
- Full randomness (1.0x multiplier)
- Visible hand-drawn wobble

### 3. **Shape Variations**

Each stroke of a multi-stroke shape has slight variations:
- Position jitter (±0.3-0.5 units)
- Size variation (±0.5-1.0 units)
- Unique roughness per stroke

### 4. **Style Presets** ✨ NEW

Three preset styles for different use cases:

| Style | Multi-Stroke | Roughness | Best For |
|-------|-------------|-----------|----------|
| **subtle** | No (1x) | 0.5x | Professional documentation |
| **standard** | Yes (2x) | 1.0x | General presentations ✓ |
| **heavy** | Yes (3x) | 2.0x | Artistic/creative work |

## New API Parameters

### `MermaidRenderer`

```python
MermaidRenderer(
    roughness=1.0,           # 0.0-2.0 (hand-drawn intensity)
    multi_stroke=True,       # NEW: Overlapping strokes
    sketch_style="standard", # NEW: Preset style
    # ... other parameters
)
```

### `sketch_style` Options

- **`"subtle"`**: Minimal hand-drawn effect
  - Single stroke
  - 0.5x randomness multiplier
  - Clean and precise

- **`"standard"`** (default): Balanced hand-drawn
  - Double stroke (2 overlapping paths)
  - 1.0x randomness multiplier
  - Natural sketchy feel

- **`"heavy"`**: Maximum hand-drawn effect
  - Triple stroke (3 overlapping paths)
  - 2.0x randomness multiplier
  - Bold artistic appearance

## Visual Comparison

### Before Enhancements
```
┌──────────┐     Single stroke
│  Box     │     Subtle roughness
└──────────┘     Minimal wobble
```

### After Enhancements (Standard)
```
┌╌╌╌╌╌╌╌╌╌┐
┆╌┌──────┐╌┆     Double stroke
┆ │  Box │ ┆     Visible roughness
└╌└──────┘╌┘     Hand-drawn wobble
```

### After Enhancements (Heavy)
```
╭╌╌╌╌╌╌╌╌╌╮
┆╭╌┌──────┐╌╮┆   Triple stroke
┆┆ │  Box │ ┆┆   Maximum roughness
╰╌╰└──────┘╌╯╯   Very sketchy
```

## Generated Showcases

### Basic Style Comparison
- `style_01_subtle.svg` - Minimal effect
- `style_02_standard.svg` - Default (recommended)
- `style_03_heavy.svg` - Maximum sketch
- `style_04_custom_extreme.svg` - Extreme roughness
- `style_05a_no_multistroke.svg` - Without multi-stroke
- `style_05b_with_multistroke.svg` - With multi-stroke

### Complex Diagram Styles
- `enhanced_01_professional.svg` - Clean documentation style
- `enhanced_02_standard.svg` - Balanced presentation style
- `enhanced_03_artistic.svg` - Heavy artistic style
- `enhanced_04_extreme.svg` - Maximum hand-drawn effect

## Technical Implementation

### Multi-Stroke Algorithm

```python
# For each shape (rectangle, circle, diamond):
for stroke_num in range(num_strokes):
    # Add jitter for subsequent strokes
    if stroke_num > 0:
        x_jitter = random_offset(roughness * 0.3)
        y_jitter = random_offset(roughness * 0.3)
        size_variation = random_offset(roughness * 0.5)

    # Draw shape with variations
    draw_shape_with_roughness(
        position + jitter,
        size + variation
    )
```

### Enhanced Roughness

**Line Segments:**
```python
# Before
num_segments = max(2, int(length / 40))
offset = random_offset(roughness * 0.5)

# After
num_segments = max(2, int(length / 20))  # More segments
offset = random_offset(roughness * 1.0)   # More visible
```

**Random Distribution:**
```python
# Gaussian distribution
sigma = max_offset / 4  # 99.7% within ±max_offset
value = random.gauss(0, sigma)
```

## Usage Examples

### Example 1: Professional Documentation

```python
from excelimermaid import MermaidRenderer

renderer = MermaidRenderer(
    roughness=0.7,
    sketch_style="subtle",
    multi_stroke=False,
    edge_routing='orthogonal'
)

diagram = renderer.parse(mermaid_script)
diagram.layout()
diagram.export('professional_diagram.svg')
```

### Example 2: Standard Presentation

```python
renderer = MermaidRenderer(
    roughness=1.0,
    sketch_style="standard",  # Default
    multi_stroke=True,
    edge_routing='orthogonal'
)

diagram = renderer.parse(mermaid_script)
diagram.layout()
diagram.export('presentation.svg')
```

### Example 3: Artistic/Whiteboard Style

```python
renderer = MermaidRenderer(
    roughness=1.5,
    sketch_style="heavy",
    multi_stroke=True,
    edge_routing='curved',
    smoothness=0.8
)

diagram = renderer.parse(mermaid_script)
diagram.layout()
diagram.export('whiteboard_sketch.svg')
```

### Example 4: Maximum Hand-Drawn

```python
renderer = MermaidRenderer(
    roughness=2.0,  # Maximum
    sketch_style="heavy",
    multi_stroke=True,
    edge_routing='curved'
)

diagram = renderer.parse(mermaid_script)
diagram.layout()
diagram.export('extreme_sketch.svg')
```

## Performance Impact

### Before
- 1 path per shape edge
- Fewer segments per line
- Faster rendering

### After
- 2-3 paths per shape edge (multi-stroke)
- More segments per line
- 2-3x more paths in SVG

### Typical File Sizes

| Style | Multiplier | Example Size |
|-------|-----------|--------------|
| Subtle (no multi-stroke) | 1.0x | 10 KB |
| Standard (double stroke) | ~2.0x | 20 KB |
| Heavy (triple stroke) | ~3.0x | 30 KB |

**Note:** Complex diagrams with many nodes benefit most from the enhanced styles.

## Default Style

⚠️ **Default style updated to extreme hand-drawn**

As of the latest version, the default style is now the extreme hand-drawn style (equivalent to style_04_custom_extreme):

```python
# New defaults (extreme hand-drawn style)
renderer = MermaidRenderer()
# Equivalent to:
renderer = MermaidRenderer(
    roughness=2.0,           # Maximum roughness
    sketch_style="heavy",    # Triple stroke
    multi_stroke=True,       # Overlapping strokes
    smoothness=0.8           # High smoothness for curves
)
```

Users can still override to use less aggressive styles:

```python
# Subtle style (minimal hand-drawn)
renderer = MermaidRenderer(
    roughness=0.7,
    sketch_style="subtle",
    multi_stroke=False
)

# Standard style (balanced hand-drawn)
renderer = MermaidRenderer(
    roughness=1.0,
    sketch_style="standard",
    multi_stroke=True
)
```

## Recommendations

### For Different Use Cases

**Technical Documentation:**
```python
sketch_style="subtle", multi_stroke=False, roughness=0.7
```

**Presentations:**
```python
sketch_style="standard", multi_stroke=True, roughness=1.0
```

**Creative/Brainstorming:**
```python
sketch_style="heavy", multi_stroke=True, roughness=1.5-2.0
```

**Whiteboard Simulation:**
```python
sketch_style="heavy", multi_stroke=True, roughness=2.0, edge_routing='curved'
```

## Files Modified

1. **`src/excelimermaid/renderer/rough_drawing.py`**
   - Added `multi_stroke` parameter
   - Added `sketch_style` presets
   - Enhanced `rough_line()` with more segments
   - Updated `rough_rectangle()` for multi-stroke
   - Updated `rough_circle()` for multi-stroke
   - Updated `rough_diamond()` for multi-stroke

2. **`src/excelimermaid/renderer/excalidraw_renderer.py`**
   - Added `multi_stroke` parameter
   - Added `sketch_style` parameter
   - Pass parameters to `RoughDrawing`

## Testing

✅ All 35 tests passing

**Key tests:**
- `test_simple_svg_render` - Basic rendering
- `test_renderer_api` - API compatibility
- `test_renderer_api_backward_compatibility` - Old code works

## Summary

**Before:** Subtle hand-drawn effect (like slightly rough digital drawing)
**After:** Bold hand-drawn effect (like actual pen-on-paper sketches)

**Key Improvements:**
- ✨ Multi-stroke drawing (2-3 overlapping paths)
- ✨ Increased line roughness (more visible wobble)
- ✨ Shape variations (position & size jitter)
- ✨ Three style presets (subtle, standard, heavy)
- ✨ Configurable intensity (roughness 0.0-2.0)

The diagrams now truly look hand-drawn! 🎨
