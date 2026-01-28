"""Hierarchical layout using Sugiyama framework."""

import networkx as nx
from typing import Dict, List, Set
from grandalf.layouts import SugiyamaLayout
from grandalf.graphs import Graph, Vertex, Edge as GEdge

from .base import LayoutEngine
from ..graph.models import Diagram, Point, BoundingBox, Node


class NodeView:
    """
    Simple view class for grandalf vertices.

    Grandalf requires vertices to have a view object with w, h, and xy attributes.
    """
    def __init__(self, w: float = 100, h: float = 60):
        self.w = w
        self.h = h
        self.xy = [0, 0]  # Will be updated by layout algorithm


class HierarchicalLayout(LayoutEngine):
    """
    Hierarchical layout algorithm using the Sugiyama framework.

    This layout is ideal for flowcharts and directed acyclic graphs (DAGs).
    It organizes nodes in layers/ranks and minimizes edge crossings.

    The algorithm has four main phases:
    1. Cycle removal (if necessary)
    2. Layer assignment
    3. Crossing reduction
    4. Coordinate assignment
    """

    def __init__(self, **config):
        """
        Initialize hierarchical layout engine.

        Args:
            **config: Configuration options
                - node_spacing: Horizontal spacing between nodes
                - rank_spacing: Vertical spacing between ranks
                - direction: Layout direction (top-down, left-right, etc.)
        """
        super().__init__(**config)

    def layout(self, diagram: Diagram) -> Diagram:
        """
        Apply hierarchical layout to the diagram.

        Args:
            diagram: The diagram to layout

        Returns:
            Diagram with positioned nodes and routed edges
        """
        if not diagram.nodes:
            return diagram

        # Build NetworkX graph for analysis
        G = self._build_networkx_graph(diagram)

        # Use grandalf for Sugiyama layout
        vertices, edges_map = self._build_grandalf_graph(diagram)

        # Create grandalf graph
        g = Graph(vertices, list(edges_map.values()))

        # Apply Sugiyama layout
        sug = SugiyamaLayout(g.C[0])  # C[0] is the main connected component
        sug.init_all()
        sug.draw()

        # Extract positions from grandalf and apply to our nodes
        self._apply_positions(diagram, vertices)

        # Route edges with obstacle avoidance
        # Use adaptive batch routing if A* is enabled with obstacle avoidance
        if (self.routing_config.avoid_obstacles and
            self.routing_config.pathfinding_algorithm == "astar"):
            # Use new adaptive A* that processes edges in order
            self._route_all_edges_adaptively(diagram)
        else:
            # Use traditional per-edge routing
            for edge in diagram.edges:
                edge.points = self._route_edge(edge, diagram.nodes)

        return diagram

    def _build_networkx_graph(self, diagram: Diagram) -> nx.DiGraph:
        """
        Build a NetworkX directed graph from the diagram.

        Args:
            diagram: The diagram to convert

        Returns:
            NetworkX DiGraph
        """
        G = nx.DiGraph()

        # Add nodes
        for node in diagram.nodes:
            G.add_node(node.id, data=node)

        # Add edges
        for edge in diagram.edges:
            G.add_edge(edge.source.id, edge.target.id, data=edge)

        return G

    def _build_grandalf_graph(self, diagram: Diagram) -> tuple[List[Vertex], Dict]:
        """
        Build grandalf graph structure.

        Args:
            diagram: The diagram to convert

        Returns:
            Tuple of (vertices list, edges dictionary)
        """
        # Create vertices
        vertices_map = {}
        for node in diagram.nodes:
            width, height = self._calculate_node_size(node)
            v = Vertex(data=node)
            # Initialize the view with our NodeView class
            v.view = NodeView(w=width, h=height)
            vertices_map[node.id] = v

        # Create edges
        edges_map = {}
        for i, edge in enumerate(diagram.edges):
            source_v = vertices_map[edge.source.id]
            target_v = vertices_map[edge.target.id]
            e = GEdge(source_v, target_v, data=edge)
            edges_map[i] = e

        return list(vertices_map.values()), edges_map

    def _apply_positions(self, diagram: Diagram, vertices: List[Vertex]) -> None:
        """
        Apply positions from grandalf vertices to diagram nodes.

        Args:
            diagram: The diagram to update
            vertices: List of positioned grandalf vertices
        """
        for vertex in vertices:
            node: Node = vertex.data
            # Grandalf gives us center positions
            x = vertex.view.xy[0]
            y = vertex.view.xy[1]
            w = vertex.view.w
            h = vertex.view.h

            # Set node position (top-left corner)
            node.position = Point(x - w / 2, y - h / 2)
            node.bbox = BoundingBox(x - w / 2, y - h / 2, w, h)
