"""PNG export functionality."""

import os
import tempfile
from pathlib import Path
import cairosvg
from ..graph.models import Diagram
from ..renderer.rough_drawing import RoughDrawing
from .svg_exporter import SVGExporter


class PNGExporter:
    """
    Exports diagrams to PNG format.

    The implementation works by first generating SVG,
    then converting to PNG using cairosvg.
    """

    def __init__(self, rough_drawing: RoughDrawing):
        """
        Initialize PNG exporter.

        Args:
            rough_drawing: Rough drawing engine for rendering shapes
        """
        self.rough = rough_drawing
        self.svg_exporter = SVGExporter(rough_drawing)

    def export(self, diagram: Diagram, output_path: str, dpi: int = 300) -> None:
        """
        Export diagram to PNG file.

        Args:
            diagram: The diagram to export
            output_path: Path to output PNG file
            dpi: DPI for the PNG output (default 300 for high quality)
        """
        # Create temporary SVG file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.svg',
            delete=False
        ) as temp_svg:
            temp_svg_path = temp_svg.name

        try:
            # Generate SVG
            self.svg_exporter.export(diagram, temp_svg_path)

            # Convert SVG to PNG using cairosvg
            # Scale factor based on DPI (96 DPI is the SVG default)
            scale = dpi / 96.0

            cairosvg.svg2png(
                url=temp_svg_path,
                write_to=output_path,
                scale=scale
            )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_svg_path):
                os.unlink(temp_svg_path)
