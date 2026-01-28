"""Data models for graph representation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple


class ShapeType(Enum):
    """Node shape types supported in flowcharts."""
    RECTANGLE = "rectangle"
    ROUNDED_RECTANGLE = "rounded_rectangle"
    STADIUM = "stadium"
    SUBROUTINE = "subroutine"
    CYLINDRICAL = "cylindrical"
    CIRCLE = "circle"
    DIAMOND = "diamond"
    HEXAGON = "hexagon"
    PARALLELOGRAM = "parallelogram"
    PARALLELOGRAM_ALT = "parallelogram_alt"
    TRAPEZOID = "trapezoid"
    TRAPEZOID_ALT = "trapezoid_alt"


class EdgeType(Enum):
    """Edge/arrow types supported in flowcharts."""
    SOLID_ARROW = "solid_arrow"
    DOTTED_ARROW = "dotted_arrow"
    THICK_ARROW = "thick_arrow"
    SOLID_LINE = "solid_line"
    DOTTED_LINE = "dotted_line"
    THICK_LINE = "thick_line"


class Direction(Enum):
    """Flow direction for the diagram."""
    TOP_DOWN = "TD"
    TOP_BOTTOM = "TB"
    BOTTOM_TOP = "BT"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"


@dataclass
class RoutingConfig:
    """Configuration for edge routing behavior."""
    edge_routing: str = "curved"  # "curved", "straight", "orthogonal" (future)
    avoid_obstacles: bool = True  # Enable obstacle detection and avoidance
    route_margin: float = 15.0  # Margin around nodes for collision detection (px)
    smoothness: float = 0.6  # Curve smoothness 0.0-1.0
    route_offset: float = 60.0  # Distance to offset when routing around obstacles (px)
    pathfinding_algorithm: str = "astar"  # Pathfinding algorithm: "astar", "heuristic"
    pathfinding_cell_size: int = 10  # Grid cell size for A* pathfinding (px)

    def __post_init__(self):
        """Validate configuration values."""
        if self.edge_routing not in ["curved", "straight", "orthogonal"]:
            raise ValueError(f"Invalid edge_routing: {self.edge_routing}. Must be 'curved', 'straight', or 'orthogonal'")
        if not 0.0 <= self.smoothness <= 1.0:
            raise ValueError(f"smoothness must be between 0.0 and 1.0, got {self.smoothness}")
        if self.route_margin < 0:
            raise ValueError(f"route_margin must be non-negative, got {self.route_margin}")
        if self.route_offset < 0:
            raise ValueError(f"route_offset must be non-negative, got {self.route_offset}")
        if self.pathfinding_algorithm not in ["astar", "heuristic"]:
            raise ValueError(f"Invalid pathfinding_algorithm: {self.pathfinding_algorithm}. Must be 'astar' or 'heuristic'")
        if self.pathfinding_cell_size < 1:
            raise ValueError(f"pathfinding_cell_size must be at least 1, got {self.pathfinding_cell_size}")


@dataclass
class Point:
    """A 2D point."""
    x: float
    y: float

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Point":
        return Point(self.x * scalar, self.y * scalar)


@dataclass
class BoundingBox:
    """Bounding box for a shape."""
    x: float
    y: float
    width: float
    height: float

    @property
    def center(self) -> Point:
        """Get the center point of the bounding box."""
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def top_left(self) -> Point:
        """Get the top-left corner."""
        return Point(self.x, self.y)

    @property
    def bottom_right(self) -> Point:
        """Get the bottom-right corner."""
        return Point(self.x + self.width, self.y + self.height)


@dataclass
class Node:
    """A node in the flowchart graph."""
    id: str
    text: str
    shape: ShapeType
    position: Optional[Point] = None
    bbox: Optional[BoundingBox] = None
    style: dict = field(default_factory=dict)

    def __hash__(self):
        return hash(self.id)


@dataclass
class Edge:
    """An edge connecting two nodes."""
    source: Node
    target: Node
    edge_type: EdgeType
    label: Optional[str] = None
    points: List[Point] = field(default_factory=list)
    style: dict = field(default_factory=dict)

    def __hash__(self):
        return hash((self.source.id, self.target.id))


@dataclass
class Diagram:
    """A complete flowchart diagram."""
    nodes: List[Node]
    edges: List[Edge]
    direction: Direction = Direction.TOP_DOWN
    title: Optional[str] = None
    metadata: dict = field(default_factory=dict)
