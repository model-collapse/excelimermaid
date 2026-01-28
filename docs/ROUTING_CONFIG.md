# Routing Configuration API

## Overview

The Exceli-Mermaid engine now provides comprehensive control over edge routing behavior through a flexible configuration API. You can customize how edges are drawn, whether they avoid obstacles, and fine-tune the appearance of curved paths.

## Configuration Options

### Edge Routing Modes

**`edge_routing`** - Controls the overall routing style

- `"curved"` (default) - Intelligent curved routing with obstacle avoidance
- `"straight"` - Simple straight lines between nodes
- `"orthogonal"` - (Future) Manhattan-style routing with horizontal/vertical segments

### Obstacle Avoidance

**`avoid_obstacles`** - Enable/disable automatic obstacle detection

- `True` (default) - Automatically detects when edges would cross nodes and routes around them
- `False` - Draw direct lines regardless of obstacles

### Fine-Tuning Parameters

**`route_margin`** - Collision detection sensitivity (float, default: 5.0)
- Margin in pixels around nodes for detecting collisions
- Higher values make the system more conservative (detect obstacles earlier)
- Lower values allow edges to pass closer to nodes

**`smoothness`** - Curve roundness (float, 0.0-1.0, default: 0.6)
- Controls how rounded the corners are in curved paths
- 0.0 = Sharp corners
- 1.0 = Maximum roundness
- Recommended range: 0.4-0.8

**`route_offset`** - Detour distance (float, default: 60.0)
- Distance in pixels to offset when routing around obstacles
- Higher values create wider curves that give obstacles more clearance
- Lower values create tighter curves that stay closer to the direct path

## API Usage

### Python API

```python
from excelimermaid import MermaidRenderer

# Default configuration (curved routing with obstacle avoidance)
renderer = MermaidRenderer()

# Straight routing mode
renderer = MermaidRenderer(edge_routing="straight")

# Curved routing with custom parameters
renderer = MermaidRenderer(
    edge_routing="curved",
    avoid_obstacles=True,
    route_margin=8.0,      # More conservative collision detection
    smoothness=0.8,        # Very smooth curves
    route_offset=80.0      # Wider detours around obstacles
)

# Disable obstacle avoidance (edges may cross nodes)
renderer = MermaidRenderer(avoid_obstacles=False)

# Parse and render
diagram = renderer.parse(mermaid_script)
diagram.layout()
diagram.export("output.svg")
```

### Command-Line Interface

```bash
# Default curved routing
excelimermaid diagram.mmd -o output.svg

# Straight routing mode
excelimermaid diagram.mmd -o output.svg --edge-routing straight

# Disable obstacle avoidance
excelimermaid diagram.mmd -o output.svg --no-avoid-obstacles

# Custom routing parameters
excelimermaid diagram.mmd -o output.svg \
    --smoothness 0.8 \
    --route-margin 10.0 \
    --route-offset 80.0

# Combined with other styling options
excelimermaid diagram.mmd -o output.svg \
    --edge-routing curved \
    --smoothness 0.7 \
    --roughness 1.2 \
    --seed 42
```

## Examples

### Example 1: Default Behavior

```python
renderer = MermaidRenderer()
```

- Uses curved routing
- Automatically avoids obstacles
- 5px collision margin
- 0.6 smoothness
- 60px offset

**When to use:** Most flowcharts - provides clean, professional-looking diagrams with automatic obstacle avoidance.

### Example 2: Technical Diagrams

```python
renderer = MermaidRenderer(
    edge_routing="straight",
    roughness=0.5  # Less hand-drawn look
)
```

- Straight lines only
- More formal appearance
- Better for technical documentation

**When to use:** Architecture diagrams, network diagrams, formal documentation where simplicity is preferred.

### Example 3: Dense Diagrams

```python
renderer = MermaidRenderer(
    route_margin=2.0,      # Tighter collision detection
    route_offset=40.0,     # Smaller detours
    smoothness=0.5         # Moderate smoothness
)
```

- Allows edges closer to nodes
- Creates more compact layouts
- Sharper curves

**When to use:** Complex diagrams with many nodes where space is limited.

### Example 4: Artistic Style

```python
renderer = MermaidRenderer(
    smoothness=0.9,        # Very smooth curves
    route_offset=100.0,    # Wide, flowing paths
    roughness=1.5          # More hand-drawn
)
```

- Maximum curve smoothness
- Wide, flowing paths
- Strong hand-drawn aesthetic

**When to use:** Presentations, creative work, when aesthetics are more important than compactness.

### Example 5: Performance Critical

```python
renderer = MermaidRenderer(
    edge_routing="straight",
    avoid_obstacles=False
)
```

- No curve calculations
- No obstacle detection
- Fastest rendering

**When to use:** Very large diagrams (100+ nodes) where performance matters more than appearance.

## Visual Comparison

