"""Tests for graph models."""

import pytest
from excelimermaid.graph.models import (
    Node,
    Edge,
    Diagram,
    Point,
    BoundingBox,
    ShapeType,
    EdgeType,
    Direction,
)


def test_point_operations():
    """Test Point arithmetic operations."""
    p1 = Point(10, 20)
    p2 = Point(5, 15)

    # Addition
    p3 = p1 + p2
    assert p3.x == 15
    assert p3.y == 35

    # Subtraction
    p4 = p1 - p2
    assert p4.x == 5
    assert p4.y == 5

    # Scalar multiplication
    p5 = p1 * 2
    assert p5.x == 20
    assert p5.y == 40


def test_bounding_box():
    """Test BoundingBox properties."""
    bbox = BoundingBox(10, 20, 100, 50)

    assert bbox.center.x == 60
    assert bbox.center.y == 45

    assert bbox.top_left.x == 10
    assert bbox.top_left.y == 20

    assert bbox.bottom_right.x == 110
    assert bbox.bottom_right.y == 70


def test_node_creation():
    """Test Node creation."""
    node = Node(
        id="A",
        text="Start",
        shape=ShapeType.RECTANGLE,
        position=Point(0, 0)
    )

    assert node.id == "A"
    assert node.text == "Start"
    assert node.shape == ShapeType.RECTANGLE
    assert node.position.x == 0
    assert node.position.y == 0


def test_edge_creation():
    """Test Edge creation."""
    node1 = Node(id="A", text="Start", shape=ShapeType.RECTANGLE)
    node2 = Node(id="B", text="End", shape=ShapeType.RECTANGLE)

    edge = Edge(
        source=node1,
        target=node2,
        edge_type=EdgeType.SOLID_ARROW,
        label="Next"
    )

    assert edge.source.id == "A"
    assert edge.target.id == "B"
    assert edge.edge_type == EdgeType.SOLID_ARROW
    assert edge.label == "Next"


def test_diagram_creation():
    """Test Diagram creation."""
    node1 = Node(id="A", text="Start", shape=ShapeType.RECTANGLE)
    node2 = Node(id="B", text="End", shape=ShapeType.RECTANGLE)
    edge = Edge(source=node1, target=node2, edge_type=EdgeType.SOLID_ARROW)

    diagram = Diagram(
        nodes=[node1, node2],
        edges=[edge],
        direction=Direction.LEFT_RIGHT
    )

    assert len(diagram.nodes) == 2
    assert len(diagram.edges) == 1
    assert diagram.direction == Direction.LEFT_RIGHT
