# Edge Routing - Quick Start Guide

Quick reference for using the improved edge routing system in excelimermaid.

## Choose Your Routing Mode

### Orthogonal (Recommended for Technical Diagrams)
Clean Manhattan-style routing with 90-degree corners only.

```python
from excelimermaid import MermaidRenderer

renderer = MermaidRenderer(edge_routing='orthogonal')
diagram = renderer.parse(your_mermaid_script)
diagram.layout()
diagram.export('output.svg')
```

**Best for**: Flowcharts, process diagrams, technical documentation

---

### Curved (Default)
Smooth flowing curves with obstacle avoidance.

```python
renderer = MermaidRenderer(edge_routing='curved', smoothness=0.6)
```

**Best for**: Organic diagrams, presentations, mind maps

---

### Straight
Direct lines, no obstacle avoidance.

```python
renderer = MermaidRenderer(edge_routing='straight')
```

**Best for**: Simple diagrams without overlaps

---

## Adjust Clearance

### Default (15px) - Recommended
```python
renderer = MermaidRenderer(route_margin=15.0)
```

### Tight Layout (10px)
```python
renderer = MermaidRenderer(route_margin=10.0)
```

### Maximum Clearance (20px)
```python
renderer = MermaidRenderer(route_margin=20.0)
```

---

## Complete Example

```python
from excelimermaid import MermaidRenderer

script = """
flowchart TD
    A[Start] --> B[Process]
    B --> C[Decision]
    C -->|Yes| D[Success]
    C -->|No| E[Retry]
    E --> B
"""

# Professional orthogonal routing
renderer = MermaidRenderer(
    edge_routing='orthogonal',
    route_margin=15.0,
    roughness=0.7,
    seed=42
)

diagram = renderer.parse(script)
diagram.layout()
diagram.export('flowchart.svg')
```

---

## CLI Usage

```bash
# Orthogonal routing (recommended)
excelimermaid diagram.mmd -o output.svg --edge-routing orthogonal

# Curved routing
excelimermaid diagram.mmd -o output.svg --edge-routing curved

# Custom margin
excelimermaid diagram.mmd -o output.svg --route-margin 20.0

# All options
excelimermaid diagram.mmd -o output.svg \
    --edge-routing orthogonal \
    --route-margin 15.0 \
    --roughness 0.7
```

---

## Visual Comparison

| Mode | Appearance | Overhead |
|------|-----------|----------|
| `straight` | Direct lines | None |
| `curved` | Smooth curves | A* pathfinding |
| `orthogonal` | 90° corners | A* pathfinding |

---

## Tips

✅ **DO**: Use orthogonal mode for technical diagrams
✅ **DO**: Use 15px margin for professional appearance
✅ **DO**: Set seed for reproducible diagrams
✅ **DO**: Adjust roughness (0.5-1.0) for hand-drawn feel

❌ **DON'T**: Use margin < 10px (paths too close to boxes)
❌ **DON'T**: Use straight mode with overlapping nodes
❌ **DON'T**: Forget to call `diagram.layout()` before export

---

## Troubleshooting

**Paths too close to boxes?**
→ Increase `route_margin` to 20.0

**Paths crossing each other?**
→ Use `orthogonal` mode instead of `curved`

**Rendering too slow?**
→ Use `straight` mode or increase `pathfinding_cell_size`

**Want reproducible output?**
→ Set `seed` parameter

---

## All Configuration Options

```python
renderer = MermaidRenderer(
    # Routing
    edge_routing='orthogonal',     # 'straight', 'curved', 'orthogonal'
    avoid_obstacles=True,          # A* pathfinding on/off
    route_margin=15.0,             # Clearance (pixels)
    smoothness=0.6,                # Curve smoothness (curved only)
    route_offset=60.0,             # Initial offset

    # Pathfinding (advanced)
    pathfinding_algorithm='astar', # Algorithm choice
    pathfinding_cell_size=10,      # Grid cell size (pixels)

    # Appearance
    roughness=0.7,                 # Hand-drawn feel (0.0-1.0)
    seed=42                        # Random seed
)
```

---

## Next Steps

- See `ROUTING_IMPROVEMENTS_SUMMARY.md` for complete details
- See `MARGIN_FIX.md` for margin configuration
- See `BOUNDARY_FIX.md` for technical details
- Run `demo_final_routing.py` to see examples

---

## Quick FAQ

**Q: Which mode should I use?**
A: `orthogonal` for technical diagrams, `curved` for presentations

**Q: What's the default margin?**
A: 15px (changed from 5px for better appearance)

**Q: Do paths avoid obstacles?**
A: Yes (except in `straight` mode)

**Q: Can I disable obstacle avoidance?**
A: Yes: `renderer = MermaidRenderer(avoid_obstacles=False)`

**Q: Is this backward compatible?**
A: Yes! Old code works, just uses better defaults now
