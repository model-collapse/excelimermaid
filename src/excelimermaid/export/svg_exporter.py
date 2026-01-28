"""SVG export functionality."""

import svgwrite
from typing import List
from ..graph.models import Diagram, Node, Edge, Point, ShapeType, EdgeType
from ..renderer.rough_drawing import RoughDrawing


class SVGExporter:
    """
    Exports diagrams to SVG format with Excalidraw styling.

    SVG is a vector format, so the output is scalable and has small file size.
    """

    def __init__(self, rough_drawing: RoughDrawing):
        """
        Initialize SVG exporter.

        Args:
            rough_drawing: Rough drawing engine for rendering shapes
        """
        self.rough = rough_drawing

    def export(self, diagram: Diagram, output_path: str) -> None:
        """
        Export diagram to SVG file.

        Args:
            diagram: The diagram to export
            output_path: Path to output SVG file
        """
        # Calculate canvas size
        bbox = self._calculate_bounding_box(diagram)
        padding = 40

        width = bbox['max_x'] - bbox['min_x'] + 2 * padding
        height = bbox['max_y'] - bbox['min_y'] + 2 * padding

        # Create SVG drawing
        dwg = svgwrite.Drawing(
            output_path,
            size=(f"{width}px", f"{height}px"),
            viewBox=f"0 0 {width} {height}"
        )

        # Add background
        dwg.add(dwg.rect(
            insert=(0, 0),
            size=(width, height),
            fill="white"
        ))

        # Offset for padding
        offset_x = padding - bbox['min_x']
        offset_y = padding - bbox['min_y']

        # Create group for diagram elements
        g = dwg.g()

        # Draw edges first (so they appear behind nodes)
        for edge in diagram.edges:
            self._draw_edge(dwg, g, edge, offset_x, offset_y)

        # Draw nodes
        for node in diagram.nodes:
            self._draw_node(dwg, g, node, offset_x, offset_y)

        dwg.add(g)
        dwg.save()

    def _calculate_bounding_box(self, diagram: Diagram) -> dict:
        """Calculate the bounding box of all nodes."""
        if not diagram.nodes:
            return {'min_x': 0, 'min_y': 0, 'max_x': 800, 'max_y': 600}

        min_x = min(node.bbox.x for node in diagram.nodes if node.bbox)
        min_y = min(node.bbox.y for node in diagram.nodes if node.bbox)
        max_x = max(node.bbox.x + node.bbox.width for node in diagram.nodes if node.bbox)
        max_y = max(node.bbox.y + node.bbox.height for node in diagram.nodes if node.bbox)

        return {'min_x': min_x, 'min_y': min_y, 'max_x': max_x, 'max_y': max_y}

    def _draw_node(
        self,
        dwg: svgwrite.Drawing,
        group: svgwrite.container.Group,
        node: Node,
        offset_x: float,
        offset_y: float
    ) -> None:
        """Draw a single node."""
        if not node.bbox:
            return

        x = node.bbox.x + offset_x
        y = node.bbox.y + offset_y
        w = node.bbox.width
        h = node.bbox.height
        center = Point(x + w / 2, y + h / 2)

        # Draw shape based on type
        if node.shape == ShapeType.RECTANGLE:
            paths = self.rough.rough_rectangle(x, y, w, h)
            for path in paths:
                self._add_path(dwg, group, path)

        elif node.shape == ShapeType.CIRCLE:
            radius = min(w, h) / 2
            paths = self.rough.rough_circle(center, radius)
            for path in paths:
                self._add_path(dwg, group, path)

        elif node.shape == ShapeType.DIAMOND:
            paths = self.rough.rough_diamond(center, w, h)
            for path in paths:
                self._add_path(dwg, group, path)

        # TODO: Add more shapes

        # Draw text
        text_element = dwg.text(
            node.text,
            insert=(center.x, center.y),
            text_anchor="middle",
            dominant_baseline="middle",
            font_family="Virgil, Comic Sans MS, cursive",
            font_size="16px",
            fill="black"
        )
        group.add(text_element)

    def _draw_edge(
        self,
        dwg: svgwrite.Drawing,
        group: svgwrite.container.Group,
        edge: Edge,
        offset_x: float,
        offset_y: float
    ) -> None:
        """Draw an edge/arrow."""
        if not edge.points or len(edge.points) < 2:
            return

        # Offset points
        offset_points = [
            Point(p.x + offset_x, p.y + offset_y)
            for p in edge.points
        ]

        # Generate rough line through ALL waypoints (not just first and last)
        rough_points = []
        for i in range(len(offset_points) - 1):
            segment_points = self.rough.rough_line(offset_points[i], offset_points[i + 1])
            if i == 0:
                rough_points.extend(segment_points)
            else:
                # Skip first point to avoid duplicates
                rough_points.extend(segment_points[1:])

        # Draw arrow
        if edge.edge_type in [EdgeType.SOLID_ARROW, EdgeType.DOTTED_ARROW, EdgeType.THICK_ARROW]:
            # Calculate adaptive arrow size based on path length
            # For short arrows, use smaller dart; for long arrows, use larger dart
            path_length = self._calculate_path_length(rough_points)

            # Base arrow size is 20, but scale down for short paths
            # Use 15% of path length, capped between 8px (min) and 20px (max)
            adaptive_arrow_size = max(8, min(20, path_length * 0.15))

            body_paths, arrow_paths = self.rough.rough_arrow(rough_points, adaptive_arrow_size)

            # Draw body
            for path in body_paths:
                stroke_dasharray = "5,5" if edge.edge_type == EdgeType.DOTTED_ARROW else None
                stroke_width = 3 if edge.edge_type == EdgeType.THICK_ARROW else 2
                self._add_path(dwg, group, path, stroke_dasharray, stroke_width)

            # Draw arrowhead
            for path in arrow_paths:
                self._add_path(dwg, group, path, stroke_width=stroke_width)
        else:
            # Just a line without arrowhead
            stroke_dasharray = "5,5" if edge.edge_type == EdgeType.DOTTED_LINE else None
            stroke_width = 3 if edge.edge_type == EdgeType.THICK_LINE else 2
            self._add_path(dwg, group, rough_points, stroke_dasharray, stroke_width)

        # Draw label if present
        if edge.label:
            # Place label near the start of the edge (where it leaves the source node)
            # This is especially important for diamond decision nodes where the label
            # should be near the attachment point, not in the middle of the path
            if len(rough_points) >= 4:
                # Use point about 1/4 along the path for better positioning
                label_idx = len(rough_points) // 4
            else:
                # For short paths, use first or second point
                label_idx = min(1, len(rough_points) - 1)

            label_point = rough_points[label_idx]
            text_element = dwg.text(
                edge.label,
                insert=(label_point.x, label_point.y - 10),
                text_anchor="middle",
                font_family="Virgil, Comic Sans MS, cursive",
                font_size="14px",
                fill="black"
            )
            group.add(text_element)

    def _calculate_path_length(self, points: List[Point]) -> float:
        """Calculate total length of a path."""
        if len(points) < 2:
            return 0.0

        total_length = 0.0
        for i in range(len(points) - 1):
            dx = points[i + 1].x - points[i].x
            dy = points[i + 1].y - points[i].y
            total_length += (dx * dx + dy * dy) ** 0.5

        return total_length

    def _create_smooth_path(self, points: List[Point]) -> str:
        """Create smooth SVG path with explicit corner rounding."""
        import math

        if len(points) < 2:
            return ""

        if len(points) == 2:
            return f"M {points[0].x},{points[0].y} L {points[1].x},{points[1].y}"

        # Detect corners (points where direction changes significantly)
        corners = self._detect_corners(points)

        # Start with first point
        path_data = f"M {points[0].x},{points[0].y}"

        # Traverse the path, rounding corners
        max_corner_radius = 50.0  # Maximum radius for corner rounding

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]

            # Check if p2 is a corner (not the last point)
            if i + 1 < len(points) - 1 and corners[i + 1]:
                p3 = points[i + 2]

                # Calculate vectors
                v1x, v1y = p2.x - p1.x, p2.y - p1.y
                v2x, v2y = p3.x - p2.x, p3.y - p2.y

                len1 = math.sqrt(v1x**2 + v1y**2)
                len2 = math.sqrt(v2x**2 + v2y**2)

                if len1 > 0 and len2 > 0:
                    # Normalize vectors
                    v1x, v1y = v1x / len1, v1y / len1
                    v2x, v2y = v2x / len2, v2y / len2

                    # Adaptive corner radius: use 40% of the shorter segment length
                    # but don't exceed max_corner_radius
                    # This ensures the curve fits within the available space
                    min_segment_len = min(len1, len2)
                    adaptive_radius = min(max_corner_radius, 0.4 * min_segment_len)

                    # Don't round if segments are too short (< 20px)
                    if min_segment_len < 20:
                        # Skip rounding for very short segments
                        path_data += f" L {p2.x},{p2.y}"
                        continue

                    offset = adaptive_radius

                    # Point before corner where curve starts
                    start_x = p2.x - v1x * offset
                    start_y = p2.y - v1y * offset

                    # Point after corner where curve ends
                    end_x = p2.x + v2x * offset
                    end_y = p2.y + v2y * offset

                    # Line to start of curve
                    path_data += f" L {start_x},{start_y}"

                    # Quadratic bezier for the corner (control point at corner)
                    path_data += f" Q {p2.x},{p2.y} {end_x},{end_y}"

                    import logging
                    logger = logging.getLogger(__name__)
                    logger.debug(
                        f"  Rounding corner at ({p2.x:.1f}, {p2.y:.1f}) with adaptive radius "
                        f"{offset:.1f}px (segments: {len1:.1f}, {len2:.1f})"
                    )
                else:
                    # Degenerate case, just draw line
                    path_data += f" L {p2.x},{p2.y}"
            else:
                # Not a corner, just draw straight line
                path_data += f" L {p2.x},{p2.y}"

        return path_data

    def _detect_corners(self, points: List[Point]) -> List[bool]:
        """Detect which points are corners (direction changes)."""
        import math
        import logging

        logger = logging.getLogger(__name__)
        corners = [False] * len(points)

        for i in range(1, len(points) - 1):
            p0, p1, p2 = points[i - 1], points[i], points[i + 1]

            # Calculate vectors
            v1x, v1y = p1.x - p0.x, p1.y - p0.y
            v2x, v2y = p2.x - p1.x, p2.y - p1.y

            len1 = math.sqrt(v1x**2 + v1y**2)
            len2 = math.sqrt(v2x**2 + v2y**2)

            if len1 > 1 and len2 > 1:  # Avoid zero-length segments
                # Normalize
                v1x, v1y = v1x / len1, v1y / len1
                v2x, v2y = v2x / len2, v2y / len2

                # Calculate dot product (cosine of angle)
                dot = v1x * v2x + v1y * v2y

                # Only round MAJOR corners (> 45 degrees)
                # dot = 1 means same direction (0°), dot = 0 means 90°, dot = -1 means 180°
                # cos(45°) ≈ 0.707
                if dot < 0.707:  # Only corners > 45 degrees
                    corners[i] = True
                    # Calculate angle in degrees
                    angle_rad = math.acos(max(-1.0, min(1.0, dot)))
                    angle_deg = math.degrees(angle_rad)
                    logger.debug(
                        f"MAJOR corner detected at point {i}: ({p1.x:.1f}, {p1.y:.1f}), "
                        f"angle={angle_deg:.1f}°"
                    )

        corner_count = sum(corners)
        if corner_count > 0:
            logger.info(f"Detected {corner_count} corners in path with {len(points)} waypoints")

        return corners

    def _add_path(
        self,
        dwg: svgwrite.Drawing,
        group: svgwrite.container.Group,
        points: List[Point],
        stroke_dasharray: str = None,
        stroke_width: int = 2
    ) -> None:
        """Add a path element to the SVG."""
        if not points:
            return

        # For paths with many waypoints, create smooth curves using cubic bezier
        if len(points) > 3:
            path_data = self._create_smooth_path(points)
        else:
            # For simple paths, just use straight lines
            path_data = f"M {points[0].x},{points[0].y}"
            for point in points[1:]:
                path_data += f" L {point.x},{point.y}"

        path = dwg.path(
            d=path_data,
            stroke="black",
            stroke_width=stroke_width,
            fill="none",
            stroke_linecap="round",
            stroke_linejoin="round"
        )

        if stroke_dasharray:
            path['stroke-dasharray'] = stroke_dasharray

        group.add(path)
