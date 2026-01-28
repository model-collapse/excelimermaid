"""High-level API for rendering Mermaid scripts."""

from typing import Optional, Literal
from pathlib import Path

from .renderer.excalidraw_renderer import MermaidRenderer


def render(
    mermaid_script: str,
    output_path: str,
    format: Literal["svg", "png"] = "svg",
    roughness: float = 1.0,
    seed: Optional[int] = None,
    dpi: int = 300,
    background_color: str = "white",
) -> None:
    """
    Render a Mermaid script to an output file.

    Args:
        mermaid_script: The Mermaid flowchart script as a string
        output_path: Path to the output file
        format: Output format, either "svg" or "png"
        roughness: Hand-drawn roughness level (0.0-2.0, default 1.0)
        seed: Random seed for reproducible output
        dpi: DPI for PNG output (default 300)
        background_color: Background color (default "white")

    Example:
        >>> render(
        ...     "flowchart TD\\n    A --> B",
        ...     "diagram.svg"
        ... )
    """
    renderer = MermaidRenderer(
        roughness=roughness,
        seed=seed,
        background_color=background_color,
    )

    diagram = renderer.parse(mermaid_script)
    diagram.layout()

    if format == "svg":
        diagram.export(output_path)
    elif format == "png":
        diagram.export(output_path, dpi=dpi)
    else:
        raise ValueError(f"Unsupported format: {format}")
