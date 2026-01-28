"""Test parser with example Mermaid files."""

import pytest
from pathlib import Path
from excelimermaid.parser import MermaidParser


def test_parse_basic_flowchart_example():
    """Test parsing the basic flowchart example."""
    example_path = Path(__file__).parent.parent / "examples" / "basic_flowchart.mmd"
    script = example_path.read_text()

    parser = MermaidParser()
    diagram = parser.parse(script)

    # Should have nodes: Start, Is it working?, Great!, Debug, End
    assert len(diagram.nodes) >= 5
    assert len(diagram.edges) >= 5

    # Check that at least one node is a diamond (decision node)
    shapes = [node.shape.name for node in diagram.nodes]
    assert 'DIAMOND' in shapes


def test_parse_decision_tree_example():
    """Test parsing the decision tree example."""
    example_path = Path(__file__).parent.parent / "examples" / "decision_tree.mmd"
    script = example_path.read_text()

    parser = MermaidParser()
    diagram = parser.parse(script)

    # Should have multiple nodes and edges
    assert len(diagram.nodes) >= 6
    assert len(diagram.edges) >= 6

    # Should have decision nodes (diamonds)
    shapes = [node.shape.name for node in diagram.nodes]
    assert 'DIAMOND' in shapes


def test_parse_complex_flow_example():
    """Test parsing the complex flow example."""
    example_path = Path(__file__).parent.parent / "examples" / "complex_flow.mmd"
    script = example_path.read_text()

    parser = MermaidParser()
    diagram = parser.parse(script)

    # Should have many nodes and edges
    assert len(diagram.nodes) >= 10
    assert len(diagram.edges) >= 10

    # Should be left-right direction
    from excelimermaid.graph.models import Direction
    assert diagram.direction == Direction.LEFT_RIGHT
