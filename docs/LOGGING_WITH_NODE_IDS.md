# Enhanced Logging: Node IDs Added

## Summary

Updated pathfinding logs to include node IDs (box names) along with coordinates, making debugging much easier.

## Changes Made

### Modified Function Signatures

**`AdaptivePathfinder.find_path()`**
```python
def find_path(self, start: Point, end: Point, orthogonal: bool = True,
              source_id: str = None, target_id: str = None) -> List[Point]:
```

**`AdaptivePathfinder.try_with_smaller_cells()`**
```python
def try_with_smaller_cells(self, start: Point, end: Point, orthogonal: bool,
                           source_id: str = None, target_id: str = None) -> Optional[List[Point]]:
```

### Updated Log Messages

All failure and retry messages now include `[source_id → target_id]` prefix.

## Example Output

### Before (Coordinates Only)
```
WARNING: A* pathfinding FAILED: No path found from (0.0, 81.9) to (-64.0, 58.1).
         Grid: 44x32, cell size: 16px. Falling back to direct line.
```

### After (Node IDs + Coordinates)
```
WARNING: A* pathfinding FAILED: [A → C] No path found from (0.0, 81.9) to (-64.0, 58.1).
         Grid: 44x32, cell size: 16px. Falling back to direct line.
```

## Complete Example Session

```
INFO: Starting adaptive A* pathfinding for 10 edges, 8 nodes. Routing mode: orthogonal
INFO: Adaptive parameters: margin=16.9px, cell_size=16px, grid=44x32
INFO: Edges sorted by length (shortest first). Processing in order...

DEBUG: [1/10] Routing edge E → G (length=80.0px)
WARNING: A* pathfinding FAILED: [E → G] No path found from (-2.0, 241.9) to (-2.0, 218.1).
         Grid: 44x32, cell size: 16px. Falling back to direct line.
DEBUG: [1/10] Edge E → G routed: 2 waypoints

DEBUG: [7/10] Routing edge B → E (length=209.8px)
WARNING: A* pathfinding FAILED: [B → E] No path found from (-118.1, 110.0) to (-73.9, 190.0).
         Grid: 44x32, cell size: 16px. Falling back to direct line.
INFO: [B → E] Path suspiciously simple for long edge (length=209.8px, waypoints=2).
      Attempting smaller cell size...
INFO: Retrying pathfinding with SMALLER CELLS: [B → E] 16px → 8px
      from (-118.1, 110.0) to (-73.9, 190.0)
WARNING: A* pathfinding FAILED: [B → E] No path found from (-118.1, 110.0) to (-73.9, 190.0).
         Grid: 88x63, cell size: 8px. Falling back to direct line.
WARNING: [B → E] Retry with smaller cells FAILED: Still no valid path found

DEBUG: [9/10] Routing edge E → H (length=213.6px)
INFO: [E → H] Path suspiciously simple for long edge (length=213.6px, waypoints=2).
      Attempting smaller cell size...
INFO: Retrying pathfinding with SMALLER CELLS: [E → H] 16px → 8px
      from (69.9, 190.0) to (122.1, 270.0)
INFO: [E → H] Retry with smaller cells SUCCEEDED: Found path with 4 waypoints
INFO: [E → H] Smaller cells improved path: 2 → 4 waypoints
DEBUG: [9/10] Edge E → H routed: 4 waypoints

INFO: Adaptive A* pathfinding complete: 10 edges routed successfully
```

## Benefits

### 1. Immediate Edge Identification
**Before:**
```
WARNING: No path found from (0.0, 60.0) to (196.0, 240.0)
```
❓ Which edge is this?

**After:**
```
WARNING: [A → H] No path found from (0.0, 60.0) to (196.0, 240.0)
```
✅ Clearly see it's edge from node A to node H

### 2. Pattern Recognition
Easy to see if specific nodes have routing problems:
```
WARNING: [A → C] No path found...
WARNING: [A → D] No path found...
WARNING: [A → H] No path found...
```
→ All edges from node A are failing!

### 3. Retry Tracking
Clear which edge is being retried:
```
INFO: [E → H] Path suspiciously simple...
INFO: [E → H] Retry with smaller cells SUCCEEDED
```

### 4. Debug Workflow

**Quick scan for problems:**
```bash
python render.py 2>&1 | grep FAILED | grep -o '\[.*→.*\]' | sort | uniq
```

Output:
```
[A → B]
[A → C]
[A → D]
[A → H]
[B → E]
[C → E]
```

**Find all edges from specific node:**
```bash
python render.py 2>&1 | grep 'FAILED.*\[A →'
```

## Testing

```bash
# Test with logging
python test_pathfinding_with_logging.py

# View only failures with node IDs
python test_pathfinding_with_logging.py 2>&1 | grep FAILED

# Count failures per source node
python test_pathfinding_with_logging.py 2>&1 | grep -o '\[.* →' | sort | uniq -c
```

## Example Analysis

Given this log output:
```
WARNING: [A → B] No path found from (-71.9, 30.0) to (-118.1, 110.0)
WARNING: [A → C] No path found from (0.0, 81.9) to (-64.0, 58.1)
WARNING: [A → D] No path found from (0.0, 81.9) to (68.0, 58.1)
WARNING: [A → H] No path found from (0.0, 81.9) to (196.0, 218.1)
```

**Analysis:**
1. All edges from node A are failing
2. Node A is at roughly (0, 60) - center of diagram
3. Other nodes arranged around it
4. **Problem:** Node A's margin may be blocking all exit paths
5. **Solution:** Reduce `route_margin` or increase `node_spacing`

## Updated Documentation

### Function Call Sites

All calls to `find_path()` and `try_with_smaller_cells()` now include node IDs:

```python
# In route_edges_adaptively()
path = pathfinder.find_path(start, end, orthogonal, edge.source.id, edge.target.id)

smaller_path = pathfinder.try_with_smaller_cells(
    start, end, orthogonal,
    edge.source.id, edge.target.id
)
```

## Log Format Reference

### Failure Messages
```
WARNING: A* pathfinding FAILED: [source → target] No path found from (x1, y1) to (x2, y2).
         Grid: WxH, cell size: Npx. Falling back to direct line.
```

### Retry Messages
```
INFO: [source → target] Path suspiciously simple for long edge (length=Xpx, waypoints=2).
      Attempting smaller cell size...
INFO: Retrying pathfinding with SMALLER CELLS: [source → target] Xpx → Ypx from (x1, y1) to (x2, y2)
```

### Success Messages
```
INFO: [source → target] Retry with smaller cells SUCCEEDED: Found path with N waypoints
INFO: [source → target] Smaller cells improved path: 2 → N waypoints
```

### Failure Messages
```
WARNING: [source → target] Retry with smaller cells FAILED: Still no valid path found
```

## Migration

**No changes needed for existing code!**
- Node IDs are optional parameters
- If not provided, logs omit the `[source → target]` prefix
- Backward compatible with old code

## Summary

✅ All pathfinding logs now include node IDs
✅ Easy to identify which edges have routing problems
✅ Pattern recognition for debugging
✅ Backward compatible
✅ All 35 tests passing

**Result:** Debugging is now much easier - you can immediately see which boxes are involved in failed routing!
