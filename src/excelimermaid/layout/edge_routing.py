"""Advanced edge routing with obstacle avoidance and curved paths."""

import math
from typing import List, Tuple, Optional
from ..graph.models import Point, BoundingBox, Node


def line_intersects_bbox(p1: Point, p2: Point, bbox: BoundingBox, margin: float = 5.0) -> bool:
    """
    Check if a line segment intersects with a bounding box (with margin).

    Args:
        p1: Start point of line
        p2: End point of line
        bbox: Bounding box to check collision with
        margin: Extra margin around bbox (default 5px)

    Returns:
        True if line intersects the expanded bounding box
    """
    # Expand bbox by margin
    left = bbox.x - margin
    right = bbox.x + bbox.width + margin
    top = bbox.y - margin
    bottom = bbox.y + bbox.height + margin

    # Quick bounding box check - if line's bbox doesn't overlap, no collision
    line_left = min(p1.x, p2.x)
    line_right = max(p1.x, p2.x)
    line_top = min(p1.y, p2.y)
    line_bottom = max(p1.y, p2.y)

    if line_right < left or line_left > right or line_bottom < top or line_top > bottom:
        return False

    # Check if either endpoint is inside the box
    if (left <= p1.x <= right and top <= p1.y <= bottom) or \
       (left <= p2.x <= right and top <= p2.y <= bottom):
        return True

    # Check if line segment intersects any of the four edges
    # Use line-line intersection for each edge
    edges = [
        (Point(left, top), Point(right, top)),      # Top edge
        (Point(right, top), Point(right, bottom)),  # Right edge
        (Point(right, bottom), Point(left, bottom)), # Bottom edge
        (Point(left, bottom), Point(left, top))     # Left edge
    ]

    for edge_start, edge_end in edges:
        if line_segments_intersect(p1, p2, edge_start, edge_end):
            return True

    return False


def line_segments_intersect(p1: Point, p2: Point, p3: Point, p4: Point) -> bool:
    """
    Check if two line segments intersect.

    Args:
        p1, p2: First line segment
        p3, p4: Second line segment

    Returns:
        True if segments intersect
    """
    def ccw(A: Point, B: Point, C: Point) -> bool:
        return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def find_obstacles(
    start: Point,
    end: Point,
    all_nodes: List[Node],
    source_node: Node,
    target_node: Node,
    margin: float = 5.0
) -> List[Node]:
    """
    Find nodes that would be crossed by a straight line from start to end.

    Args:
        start: Start point
        end: End point
        all_nodes: All nodes in the diagram
        source_node: Source node (to exclude)
        target_node: Target node (to exclude)
        margin: Extra margin around nodes for collision detection (default 5px)

    Returns:
        List of nodes that are obstacles
    """
    obstacles = []

    for node in all_nodes:
        # Skip source and target nodes
        if node == source_node or node == target_node:
            continue

        if not node.bbox:
            continue

        # Check if straight line crosses this node
        if line_intersects_bbox(start, end, node.bbox, margin=margin):
            obstacles.append(node)

    return obstacles


def route_around_obstacles(
    start: Point,
    end: Point,
    obstacles: List[Node],
    source_node: Node,
    target_node: Node,
    offset: float = 60.0
) -> List[Point]:
    """
    Generate waypoints to route around obstacles using curved paths.

    Strategy:
    1. If no obstacles, return direct path
    2. If obstacles exist, try routing above/below or left/right
    3. Choose the route with fewest additional obstacles

    Args:
        start: Start point on source boundary
        end: End point on target boundary
        obstacles: List of obstacle nodes
        source_node: Source node
        target_node: Target node
        offset: Distance to offset when routing around obstacles (default 60px)

    Returns:
        List of waypoints forming the path (including start and end)
    """
    if not obstacles:
        return [start, end]

    # Calculate primary direction
    dx = end.x - start.x
    dy = end.y - start.y

    # Determine if connection is more horizontal or vertical
    is_horizontal = abs(dx) > abs(dy)

    if is_horizontal:
        # Try routing above or below
        waypoints_above = _try_horizontal_route(start, end, obstacles, offset=-offset)
        waypoints_below = _try_horizontal_route(start, end, obstacles, offset=offset)

        # Choose the route with fewer crossings
        if waypoints_above and waypoints_below:
            # Pick the one that goes away from most obstacles
            return waypoints_above if _count_path_crossings(waypoints_above, obstacles) <= _count_path_crossings(waypoints_below, obstacles) else waypoints_below
        elif waypoints_above:
            return waypoints_above
        elif waypoints_below:
            return waypoints_below
    else:
        # Try routing left or right
        waypoints_left = _try_vertical_route(start, end, obstacles, offset=-offset)
        waypoints_right = _try_vertical_route(start, end, obstacles, offset=offset)

        if waypoints_left and waypoints_right:
            return waypoints_left if _count_path_crossings(waypoints_left, obstacles) <= _count_path_crossings(waypoints_right, obstacles) else waypoints_right
        elif waypoints_left:
            return waypoints_left
        elif waypoints_right:
            return waypoints_right

    # Fallback to direct path if routing fails
    return [start, end]


