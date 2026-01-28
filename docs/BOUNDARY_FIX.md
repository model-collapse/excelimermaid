# Fix: Arrow Paths Starting Inside Source Boxes

## Issue
Arrow paths were starting inside the source box and then exiting, rather than starting cleanly from the box boundary.

## Root Cause
When A* pathfinding started from a point exactly on the box boundary, the obstacle detection margin caused A* to think the starting point was inside an obstacle. This made A* route the path to first exit the "obstacle" before heading toward the target.

## Solution
Implemented a two-step approach:
1. **Push start/end points outward** by `margin + 5` pixels before pathfinding
2. **Replace with original boundary points** after pathfinding completes

This ensures A* starts from clear space while the rendered path connects cleanly to box boundaries.

## Changes Made

### New Function: `_push_point_outward()` in `pathfinding.py`

```python
def _push_point_outward(point: Point, bbox: BoundingBox, distance: float) -> Point:
    """
    Push a point outward from a bounding box by a specified distance.

    This ensures the point is in clear space, not on the box boundary.
    """
    import math

    # Calculate center of box
    center_x = bbox.x + bbox.width / 2
    center_y = bbox.y + bbox.height / 2

    # Calculate direction from center to point
    dx = point.x - center_x
    dy = point.y - center_y

    # Normalize direction
    length = math.sqrt(dx * dx + dy * dy)
    if length < 0.001:  # Point is at center, push right
        return Point(point.x + distance, point.y)

    dx /= length
    dy /= length

    # Push point outward
    return Point(point.x + dx * distance, point.y + dy * distance)
```

### Modified: `astar_route_around_obstacles()` in `pathfinding.py`

```python
# Push start and end points outward from their boxes to ensure they're in clear space
# This prevents A* from thinking the start/end is inside an obstacle
start_adjusted = _push_point_outward(start, source_node.bbox, margin + 5)
end_adjusted = _push_point_outward(end, target_node.bbox, margin + 5)

# Find path with or without diagonal movement
allow_diagonal = not orthogonal
path = pathfinder.find_path(start_adjusted, end_adjusted, allow_diagonal=allow_diagonal)

# Replace first and last points with original boundary points
if len(path) > 0:
    path[0] = start
if len(path) > 1:
    path[-1] = end

return path
```

## How It Works

### Before Fix:
```
┌─────────┐
│  Start  │
│    ↓    │  <-- Path starts inside box
└────↓────┘
     ↓
     ↓→Target
```

The boundary point (159, 100) was marked as obstacle due to margin, so A* routed inside first.

### After Fix:
```
┌─────────┐
│  Start  │
└────↓────┘  <-- Path starts at boundary
     ↓
     ↓
     ↓→Target
```

1. Pathfinding uses adjusted point (159, 105) which is in clear space
2. A* finds clean path from clear space to clear space
3. Rendered path uses original boundary points (159, 100) for clean connection

## Technical Details

**Push Distance**: `margin + 5` pixels
- If margin = 15px, push distance = 20px
- This ensures the adjusted point is well outside the obstacle zone
- Larger margin requires larger push to stay clear

**Direction Calculation**:
- Pushes radially outward from box center
- Maintains the connection angle to the box
- Special case: if point is at center, pushes right

**Boundary Preservation**:
- Original boundary points calculated by edge routing algorithm
- Only pathfinding uses adjusted points
- Final path always uses original boundaries for rendering

## Verification

Test diagram analysis (`test_fixed_boundary.svg`):

| Box | Center | Boundary | Arrow Start | Status |
|-----|--------|----------|-------------|--------|
| Start | (159, 70) | y=100 (bottom) | (159.0, 100.0) | ✅ On boundary |
| Center Point | (159, 150) | y=180 (bottom) | (184.9, 180.0) | ✅ On boundary |
| Center Point | (159, 150) | y=180 (bottom) | (133.2, 180.1) | ✅ On boundary |

All arrows now start exactly at box boundaries, not inside boxes.

## Impact

### Before:
- Paths appeared to start inside source boxes
- Visual confusion about connection points
- Unprofessional appearance

### After:
- Paths start cleanly from box boundaries
- Clear visual connection from box edge to target
- Professional, polished look
- Maintains obstacle avoidance benefits of A*

## Test Results

**All 35 tests passing** ✅

Generated test diagram:
- `test_fixed_boundary.svg` - Demonstrates clean boundary connections

## Files Modified

1. `src/excelimermaid/layout/pathfinding.py`
   - Added `_push_point_outward()` function
   - Modified `astar_route_around_obstacles()` to use adjusted points

## Summary

The boundary fix ensures that A* pathfinding operates in clear space while maintaining clean visual connections to box boundaries. This combines the benefits of robust obstacle avoidance with professional-looking edge routing.

**Key Insight**: Pathfinding and rendering can use different start/end points - adjusted points for algorithm clarity, original points for visual correctness.
