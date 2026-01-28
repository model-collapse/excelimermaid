# Using A* Pathfinding with Excelimermaid

## Quick Answer

**A* pathfinding is ENABLED BY DEFAULT** for all edges when using obstacle avoidance.

## CLI Usage

### Basic A* Usage (Default)

```bash
# A* is enabled by default - just specify routing mode
excelimermaid test_crossing.mmd -o output.svg --edge-routing orthogonal
```

### Explicit A* with Options

```bash
# Explicitly specify A* algorithm
excelimermaid test_crossing.mmd -o output.svg \
    --edge-routing orthogonal \
    --pathfinding-algorithm astar \
    --pathfinding-cell-size 10
```

### Alternative: Heuristic Pathfinding

```bash
# Use faster heuristic algorithm (less optimal paths)
excelimermaid test_crossing.mmd -o output.svg \
    --edge-routing orthogonal \
    --pathfinding-algorithm heuristic
```

### Disable Obstacle Avoidance

```bash
# No pathfinding - direct lines (edges may cross nodes)
excelimermaid test_crossing.mmd -o output.svg \
    --no-avoid-obstacles
```

## CLI Options for Pathfinding

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--pathfinding-algorithm` | `astar`, `heuristic` | `astar` | Algorithm for finding paths around obstacles |
| `--pathfinding-cell-size` | Integer (pixels) | `10` | Grid cell size for A* (smaller = more precise, slower) |
| `--edge-routing` | `orthogonal`, `curved`, `straight` | `curved` | Edge routing style |
| `--no-avoid-obstacles` | Flag | False | Disable pathfinding entirely |
| `--route-margin` | Float (pixels) | `15.0` | Safety margin around nodes |
| `--route-offset` | Float (pixels) | `60.0` | Distance to route around obstacles |

## Complete CLI Examples

### Example 1: Orthogonal with A* (Recommended)

```bash
excelimermaid test_crossing.mmd -o output.svg \
    --edge-routing orthogonal \
    --pathfinding-algorithm astar \
    --route-offset 80
```

**Result:** Manhattan-style paths with optimal A* routing around all obstacles.

### Example 2: Curved with A* (Artistic)

```bash
excelimermaid test_crossing.mmd -o output.svg \
    --edge-routing curved \
    --pathfinding-algorithm astar \
    --smoothness 0.8 \
    --route-offset 100
```

**Result:** Smooth curves that intelligently avoid obstacles.

### Example 3: Fine-Grained A* Grid

```bash
excelimermaid test_crossing.mmd -o output.svg \
    --edge-routing orthogonal \
    --pathfinding-algorithm astar \
    --pathfinding-cell-size 5 \
    --route-margin 20
```

**Result:** More precise pathfinding with smaller grid cells (slower but more accurate).

### Example 4: Fast Heuristic (Large Diagrams)

```bash
excelimermaid test_crossing.mmd -o output.svg \
    --edge-routing orthogonal \
    --pathfinding-algorithm heuristic
```

**Result:** Faster pathfinding for large diagrams (paths may be less optimal).

## Per-Edge A* Specification (Not Supported)

### Can I specify A* per edge in the .mmd file?

**No.** Standard Mermaid syntax does not support per-edge pathfinding algorithm specification.

**Why?**
- Mermaid is a declarative diagram language focused on structure, not rendering
- Pathfinding is a rendering/layout concern, not a diagram structure concern
- Standard Mermaid syntax: `A --> B` doesn't have attributes for rendering algorithms

### Workarounds

If you need different routing for different edges:

#### Option 1: Separate Diagrams
```bash
# Diagram 1 with A*
excelimermaid diagram1.mmd -o output1.svg --pathfinding-algorithm astar

# Diagram 2 with heuristic
excelimermaid diagram2.mmd -o output2.svg --pathfinding-algorithm heuristic
```

#### Option 2: Python API (Programmatic Control)
```python
from excelimermaid import MermaidRenderer

# You can create multiple renderers with different settings
renderer_astar = MermaidRenderer(
    pathfinding_algorithm='astar',
    edge_routing='orthogonal'
)

renderer_heuristic = MermaidRenderer(
    pathfinding_algorithm='heuristic',
    edge_routing='curved'
)

