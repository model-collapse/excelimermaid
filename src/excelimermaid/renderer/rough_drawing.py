"""
Rough drawing primitives for hand-drawn aesthetic.

This module implements the core algorithms for creating hand-drawn,
sketchy lines and shapes similar to Rough.js and Excalidraw.
"""

import random
import math
from typing import List, Tuple, Optional
from ..graph.models import Point


class RoughDrawing:
    """
    Creates hand-drawn style drawing primitives.

    The roughness effect is achieved by:
    - Adding controlled random offsets to line segments
    - Drawing multiple overlapping strokes
    - Using slight variations in angles and dimensions
    """

    def __init__(
        self,
        roughness: float = 1.0,
        bowing: float = 1.0,
        seed: Optional[int] = None,
        multi_stroke: bool = True,
        sketch_style: str = "standard"
    ):
        """
        Initialize rough drawing engine.

        Args:
            roughness: Overall roughness level (0.0-2.0), default 1.0
            bowing: Curvature/bowing of lines (0.0-10.0), default 1.0
            seed: Random seed for reproducibility
            multi_stroke: Draw shapes with multiple overlapping strokes (default: True)
            sketch_style: Style preset - "subtle", "standard" (default), "heavy"
        """
        self.roughness = max(0.0, min(2.0, roughness))
        self.bowing = max(0.0, min(10.0, bowing))
        self.multi_stroke = multi_stroke
        self.sketch_style = sketch_style

        # Adjust parameters based on style preset
        if sketch_style == "subtle":
            self.max_randomness_offset = 0.5
            self.num_strokes = 1
        elif sketch_style == "heavy":
            self.max_randomness_offset = 2.0
            self.num_strokes = 3 if multi_stroke else 1
        else:  # standard
            self.max_randomness_offset = 1.0
            self.num_strokes = 2 if multi_stroke else 1

        self.random = random.Random(seed)

    def rough_line(
        self,
        p1: Point,
        p2: Point,
        preserve_vertices: bool = False
    ) -> List[Point]:
        """
        Generate a rough line from p1 to p2.

        Args:
            p1: Start point
            p2: End point
            preserve_vertices: If True, keep endpoints exact

        Returns:
            List of points forming the rough line
        """
        length = self._distance(p1, p2)
        # More segments for rougher appearance
        # Adjusted based on sketch style
        if self.sketch_style == "heavy":
            num_segments = max(2, int(length / 20))
        else:
            num_segments = max(2, int(length / 30))

        points = []

        for i in range(num_segments + 1):
            t = i / num_segments
            x = self._lerp(p1.x, p2.x, t)
            y = self._lerp(p1.y, p2.y, t)

            # Add perpendicular offset for roughness
            if 0 < i < num_segments or not preserve_vertices:
                # More visible randomness for hand-drawn effect
                offset = self._offset(self.max_randomness_offset * self.roughness)
                angle = math.atan2(p2.y - p1.y, p2.x - p1.x) + math.pi / 2
                x += math.cos(angle) * offset
                y += math.sin(angle) * offset

            points.append(Point(x, y))

        return points

    def rough_rectangle(
        self,
        x: float,
        y: float,
        width: float,
        height: float
    ) -> List[List[Point]]:
        """
        Generate a rough rectangle with optional multi-stroke sketchy effect.

        Args:
            x: Top-left x coordinate
            y: Top-left y coordinate
            width: Rectangle width
            height: Rectangle height

        Returns:
            List of paths (each path is a list of points)
        """
        paths = []

        # Slight random variation in dimensions for hand-drawn look
        w_offset = self._offset(self.roughness * 0.5)
        h_offset = self._offset(self.roughness * 0.5)

        # Draw multiple overlapping strokes for sketchy effect
        for stroke_num in range(self.num_strokes):
            # Add slight offset for each stroke
            if stroke_num > 0:
                x_jitter = self._offset(self.roughness * 0.3)
                y_jitter = self._offset(self.roughness * 0.3)
            else:
                x_jitter = 0
                y_jitter = 0

            corners = [
                Point(x + x_jitter, y + y_jitter),
                Point(x + width + w_offset + x_jitter, y + y_jitter),
                Point(x + width + w_offset + x_jitter, y + height + h_offset + y_jitter),
                Point(x + x_jitter, y + height + h_offset + y_jitter),
            ]

            # Draw each side with roughness
            for i in range(4):
                start = corners[i]
                end = corners[(i + 1) % 4]
                path = self.rough_line(start, end)
                paths.append(path)

        return paths

    def rough_circle(
        self,
        center: Point,
        radius: float
    ) -> List[List[Point]]:
        """
        Generate a rough circle (ellipse with slight variations).

        Args:
            center: Center point of the circle
            radius: Circle radius

        Returns:
            List of paths forming the circle
        """
        num_points = max(20, int(radius * 0.5))
        paths = []

        # Draw multiple overlapping circles for sketchy effect
        for stroke_num in range(self.num_strokes):
            points = []

            # Variation in radius for imperfection (more for multi-stroke)
            variation = 0.05 * self.roughness if stroke_num > 0 else 0.03 * self.roughness
            rx = radius * (1 + self._offset(variation))
            ry = radius * (1 + self._offset(variation))

            # Slight center offset for each stroke
            if stroke_num > 0:
                cx = center.x + self._offset(self.roughness * 0.5)
                cy = center.y + self._offset(self.roughness * 0.5)
            else:
                cx = center.x
                cy = center.y

            for i in range(num_points + 1):
                angle = (i / num_points) * 2 * math.pi
                x = cx + rx * math.cos(angle)
                y = cy + ry * math.sin(angle)

                # Roughness on circles
                offset_x = self._offset(self.max_randomness_offset * self.roughness * 0.4)
                offset_y = self._offset(self.max_randomness_offset * self.roughness * 0.4)

                points.append(Point(x + offset_x, y + offset_y))

            paths.append(points)

        return paths

    def rough_diamond(
        self,
        center: Point,
        width: float,
        height: float
    ) -> List[List[Point]]:
        """
        Generate a rough diamond shape with optional multi-stroke.

        Args:
            center: Center point
            width: Diamond width
            height: Diamond height

        Returns:
            List of paths forming the diamond
        """
        paths = []

        # Draw multiple overlapping diamonds for sketchy effect
        for stroke_num in range(self.num_strokes):
            half_w = width / 2
            half_h = height / 2

            # Add slight size variation for each stroke
            if stroke_num > 0:
                half_w += self._offset(self.roughness * 0.5)
                half_h += self._offset(self.roughness * 0.5)
                cx = center.x + self._offset(self.roughness * 0.3)
                cy = center.y + self._offset(self.roughness * 0.3)
            else:
                cx = center.x
                cy = center.y

            # Diamond vertices (top, right, bottom, left)
            vertices = [
                Point(cx, cy - half_h),
                Point(cx + half_w, cy),
                Point(cx, cy + half_h),
                Point(cx - half_w, cy),
            ]

            # Draw each edge
            for i in range(4):
                start = vertices[i]
                end = vertices[(i + 1) % 4]
                path = self.rough_line(start, end)
                paths.append(path)

        return paths

    def rough_arrow(
        self,
        points: List[Point],
        arrow_size: float = 20
    ) -> Tuple[List[List[Point]], List[List[Point]]]:
        """
        Generate a rough arrow along a path.

        Args:
            points: Path points for the arrow body
            arrow_size: Size of the arrowhead

        Returns:
            Tuple of (body_paths, arrowhead_paths)
        """
        if len(points) < 2:
            return ([], [])

        # Body is the rough line
        body_paths = [points]

        # Arrowhead at the end
        p1 = points[-2]
        p2 = points[-1]

        angle = math.atan2(p2.y - p1.y, p2.x - p1.x)
        arrow_angle = 0.4  # ~23 degrees

        # Two lines forming the arrowhead
        left = Point(
            p2.x - arrow_size * math.cos(angle - arrow_angle),
            p2.y - arrow_size * math.sin(angle - arrow_angle)
        )
        right = Point(
            p2.x - arrow_size * math.cos(angle + arrow_angle),
            p2.y - arrow_size * math.sin(angle + arrow_angle)
        )

        arrowhead_paths = [
            self.rough_line(left, p2, preserve_vertices=True),
            self.rough_line(right, p2, preserve_vertices=True),
        ]

        return (body_paths, arrowhead_paths)

    def _distance(self, p1: Point, p2: Point) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)

    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation between a and b."""
        return a + (b - a) * t

    def _offset(self, max_offset: float) -> float:
        """Generate a random offset with Gaussian distribution."""
        # Tighter distribution: sigma = max_offset / 4 (was /3)
        # This keeps 99.7% of values within ±max_offset but with less extreme values
        return self.random.gauss(0, max_offset / 4)
