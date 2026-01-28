# Changelog

## [Unreleased]

### Major Improvements

#### Intelligent Edge Routing
- **Distance-based attachment point selection**: Edges now connect via geometrically closest sides
- **Flow-direction awareness**: Routing respects flowchart direction (LR, TD, etc.) with 20% penalty for non-flow-appropriate connections
- **Adaptive push distance**: Minimum cell_size push for close boxes to clear obstacle grid
- **Multi-attachment A* optimization**: When A* pathfinding is needed, tries multiple attachment point combinations and selects shortest path

#### Path Optimization
- **String pulling algorithm**: Removes unnecessary waypoints using line-of-sight optimization
- **Aggressive simplification**: Reduces paths by 80-90% (e.g., 50→5 waypoints) while maintaining valid routing
- **Gentle curve generation**: Adds subtle parabolic curves (2.5% of line length) to simplified straight segments
- **Catmull-Rom spline smoothing**: Creates natural curves through multi-waypoint paths

#### Visual Refinements
- **Adaptive corner rounding**: Only rounds major corners (>45°), with radius scaled to 40% of shorter segment (max 50px)
- **Adaptive arrow sizing**: Arrow head scales from 8px (short paths) to 20px (long paths) based on 15% of path length
- **Reduced roughness**: Default roughness reduced to 1.0 (from 2.0) for cleaner hand-drawn appearance
- **Edge label positioning**: Labels placed at 1/4 path length for decision nodes (near source) instead of midpoint

### Bug Fixes
- Fixed obstacle visualization: Grid dimensions now properly reset after adaptive cell size retry
- Fixed box obstacle marking: Removed margin expansion - boxes mark only exact area
- Fixed edge obstacle marking: Edges mark single-cell width without expansion
- Fixed path checking failure: Ensured minimum push distance equals cell_size to clear obstacle grid cells
- Fixed backwards connections: Flow-appropriate side selection prevents wrong-direction routing

### Performance
- Path optimization reduces waypoint count by 80-90%
- Cleaner SVG output with fewer path segments
- Faster pathfinding with distance-sorted attachment point testing

### Examples
- Generated 15 comprehensive example diagrams covering:
  - Basic workflows and debug patterns
  - Business processes (auth, pipelines, requests)
  - Architecture (microservices, networks, events)
  - Decision trees and control flow
  - Machine learning pipelines
- All examples showcase latest routing and styling improvements

### Cleanup
- Removed 88 debug grid visualization PNG files
- Removed 60+ test SVG files and intermediate outputs
- Cleaned Python cache files (__pycache__, .pyc)
- Organized examples with numbered naming (01-15)
- Updated .gitignore to exclude debug files
- Merged README_ADDITIONS.md into main README.md
- Added examples/README.md documentation

## Technical Details

### Routing Algorithm Flow
1. Try direct paths with distance-sorted attachment points (closest first)
2. If all blocked, use A* with multiple attachment combinations
3. Select shortest A* path by actual path length
4. Apply string-pulling optimization to remove unnecessary waypoints
5. Add gentle curves to simplified straight segments
6. Apply Catmull-Rom smoothing to multi-waypoint paths
7. Round major corners with adaptive radius

### Key Parameters
- Cell size: Adaptive based on diagram size (typically 8-12px)
- Margin: 0.08 * min(width, height), max 15px (reduced from 40px)
- Push distance: cell_size for gaps < 30px, otherwise 40% of gap
- Corner radius: 40% of shorter segment, max 50px, min 20px segment length
- Arrow size: 15% of path length, clamped 8-20px
- Roughness: 1.0 (default), down from 2.0

