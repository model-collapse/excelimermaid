"""Tests for Mermaid parser."""

import pytest
from excelimermaid.parser import MermaidParser
from excelimermaid.graph.models import ShapeType, EdgeType, Direction


def test_parser_initialization():
    """Test parser can be initialized."""
    parser = MermaidParser()
    assert parser is not None


def test_parse_simple_flowchart():
    """Test parsing a simple flowchart."""
    parser = MermaidParser()
    script = """
    flowchart TD
        A[Start] --> B[End]
    """
    diagram = parser.parse(script)

    assert len(diagram.nodes) == 2
    assert len(diagram.edges) == 1
    assert diagram.direction == Direction.TOP_DOWN

    # Check nodes
    nodes_by_id = {node.id: node for node in diagram.nodes}
    assert 'A' in nodes_by_id
    assert 'B' in nodes_by_id
    assert nodes_by_id['A'].text == 'Start'
    assert nodes_by_id['B'].text == 'End'
    assert nodes_by_id['A'].shape == ShapeType.RECTANGLE
    assert nodes_by_id['B'].shape == ShapeType.RECTANGLE

    # Check edge
    edge = diagram.edges[0]
    assert edge.source.id == 'A'
    assert edge.target.id == 'B'
    assert edge.edge_type == EdgeType.SOLID_ARROW
    assert edge.label is None


def test_parse_with_diamond_shape():
    """Test parsing diamond (decision) shapes."""
    parser = MermaidParser()
    script = """
    flowchart TD
        A[Start] --> B{Decision}
        B -->|Yes| C[Action]
    """
    diagram = parser.parse(script)

    assert len(diagram.nodes) == 3
    nodes_by_id = {node.id: node for node in diagram.nodes}
    assert nodes_by_id['B'].shape == ShapeType.DIAMOND
    assert nodes_by_id['B'].text == 'Decision'


def test_parse_with_edge_labels():
    """Test parsing edges with labels."""
    parser = MermaidParser()
    script = """
    flowchart TD
        A --> B
        B -->|Yes| C
        B -->|No| D
    """
    diagram = parser.parse(script)

    assert len(diagram.edges) == 3
    labeled_edges = [e for e in diagram.edges if e.label]
    assert len(labeled_edges) == 2

    labels = [e.label for e in labeled_edges]
    assert 'Yes' in labels
    assert 'No' in labels


def test_parse_different_directions():
    """Test parsing different flow directions."""
    parser = MermaidParser()

    # Left to right
    script_lr = "flowchart LR\n    A --> B"
    diagram = parser.parse(script_lr)
    assert diagram.direction == Direction.LEFT_RIGHT

    # Right to left
    script_rl = "flowchart RL\n    A --> B"
    diagram = parser.parse(script_rl)
    assert diagram.direction == Direction.RIGHT_LEFT

    # Bottom to top
    script_bt = "flowchart BT\n    A --> B"
    diagram = parser.parse(script_bt)
    assert diagram.direction == Direction.BOTTOM_TOP


def test_parse_rounded_rectangle():
    """Test parsing rounded rectangle shapes."""
    parser = MermaidParser()
    script = """
    flowchart TD
        A(Rounded) --> B[Square]
    """
    diagram = parser.parse(script)

    nodes_by_id = {node.id: node for node in diagram.nodes}
    assert nodes_by_id['A'].shape == ShapeType.ROUNDED_RECTANGLE
    assert nodes_by_id['A'].text == 'Rounded'


def test_parse_circle():
    """Test parsing circle shapes."""
    parser = MermaidParser()
    script = """
    flowchart TD
        A((Circle)) --> B[Square]
    """
    diagram = parser.parse(script)

    nodes_by_id = {node.id: node for node in diagram.nodes}
    assert nodes_by_id['A'].shape == ShapeType.CIRCLE
    assert nodes_by_id['A'].text == 'Circle'


def test_parse_dotted_arrow():
    """Test parsing dotted arrows."""
    parser = MermaidParser()
    script = """
    flowchart TD
        A -.-> B
    """
    diagram = parser.parse(script)

    assert len(diagram.edges) == 1
    assert diagram.edges[0].edge_type == EdgeType.DOTTED_ARROW


def test_parse_thick_arrow():
    """Test parsing thick arrows."""
    parser = MermaidParser()
    script = """
    flowchart TD
        A ==> B
    """
    diagram = parser.parse(script)

    assert len(diagram.edges) == 1
    assert diagram.edges[0].edge_type == EdgeType.THICK_ARROW


def test_parse_comments():
    """Test that comments are ignored."""
    parser = MermaidParser()
    script = """
    flowchart TD
        %% This is a comment
        A --> B
        %% Another comment
    """
    diagram = parser.parse(script)

    assert len(diagram.nodes) == 2
    assert len(diagram.edges) == 1


def test_parse_complex_flowchart():
    """Test parsing a more complex flowchart."""
    parser = MermaidParser()
    script = """
    flowchart TD
        Start[Start] --> Auth{Authenticated?}
        Auth -->|Yes| Dashboard[Dashboard]
        Auth -->|No| Login[Login Page]
        Login --> Start
        Dashboard --> End[End]
    """
    diagram = parser.parse(script)

    assert len(diagram.nodes) == 5
    assert len(diagram.edges) == 5

    # Check that decision node is diamond
    nodes_by_id = {node.id: node for node in diagram.nodes}
    assert nodes_by_id['Auth'].shape == ShapeType.DIAMOND
