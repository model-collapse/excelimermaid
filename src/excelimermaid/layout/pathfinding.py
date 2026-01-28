"""Grid-based A* pathfinding for diagram edge routing with obstacle avoidance."""

import math
from typing import List, Tuple
from pathfinding.core.grid import Grid
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder

from ..graph.models import Point, BoundingBox, Node


class DiagramPathfinder:
    """
    Grid-based A* pathfinding for diagram edge routing.

    Converts the continuous 2D diagram space into a discrete grid and uses
    A* algorithm to find optimal paths around obstacles.

    Example:
        pathfinder = DiagramPathfinder(1000, 800, cell_size=10)
        pathfinder.mark_obstacle(node.bbox, margin=5.0)
        path = pathfinder.find_path(start_point, end_point)
    """

    def __init__(self, diagram_width: float, diagram_height: float, cell_size: int = 10):
        """
        Initialize pathfinder with diagram dimensions.

        Args:
            diagram_width: Width of diagram in pixels
            diagram_height: Height of diagram in pixels
            cell_size: Size of each grid cell in pixels (smaller = more precise, slower)
        """
        self.cell_size = cell_size
        self.width = int(diagram_width / cell_size) + 1
        self.height = int(diagram_height / cell_size) + 1

        # Initialize grid with all cells walkable (1 = walkable, 0 = obstacle)
        self.matrix = [[1] * self.width for _ in range(self.height)]

    def mark_obstacle(self, bbox: BoundingBox, margin: float = 5.0) -> None:
        """
        Mark a rectangular obstacle in the grid.

        Args:
            bbox: Bounding box of the obstacle (typically a node)
            margin: Extra margin around the obstacle in pixels
        """
        # Convert pixel coordinates to grid coordinates with margin
        left = max(0, int((bbox.x - margin) / self.cell_size))
        right = min(self.width - 1, int((bbox.x + bbox.width + margin) / self.cell_size))
        top = max(0, int((bbox.y - margin) / self.cell_size))
        bottom = min(self.height - 1, int((bbox.y + bbox.height + margin) / self.cell_size))

        # Mark all cells in the obstacle region as unwalkable
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                self.matrix[y][x] = 0  # 0 = obstacle

    def find_path(self, start: Point, end: Point, allow_diagonal: bool = True) -> List[Point]:
        """
        Find optimal path from start to end using A* algorithm.

        Args:
            start: Starting point (typically on edge of source node)
            end: Ending point (typically on edge of target node)
            allow_diagonal: Whether to allow diagonal movement (default: True)

        Returns:
            List of waypoints forming the path. Returns [start, end] if no path found.
        """
        # Convert pixel coordinates to grid coordinates
        start_x = int(start.x / self.cell_size)
        start_y = int(start.y / self.cell_size)
        end_x = int(end.x / self.cell_size)
        end_y = int(end.y / self.cell_size)

        # Ensure coordinates are within bounds
        start_x = max(0, min(self.width - 1, start_x))
        start_y = max(0, min(self.height - 1, start_y))
        end_x = max(0, min(self.width - 1, end_x))
        end_y = max(0, min(self.height - 1, end_y))

        # Temporarily mark start and end cells as walkable
        # This prevents pathfinding failure when points land on obstacle boundaries
        start_was_obstacle = (self.matrix[start_y][start_x] == 0)
        end_was_obstacle = (self.matrix[end_y][end_x] == 0)

        self.matrix[start_y][start_x] = 1  # Force walkable
        self.matrix[end_y][end_x] = 1  # Force walkable

        # Create grid for pathfinding
        grid = Grid(matrix=self.matrix)

        # Get start and end nodes
        start_node = grid.node(start_x, start_y)
        end_node = grid.node(end_x, end_y)

        # Restore original obstacle state after getting nodes
        if start_was_obstacle:
            self.matrix[start_y][start_x] = 0
        if end_was_obstacle:
            self.matrix[end_y][end_x] = 0

        # Configure diagonal movement
        diagonal = DiagonalMovement.always if allow_diagonal else DiagonalMovement.never

        # Find path using A*
        finder = AStarFinder(diagonal_movement=diagonal)
        path, runs = finder.find_path(start_node, end_node, grid)

        # Check if path was found
        if not path or len(path) < 2:
            # No path found, return direct line as fallback
            return [start, end]

        # Convert grid coordinates back to pixel coordinates
        pixel_path = [
            Point(x * self.cell_size, y * self.cell_size)
            for x, y in path
        ]

        # Simplify path to reduce waypoints while preserving shape
        # For orthogonal paths, use different simplification to preserve right angles
        if not allow_diagonal:
            simplified_path = self.simplify_orthogonal_path(pixel_path)
        else:
            simplified_path = self.simplify_path(pixel_path, tolerance=15)

        return simplified_path

    def simplify_path(self, path: List[Point], tolerance: float = 15.0) -> List[Point]:
        """
        Simplify path using Ramer-Douglas-Peucker algorithm.

        Reduces the number of waypoints while preserving the overall shape.
        This makes paths cleaner and reduces file size.

        Args:
            path: List of points forming the path
            tolerance: Maximum distance a point can be from the line to be removed

        Returns:
            Simplified path with fewer waypoints
        """
        if len(path) <= 2:
            return path

        def perpendicular_distance(point: Point, line_start: Point, line_end: Point) -> float:
            """Calculate perpendicular distance from point to line segment."""
            dx = line_end.x - line_start.x
            dy = line_end.y - line_start.y

            # Handle degenerate case (line is a point)
            if dx == 0 and dy == 0:
                return math.sqrt((point.x - line_start.x)**2 + (point.y - line_start.y)**2)

            # Calculate projection parameter
            t = ((point.x - line_start.x) * dx + (point.y - line_start.y) * dy) / (dx*dx + dy*dy)
            t = max(0, min(1, t))  # Clamp to line segment

            # Calculate closest point on line
            proj_x = line_start.x + t * dx
            proj_y = line_start.y + t * dy

            # Return distance to projection
            return math.sqrt((point.x - proj_x)**2 + (point.y - proj_y)**2)

        # Find point with maximum distance from line
        dmax = 0.0
        index = 0
        for i in range(1, len(path) - 1):
            d = perpendicular_distance(path[i], path[0], path[-1])
            if d > dmax:
                index = i
                dmax = d

        # If max distance is greater than tolerance, recursively simplify
        if dmax > tolerance:
            # Recursively simplify both segments
            left = self.simplify_path(path[:index+1], tolerance)
            right = self.simplify_path(path[index:], tolerance)
            # Concatenate results (avoid duplicate middle point)
            return left[:-1] + right
        else:
            # All points are close to the line, just return endpoints
            return [path[0], path[-1]]

    def simplify_orthogonal_path(self, path: List[Point]) -> List[Point]:
        """
        Simplify orthogonal path by removing collinear waypoints.

        For orthogonal (Manhattan) paths, removes intermediate points that lie
        on the same horizontal or vertical line segment.

        Args:
            path: List of points forming orthogonal path

        Returns:
            Simplified path with only corner points
        """
        if len(path) <= 2:
            return path

        simplified = [path[0]]

        for i in range(1, len(path) - 1):
            prev = simplified[-1]
            curr = path[i]
            next_pt = path[i + 1]

            # Check if three points are collinear (horizontal or vertical)
            is_horizontal_line = (prev.y == curr.y == next_pt.y)
            is_vertical_line = (prev.x == curr.x == next_pt.x)

            # Only keep the point if it's a corner (changes direction)
            if not (is_horizontal_line or is_vertical_line):
                simplified.append(curr)

        simplified.append(path[-1])
        return simplified


