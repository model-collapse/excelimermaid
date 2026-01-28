# Example: Routing Edges Around Obstacles

## Quick Command

To parse `test_crossing.mmd` with automatic obstacle avoidance:

```bash
python parse_test_crossing.py
```

This generates 4 SVG files showing different routing strategies.

## Minimal Python Example

```python
from excelimermaid import MermaidRenderer

# Read the file
with open('test_crossing.mmd', 'r') as f:
    mermaid_script = f.read()

# Create renderer with obstacle avoidance
renderer = MermaidRenderer(
    edge_routing='orthogonal',    # Manhattan-style routing
    avoid_obstacles=True,          # Enable pathfinding
    route_offset=80.0              # Distance to route around
)

# Parse, layout, export
diagram = renderer.parse(mermaid_script)
diagram.layout()
diagram.export('output.svg')
```

The edge from **Input (A)** to **Output C (H)** will automatically route around all intermediate nodes!

## Key Parameters for Obstacle Avoidance

| Parameter | Value | Effect |
|-----------|-------|--------|
| `edge_routing` | `'orthogonal'` | Manhattan-style paths (recommended) |
| `avoid_obstacles` | `True` | Enable automatic pathfinding |
| `pathfinding_algorithm` | `'astar'` | Use A* algorithm (default) |
| `route_margin` | `20.0` | Safety margin around nodes (px) |
| `route_offset` | `80.0` | Distance to route around obstacles (px) |

## Routing Styles Comparison

### 1. Orthogonal Routing (Recommended)
```python
renderer = MermaidRenderer(
    edge_routing='orthogonal',
    avoid_obstacles=True,
    route_offset=80.0
)
```
- Manhattan-style paths (horizontal/vertical only)
- Clean, professional appearance
- Perfect for technical diagrams

### 2. Curved Routing
```python
renderer = MermaidRenderer(
    edge_routing='curved',
    avoid_obstacles=True,
    smoothness=0.8
)
```
- Smooth curves around obstacles
- Organic, hand-drawn appearance
- Great for presentations

### 3. Wide Offset Routing
```python
renderer = MermaidRenderer(
    edge_routing='orthogonal',
    avoid_obstacles=True,
    route_offset=120.0,  # Wider paths
    route_margin=30.0    # More clearance
)
```
- Extra wide paths around obstacles
- Maximum clarity
- Good for complex diagrams

### 4. Straight Edges (No Avoidance)
```python
renderer = MermaidRenderer(
    edge_routing='straight',
    avoid_obstacles=False
)
```
- Direct lines between nodes
- May cross other elements
- Use only for simple diagrams

## Generated Files

Running `parse_test_crossing.py` generates:

1. **test_crossing_routed.svg** - Orthogonal routing with A* pathfinding
2. **test_crossing_curved.svg** - Curved routing with obstacle avoidance
3. **test_crossing_wide.svg** - Wider routing offset for maximum clarity
4. **test_crossing_straight.svg** - No avoidance (comparison)

## How It Works

The A* pathfinding algorithm:

1. **Analyzes the layout**: Identifies all node positions and sizes
2. **Creates obstacle map**: Marks areas occupied by nodes + margins
3. **Finds optimal path**: Uses A* to route around obstacles
4. **Generates waypoints**: Creates path points avoiding all obstacles
5. **Renders edge**: Draws the edge following the waypoints

The edge from Input (A) to Output C (H) must cross through the middle of the diagram, so it automatically:
- Routes around Process A/B/C nodes
- Avoids the Middle node
- Maintains proper clearance
- Finds the shortest valid path

## Diagram Structure

```
Input (A) ─┬─→ Process A (B) ─┐
           ├─→ Process B (C) ─┼─→ Middle (E) ─┬─→ Output A (F)
           ├─→ Process C (D) ─┘                ├─→ Output B (G)
           │                                   ├─→ Output C (H)
           └─────────(routes around)───────────┘
```

The long connection from A to H intelligently routes around all intermediate nodes!

## Tips

- **Increase `route_offset`** for wider routing paths
- **Increase `route_margin`** for more node clearance
- **Use `'orthogonal'`** for technical/professional diagrams
- **Use `'curved'`** for more organic/hand-drawn appearance
- **Set `seed`** for reproducible results
- **Adjust spacing** (`node_spacing`, `rank_spacing`) for clearer layouts