def _try_horizontal_route(
    start: Point,
    end: Point,
    obstacles: List[Node],
    offset: float
) -> Optional[List[Point]]:
    """
    Try routing with horizontal segments and vertical offset.

    Creates path: start -> waypoint1 -> waypoint2 -> end
    Where waypoint1 is offset vertically from start
    And waypoint2 is offset vertically from end
    """
    # Create waypoints offset vertically
    mid_x = (start.x + end.x) / 2

    waypoint1 = Point(mid_x, start.y + offset)
    waypoint2 = Point(mid_x, end.y + offset)

    path = [start, waypoint1, waypoint2, end]

    # Check if this path still crosses obstacles
    # We allow some crossing since we're trying to minimize it
    return path


def _try_vertical_route(
    start: Point,
    end: Point,
    obstacles: List[Node],
    offset: float
) -> Optional[List[Point]]:
    """
    Try routing with vertical segments and horizontal offset.
    """
    mid_y = (start.y + end.y) / 2

    waypoint1 = Point(start.x + offset, mid_y)
    waypoint2 = Point(end.x + offset, mid_y)

    path = [start, waypoint1, waypoint2, end]

    return path


def _count_path_crossings(waypoints: List[Point], obstacles: List[Node]) -> int:
    """Count how many obstacles the path crosses."""
    count = 0
    for i in range(len(waypoints) - 1):
        for obstacle in obstacles:
            if obstacle.bbox and line_intersects_bbox(waypoints[i], waypoints[i + 1], obstacle.bbox):
                count += 1
    return count


def create_smooth_curve(waypoints: List[Point], smoothness: float = 0.5) -> List[Point]:
    """
    Convert waypoints into a smooth curve using control points.

    For sharp corners, this creates rounded transitions.

    Args:
        waypoints: List of waypoints
        smoothness: How much to round corners (0.0-1.0)

    Returns:
        List of points forming a smooth curve
    """
    if len(waypoints) <= 2:
        return waypoints

    smooth_path = [waypoints[0]]  # Start point

    for i in range(1, len(waypoints) - 1):
        prev = waypoints[i - 1]
        curr = waypoints[i]
        next_pt = waypoints[i + 1]

        # Calculate vectors
        v1 = Point(curr.x - prev.x, curr.y - prev.y)
        v2 = Point(next_pt.x - curr.x, next_pt.y - curr.y)

        # Normalize
        len1 = math.sqrt(v1.x ** 2 + v1.y ** 2)
        len2 = math.sqrt(v2.x ** 2 + v2.y ** 2)

        if len1 > 0:
            v1 = Point(v1.x / len1, v1.y / len1)
        if len2 > 0:
            v2 = Point(v2.x / len2, v2.y / len2)

        # Create rounded corner
        corner_radius = min(len1, len2) * smoothness * 0.5

        # Point before corner
        before = Point(
            curr.x - v1.x * corner_radius,
            curr.y - v1.y * corner_radius
        )

        # Point after corner
        after = Point(
            curr.x + v2.x * corner_radius,
            curr.y + v2.y * corner_radius
        )

        # Add points for the curve
        smooth_path.append(before)

        # Add intermediate points for the curve (simple arc approximation)
        steps = 4
        for j in range(1, steps):
            t = j / steps
            # Quadratic interpolation through the corner
            x = (1 - t) * (1 - t) * before.x + 2 * (1 - t) * t * curr.x + t * t * after.x
            y = (1 - t) * (1 - t) * before.y + 2 * (1 - t) * t * curr.y + t * t * after.y
            smooth_path.append(Point(x, y))

        smooth_path.append(after)

    smooth_path.append(waypoints[-1])  # End point

    return smooth_path
