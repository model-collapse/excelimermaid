"""End-to-end integration tests."""

import pytest
import tempfile
import os
from pathlib import Path
from excelimermaid import render, MermaidRenderer


def test_simple_svg_render():
    """Test rendering a simple flowchart to SVG."""
    script = """
    flowchart TD
        A[Start] --> B[End]
    """

    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
        output_path = f.name

    try:
        render(script, output_path, format='svg')

        # Check file exists and has content
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

        # Check it's valid SVG (basic check)
        content = Path(output_path).read_text()
        assert '<svg' in content
        assert '</svg>' in content

    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_simple_png_render():
    """Test rendering a simple flowchart to PNG."""
    script = """
    flowchart TD
        A[Start] --> B[End]
    """

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        output_path = f.name

    try:
        render(script, output_path, format='png', dpi=150)

        # Check file exists and has content
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

        # Check PNG signature
        with open(output_path, 'rb') as f:
            signature = f.read(8)
            assert signature == b'\x89PNG\r\n\x1a\n'

    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_complex_flowchart_svg():
    """Test rendering a complex flowchart with various shapes."""
    script = """
    flowchart TD
        A[Start] --> B{Decision}
        B -->|Yes| C(Rounded Action)
        B -->|No| D[Regular Action]
        C --> E((Circle))
        D --> E
        E --> F[End]
    """

    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
        output_path = f.name

    try:
        render(script, output_path, format='svg', roughness=1.5, seed=42)

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 1000  # Should be substantial

        content = Path(output_path).read_text()
        assert '<svg' in content
        # Should have multiple paths (for shapes)
        assert content.count('<path') > 5

    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_renderer_api():
    """Test the MermaidRenderer API."""
    script = """
    flowchart LR
        A[Input] --> B[Process]
        B --> C[Output]
    """

    renderer = MermaidRenderer(
        roughness=1.0,
        seed=123,
        background_color="white"
    )

    diagram = renderer.parse(script)
    assert len(diagram.diagram.nodes) == 3
    assert len(diagram.diagram.edges) == 2

    diagram.layout()

    # All nodes should have positions after layout
    for node in diagram.diagram.nodes:
        assert node.position is not None
        assert node.bbox is not None

    # Export to temp file
    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
        output_path = f.name

    try:
        diagram.export(output_path)
        assert os.path.exists(output_path)
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_example_file_render():
    """Test rendering from an example file."""
    example_path = Path(__file__).parent.parent / "examples" / "basic_flowchart.mmd"
    script = example_path.read_text()

    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
        output_path = f.name

    try:
        render(script, output_path, format='svg')
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_reproducible_with_seed():
    """Test that rendering with the same seed produces identical output."""
    script = """
    flowchart TD
        A --> B
        B --> C
    """

    renderer1 = MermaidRenderer(seed=42)
    renderer2 = MermaidRenderer(seed=42)

    diagram1 = renderer1.parse(script)
    diagram1.layout()

    diagram2 = renderer2.parse(script)
    diagram2.layout()

    # Nodes should have the same positions with same seed
    for node1, node2 in zip(diagram1.diagram.nodes, diagram2.diagram.nodes):
        assert node1.position.x == node2.position.x
        assert node1.position.y == node2.position.y
