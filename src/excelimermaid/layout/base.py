"""Base class for layout engines."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from ..graph.models import Diagram, Point, Node, RoutingConfig
from .geometry import get_shape_boundary_point
from .edge_routing import (
    find_obstacles,
    route_around_obstacles,
    create_smooth_curve
)
from .pathfinding import astar_route_around_obstacles
from .pathfinding_v2 import route_edges_adaptively


class LayoutEngine(ABC):
    """
    Abstract base class for graph layout algorithms.

    Subclasses should implement the layout() method to position nodes
    and route edges in a Diagram.
    """

    def __init__(self, routing_config: Optional[RoutingConfig] = None, **config: Any):
        """
        Initialize the layout engine with configuration.

        Args:
            routing_config: Edge routing configuration
            **config: Layout-specific configuration options
        """
        self.config = config
        self.node_spacing: int = config.get("node_spacing", 80)
        self.rank_spacing: int = config.get("rank_spacing", 100)
        self.routing_config = routing_config or RoutingConfig()

    @abstractmethod
    def layout(self, diagram: Diagram) -> Diagram:
        """
        Apply layout algorithm to position nodes and route edges.

        Args:
            diagram: The diagram to layout

        Returns:
            The same diagram with updated node positions and edge routes
        """
        pass

    def _calculate_node_size(self, node) -> tuple[float, float]:
        """
        Calculate the size of a node based on its text and shape.

        Args:
            node: Node to calculate size for

        Returns:
            Tuple of (width, height) in pixels
        """
        # Base size calculation
        # TODO: Consider text length, font size, padding
        text_length = len(node.text)
        base_width = max(100, text_length * 8 + 40)
        base_height = 60

        # Adjust for shape
        if node.shape.name == "CIRCLE":
            # Circle needs to be square
            size = max(base_width, base_height)
            return (size, size)
        elif node.shape.name == "DIAMOND":
            # Diamond needs more space
            return (base_width * 1.4, base_height * 1.4)

        return (base_width, base_height)

    def _route_edge(self, edge, all_nodes: List[Node]) -> list[Point]:
        """
        Calculate control points for an edge between two nodes.
        Uses obstacle avoidance to route around other nodes based on routing configuration.

        Args:
            edge: Edge to route
            all_nodes: All nodes in the diagram (to detect obstacles)

        Returns:
            List of points defining the edge path
        """
        if not (edge.source.bbox and edge.target.bbox):
            return []

        # Get centers of source and target nodes
        source_center = edge.source.bbox.center
        target_center = edge.target.bbox.center

        # Calculate boundary points where edge meets the shapes
        source_point = get_shape_boundary_point(
            source_center,
            edge.source.bbox,
            edge.source.shape,
            target_center
        )

        target_point = get_shape_boundary_point(
            target_center,
            edge.target.bbox,
            edge.target.shape,
            source_center
        )

        # Check routing configuration
        if self.routing_config.edge_routing == "straight":
            # Always use direct path for straight routing
            return [source_point, target_point]

        # For curved/orthogonal routing, check if obstacle avoidance is enabled
        if not self.routing_config.avoid_obstacles:
            # No obstacle avoidance, just draw direct line
            return [source_point, target_point]

        # Check if using orthogonal routing
        is_orthogonal = (self.routing_config.edge_routing == "orthogonal")

        # Use pathfinding algorithm configured
        if self.routing_config.pathfinding_algorithm == "astar":
            # Use A* pathfinding - ALWAYS mark all nodes as obstacles
            # A* will find optimal path even if direct line is clear
            waypoints = astar_route_around_obstacles(
                source_point,
                target_point,
                all_nodes,
                edge.source,
                edge.target,
                margin=self.routing_config.route_margin,
                cell_size=self.routing_config.pathfinding_cell_size,
                orthogonal=is_orthogonal
            )

            # For orthogonal routing, keep sharp corners; for curved, apply smoothing
            if is_orthogonal:
                return waypoints  # Keep sharp orthogonal corners
            else:
                return create_smooth_curve(waypoints, smoothness=self.routing_config.smoothness)
        else:
            # Use heuristic routing - only route around if obstacles detected on direct line
            obstacles = find_obstacles(
                source_point,
                target_point,
                all_nodes,
                edge.source,
                edge.target,
                margin=self.routing_config.route_margin
            )

            if obstacles:
                # Use heuristic routing around detected obstacles
                waypoints = route_around_obstacles(
                    source_point,
                    target_point,
                    obstacles,
                    edge.source,
                    edge.target,
                    offset=self.routing_config.route_offset
                )
                return create_smooth_curve(waypoints, smoothness=self.routing_config.smoothness)
            else:
                # Direct path is clear
                return [source_point, target_point]

    def _route_all_edges_adaptively(self, diagram: Diagram) -> None:
        """
        Route all edges using adaptive A* pathfinding.

        This routes edges in order (short first), marking routed edges
        as obstacles for subsequent edges. Follows improved algorithm:
        1. Heuristically define margin based on diagram size
        2. Grid canvas using margin as cell size
        3. Mark boxes AND easy edges as obstacles
        4. A* search in grid space
        5. Regress cell-wise path to smooth curve
        6. Process short edges first
        7. Check edge crossings for longer edges
        8. Reduce cell size when space is tight

        Args:
            diagram: Diagram with positioned nodes
        """
        is_orthogonal = (self.routing_config.edge_routing == "orthogonal")

        # Route all edges using new adaptive algorithm
        edge_paths = route_edges_adaptively(
            all_nodes=diagram.nodes,
            all_edges=diagram.edges,
            margin=self.routing_config.route_margin,
            orthogonal=is_orthogonal,
            direction=diagram.direction
        )

        # Apply paths to edges
        for edge, waypoints in edge_paths.items():
            # Paths from route_edges_adaptively are already smoothed with Catmull-Rom splines
            # Just use them directly
            edge.points = waypoints