def astar_route_around_obstacles(
    start: Point,
    end: Point,
    all_nodes: List[Node],
    source_node: Node,
    target_node: Node,
    margin: float = 5.0,
    cell_size: int = 10,
    orthogonal: bool = False
) -> List[Point]:
    """
    Route an edge around obstacles using A* pathfinding.

    This is a convenience function that creates a pathfinder, marks obstacles,
    and finds the path in one call.

    Args:
        start: Starting point on edge of source node
        end: Ending point on edge of target node
        all_nodes: All nodes in the diagram (for obstacle detection)
        source_node: Source node (excluded from obstacles)
        target_node: Target node (excluded from obstacles)
        margin: Margin around obstacles in pixels
        cell_size: Grid cell size for pathfinding
        orthogonal: If True, use only horizontal/vertical segments (Manhattan routing)

    Returns:
        List of waypoints forming obstacle-free path
    """
    # Calculate diagram bounds
    max_x = 0.0
    max_y = 0.0
    for node in all_nodes:
        if node.bbox:
            max_x = max(max_x, node.bbox.x + node.bbox.width)
            max_y = max(max_y, node.bbox.y + node.bbox.height)

    # Add padding for boundary
    diagram_width = max_x + 100
    diagram_height = max_y + 100

    # Create pathfinder
    pathfinder = DiagramPathfinder(diagram_width, diagram_height, cell_size=cell_size)

    # Mark all obstacles (excluding source and target nodes)
    for node in all_nodes:
        if node == source_node or node == target_node:
            continue
        if node.bbox:
            pathfinder.mark_obstacle(node.bbox, margin=margin)

    # Push start and end points outward from their boxes to ensure they're in clear space
    # This prevents A* from thinking the start/end is inside an obstacle
    start_adjusted = _push_point_outward(start, source_node.bbox, margin + 5)
    end_adjusted = _push_point_outward(end, target_node.bbox, margin + 5)

    # Find path with or without diagonal movement
    allow_diagonal = not orthogonal  # Orthogonal means no diagonals
    path = pathfinder.find_path(start_adjusted, end_adjusted, allow_diagonal=allow_diagonal)

    # Replace first and last points with original boundary points
    if len(path) > 0:
        path[0] = start
    if len(path) > 1:
        path[-1] = end

    return path


def _push_point_outward(point: Point, bbox: BoundingBox, distance: float) -> Point:
    """
    Push a point outward from a bounding box by a specified distance.

    This ensures the point is in clear space, not on the box boundary.

    Args:
        point: Point on or near the box boundary
        bbox: Bounding box to push away from
        distance: Distance to push outward in pixels

    Returns:
        New point pushed outward from the box
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
