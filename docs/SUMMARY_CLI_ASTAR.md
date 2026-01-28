# Summary: A* Pathfinding in Excelimermaid

## Your Questions Answered

### Q1: How can I specify an edge that should be using A* in .mmd?

**Answer:** You cannot specify A* per-edge in the .mmd file.

**Why?**
- Standard Mermaid syntax (`A --> B`) doesn't support rendering attributes
- Mermaid is declarative (structure only), not prescriptive (rendering details)
- Pathfinding is a rendering concern, not a diagram structure concern

**What happens instead:**
- A* pathfinding is applied **globally to all edges** in the diagram
- This ensures consistency and predictability
- All edges follow the same routing rules

### Q2: How can I enable A* in the CLI?

**Answer:** A* is **ENABLED BY DEFAULT**. You don't need to do anything special.

## CLI Usage

### Default Behavior (A* Enabled)

```bash
# A* is already enabled by default
excelimermaid test_crossing.mmd -o output.svg --edge-routing orthogonal
```

### Explicit A* Configuration

```bash
# Explicitly specify A* with custom settings
excelimermaid test_crossing.mmd -o output.svg \
    --edge-routing orthogonal \
    --pathfinding-algorithm astar \
    --pathfinding-cell-size 10 \
    --route-offset 100
```

### Alternative Algorithms

```bash
# Heuristic pathfinding (faster, less optimal)
excelimermaid test_crossing.mmd -o output.svg \
    --pathfinding-algorithm heuristic

# No pathfinding (direct lines, may cross)
excelimermaid test_crossing.mmd -o output.svg \
    --no-avoid-obstacles
```

## CLI Options Added

The following new options were added to the CLI:

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--pathfinding-algorithm` | `astar`, `heuristic` | `astar` | Algorithm choice |
| `--pathfinding-cell-size` | Integer | `10` | Grid cell size (pixels) |
| `--sketch-style` | `subtle`, `standard`, `heavy` | `heavy` | Hand-drawn preset |
| `--no-multi-stroke` | Flag | False | Disable multi-stroke drawing |

Existing options that control pathfinding:
| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--edge-routing` | `orthogonal`, `curved`, `straight` | `curved` | Routing style |
| `--no-avoid-obstacles` | Flag | False | Disable pathfinding |
| `--route-margin` | Float | `15.0` | Collision margin |
| `--route-offset` | Float | `60.0` | Routing distance |
| `--smoothness` | Float | `0.8` | Curve smoothness |

## Complete Example for test_crossing.mmd

### Recommended Command

```bash
excelimermaid test_crossing.mmd -o output.svg \
    --edge-routing orthogonal \
    --pathfinding-algorithm astar \
    --route-offset 100 \
    --route-margin 20
```

**Result:** The edge from Input (A) to Output C (H) will intelligently route AROUND all intermediate nodes using A* pathfinding.

### What Happens

1. **Layout Phase**: Nodes are positioned using hierarchical layout
2. **Pathfinding Phase**: For each edge (including A → H):
   - Creates obstacle map from node positions
   - Runs A* algorithm to find optimal path avoiding obstacles
   - Generates waypoints for the path
3. **Rendering Phase**: Draws edges following the waypoints

### Visual Result

```
Input (A) ─┬─→ Process A (B) ─┐
           ├─→ Process B (C) ─┼─→ Middle (E) ─┬─→ Output A (F)
           ├─→ Process C (D) ─┘                ├─→ Output B (G)
           │                                   ├─→ Output C (H)
           └─────────(routes AROUND)───────────┘
                    ↑ A* pathfinding here!
```

## Python API (Alternative)

If you need programmatic control:

```python
from excelimermaid import MermaidRenderer

with open('test_crossing.mmd') as f:
    script = f.read()

renderer = MermaidRenderer(
    edge_routing='orthogonal',
    avoid_obstacles=True,              # Enable pathfinding
    pathfinding_algorithm='astar',     # A* (default)
    pathfinding_cell_size=10,          # Grid precision
    route_offset=100.0,                # Routing distance
    route_margin=20.0                  # Collision margin
)

diagram = renderer.parse(script)
diagram.layout()
diagram.export('output.svg')
```

## Files Created

### Documentation
- ✅ **ASTAR_USAGE.md** - Comprehensive A* pathfinding guide
- ✅ **CLI_QUICK_REFERENCE.md** - Quick command reference
- ✅ **SUMMARY_CLI_ASTAR.md** - This file

### Test Files Generated
- ✅ `cli_test_astar.svg` - Using A* pathfinding
- ✅ `cli_test_heuristic.svg` - Using heuristic pathfinding

### Example Scripts
- ✅ `parse_test_crossing.py` - Python example (4 routing styles)
- ✅ `simple_crossing.py` - Minimal Python example
- ✅ `EXAMPLE_CROSSING.md` - Obstacle avoidance examples

## CLI Changes Summary

**File Modified:** `src/excelimermaid/cli.py`

**Changes:**
1. Added `--pathfinding-algorithm` option (default: `astar`)
2. Added `--pathfinding-cell-size` option (default: `10`)
3. Added `--sketch-style` option (default: `heavy`)
4. Added `--no-multi-stroke` flag
5. Updated default `--roughness` to `2.0` (was `1.0`)
6. Updated default `--smoothness` to `0.8` (was `0.6`)
7. Updated help text with A* examples
8. Passed new parameters to `MermaidRenderer`

**Testing:**
- ✅ All 35 tests passing
- ✅ CLI tested with both `astar` and `heuristic` algorithms
- ✅ Backward compatible

## Key Takeaways

1. **A* is on by default** - You get intelligent pathfinding automatically
2. **No per-edge control in .mmd** - Global algorithm for all edges
3. **CLI is ready to use** - Just specify `--edge-routing orthogonal`
4. **Customizable** - Many options to tune pathfinding behavior
5. **Fast alternative available** - Use `--pathfinding-algorithm heuristic` for large diagrams

## Quick Start

```bash
# Test with your file
excelimermaid test_crossing.mmd -o output.svg --edge-routing orthogonal

# See help
excelimermaid --help

# Compare algorithms
excelimermaid test.mmd -o astar.svg --pathfinding-algorithm astar
excelimermaid test.mmd -o heuristic.svg --pathfinding-algorithm heuristic
```

## Need More Help?

- See `ASTAR_USAGE.md` for comprehensive guide
- See `CLI_QUICK_REFERENCE.md` for quick commands
- Run `excelimermaid --help` for all options
- Check `EXAMPLE_CROSSING.md` for obstacle avoidance examples
