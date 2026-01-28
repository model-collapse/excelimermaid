"""Main renderer that coordinates parsing, layout, and drawing."""

from typing import Optional
from ..parser.mermaid_parser import MermaidParser
from ..layout.hierarchical import HierarchicalLayout
from ..graph.models import Diagram, RoutingConfig
from .rough_drawing import RoughDrawing


class RenderedDiagram:
    """
    A diagram that has been parsed and is ready for rendering/export.
    """

    def __init__(
        self,
        diagram: Diagram,
        layout_engine: HierarchicalLayout,
        rough_drawing: RoughDrawing
    ):
        """
        Initialize rendered diagram.

        Args:
            diagram: The parsed diagram
            layout_engine: Layout algorithm to use
            rough_drawing: Rough drawing engine for styling
        """
        self.diagram = diagram
        self.layout_engine = layout_engine
        self.rough_drawing = rough_drawing
        self._is_laid_out = False

    def layout(self, algorithm: str = "hierarchical") -> "RenderedDiagram":
        """
        Apply layout algorithm to position nodes.

        Args:
            algorithm: Layout algorithm name (default: "hierarchical")

        Returns:
            Self for method chaining
        """
        if algorithm == "hierarchical":
            self.diagram = self.layout_engine.layout(self.diagram)
        else:
            raise ValueError(f"Unknown layout algorithm: {algorithm}")

        self._is_laid_out = True
        return self

    def export(self, output_path: str, dpi: int = 300) -> None:
        """
        Export the diagram to a file.

        Args:
            output_path: Path to output file (.svg or .png)
            dpi: DPI for PNG output (ignored for SVG)

        Raises:
            ValueError: If diagram hasn't been laid out yet
        """
        if not self._is_laid_out:
            raise ValueError("Must call layout() before export()")

        # Determine format from extension
        if output_path.endswith('.svg'):
            self._export_svg(output_path)
        elif output_path.endswith('.png'):
            self._export_png(output_path, dpi)
        else:
            raise ValueError("Output path must end with .svg or .png")

    def _export_svg(self, output_path: str) -> None:
        """Export diagram to SVG format."""
        from ..export.svg_exporter import SVGExporter

        exporter = SVGExporter(self.rough_drawing)
        exporter.export(self.diagram, output_path)

    def _export_png(self, output_path: str, dpi: int) -> None:
        """Export diagram to PNG format."""
        from ..export.png_exporter import PNGExporter

        exporter = PNGExporter(self.rough_drawing)
        exporter.export(self.diagram, output_path, dpi)


class MermaidRenderer:
    """
    Main renderer for Mermaid flowcharts with Excalidraw styling.

    This class coordinates the entire rendering pipeline:
    1. Parse Mermaid syntax
    2. Build graph structure
    3. Apply layout
    4. Render with rough style
    5. Export to SVG/PNG

    Example:
        >>> renderer = MermaidRenderer(roughness=1.5)
        >>> diagram = renderer.parse("flowchart TD\\n    A --> B")
        >>> diagram.layout()
        >>> diagram.export("output.svg")
    """

    def __init__(
        self,
        roughness: float = 1.0,
        bowing: float = 1.0,
        seed: Optional[int] = None,
        background_color: str = "white",
        stroke_width: int = 2,
        font_family: str = "Virgil",
        font_size: int = 16,
        node_spacing: int = 80,
        rank_spacing: int = 100,
        # Hand-drawn style
        multi_stroke: bool = True,
        sketch_style: str = "heavy",
        # Routing configuration
        edge_routing: str = "curved",
        avoid_obstacles: bool = True,
        route_margin: float = 15.0,
        smoothness: float = 0.8,
        route_offset: float = 60.0,
        pathfinding_algorithm: str = "astar",
        pathfinding_cell_size: int = 10,
    ):
        """
        Initialize the Mermaid renderer.

        Args:
            roughness: Hand-drawn roughness level (0.0-2.0, default: 2.0)
            bowing: Line curvature (0.0-10.0)
            seed: Random seed for reproducibility
            background_color: Background color (default: "white")
            stroke_width: Base stroke width in pixels
            font_family: Font family for text (default: "Virgil")
            font_size: Font size in pixels
            node_spacing: Horizontal spacing between nodes
            rank_spacing: Vertical spacing between ranks
            multi_stroke: Draw shapes with multiple overlapping strokes (default: True)
            sketch_style: Style preset - "subtle", "standard", "heavy" (default: "heavy")
            edge_routing: Edge routing style - "curved" (default), "straight", or "orthogonal"
            avoid_obstacles: Enable automatic obstacle avoidance (default: True)
            route_margin: Margin around nodes for collision detection in pixels (default: 15.0)
            smoothness: Curve smoothness 0.0-1.0 (default: 0.8, higher = more rounded)
            route_offset: Distance to offset when routing around obstacles in pixels (default: 60.0)
            pathfinding_algorithm: Pathfinding algorithm - "astar" (default) or "heuristic"
            pathfinding_cell_size: Grid cell size for A* pathfinding in pixels (default: 10)
        """
        self.roughness = roughness
        self.bowing = bowing
        self.seed = seed
        self.background_color = background_color
        self.stroke_width = stroke_width
        self.font_family = font_family
        self.font_size = font_size

        # Create routing configuration
        self.routing_config = RoutingConfig(
            edge_routing=edge_routing,
            avoid_obstacles=avoid_obstacles,
            route_margin=route_margin,
            smoothness=smoothness,
            route_offset=route_offset,
            pathfinding_algorithm=pathfinding_algorithm,
            pathfinding_cell_size=pathfinding_cell_size
        )

        # Initialize components
        self.parser = MermaidParser()
        self.layout_engine = HierarchicalLayout(
            node_spacing=node_spacing,
            rank_spacing=rank_spacing,
            routing_config=self.routing_config
        )
        self.rough_drawing = RoughDrawing(
            roughness=roughness,
            bowing=bowing,
            seed=seed,
            multi_stroke=multi_stroke,
            sketch_style=sketch_style
        )

    def parse(self, mermaid_script: str) -> RenderedDiagram:
        """
        Parse a Mermaid script into a renderable diagram.

        Args:
            mermaid_script: Mermaid flowchart syntax

        Returns:
            RenderedDiagram that can be laid out and exported
        """
        diagram = self.parser.parse(mermaid_script)

        return RenderedDiagram(
            diagram=diagram,
            layout_engine=self.layout_engine,
            rough_drawing=self.rough_drawing
        )
