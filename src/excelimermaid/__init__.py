"""
Exceli-Mermaid: Offline Python engine for rendering Mermaid flowcharts with Excalidraw style.

This package provides tools to parse Mermaid flowchart syntax and render them
with a hand-drawn, sketchy aesthetic inspired by Excalidraw.
"""

__version__ = "0.1.0"

from .renderer.excalidraw_renderer import MermaidRenderer
from .api import render

__all__ = ["MermaidRenderer", "render", "__version__"]
