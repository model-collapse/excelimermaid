"""Tests for routing configuration."""

import pytest
from excelimermaid import MermaidRenderer
from excelimermaid.graph.models import RoutingConfig


def test_routing_config_defaults():
    """Test that RoutingConfig has correct defaults."""
    config = RoutingConfig()
    assert config.edge_routing == "curved"
    assert config.avoid_obstacles is True
    assert config.route_margin == 15.0
    assert config.smoothness == 0.6
    assert config.route_offset == 60.0


def test_routing_config_validation():
    """Test that RoutingConfig validates input."""
    # Invalid edge_routing
    with pytest.raises(ValueError, match="Invalid edge_routing"):
        RoutingConfig(edge_routing="invalid")

    # Invalid smoothness (too low)
    with pytest.raises(ValueError, match="smoothness must be between"):
        RoutingConfig(smoothness=-0.1)

    # Invalid smoothness (too high)
    with pytest.raises(ValueError, match="smoothness must be between"):
        RoutingConfig(smoothness=1.5)

    # Invalid route_margin (negative)
    with pytest.raises(ValueError, match="route_margin must be non-negative"):
        RoutingConfig(route_margin=-5.0)

    # Invalid route_offset (negative)
    with pytest.raises(ValueError, match="route_offset must be non-negative"):
        RoutingConfig(route_offset=-10.0)


def test_renderer_with_curved_routing():
    """Test renderer with curved routing (default)."""
    script = """
    flowchart LR
        A[Start] --> B[Middle]
        A --> C[End]
        B --> C
    """

    renderer = MermaidRenderer(edge_routing="curved", seed=42)
    diagram = renderer.parse(script)
    diagram.layout()

    # Check that some edges might be curved (have more than 2 points)
    # Not all edges will be curved, only those with obstacles
    assert len(diagram.diagram.edges) > 0


def test_renderer_with_straight_routing():
    """Test renderer with straight routing mode."""
    script = """
    flowchart LR
        A[Start] --> B[Middle]
        A --> C[End]
        B --> C
    """

    renderer = MermaidRenderer(edge_routing="straight", seed=42)
    diagram = renderer.parse(script)
    diagram.layout()

    # All edges should be straight (exactly 2 points)
    for edge in diagram.diagram.edges:
        assert len(edge.points) == 2, f"Edge {edge.source.text} -> {edge.target.text} should be straight"


def test_renderer_with_obstacle_avoidance_disabled():
    """Test renderer with obstacle avoidance disabled."""
    script = """
    flowchart LR
        A[Start] --> B[Middle]
        A --> C[End]
        B --> C
    """

    renderer = MermaidRenderer(avoid_obstacles=False, seed=42)
    diagram = renderer.parse(script)
    diagram.layout()

    # All edges should be direct (exactly 2 points) even if obstacles exist
    for edge in diagram.diagram.edges:
        assert len(edge.points) == 2


def test_renderer_with_custom_margin():
    """Test renderer with custom collision margin."""
    script = """
    flowchart TD
        A --> B
        B --> C
    """

    # Larger margin might detect more obstacles
    renderer_large = MermaidRenderer(route_margin=20.0, seed=42)
    diagram_large = renderer_large.parse(script)
    diagram_large.layout()

    # Smaller margin might detect fewer obstacles
    renderer_small = MermaidRenderer(route_margin=1.0, seed=42)
    diagram_small = renderer_small.parse(script)
    diagram_small.layout()

    # Both should render successfully
    assert len(diagram_large.diagram.edges) > 0
    assert len(diagram_small.diagram.edges) > 0


def test_renderer_with_custom_smoothness():
    """Test renderer with custom smoothness values."""
    script = """
    flowchart LR
        A[Start] --> B[Middle]
        A --> C[End]
        B --> C
    """

    # Sharp corners
    renderer_sharp = MermaidRenderer(smoothness=0.2, seed=42)
    diagram_sharp = renderer_sharp.parse(script)
    diagram_sharp.layout()

    # Very smooth corners
    renderer_smooth = MermaidRenderer(smoothness=0.9, seed=42)
    diagram_smooth = renderer_smooth.parse(script)
    diagram_smooth.layout()

    # Both should render successfully
    assert len(diagram_sharp.diagram.edges) > 0
    assert len(diagram_smooth.diagram.edges) > 0


def test_renderer_with_custom_offset():
    """Test renderer with custom route offset."""
    script = """
    flowchart LR
        A[Start] --> B[Middle]
        A --> C[End]
        B --> C
    """

    # Small offset
    renderer_small = MermaidRenderer(route_offset=30.0, seed=42)
    diagram_small = renderer_small.parse(script)
    diagram_small.layout()

    # Large offset
    renderer_large = MermaidRenderer(route_offset=100.0, seed=42)
    diagram_large = renderer_large.parse(script)
    diagram_large.layout()

    # Both should render successfully
    assert len(diagram_small.diagram.edges) > 0
    assert len(diagram_large.diagram.edges) > 0


def test_renderer_api_backward_compatibility():
    """Test that existing code without routing params still works."""
    script = """
    flowchart TD
        A --> B
        B --> C
    """

    # Old-style initialization without routing params
    renderer = MermaidRenderer(roughness=1.0, seed=42)
    diagram = renderer.parse(script)
    diagram.layout()

    # Should use defaults and work fine
    assert len(diagram.diagram.nodes) == 3
    assert len(diagram.diagram.edges) == 2


def test_routing_config_in_renderer():
    """Test that routing config is properly stored in renderer."""
    renderer = MermaidRenderer(
        edge_routing="straight",
        avoid_obstacles=False,
        route_margin=10.0,
        smoothness=0.8,
        route_offset=80.0
    )

    config = renderer.routing_config
    assert config.edge_routing == "straight"
    assert config.avoid_obstacles is False
    assert config.route_margin == 10.0
    assert config.smoothness == 0.8
    assert config.route_offset == 80.0
