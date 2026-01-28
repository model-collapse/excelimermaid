# Fix: Arrow Paths Overlapping Box Borders

## Issue
Arrow paths were coming too close to box borders, sometimes appearing to overlap with them.

## Root Cause
The default collision margin (`route_margin`) was set to 5.0 pixels, which provided insufficient clearance between edges and node bounding boxes.

## Solution
Increased the default margin from **5px to 15px** for better visual separation.

## Changes Made

### 1. RoutingConfig Default (`models.py`)
```python
# BEFORE
route_margin: float = 5.0

# AFTER  
route_margin: float = 15.0
```

### 2. MermaidRenderer Default (`excalidraw_renderer.py`)
```python
# BEFORE
route_margin: float = 5.0

# AFTER
route_margin: float = 15.0
```

### 3. CLI Default (`cli.py`)
```python
# BEFORE
--route-margin default=5.0

# AFTER
--route-margin default=15.0
```

### 4. Test Update (`test_routing_config.py`)
```python
# BEFORE
assert config.route_margin == 5.0

# AFTER
assert config.route_margin == 15.0
```

## Margin Guidelines

| Margin | Use Case | Visual Effect |
|--------|----------|---------------|
| 5px    | Dense layouts, space-constrained | ⚠️ Edges very close to boxes |
| 10px   | Moderate clearance | Good for most diagrams |
| **15px** | **Default - Recommended** | **Professional clearance** |
| 20px   | Conservative | Maximum visual separation |

## Impact

### Before (5px margin):
- Edges could come within 5 pixels of box borders
- Visual appearance of overlap in some cases
- Less professional look

### After (15px margin):
- Edges maintain 15 pixels clearance from boxes
- Clean, professional appearance
- No visual overlap
- Better readability

## Backward Compatibility

✅ **Fully backward compatible** - Users can still specify custom margins:

```python
# Use smaller margin if needed
renderer = MermaidRenderer(route_margin=5.0)

# Use larger margin for more space
renderer = MermaidRenderer(route_margin=20.0)
```

```bash
# CLI with custom margin
excelimermaid diagram.mmd -o output.svg --route-margin 10.0
```

## Test Results

**All 35 tests passing** ✅

Generated comparison diagrams:
- `margin_5px.svg` - Old default (tight)
- `margin_10px.svg` - Medium clearance
- `margin_15px.svg` - New default (recommended)
- `margin_20px.svg` - Conservative clearance

## Files Modified

1. `src/excelimermaid/graph/models.py` - Default changed
2. `src/excelimermaid/renderer/excalidraw_renderer.py` - Default changed
3. `src/excelimermaid/cli.py` - Default changed
4. `tests/test_routing_config.py` - Test updated

## Summary

The 15px margin provides a good balance between:
- **Compact layouts** (not too much wasted space)
- **Visual clarity** (sufficient clearance from boxes)
- **Professional appearance** (clean, polished look)

This fix ensures edges maintain proper clearance from node borders while using A* pathfinding with orthogonal routing.
