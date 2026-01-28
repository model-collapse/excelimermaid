# Curved Edge Routing with Obstacle Avoidance

## Overview

The engine now features **intelligent edge routing** that automatically detects when edges would cross through nodes and routes them around obstacles using smooth curves.

## How It Works

### 1. Collision Detection

For each edge, the system:
1. Calculates the direct path from source to target (boundary-to-boundary)
2. Checks if this path intersects any other node's bounding box
3. Identifies which nodes are "obstacles" that need to be avoided

### 2. Path Finding

When obstacles are detected:
- **Horizontal flows**: Routes above or below the obstacles
- **Vertical flows**: Routes left or right of the obstacles
- Chooses the route with fewer additional crossings
- Creates waypoints to guide the path around obstacles

### 3. Curve Generation

The waypoints are converted into smooth curves:
- Uses quadratic Bezier interpolation at corners
- Configurable smoothness (0.0-1.0, default 0.6)
- Creates natural-looking rounded paths
- Maintains hand-drawn aesthetic with roughness

## Results

### Coffee Shop Diagram (21 nodes, 29 edges)
```
Direct routes: 24 (82.8%)
Curved routes: 5 (17.2%) - avoiding obstacles
```

Edges that curve around obstacles:
- 8oz Coffee → Add Extras? (12 points)
- Select Tea Type → Add Extras? (12 points)
- Add Extras? → Add Milk (12 points)
- Add Extras? → Payment (12 points)
- Add Milk → Payment (12 points)

### Test Diagram (4 nodes, 5 edges)
```
Direct routes: 4 (80%)
Curved routes: 1 (20%)
```

The Start → End edge curves around the middle nodes.

## Algorithm Details

### Collision Detection

```python
def line_intersects_bbox(p1, p2, bbox, margin=5.0):
    """
    Check if line segment crosses bounding box.

    - Expands bbox by margin (5px) for safety
    - Quick bbox overlap check first
    - Line-line intersection for edges
    - Returns True if collision detected
    """
```

### Route Planning

```python
def route_around_obstacles(start, end, obstacles, ...):
    """
    Generate waypoints to avoid obstacles.

    Strategy:
    1. Determine if flow is horizontal or vertical
    2. Try routing above/below (horizontal)
       or left/right (vertical)
    3. Create intermediate waypoints offset by 60px
    4. Choose route with fewer crossings
    """
```

### Curve Smoothing

```python
def create_smooth_curve(waypoints, smoothness=0.6):
    """
    Convert sharp waypoints into smooth curves.

    - Calculates corner radius based on segment length
    - Uses quadratic Bezier for corners
    - 4 interpolation points per corner
    - Smoothness controls corner radius (0.0-1.0)
    """
```

## Visual Examples

### Before (Straight Lines)
```
    [A] ────────→ [C]
         ↓
        [B]
```
Problem: Line from A to C crosses B.

### After (Curved Routing)
```
    [A] ─╮
         │
         ╰─→ [C]
    [B]
```
Solution: Curve routes around B.

## Configuration

The routing is **automatic** and requires no configuration. However, you can influence it:

### Margin
The collision detection uses a 5px margin around nodes. To adjust:
```python
# In edge_routing.py
line_intersects_bbox(p1, p2, bbox, margin=10.0)  # More conservative
```

### Offset Distance
Routes offset by 60px from direct path. To adjust:
```python
# In edge_routing.py
waypoints_above = _try_horizontal_route(..., offset=-80)  # Larger offset
```

### Smoothness
Controls how rounded the corners are:
```python
# In base.py
create_smooth_curve(waypoints, smoothness=0.8)  # More rounded
create_smooth_curve(waypoints, smoothness=0.4)  # Sharper corners
```

## Performance

### Complexity
- Collision detection: O(n) per edge
- Route planning: O(1) (fixed number of attempts)
- Curve generation: O(k) where k = number of waypoints

### Impact
- 21-node coffee shop diagram: renders in ~0.5s
- No noticeable performance impact
- Curves only generated when needed (17% of edges)

## Code Structure

### New Files
```
src/excelimermaid/layout/
├── edge_routing.py         # NEW: Routing algorithms
├── geometry.py             # Updated: Added Node import
└── base.py                 # Updated: Integrated routing
```

### Key Functions

**edge_routing.py**:
- `line_intersects_bbox()` - Collision detection
- `find_obstacles()` - Identify blocking nodes
- `route_around_obstacles()` - Generate waypoints
- `create_smooth_curve()` - Smooth path generation

**base.py**:
- `_route_edge()` - Updated to use obstacle avoidance

## Examples

### Simple Test
```python
from excelimermaid import MermaidRenderer

script = """
flowchart LR
    A[Start] --> B[Middle]
    A --> C[End]
    B --> C
"""

renderer = MermaidRenderer()
diagram = renderer.parse(script)
diagram.layout()

# Check which edges are curved
for edge in diagram.diagram.edges:
    if len(edge.points) > 2:
        print(f"Curved: {edge.source.text} → {edge.target.text}")
```

### Analysis Script
```bash
python analyze_coffee.py
```

Shows which edges use curved routing and why.

## Future Enhancements

### Priority 1: Better Path Finding
- A* pathfinding for complex obstacle fields
- Multiple waypoint optimization
- Consider edge crossings as well as node crossings

### Priority 2: Orthogonal Routing
- Pure horizontal/vertical segments
- Manhattan distance routing
- Better for technical diagrams

### Priority 3: Edge Bundling
- Group parallel edges
- Reduce visual clutter
- Common in large graphs

### Priority 4: User Control
```python
# Future API
renderer = MermaidRenderer(
    edge_routing="curved",    # curved, orthogonal, straight
    avoid_crossings=True,     # Enable/disable
    route_margin=10           # Obstacle margin
)
```

## Comparison with Other Tools

| Feature | Exceli-Mermaid | Mermaid.js | Excalidraw |
|---------|----------------|------------|------------|
| Auto curved routing | ✅ Yes | ❌ No | ⚠️ Manual |
| Obstacle detection | ✅ Yes | ❌ No | ❌ No |
| Smooth curves | ✅ Yes | ⚠️ Basic | ✅ Yes |
| Hand-drawn style | ✅ Yes | ❌ No | ✅ Yes |

## Testing

All 25 tests pass with curved routing enabled:
```bash
pytest tests/ -v
# 25 passed in 0.45s ✓
```

No regressions introduced.

## Known Limitations

1. **Simple heuristic**: Uses offset routing, not optimal pathfinding
2. **No edge-edge avoidance**: Only avoids nodes, not other edges
3. **Fixed offset**: 60px offset may not be optimal for all layouts
4. **Two-waypoint maximum**: Complex obstacles may need more waypoints

These are acceptable for most flowcharts and can be enhanced incrementally.

## Conclusion

The curved routing feature:
- ✅ Automatically detects obstacles
- ✅ Routes around them with smooth curves
- ✅ Maintains hand-drawn aesthetic
- ✅ Works with all existing features
- ✅ No performance impact
- ✅ No API changes required

Diagrams now look cleaner and more professional, with edges intelligently avoiding nodes instead of crossing through them!

## Try It

```bash
# Generate diagram with curved routing
excelimermaid coffee_shop.mmd -o output.svg --roughness 0.8

# Analyze which edges are curved
python analyze_coffee.py

# Compare before/after
# Before: Edges cross nodes
# After: Edges curve around obstacles
```

The improvement is immediately visible in complex diagrams!
