# Grid Visualization for Pathfinding Debug

## Overview

When debug logging is enabled, the pathfinding system automatically generates a visual representation of the grid showing obstacles, nodes, and routed paths.

## Usage

Simply enable debug mode:

```bash
excelimermaid diagram.mmd -o output.svg --debug
```

This will:
1. Render your diagram normally
2. Generate a PNG image showing the pathfinding grid
3. Save it as `pathfinding_grid_debug_TIMESTAMP.png`

## What's in the Visualization

The generated image shows:

### Grid Cells
- **Red cells** - Obstacles (node boundaries + margins)
- **White cells** - Walkable areas
- **Grid lines** - Cell boundaries

### Nodes
- **Blue rectangles** - Node bounding boxes
- **Blue labels** - Node IDs (A, B, C, etc.)

### Paths (if routed)
- **Colored lines** - Routed edge paths
- Multiple colors for different edges

### Legend
Right side shows:
- Obstacle cells (red)
- Walkable cells (white)
- Node boundaries (blue)
- Routed paths count

### Info Bar
Bottom shows:
- Grid dimensions (e.g., 44x32 cells)
- Cell size in pixels
- Margin size
- Number of nodes
- Number of routed edges

## Example Output

```bash
$ excelimermaid test_crossing.mmd -o output.svg --debug
...
INFO: Adaptive A* pathfinding complete: 10 edges routed successfully
INFO: Grid visualization saved to pathfinding_grid_debug_20260128_104133.png
INFO: Grid visualization: 44x32 cells, 1801 obstacle cells
✓ Saved to output.svg
```

File created: `pathfinding_grid_debug_20260128_104133.png`

## Interpreting the Visualization

### Red Areas (Obstacles)
These are where edges **cannot** pass through:
- Node bounding boxes + margin
- Previously routed edges (marked as obstacles for later edges)

### White Areas (Walkable)
These are valid paths for routing edges.

### Dense Red vs Sparse Red
- **Dense red** - Tight spaces, difficult routing
- **Sparse red** - Open spaces, easier routing

### Node Positions
Blue rectangles show actual node positions and sizes. If nodes are very close together, routing becomes difficult.

### Path Lines
Colored lines show how edges were successfully routed around obstacles.

## Debugging with Visualization

### Problem: All edges fail routing
**Look for:**
- Very dense red areas (too many obstacles)
- Red covering most of the grid
- Nodes too close together

**Solution:**
- Increase `--node-spacing`
- Reduce `--route-margin`

### Problem: Specific edges fail
**Look for:**
- Red blocking the direct path between two nodes
- No white path connecting them

**Solution:**
- The edges that fail are using direct lines (visible in diagram)
- May need layout adjustment

### Problem: Paths look strange
**Look for:**
- Paths going around red areas (correct behavior)
- Paths crossing red areas (shouldn't happen, but if so it's a bug)

## File Naming

Files are timestamped for uniqueness:
```
pathfinding_grid_debug_20260128_104133.png
                       YYYYMMDD_HHMMSS
```

This allows multiple runs without overwriting previous debug images.

## Requirements

- **PIL/Pillow** - Required for image generation
- Automatically installed with excelimermaid

If PIL is not available:
```
WARNING: PIL not available - cannot generate grid visualization
```

Install with:
```bash
pip install Pillow
```

## Visualization Details

### Cell Size
Cell pixel size is automatically calculated based on grid dimensions:
- Larger cells for small grids (better visibility)
- Smaller cells for large grids (image fits in reasonable size)
- Range: 8-20 pixels per cell

### Image Dimensions
- Width: grid_width × cell_size + 200px (legend space)
- Height: grid_height × cell_size + 50px (info bar)
- Typical size: 400-800 pixels wide

### Colors Used
- **Obstacles**: Light red (#ffcccc) with red outline (#ff0000)
- **Walkable**: White with light gray grid (#e0e0e0)
- **Nodes**: Blue outlines (#0000ff)
- **Paths**: Various colors (#0066ff, #00cc00, #ff00ff, etc.)

## Examples

### Example 1: Simple Diagram
```bash
excelimermaid simple.mmd -o output.svg --debug
```

Generated grid:
- Small grid (20x15 cells)
- Large cells (20px each)
- Clear visualization of all nodes and paths

### Example 2: Complex Diagram
```bash
excelimermaid complex.mmd -o output.svg --debug
```

Generated grid:
- Large grid (80x60 cells)
- Small cells (8px each)
- Shows overall obstacle density

### Example 3: With Custom Margins
```bash
excelimermaid diagram.mmd -o output.svg --debug --route-margin 30
```

You'll see:
- Larger red areas around nodes (30px margin)
- Less white space for routing
- Explains why edges might fail

## Disabling Visualization

Grid visualization only happens with `--debug`. Use other log levels to skip it:

```bash
# No visualization
excelimermaid diagram.mmd -o output.svg

# No visualization (INFO logging)
excelimermaid diagram.mmd -o output.svg --verbose

# YES - visualization (DEBUG logging)
excelimermaid diagram.mmd -o output.svg --debug
```

## Performance Impact

- Visualization adds ~50-100ms to render time
- Only runs when `--debug` is enabled
- No impact on normal rendering

## Troubleshooting

### Problem: No PNG generated
**Check:**
1. Is `--debug` flag used?
2. Is PIL/Pillow installed?
3. Check logs for error messages

### Problem: Image is too small/large
**Automatic:** Cell size adapts to grid dimensions. No manual adjustment needed.

### Problem: Can't see node labels
**Solution:** Node labels are automatically sized. On very large grids they may be small.

### Problem: Paths overlap
**Normal:** Multiple edges may use similar paths. Different colors help distinguish them.

## Use Cases

### 1. Understanding Why Edges Fail
```bash
excelimermaid diagram.mmd -o output.svg --debug 2>&1 | grep FAILED
# Then open pathfinding_grid_debug_*.png to see why
```

Visual inspection shows:
- Red areas blocking the path
- Nodes too close together
- No walkable route available

### 2. Tuning Parameters
Try different margins and see the effect:
```bash
excelimermaid diagram.mmd -o output1.svg --debug --route-margin 10
excelimermaid diagram.mmd -o output2.svg --debug --route-margin 20
excelimermaid diagram.mmd -o output3.svg --debug --route-margin 30
```

Compare the PNG files to see obstacle density.

### 3. Validating Layout
Check if node layout creates routing problems:
```bash
excelimermaid diagram.mmd -o output.svg --debug --node-spacing 100
```

See if more spacing helps routing.

### 4. Bug Reports
Include the grid visualization when reporting routing issues:
```bash
excelimermaid problem.mmd -o output.svg --debug
# Attach pathfinding_grid_debug_*.png to bug report
```

## Summary

**Grid visualization:**
- ✅ Automatic with `--debug` flag
- ✅ Shows obstacles (red), walkable (white), nodes (blue), paths (colored)
- ✅ Timestamped filenames
- ✅ Legend and info included
- ✅ Requires PIL/Pillow
- ✅ Perfect for debugging routing issues
- ✅ Visual feedback on parameter tuning

**Use it to:**
- Understand why edges fail
- See obstacle density
- Validate margin settings
- Debug layout issues
- Report bugs visually