# But all edges in a single diagram use the same algorithm
diagram = renderer_astar.parse(script)
```

#### Option 3: Post-Processing (Advanced)
- Render diagram
- Programmatically modify specific edge paths in the SVG
- Requires custom SVG manipulation

### Why Apply Algorithm Globally?

**Design Philosophy:**
- Consistency: All edges follow same routing rules
- Predictability: Same input always produces same layout
- Performance: Single pathfinding pass for all edges
- Simplicity: One algorithm configuration for entire diagram

**Alternative Mermaid Tools:**
- Standard Mermaid.js: No pathfinding at all (simple curved lines)
- Excelimermaid: Global pathfinding for all edges (current)
- Custom Extensions: Would require non-standard Mermaid syntax

## Python API Usage

For programmatic control:

```python
from excelimermaid import MermaidRenderer

# A* pathfinding (default)
renderer = MermaidRenderer(
    edge_routing='orthogonal',
    avoid_obstacles=True,              # Enable pathfinding
    pathfinding_algorithm='astar',     # A* algorithm
    pathfinding_cell_size=10,          # Grid precision
    route_offset=80.0                  # Routing distance
)

diagram = renderer.parse(mermaid_script)
diagram.layout()
diagram.export('output.svg')
```

## Algorithm Comparison

### A* Pathfinding (Default)

**Pros:**
- Optimal paths (shortest valid route)
- Guaranteed to avoid all obstacles
- Widely used, well-tested algorithm
- Good for complex diagrams

**Cons:**
- Slower on very large diagrams
- Memory usage increases with diagram size

**Best for:**
- General use
- Complex diagrams with many obstacles
- When path optimality matters

### Heuristic Pathfinding

**Pros:**
- Faster than A*
- Lower memory usage
- Good for large diagrams

**Cons:**
- Paths may not be optimal
- Still avoids obstacles but may take longer routes

**Best for:**
- Large diagrams (100+ nodes)
- When speed is more important than optimal paths
- Prototyping/iteration

## Performance Tips

### For Small Diagrams (< 20 nodes)
```bash
excelimermaid diagram.mmd -o output.svg \
    --pathfinding-algorithm astar \
    --pathfinding-cell-size 5  # Higher precision
```

### For Medium Diagrams (20-50 nodes)
```bash
excelimermaid diagram.mmd -o output.svg \
    --pathfinding-algorithm astar \
    --pathfinding-cell-size 10  # Default
```

### For Large Diagrams (50+ nodes)
```bash
excelimermaid diagram.mmd -o output.svg \
    --pathfinding-algorithm heuristic \
    --pathfinding-cell-size 15  # Larger cells
```

## Common Use Cases

### Case 1: Long-Distance Edges (Like test_crossing.mmd)

The edge from Input (A) to Output C (H) must cross the entire diagram:

```bash
excelimermaid test_crossing.mmd -o output.svg \
    --edge-routing orthogonal \
    --pathfinding-algorithm astar \
    --route-offset 100  # Wide paths for clarity
```

### Case 2: Dense Diagrams

Many nodes close together:

```bash
excelimermaid dense.mmd -o output.svg \
    --edge-routing curved \
    --pathfinding-algorithm astar \
    --route-margin 25  # More clearance
```

### Case 3: Presentation Quality

Optimal paths with smooth curves:

```bash
excelimermaid diagram.mmd -o output.svg \
    --edge-routing curved \
    --pathfinding-algorithm astar \
    --smoothness 0.9 \
    --route-offset 120
```

## Installation and Entry Point

The CLI is installed as `excelimermaid` command:

```bash
# After installation
pip install -e .

# Use the command
excelimermaid --help
excelimermaid diagram.mmd -o output.svg
```

Or run directly:

```bash
python -m excelimermaid.cli diagram.mmd -o output.svg
```

## Summary

| Question | Answer |
|----------|--------|
| **Is A* enabled by default?** | Yes, when `avoid_obstacles=True` (default) |
| **How to use A* in CLI?** | Just use `--edge-routing orthogonal` (A* is default algorithm) |
| **How to specify A* per edge in .mmd?** | Not supported - Mermaid syntax doesn't have rendering attributes |
| **Can I disable A*?** | Yes: `--no-avoid-obstacles` or `--pathfinding-algorithm heuristic` |
| **How to customize A*?** | Use `--pathfinding-cell-size`, `--route-offset`, `--route-margin` |
| **Which algorithm is faster?** | Heuristic is faster, A* is more optimal |

## Getting Help

```bash
# See all CLI options
excelimermaid --help

# See version
excelimermaid --version
```

## Testing

Generated test files with different algorithms:
- `cli_test_astar.svg` - A* pathfinding (optimal)
- `cli_test_heuristic.svg` - Heuristic pathfinding (faster)

Compare these to see the difference!
