"""Geometry utilities for edge routing and shape intersections."""

import math
from typing import Optional, Tuple, List
from ..graph.models import Point, BoundingBox, ShapeType, Node


def get_shape_boundary_point(
    center: Point,
    bbox: BoundingBox,
    shape: ShapeType,
    target_point: Point
) -> Point:
    """
    Calculate the point where a line from center to target intersects the shape boundary.

    Args:
        center: Center of the shape
        bbox: Bounding box of the shape
        shape: Type of shape
        target_point: Point we're connecting to

    Returns:
        Point on the shape's boundary
    """
    # Calculate direction from center to target
    dx = target_point.x - center.x
    dy = target_point.y - center.y

    if dx == 0 and dy == 0:
        return center

    # Normalize direction
    length = math.sqrt(dx * dx + dy * dy)
    dx /= length
    dy /= length

    if shape == ShapeType.RECTANGLE or shape == ShapeType.ROUNDED_RECTANGLE:
        return _rectangle_boundary_point(center, bbox, dx, dy)
    elif shape == ShapeType.CIRCLE:
        return _circle_boundary_point(center, bbox, dx, dy)
    elif shape == ShapeType.DIAMOND:
        return _diamond_boundary_point(center, bbox, dx, dy)
    elif shape == ShapeType.STADIUM:
        return _stadium_boundary_point(center, bbox, dx, dy)
    else:
        # Default to rectangle for other shapes
        return _rectangle_boundary_point(center, bbox, dx, dy)


def _rectangle_boundary_point(
    center: Point,
    bbox: BoundingBox,
    dx: float,
    dy: float
) -> Point:
    """Calculate intersection with rectangle boundary."""
    half_w = bbox.width / 2
    half_h = bbox.height / 2

    # Calculate which edge the line hits first
    if dx != 0:
        t_x = half_w / abs(dx)
    else:
        t_x = float('inf')

    if dy != 0:
        t_y = half_h / abs(dy)
    else:
        t_y = float('inf')

    # Use the smaller t (hits boundary first)
    t = min(t_x, t_y)

    return Point(center.x + dx * t, center.y + dy * t)


def _circle_boundary_point(
    center: Point,
    bbox: BoundingBox,
    dx: float,
    dy: float
) -> Point:
    """Calculate intersection with circle boundary."""
    # Use average of width and height as radius
    radius = min(bbox.width, bbox.height) / 2

    return Point(
        center.x + dx * radius,
        center.y + dy * radius
    )


def _diamond_boundary_point(
    center: Point,
    bbox: BoundingBox,
    dx: float,
    dy: float
) -> Point:
    """Calculate intersection with diamond boundary."""
    half_w = bbox.width / 2
    half_h = bbox.height / 2

    # Diamond is rotated square, so we calculate based on Manhattan distance
    # The boundary is at: |x|/half_w + |y|/half_h = 1
    # Solving for t where (dx*t, dy*t) hits the boundary
    if abs(dx) / half_w + abs(dy) / half_h > 0:
        t = 1 / (abs(dx) / half_w + abs(dy) / half_h)
    else:
        t = 0

    return Point(center.x + dx * t, center.y + dy * t)


def _stadium_boundary_point(
    center: Point,
    bbox: BoundingBox,
    dx: float,
    dy: float
) -> Point:
    """Calculate intersection with stadium (pill) boundary."""
    # Stadium is rectangle with semicircular ends
    half_w = bbox.width / 2
    half_h = bbox.height / 2

    # Determine if we're hitting the flat sides or the rounded ends
    if bbox.width > bbox.height:
        # Horizontal stadium
        flat_half_width = (half_w - half_h)

        if abs(center.x + dx * half_h) < flat_half_width:
            # Hit the top or bottom flat part
            if dy != 0:
                t = half_h / abs(dy)
                return Point(center.x + dx * t, center.y + dy * t)

        # Hit the circular ends
        if dx > 0:
            circle_center_x = flat_half_width
        else:
            circle_center_x = -flat_half_width

        # Calculate intersection with circle
        adj_dx = dx
        adj_dy = dy
        adj_length = math.sqrt(adj_dx ** 2 + adj_dy ** 2)
        if adj_length > 0:
            return Point(
                center.x + circle_center_x + (adj_dx / adj_length) * half_h,
                center.y + (adj_dy / adj_length) * half_h
            )
    else:
        # Vertical stadium
        flat_half_height = (half_h - half_w)

        if abs(center.y + dy * half_w) < flat_half_height:
            # Hit the left or right flat part
            if dx != 0:
                t = half_w / abs(dx)
                return Point(center.x + dx * t, center.y + dy * t)

        # Hit the circular ends
        if dy > 0:
            circle_center_y = flat_half_height
        else:
            circle_center_y = -flat_half_height

        # Calculate intersection with circle
        adj_dx = dx
        adj_dy = dy
        adj_length = math.sqrt(adj_dx ** 2 + adj_dy ** 2)
        if adj_length > 0:
            return Point(
                center.x + (adj_dx / adj_length) * half_w,
                center.y + circle_center_y + (adj_dy / adj_length) * half_w
            )

    # Fallback to rectangle
    return _rectangle_boundary_point(center, bbox, dx, dy)
