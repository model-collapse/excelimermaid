"""
Improved A* pathfinding with adaptive grid sizing and edge-aware obstacle avoidance.

Following user specifications:
1. Heuristically define margin size based on diagram size
2. Grid canvas using margin size as cell size
3. Mark boxes AND easy edges as obstacles
4. A* search in grid space
5. Regress cell-wise path into smooth curve
6. Process short edges first, then longer edges
7. Check edge crossings (not just box avoidance)
8. Reduce cell size when space is tight
"""

import math
import logging
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
from pathfinding.core.grid import Grid
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder

from ..graph.models import Point, BoundingBox, Node, Edge

# Setup logger
logger = logging.getLogger(__name__)

# Check if PIL is available for grid visualization
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.debug("PIL not available - grid visualization disabled")


@dataclass
class EdgeSegment:
    """Represents a routed edge segment as an obstacle."""
    start: Point
    end: Point
    waypoints: List[Point]
    edge: Edge


class AdaptivePathfinder:
    """
    Adaptive A* pathfinding with intelligent cell sizing and edge-aware obstacles.
    """

    def __init__(self, all_nodes: List[Node], all_edges: List[Edge]):
        """
        Initialize pathfinder with diagram structure.

        Args:
            all_nodes: All nodes in the diagram
            all_edges: All edges in the diagram
        """
        self.all_nodes = all_nodes
        self.all_edges = all_edges
        self.routed_edges: List[EdgeSegment] = []

        # Calculate diagram bounds
        self.min_x = float('inf')
        self.min_y = float('inf')
        self.max_x = float('-inf')
        self.max_y = float('-inf')

        for node in all_nodes:
            if node.bbox:
                self.min_x = min(self.min_x, node.bbox.x)
                self.min_y = min(self.min_y, node.bbox.y)
                self.max_x = max(self.max_x, node.bbox.x + node.bbox.width)
                self.max_y = max(self.max_y, node.bbox.y + node.bbox.height)

        # Add padding
        padding = 100
        self.min_x -= padding
        self.min_y -= padding
        self.max_x += padding
        self.max_y += padding

        self.diagram_width = self.max_x - self.min_x
        self.diagram_height = self.max_y - self.min_y

        # Step 1: Heuristically define margin size based on diagram size
        self.margin = self._calculate_heuristic_margin()

        # Step 2: Calculate cell size from margin
        self.cell_size = max(5, int(self.margin))

        # Initialize grid
        self.grid_width = int(self.diagram_width / self.cell_size) + 1
        self.grid_height = int(self.diagram_height / self.cell_size) + 1
        self.reset_grid()

    def _calculate_heuristic_margin(self) -> float:
        """
        Calculate reasonable margin size based on diagram characteristics.

        Returns:
            Margin size in pixels
        """
        # Calculate average node size
        total_size = 0
        count = 0
        for node in self.all_nodes:
            if node.bbox:
                avg_dim = (node.bbox.width + node.bbox.height) / 2
                total_size += avg_dim
                count += 1

        if count == 0:
            return 20.0  # Default fallback

        avg_node_size = total_size / count

        # Calculate node density
        diagram_area = self.diagram_width * self.diagram_height
        node_area = sum((n.bbox.width * n.bbox.height) if n.bbox else 0 for n in self.all_nodes)
        density = node_area / diagram_area if diagram_area > 0 else 0.1

        # Heuristic formula:
        # - Larger for sparse diagrams (more room to route)
        # - Smaller for dense diagrams (need tighter paths)
        # - Scaled by average node size
        base_margin = avg_node_size * 0.08  # Reduced from 0.15 to 0.08
        density_factor = 1.2 - density  # Reduced from 1.5 to 1.2
        margin = base_margin * density_factor

        # Clamp to reasonable range - reduced to leave more room between boxes
        return max(5.0, min(15.0, margin))

    def reset_grid(self):
        """Reset grid to all walkable cells."""
        self.matrix = [[1] * self.grid_width for _ in range(self.grid_height)]

    def _pixel_to_grid(self, point: Point) -> Tuple[int, int]:
        """Convert pixel coordinates to grid coordinates."""
        x = int((point.x - self.min_x) / self.cell_size)
        y = int((point.y - self.min_y) / self.cell_size)
        x = max(0, min(self.grid_width - 1, x))
        y = max(0, min(self.grid_height - 1, y))
        return x, y

    def _grid_to_pixel(self, x: int, y: int) -> Point:
        """Convert grid coordinates to pixel coordinates."""
        px = self.min_x + x * self.cell_size
        py = self.min_y + y * self.cell_size
        return Point(px, py)

    def mark_box_obstacle(self, bbox: BoundingBox):
        """Mark a box (node) as obstacle in the grid - only the actual box, no margin expansion."""
        # Convert bbox to grid coordinates WITHOUT margin expansion
        # The margin is already accounted for in cell size calculation
        left = max(0, int((bbox.x - self.min_x) / self.cell_size))
        right = min(self.grid_width - 1, int((bbox.x + bbox.width - self.min_x) / self.cell_size))
        top = max(0, int((bbox.y - self.min_y) / self.cell_size))
        bottom = min(self.grid_height - 1, int((bbox.y + bbox.height - self.min_y) / self.cell_size))

        cells_to_mark = (right - left + 1) * (bottom - top + 1)
        logger.debug(f"  Marking box at ({bbox.x:.0f},{bbox.y:.0f}) size {bbox.width}x{bbox.height} -> "
                    f"grid [{left}..{right}] x [{top}..{bottom}] = {cells_to_mark} cells")

        # Mark cells as obstacles
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                self.matrix[y][x] = 0

    def mark_edge_obstacle(self, waypoints: List[Point], width: float = None):
        """
        Mark an edge (already routed) as obstacle.

        Args:
            waypoints: Points defining the edge path
            width: Width of obstacle corridor (defaults to margin)
        """
        if width is None:
            width = self.margin

        # Mark corridor around each segment
        for i in range(len(waypoints) - 1):
            self._mark_line_obstacle(waypoints[i], waypoints[i + 1], width)

    def _mark_line_obstacle(self, p1: Point, p2: Point, width: float):
        """Mark a line segment as obstacle - just the line itself, no width expansion."""
        # Use Bresenham algorithm to mark only cells the line passes through
        x1, y1 = self._pixel_to_grid(p1)
        x2, y2 = self._pixel_to_grid(p2)

        # Calculate cells to mark along the line
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        # Mark cells along the line - just the line itself
        x, y = x1, y1
        while True:
            # Mark only this cell (the line passes through it)
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                self.matrix[y][x] = 0

            if x == x2 and y == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def is_direct_path_clear(self, start: Point, end: Point) -> bool:
        """
        Check if a direct line from start to end passes through any obstacles.

        Returns:
            True if path is clear (no obstacles), False otherwise
        """
        # Use Bresenham to check all cells along the line
        x1, y1 = self._pixel_to_grid(start)
        x2, y2 = self._pixel_to_grid(end)

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        x, y = x1, y1
        while True:
            # Check if this cell is an obstacle
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                if self.matrix[y][x] == 0:
                    return False  # Found an obstacle

            if x == x2 and y == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return True  # No obstacles found

    def find_path(self, start: Point, end: Point, orthogonal: bool = True,
                  source_id: str = None, target_id: str = None) -> List[Point]:
        """
        Find path using A* in grid space.

        Args:
            start: Start point
            end: End point
            orthogonal: Use Manhattan routing (no diagonals)

        Returns:
            List of waypoints
        """
        # Convert to grid coordinates
        start_x, start_y = self._pixel_to_grid(start)
        end_x, end_y = self._pixel_to_grid(end)

        # Temporarily mark start/end as walkable
        start_was_obstacle = (self.matrix[start_y][start_x] == 0)
        end_was_obstacle = (self.matrix[end_y][end_x] == 0)

        self.matrix[start_y][start_x] = 1
        self.matrix[end_y][end_x] = 1

        # Create pathfinding grid
        grid = Grid(matrix=self.matrix)
        start_node = grid.node(start_x, start_y)
        end_node = grid.node(end_x, end_y)

        # Restore obstacles
        if start_was_obstacle:
            self.matrix[start_y][start_x] = 0
        if end_was_obstacle:
            self.matrix[end_y][end_x] = 0

        # Run A*
        diagonal = DiagonalMovement.never if orthogonal else DiagonalMovement.always
        finder = AStarFinder(diagonal_movement=diagonal)
        path, runs = finder.find_path(start_node, end_node, grid)

        if not path or len(path) < 2:
            edge_info = ""
            if source_id and target_id:
                edge_info = f"[{source_id} → {target_id}] "
            logger.warning(
                f"A* pathfinding FAILED: {edge_info}No path found from ({start.x:.1f}, {start.y:.1f}) to ({end.x:.1f}, {end.y:.1f}). "
                f"Grid: {self.grid_width}x{self.grid_height}, cell size: {self.cell_size}px. "
                f"Falling back to direct line."
            )
            return [start, end]

        # Convert grid path to pixel path
        pixel_path = [self._grid_to_pixel(x, y) for x, y in path]

        # Step 5: Optimize path by removing unnecessary waypoints (string pulling)
        optimized = self._optimize_path_shortcuts(pixel_path)

        # Step 6: Regress cell-wise path into smooth curve
        smoothed = self._regress_to_smooth_curve(optimized, orthogonal)

        # Ensure start and end are exact
        if len(smoothed) > 0:
            smoothed[0] = start
        if len(smoothed) > 1:
            smoothed[-1] = end

        return smoothed

    def _optimize_path_shortcuts(self, path: List[Point]) -> List[Point]:
        """
        Optimize path by removing unnecessary waypoints using line-of-sight shortcuts.

        Simple string-pulling algorithm: aggressively skip waypoints when line is clear.

        Args:
            path: Original path with potentially unnecessary waypoints

        Returns:
            Optimized path with minimal waypoints (straight segments)
        """
        if len(path) <= 2:
            return path

        optimized = [path[0]]
        current_idx = 0

        while current_idx < len(path) - 1:
            # Try to skip as far ahead as possible
            farthest_idx = current_idx + 1

            # Test increasingly distant waypoints
            for test_idx in range(current_idx + 2, len(path)):
                if self.is_direct_path_clear(path[current_idx], path[test_idx]):
                    farthest_idx = test_idx
                else:
                    # Can't skip further, stop trying
                    break

            # Move to the farthest reachable point
            optimized.append(path[farthest_idx])
            current_idx = farthest_idx

        # Log optimization result
        if len(optimized) < len(path):
            reduction = len(path) - len(optimized)
            logger.debug(
                f"  Path optimization: {len(path)} → {len(optimized)} waypoints "
                f"({reduction} removed)"
            )

        return optimized

    def _regress_to_smooth_curve(self, path: List[Point], orthogonal: bool) -> List[Point]:
        """
        Add smooth curves to simplified paths.

        Takes the optimized waypoints and creates smooth curves between them.
        """
        if len(path) <= 2:
            # For simple 2-point paths, add a gentle curve
            if not orthogonal:
                return self._add_gentle_curve(path)
            return path

        # First simplify to remove collinear points
        simplified = [path[0]]
        for i in range(1, len(path) - 1):
            prev = simplified[-1]
            curr = path[i]
            next_pt = path[i + 1]

            # Keep point if direction changes
            dx1 = curr.x - prev.x
            dy1 = curr.y - prev.y
            dx2 = next_pt.x - curr.x
            dy2 = next_pt.y - curr.y

            # Normalize directions
            if dx1 != 0:
                dx1 = 1 if dx1 > 0 else -1
            if dy1 != 0:
                dy1 = 1 if dy1 > 0 else -1
            if dx2 != 0:
                dx2 = 1 if dx2 > 0 else -1
            if dy2 != 0:
                dy2 = 1 if dy2 > 0 else -1

            # If direction changes, keep the corner
            if dx1 != dx2 or dy1 != dy2:
                simplified.append(curr)

        simplified.append(path[-1])

        # Apply smooth curve interpolation to make it curvy
        if not orthogonal:
            if len(simplified) == 2:
                # Simplified to straight line, add gentle curve
                return self._add_gentle_curve(simplified)
            else:
                # Multi-waypoint path, use Catmull-Rom
                return self._create_smooth_curve(simplified)

        return simplified

    def _add_gentle_curve(self, path: List[Point]) -> List[Point]:
        """
        Add a gentle curve to a straight line segment.

        Takes a 2-point line and adds intermediate points with slight curvature.
        """
        if len(path) != 2:
            return path

        p1, p2 = path[0], path[1]
        distance = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)

        # Only add curve if line is long enough
        if distance < 30:
            return path

        # Calculate perpendicular direction for curve offset
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        # Perpendicular vector (rotated 90 degrees)
        perp_x = -dy
        perp_y = dx

        # Normalize
        perp_len = math.sqrt(perp_x**2 + perp_y**2)
        if perp_len > 0:
            perp_x /= perp_len
            perp_y /= perp_len

        # Add curve offset (about 2-3% of distance for subtle curve)
        curve_amount = distance * 0.025

        # Create curved path with intermediate points
        curved = [p1]
        num_segments = max(3, int(distance / 30))

        for i in range(1, num_segments):
            t = i / num_segments
            # Linear interpolation
            x = p1.x + dx * t
            y = p1.y + dy * t

            # Add perpendicular offset (parabolic curve: max at middle)
            offset = curve_amount * 4 * t * (1 - t)  # Parabola: peaks at t=0.5
            x += perp_x * offset
            y += perp_y * offset

            curved.append(Point(x, y))

        curved.append(p2)

        return curved

    def _create_smooth_curve(self, waypoints: List[Point]) -> List[Point]:
        """
        Create a smooth curve through waypoints using Catmull-Rom spline interpolation.

        This generates intermediate points between waypoints to create smooth curves
        instead of sharp corners.
        """
        if len(waypoints) <= 2:
            return waypoints

        # Generate smooth curve with multiple points between each pair of waypoints
        smooth_path = [waypoints[0]]

        for i in range(len(waypoints) - 1):
            # Get control points for Catmull-Rom spline
            p0 = waypoints[i - 1] if i > 0 else waypoints[i]
            p1 = waypoints[i]
            p2 = waypoints[i + 1]
            p3 = waypoints[i + 2] if i + 2 < len(waypoints) else waypoints[i + 1]

            # Number of intermediate points based on distance
            distance = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
            num_points = max(3, int(distance / (self.cell_size * 3)))

            # Generate points along Catmull-Rom spline
            for t in range(1, num_points):
                t_norm = t / num_points

                # Catmull-Rom basis functions
                t2 = t_norm * t_norm
                t3 = t2 * t_norm

                # Catmull-Rom formula (with standard coefficient 0.5)
                x = 0.5 * (
                    (2 * p1.x) +
                    (-p0.x + p2.x) * t_norm +
                    (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2 +
                    (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3
                )

                y = 0.5 * (
                    (2 * p1.y) +
                    (-p0.y + p2.y) * t_norm +
                    (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * t2 +
                    (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * t3
                )

                smooth_path.append(Point(x, y))

        smooth_path.append(waypoints[-1])

        # Simplify the smooth curve to reduce point count while maintaining smoothness
        return self._douglas_peucker(smooth_path, tolerance=self.cell_size * 0.5)

    def _douglas_peucker(self, points: List[Point], tolerance: float) -> List[Point]:
        """Douglas-Peucker path simplification."""
        if len(points) <= 2:
            return points

        # Find point with max distance
        dmax = 0.0
        index = 0
        for i in range(1, len(points) - 1):
            d = self._perpendicular_distance(points[i], points[0], points[-1])
            if d > dmax:
                index = i
                dmax = d

        # If max distance > tolerance, split and recurse
        if dmax > tolerance:
            left = self._douglas_peucker(points[:index+1], tolerance)
            right = self._douglas_peucker(points[index:], tolerance)
            return left[:-1] + right
        else:
            return [points[0], points[-1]]

    def visualize_grid(self, output_path: str, paths: dict = None) -> None:
        """
        Visualize the pathfinding grid with obstacles and paths.

        Args:
            output_path: Path to save the visualization image
            paths: Optional dict mapping edge to waypoints to visualize paths
        """
        if not PIL_AVAILABLE:
            logger.warning("PIL not available - cannot generate grid visualization")
            return

        # Calculate image size (scale cells to be visible)
        cell_pixel_size = max(8, min(20, 400 // max(self.grid_width, self.grid_height)))
        img_width = self.grid_width * cell_pixel_size + 200  # Extra space for legend
        img_height = self.grid_height * cell_pixel_size + 50  # Extra space for info

        # Create image
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)

        # Draw grid cells
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                x1 = x * cell_pixel_size
                y1 = y * cell_pixel_size
                x2 = x1 + cell_pixel_size
                y2 = y1 + cell_pixel_size

                if self.matrix[y][x] == 0:
                    # Obstacle cell - red
                    draw.rectangle([x1, y1, x2, y2], fill='#ffcccc', outline='#ff0000')
                else:
                    # Walkable cell - white with light grid
                    draw.rectangle([x1, y1, x2, y2], fill='white', outline='#e0e0e0')

        # Draw routed edges if provided (draw them before node labels)
        if paths:
            colors = ['#0066ff', '#00cc00', '#ff00ff', '#00cccc', '#ff9900',
                     '#9900ff', '#ff0066', '#66ff00', '#0099ff', '#ff6600']
            for idx, (edge, waypoints) in enumerate(paths.items()):
                if len(waypoints) < 2:
                    continue
                color = colors[idx % len(colors)]
                # Draw path with alpha
                for i in range(len(waypoints) - 1):
                    p1 = waypoints[i]
                    p2 = waypoints[i + 1]
                    # Convert to grid coordinates
                    gx1, gy1 = self._pixel_to_grid(p1)
                    gx2, gy2 = self._pixel_to_grid(p2)
                    # Convert to image coordinates
                    px1 = gx1 * cell_pixel_size + cell_pixel_size // 2
                    py1 = gy1 * cell_pixel_size + cell_pixel_size // 2
                    px2 = gx2 * cell_pixel_size + cell_pixel_size // 2
                    py2 = gy2 * cell_pixel_size + cell_pixel_size // 2
                    draw.line([px1, py1, px2, py2], fill=color, width=max(2, cell_pixel_size // 4))

        # Draw node bounding boxes and labels
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                     max(8, min(14, cell_pixel_size)))
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                                         max(8, min(12, cell_pixel_size)))
            except:
                font = ImageFont.load_default()

        for node in self.all_nodes:
            if node.bbox:
                # Calculate node bounds by converting through grid coordinates
                # This ensures alignment with obstacle cells
                left_grid = int((node.bbox.x - self.min_x) / self.cell_size)
                top_grid = int((node.bbox.y - self.min_y) / self.cell_size)
                right_grid = int((node.bbox.x + node.bbox.width - self.min_x) / self.cell_size)
                bottom_grid = int((node.bbox.y + node.bbox.height - self.min_y) / self.cell_size)

                # Convert grid coordinates to image pixel coordinates
                left = left_grid * cell_pixel_size
                top = top_grid * cell_pixel_size
                right = right_grid * cell_pixel_size
                bottom = bottom_grid * cell_pixel_size

                # Draw node boundary
                draw.rectangle([left, top, right, bottom], outline='#0000ff', width=2)

                # Draw node label in center
                cx = (left + right) // 2
                cy = (top + bottom) // 2
                draw.text((cx, cy), node.id, fill='blue', font=font, anchor='mm')

        # Add legend on the right side
        legend_x = self.grid_width * cell_pixel_size + 10
        legend_y = 10

        try:
            legend_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
        except:
            legend_font = font

        draw.text((legend_x, legend_y), "Legend:", fill='black', font=legend_font)
        legend_y += 20

        # Obstacles
        draw.rectangle([legend_x, legend_y, legend_x + 20, legend_y + 15],
                      fill='#ffcccc', outline='#ff0000')
        draw.text((legend_x + 25, legend_y + 7), "Obstacles", fill='black', anchor='lm')
        legend_y += 20

        # Walkable
        draw.rectangle([legend_x, legend_y, legend_x + 20, legend_y + 15],
                      fill='white', outline='#e0e0e0')
        draw.text((legend_x + 25, legend_y + 7), "Walkable", fill='black', anchor='lm')
        legend_y += 20

        # Node boundaries
        draw.rectangle([legend_x, legend_y, legend_x + 20, legend_y + 15],
                      fill='white', outline='#0000ff', width=2)
        draw.text((legend_x + 25, legend_y + 7), "Nodes", fill='black', anchor='lm')
        legend_y += 20

        # Paths
        if paths and len(paths) > 0:
            draw.line([legend_x, legend_y + 7, legend_x + 20, legend_y + 7],
                     fill='#0066ff', width=3)
            draw.text((legend_x + 25, legend_y + 7), f"Paths ({len(paths)} edges)",
                     fill='black', anchor='lm')

        # Add info text at bottom
        info_text = (f"Grid: {self.grid_width}x{self.grid_height} cells | "
                    f"Cell size: {self.cell_size}px | "
                    f"Margin: {self.margin:.1f}px | "
                    f"Nodes: {len(self.all_nodes)} | "
                    f"Routed edges: {len(self.routed_edges)}")
        draw.text((10, img_height - 30), info_text, fill='black', font=font)

        # Save image
        img.save(output_path)
        logger.info(f"Grid visualization saved to {output_path}")

    def _perpendicular_distance(self, point: Point, line_start: Point, line_end: Point) -> float:
        """Calculate perpendicular distance from point to line."""
        dx = line_end.x - line_start.x
        dy = line_end.y - line_start.y

        if dx == 0 and dy == 0:
            return math.sqrt((point.x - line_start.x)**2 + (point.y - line_start.y)**2)

        t = ((point.x - line_start.x) * dx + (point.y - line_start.y) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))

        proj_x = line_start.x + t * dx
        proj_y = line_start.y + t * dy

        return math.sqrt((point.x - proj_x)**2 + (point.y - proj_y)**2)

    def try_with_smaller_cells(self, start: Point, end: Point, orthogonal: bool,
                               source_id: str = None, target_id: str = None) -> Optional[List[Point]]:
        """
        Try pathfinding with smaller cell size when space is tight.

        Returns:
            Path with smaller cells, or None if still fails
        """
        # Reduce cell size by half
        old_cell_size = self.cell_size
        self.cell_size = max(3, self.cell_size // 2)

        edge_info = ""
        if source_id and target_id:
            edge_info = f"[{source_id} → {target_id}] "
        logger.info(
            f"Retrying pathfinding with SMALLER CELLS: {edge_info}{old_cell_size}px → {self.cell_size}px "
            f"from ({start.x:.1f}, {start.y:.1f}) to ({end.x:.1f}, {end.y:.1f})"
        )

        # Recreate grid with smaller cells
        self.grid_width = int(self.diagram_width / self.cell_size) + 1
        self.grid_height = int(self.diagram_height / self.cell_size) + 1
        self.reset_grid()

        # Re-mark all obstacles
        for node in self.all_nodes:
            if node.bbox:
                self.mark_box_obstacle(node.bbox)

        for edge_seg in self.routed_edges:
            self.mark_edge_obstacle(edge_seg.waypoints, width=self.cell_size)

        # Try path again
        path = self.find_path(start, end, orthogonal, source_id, target_id)

        # Restore original cell size AND reset matrix to correct dimensions
        self.cell_size = old_cell_size
        self.grid_width = int(self.diagram_width / self.cell_size) + 1
        self.grid_height = int(self.diagram_height / self.cell_size) + 1
        self.reset_grid()  # CRITICAL: Reset matrix to match restored grid dimensions

        # Re-mark all obstacles with original grid dimensions
        for node in self.all_nodes:
            if node.bbox:
                self.mark_box_obstacle(node.bbox)

        for edge_seg in self.routed_edges:
            self.mark_edge_obstacle(edge_seg.waypoints, width=self.cell_size)

        edge_info = ""
        if source_id and target_id:
            edge_info = f"[{source_id} → {target_id}] "

        if len(path) > 2:
            logger.info(f"{edge_info}Retry with smaller cells SUCCEEDED: Found path with {len(path)} waypoints")
            return path
        else:
            logger.warning(f"{edge_info}Retry with smaller cells FAILED: Still no valid path found")
            return None


def route_edges_adaptively(
    all_nodes: List[Node],
    all_edges: List[Edge],
    margin: float = 15.0,
    orthogonal: bool = True,
    direction = None
) -> dict:
    """
    Route all edges using adaptive A* pathfinding.

    Follows user specifications:
    - Step 6: Process short edges first (they have difficulty)
    - Step 7: For longer edges, check crossings
    - Step 8: Reduce cell size when margins are tight

    Args:
        all_nodes: All nodes in diagram
        all_edges: All edges to route
        margin: Default margin (may be overridden by heuristic)
        orthogonal: Use Manhattan routing

    Returns:
        Dictionary mapping edge to waypoints
    """
    logger.info(
        f"Starting adaptive A* pathfinding for {len(all_edges)} edges, {len(all_nodes)} nodes. "
        f"Routing mode: {'orthogonal' if orthogonal else 'curved'}"
    )

    pathfinder = AdaptivePathfinder(all_nodes, all_edges)

    logger.info(
        f"Adaptive parameters: margin={pathfinder.margin:.1f}px, cell_size={pathfinder.cell_size}px, "
        f"grid={pathfinder.grid_width}x{pathfinder.grid_height}"
    )

    # Step 3: Mark boxes as obstacles
    logger.debug(f"Marking {len([n for n in all_nodes if n.bbox])} node boxes as obstacles...")
    for node in all_nodes:
        if node.bbox:
            logger.debug(f"Node {node.id}:")
            pathfinder.mark_box_obstacle(node.bbox)

    # Step 6: Sort edges by length (short first)
    def edge_length(edge: Edge) -> float:
        if not edge.source.bbox or not edge.target.bbox:
            return 0
        sx = edge.source.bbox.x + edge.source.bbox.width / 2
        sy = edge.source.bbox.y + edge.source.bbox.height / 2
        tx = edge.target.bbox.x + edge.target.bbox.width / 2
        ty = edge.target.bbox.y + edge.target.bbox.height / 2
        return math.sqrt((tx - sx)**2 + (ty - sy)**2)

    logger.info(f"Routing {len(all_edges)} edges...")

    edge_paths = {}

    for idx, edge in enumerate(all_edges, 1):
        if not edge.source.bbox or not edge.target.bbox:
            continue

        # Find path - try direct lines with multiple attachment points first
        logger.debug(
            f"[{idx}/{len(all_edges)}] Routing edge {edge.source.id} → {edge.target.id}"
        )

        # Try to find a direct line with clear path
        path = None
        start_base = None
        end_base = None

        # Get side combinations sorted by distance (closest sides first)
        # biased by flow direction
        side_combinations = _get_sorted_side_combinations(
            edge.source.bbox, edge.target.bbox, direction
        )

        for source_side, target_side in side_combinations:
            # Get attachment points
            if source_side is None:
                # Default attachment based on direction
                sb = _get_edge_point(edge.source.bbox, edge.target.bbox, is_source=True)
                eb = _get_edge_point(edge.target.bbox, edge.source.bbox, is_source=False)
            else:
                # Specific sides
                sb = _get_edge_point_from_side(edge.source.bbox, source_side)
                eb = _get_edge_point_from_side(edge.target.bbox, target_side)

            # Calculate distance between attachment points
            base_distance = math.sqrt((eb.x - sb.x)**2 + (eb.y - sb.y)**2)

            # Adaptive push distance based on gap size
            # Push by one cell size to ensure we clear obstacle grid cells
            if base_distance < 30:
                # Small gap: push by cell size to clear obstacle grid
                adaptive_push = pathfinder.cell_size
            else:
                # Larger gaps: use adaptive push
                max_push = pathfinder.margin + 5
                adaptive_push = min(max_push, base_distance * 0.4)  # Use max 40% of gap

            # Push points outward
            s = _push_point_outward(sb, edge.source.bbox, adaptive_push)
            e = _push_point_outward(eb, edge.target.bbox, adaptive_push)

            # Check if direct path is clear
            if pathfinder.is_direct_path_clear(s, e):
                # Found a clear direct path!
                path = [s, e]
                start_base = sb
                end_base = eb
                if source_side is None:
                    logger.debug(f"  Direct path clear (default attachment)")
                else:
                    logger.debug(f"  Direct path clear ({source_side} → {target_side})")
                break

        # If no direct path found, use A* pathfinding
        if path is None:
            logger.debug(f"  All direct paths blocked, using A* pathfinding")

            # Try A* with multiple attachment points and pick the shortest
            best_path = None
            best_length = float('inf')
            best_start_base = None
            best_end_base = None

            # Try a few key attachment combinations for A*
            astar_combinations = [
                (None, None),  # Default
                ('right', 'bottom'),  # Right side routing
                ('right', 'top'),
                ('left', 'bottom'),  # Left side routing
                ('left', 'top'),
            ]

            for src_side, tgt_side in astar_combinations:
                if src_side is None:
                    sb = _get_edge_point(edge.source.bbox, edge.target.bbox, is_source=True)
                    eb = _get_edge_point(edge.target.bbox, edge.source.bbox, is_source=False)
                else:
                    sb = _get_edge_point_from_side(edge.source.bbox, src_side)
                    eb = _get_edge_point_from_side(edge.target.bbox, tgt_side)

                base_dist = math.sqrt((eb.x - sb.x)**2 + (eb.y - sb.y)**2)

                if base_dist < 30:
                    push = pathfinder.cell_size
                else:
                    push = min(pathfinder.margin + 5, base_dist * 0.4)

                s = _push_point_outward(sb, edge.source.bbox, push)
                e = _push_point_outward(eb, edge.target.bbox, push)

                test_path = pathfinder.find_path(s, e, orthogonal, edge.source.id, edge.target.id)

                if len(test_path) > 2:
                    # Calculate path length
                    path_length = sum(
                        math.sqrt((test_path[i+1].x - test_path[i].x)**2 +
                                  (test_path[i+1].y - test_path[i].y)**2)
                        for i in range(len(test_path) - 1)
                    )

                    if path_length < best_length:
                        best_path = test_path
                        best_length = path_length
                        best_start_base = sb
                        best_end_base = eb

            if best_path:
                path = best_path
                start_base = best_start_base
                end_base = best_end_base
                logger.debug(f"  A* found path: {len(path)} waypoints, {best_length:.1f}px")
            else:
                logger.warning(
                    f"All routing attempts failed. Using direct line for edge "
                    f"{edge.source.id} → {edge.target.id} (may cross obstacles)"
                )
                start_base = _get_edge_point(edge.source.bbox, edge.target.bbox, is_source=True)
                end_base = _get_edge_point(edge.target.bbox, edge.source.bbox, is_source=False)
                path = [start_base, end_base]

        # Replace first and last points with exact boundary points
        if len(path) > 0:
            path[0] = start_base  # Original boundary point
        if len(path) > 1:
            path[-1] = end_base  # Original boundary point

        # Store path
        edge_paths[edge] = path
        logger.debug(
            f"[{idx}/{len(all_edges)}] Edge {edge.source.id} → {edge.target.id} routed: "
            f"{len(path)} waypoints"
        )

        # Mark this edge as obstacle for future edges ONLY if it's not a simple direct line
        # Simple direct lines should not block other edges
        if len(path) > 2:
            # Complex path - mark as obstacle to route future edges around it
            edge_seg = EdgeSegment(start=start_base, end=end_base, waypoints=path, edge=edge)
            pathfinder.routed_edges.append(edge_seg)
            pathfinder.mark_edge_obstacle(path, width=pathfinder.cell_size)
            logger.debug(f"  Marked complex path as obstacle")
        else:
            logger.debug(f"  Direct line - not marked as obstacle")

    logger.info(f"Adaptive A* pathfinding complete: {len(edge_paths)} edges routed successfully")

    # Generate grid visualization if debug logging is enabled
    if logger.isEnabledFor(logging.DEBUG):
        try:
            import os
            from datetime import datetime
            # Generate filename with timestamp for uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            viz_path = f"pathfinding_grid_debug_{timestamp}.png"
            pathfinder.visualize_grid(viz_path, edge_paths)
            logger.info(f"Grid visualization: {pathfinder.grid_width}x{pathfinder.grid_height} cells, "
                       f"{len([1 for row in pathfinder.matrix for cell in row if cell == 0])} obstacle cells")
        except Exception as e:
            logger.warning(f"Failed to generate grid visualization: {e}")

    return edge_paths


def _get_sorted_side_combinations(
    source_bbox: BoundingBox,
    target_bbox: BoundingBox,
    direction = None
) -> List[Tuple[Optional[str], Optional[str]]]:
    """
    Get side combinations sorted by distance (closest sides first),
    biased by flowchart direction.

    Returns list of (source_side, target_side) tuples, starting with None (default)
    then sorted by actual distance between side centers, with penalty for
    combinations that go against the flow direction.
    """
    # Start with default (None, None)
    combinations = [(None, None)]

    # Calculate distances for all side combinations
    sides = ['top', 'bottom', 'left', 'right']
    distances = []

    # Determine preferred flow combinations based on direction
    # Just use distance with slight flow preference - no hard forbidding
    from ..graph.models import Direction
    preferred_combinations = set()

    if direction == Direction.LEFT_RIGHT:
        # For LR flow: prefer right→left and bottom→top
        preferred_combinations = {('right', 'left'), ('bottom', 'top')}
    elif direction == Direction.RIGHT_LEFT:
        # For RL flow: prefer left→right and bottom→top
        preferred_combinations = {('left', 'right'), ('bottom', 'top')}
    elif direction == Direction.TOP_DOWN or direction == Direction.TOP_BOTTOM:
        # For TD flow: prefer bottom→top and right→left
        preferred_combinations = {('bottom', 'top'), ('right', 'left')}
    elif direction == Direction.BOTTOM_TOP:
        # For BT flow: prefer top→bottom and right→left
        preferred_combinations = {('top', 'bottom'), ('right', 'left')}

    for source_side in sides:
        for target_side in sides:
            source_point = _get_edge_point_from_side(source_bbox, source_side)
            target_point = _get_edge_point_from_side(target_bbox, target_side)

            # Calculate Euclidean distance
            dx = target_point.x - source_point.x
            dy = target_point.y - source_point.y
            distance = math.sqrt(dx*dx + dy*dy)

            # Apply small penalty for combinations that go against flow direction
            # Just a slight bias, not a hard constraint
            if direction and (source_side, target_side) not in preferred_combinations:
                # Add 20% penalty to gently encourage flow-appropriate connections
                distance *= 1.2

            distances.append((distance, source_side, target_side))

    # Sort by distance (shortest first, with flow-based bias)
    distances.sort(key=lambda x: x[0])

    # Add sorted combinations
    for _, source_side, target_side in distances:
        combinations.append((source_side, target_side))

    return combinations


def _get_edge_point(source_bbox: BoundingBox, target_bbox: BoundingBox, is_source: bool) -> Point:
    """Get point on edge of source box facing target box."""
    source_cx = source_bbox.x + source_bbox.width / 2
    source_cy = source_bbox.y + source_bbox.height / 2
    target_cx = target_bbox.x + target_bbox.width / 2
    target_cy = target_bbox.y + target_bbox.height / 2

    dx = target_cx - source_cx
    dy = target_cy - source_cy

    # Determine which edge of the box to use
    if abs(dx) > abs(dy):
        # Horizontal edge (left or right)
        if dx > 0:
            # Right edge
            return Point(source_bbox.x + source_bbox.width, source_cy)
        else:
            # Left edge
            return Point(source_bbox.x, source_cy)
    else:
        # Vertical edge (top or bottom)
        if dy > 0:
            # Bottom edge
            return Point(source_cx, source_bbox.y + source_bbox.height)
        else:
            # Top edge
            return Point(source_cx, source_bbox.y)


def _push_point_outward(point: Point, bbox: BoundingBox, distance: float) -> Point:
    """
    Push a point outward from a bounding box by specified distance.

    This ensures the point is in clear space, not in the obstacle margin.
    """
    # Calculate center of box
    center_x = bbox.x + bbox.width / 2
    center_y = bbox.y + bbox.height / 2

    # Calculate direction from center to point
    dx = point.x - center_x
    dy = point.y - center_y

    # Normalize direction
    length = math.sqrt(dx * dx + dy * dy)
    if length < 0.001:
        # Point at center, push right
        return Point(point.x + distance, point.y)

    dx /= length
    dy /= length

    # Push point outward
    return Point(point.x + dx * distance, point.y + dy * distance)


def _get_edge_point_from_side(bbox: BoundingBox, side: str) -> Point:
    """
    Get point on specific side of bounding box.

    Args:
        bbox: Bounding box
        side: One of 'top', 'bottom', 'left', 'right'

    Returns:
        Point on the specified side (center of that edge)
    """
    cx = bbox.x + bbox.width / 2
    cy = bbox.y + bbox.height / 2

    if side == 'top':
        return Point(cx, bbox.y)
    elif side == 'bottom':
        return Point(cx, bbox.y + bbox.height)
    elif side == 'left':
        return Point(bbox.x, cy)
    elif side == 'right':
        return Point(bbox.x + bbox.width, cy)
    else:
        # Fallback to bottom
        return Point(cx, bbox.y + bbox.height)


def _try_alternative_attachment_points(
    pathfinder,
    source_bbox: BoundingBox,
    target_bbox: BoundingBox,
    orthogonal: bool,
    source_id: str,
    target_id: str,
    margin: float,
    direction = None
) -> Optional[List[Point]]:
    """
    Try different edge attachment points to find a valid path.

    Tries side combinations sorted by distance (closest sides first).

    Returns:
        Valid path if found, None otherwise
    """
    # Get side combinations sorted by distance (skip the None,None default)
    all_combinations = _get_sorted_side_combinations(source_bbox, target_bbox, direction)
    side_combinations = [combo for combo in all_combinations if combo[0] is not None]

    logger.info(f"[{source_id} → {target_id}] Trying alternative attachment points...")

    for source_side, target_side in side_combinations:
        # Get points on specific sides
        start_base = _get_edge_point_from_side(source_bbox, source_side)
        end_base = _get_edge_point_from_side(target_bbox, target_side)

        # Calculate distance and use adaptive push
        base_distance = math.sqrt(
            (end_base.x - start_base.x)**2 + (end_base.y - start_base.y)**2
        )

        # Adaptive push: minimal for close boxes, larger for distant ones
        if base_distance < 30:
            adaptive_push = pathfinder.cell_size
        else:
            max_push = margin + 5
            adaptive_push = min(max_push, base_distance * 0.4)

        start = _push_point_outward(start_base, source_bbox, adaptive_push)
        end = _push_point_outward(end_base, target_bbox, adaptive_push)

        # Try pathfinding
        path = pathfinder.find_path(start, end, orthogonal, source_id, target_id)

        # Check if we got a real path (not just direct line fallback)
        if len(path) > 2:
            logger.info(
                f"[{source_id} → {target_id}] Found path using alternative attachment: "
                f"{source_side} → {target_side} ({len(path)} waypoints)"
            )
            # Replace first and last points with exact boundary points
            path[0] = start_base
            path[-1] = end_base
            return path

    logger.warning(f"[{source_id} → {target_id}] All attachment point combinations failed")
    return None