### Curved Routing (Default)
```
    [A] ─╮
         │  ╭─ [C]
         ╰──╯
    [B]
```
Smooth curves route around obstacles naturally.

### Straight Routing
```
    [A] ───────→ [C]
         ↓
        [B]
```
Direct lines may cross nodes.

### Curved with High Smoothness (0.9)
```
    [A] ─────╮
              ╰─────→ [C]
    [B]
```
Very round, flowing curves.

### Curved with Low Smoothness (0.3)
```
    [A] ──┐
          └──→ [C]
    [B]
```
Sharper corners, more angular.

## Parameter Guidelines

### Route Margin

| Value | Effect | Use Case |
|-------|--------|----------|
| 2.0 | Tight - edges pass very close to nodes | Dense layouts, minimal spacing |
| 5.0 | Default - good balance | Most diagrams |
| 10.0 | Conservative - wide berth around nodes | Clean, spacious layouts |
| 20.0 | Very conservative - maximum clearance | When clarity is critical |

### Smoothness

| Value | Effect | Use Case |
|-------|--------|----------|
| 0.2 | Sharp corners, almost angular | Technical, formal diagrams |
| 0.4 | Slightly rounded | Balanced appearance |
| 0.6 | Default - natural curves | Most flowcharts |
| 0.8 | Very smooth | Artistic, presentation style |
| 1.0 | Maximum roundness | Creative work, emphasis on aesthetics |

### Route Offset

| Value | Effect | Use Case |
|-------|--------|----------|
| 30 | Tight curves, minimal detour | Space-constrained layouts |
| 60 | Default - balanced | Most diagrams |
| 80 | Wider curves, clear separation | Complex diagrams |
| 100+ | Very wide curves, flowing paths | Presentation, emphasis on flow |

## Backward Compatibility

All routing parameters are optional with sensible defaults. Existing code continues to work without modifications:

```python
# Old code - still works perfectly
renderer = MermaidRenderer(roughness=1.0, seed=42)
diagram = renderer.parse(script)
diagram.layout()
diagram.export("output.svg")
```

The engine will use default routing configuration (`curved` mode with obstacle avoidance enabled).

## Performance Considerations

### Routing Mode Performance

1. **Straight (Fastest)**
   - No curve calculations
   - No obstacle detection
   - O(n) where n = number of edges

2. **Curved without obstacles (Fast)**
   - Direct paths only
   - O(n) where n = number of edges

3. **Curved with obstacles (Default)**
   - Obstacle detection per edge
   - Curve generation when needed
   - O(n*m) where n = edges, m = nodes
   - Still very fast for typical diagrams (<100 nodes)

### Recommendations

- **Small diagrams (<20 nodes):** Use any configuration, performance difference is negligible
- **Medium diagrams (20-50 nodes):** Default configuration works well (<1 second)
- **Large diagrams (50-100 nodes):** Consider disabling obstacle avoidance if speed is critical
- **Very large diagrams (100+ nodes):** Use straight routing mode for optimal performance

## Testing

The routing configuration is thoroughly tested with 10 dedicated test cases covering:

- Configuration defaults and validation
- All routing modes (curved, straight)
- Obstacle avoidance on/off
- Custom margin, smoothness, and offset values
- Backward compatibility
- API consistency

Run tests:
```bash
pytest tests/test_routing_config.py -v
```

## Future Enhancements

### Orthogonal Routing (Coming Soon)

```python
renderer = MermaidRenderer(edge_routing="orthogonal")
```

Will provide Manhattan-style routing with pure horizontal/vertical segments, ideal for circuit diagrams and technical schematics.

### Advanced Path Finding

Future versions may include:
- A* pathfinding for complex obstacle fields
- Multiple waypoint optimization
- Edge bundling for parallel connections
- User-defined waypoints

## FAQ

**Q: When should I use straight routing vs curved?**

A: Use straight routing for technical diagrams where simplicity is preferred. Use curved (default) for most flowcharts where visual clarity and avoiding node overlaps is important.

**Q: Why are some edges straight even with curved routing enabled?**

A: The engine only curves edges when obstacles are detected in the direct path. If the straight line is clear, it uses a direct path for efficiency and cleaner appearance.

**Q: Can I disable curves but keep obstacle avoidance?**

A: Currently no - obstacle avoidance is implemented through curved routing. Use `edge_routing="straight"` for all straight lines, or keep `edge_routing="curved"` for smart routing.

**Q: What's the performance impact of obstacle avoidance?**

A: For typical diagrams (<50 nodes), the impact is negligible (<0.1 seconds). Only very large diagrams (100+ nodes) may see noticeable impact.

**Q: How do I make curves more pronounced?**

A: Increase `route_offset` (e.g., 100.0) for wider detours and increase `smoothness` (e.g., 0.8) for rounder corners.

## See Also

- [CURVED_ROUTING.md](CURVED_ROUTING.md) - Technical details of the routing algorithm
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Complete improvement history
- [README.md](README.md) - General usage and getting started
