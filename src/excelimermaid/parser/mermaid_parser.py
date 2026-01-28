"""Mermaid flowchart parser using pyparsing."""

from typing import Dict, Any, Optional as OptionalType, Tuple
import re
import pyparsing as pp
from pyparsing import (
    Word, alphanums, alphas, Literal, Optional, ZeroOrMore,
    Suppress, Group, QuotedString, Regex, OneOrMore, LineEnd
)

from ..graph.models import (
    Node, Edge, Diagram, ShapeType, EdgeType, Direction
)


class MermaidParser:
    """
    Parser for Mermaid flowchart syntax.

    Supports:
    - Node definitions with various shapes
    - Edge connections with different arrow types
    - Edge labels
    - Flow directions (TD, LR, etc.)

    Example:
        >>> parser = MermaidParser()
        >>> diagram = parser.parse(\"\"\"
        ... flowchart TD
        ...     A[Start] --> B[End]
        ... \"\"\")
    """

    def __init__(self):
        """Initialize the parser with grammar rules."""
        self._setup_grammar()

    def _setup_grammar(self):
        """Set up pyparsing grammar for Mermaid flowcharts."""
        # TODO: Implement full grammar
        # Basic tokens
        self.identifier = Word(alphas + "_", alphanums + "_")

        # Node shapes - patterns to recognize different bracket types
        # [Text] - rectangle
        # (Text) - rounded rectangle
        # ((Text)) - circle
        # {Text} - diamond
        # etc.

        # Edge types - patterns for arrows
        # --> solid arrow
        # -.-> dotted arrow
        # ==> thick arrow
        # etc.

        # Direction
        self.direction = (
            Literal("TD") | Literal("TB") | Literal("LR") |
            Literal("RL") | Literal("BT")
        )

        # Flowchart declaration
        self.flowchart_decl = (
            Literal("flowchart") + self.direction
        )

    def parse(self, mermaid_script: str) -> Diagram:
        """
        Parse a Mermaid flowchart script into a Diagram object.

        Args:
            mermaid_script: Mermaid flowchart syntax as a string

        Returns:
            Diagram object with nodes and edges

        Raises:
            ParseException: If the script contains syntax errors
        """
        lines = mermaid_script.strip().split('\n')
        nodes_dict: Dict[str, Node] = {}
        edges_list = []
        direction = Direction.TOP_DOWN

        for line in lines:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('%%'):
                continue

            # Parse flowchart declaration
            if line.startswith('flowchart') or line.startswith('graph'):
                if 'TD' in line or 'TB' in line:
                    direction = Direction.TOP_DOWN
                elif 'LR' in line:
                    direction = Direction.LEFT_RIGHT
                elif 'RL' in line:
                    direction = Direction.RIGHT_LEFT
                elif 'BT' in line:
                    direction = Direction.BOTTOM_TOP
                continue

            # Try to parse as an edge
            edge_result = self._parse_edge(line)
            if edge_result:
                source_def, target_def, arrow_text, edge_type, label = edge_result

                # Parse source node
                source_id, source_text, source_shape = self._parse_node_shape(source_def)
                if source_id not in nodes_dict:
                    nodes_dict[source_id] = Node(
                        id=source_id,
                        text=source_text,
                        shape=source_shape
                    )

                # Parse target node
                target_id, target_text, target_shape = self._parse_node_shape(target_def)
                if target_id not in nodes_dict:
                    nodes_dict[target_id] = Node(
                        id=target_id,
                        text=target_text,
                        shape=target_shape
                    )

                # Create edge
                edge = Edge(
                    source=nodes_dict[source_id],
                    target=nodes_dict[target_id],
                    edge_type=edge_type,
                    label=label
                )
                edges_list.append(edge)

            else:
                # Try to parse as a standalone node definition
                # This handles cases like: A[Start]
                try:
                    node_id, text, shape = self._parse_node_shape(line)
                    if node_id and node_id not in nodes_dict:
                        nodes_dict[node_id] = Node(
                            id=node_id,
                            text=text,
                            shape=shape
                        )
                except Exception:
                    # Skip lines we can't parse
                    pass

        # Create diagram with parsed nodes and edges
        diagram = Diagram(
            nodes=list(nodes_dict.values()),
            edges=edges_list,
            direction=direction
        )

        return diagram

    def _parse_node_shape(self, node_def: str) -> Tuple[str, str, ShapeType]:
        """
        Parse a node definition to extract ID, text, and shape type.

        Examples:
            A[Text] -> ("A", "Text", ShapeType.RECTANGLE)
            B(Text) -> ("B", "Text", ShapeType.ROUNDED_RECTANGLE)
            C{Text} -> ("C", "Text", ShapeType.DIAMOND)

        Args:
            node_def: Node definition string

        Returns:
            Tuple of (node_id, text, shape_type)
        """
        node_def = node_def.strip()

        # Try different shape patterns
        patterns = [
            # ((Text)) - Circle
            (r'^(\w+)\(\((.*?)\)\)$', ShapeType.CIRCLE),
            # ([Text]) - Stadium
            (r'^(\w+)\(\[(.*?)\]\)$', ShapeType.STADIUM),
            # (Text) - Rounded rectangle
            (r'^(\w+)\((.*?)\)$', ShapeType.ROUNDED_RECTANGLE),
            # [[Text]] - Subroutine
            (r'^(\w+)\[\[(.*?)\]\]$', ShapeType.SUBROUTINE),
            # [(Text)] - Cylindrical/Database
            (r'^(\w+)\[\((.*?)\)\]$', ShapeType.CYLINDRICAL),
            # {{Text}} - Hexagon
            (r'^(\w+)\{\{(.*?)\}\}$', ShapeType.HEXAGON),
            # {Text} - Diamond
            (r'^(\w+)\{(.*?)\}$', ShapeType.DIAMOND),
            # [/Text/] - Parallelogram
            (r'^(\w+)\[/(.*?)/\]$', ShapeType.PARALLELOGRAM),
            # [\Text\] - Alt Parallelogram
            (r'^(\w+)\[\\(.*?)\\\]$', ShapeType.PARALLELOGRAM_ALT),
            # [/Text\] - Trapezoid
            (r'^(\w+)\[/(.*?)\\\]$', ShapeType.TRAPEZOID),
            # [\Text/] - Alt Trapezoid
            (r'^(\w+)\[\\(.*?)/\]$', ShapeType.TRAPEZOID_ALT),
            # [Text] - Rectangle (default)
            (r'^(\w+)\[(.*?)\]$', ShapeType.RECTANGLE),
        ]

        for pattern, shape_type in patterns:
            match = re.match(pattern, node_def)
            if match:
                node_id = match.group(1)
                text = match.group(2)
                return (node_id, text, shape_type)

        # If no match, treat as simple ID (bare node reference)
        return (node_def, node_def, ShapeType.RECTANGLE)

    def _parse_edge(self, line: str) -> OptionalType[Tuple[str, str, str, EdgeType, OptionalType[str]]]:
        """
        Parse an edge definition from a line.

        Examples:
            A --> B -> ("A", "B", "-->", EdgeType.SOLID_ARROW, None)
            A -->|Label| B -> ("A", "B", "-->", EdgeType.SOLID_ARROW, "Label")

        Args:
            line: Line containing edge definition

        Returns:
            Tuple of (source_node_def, target_node_def, arrow_text, edge_type, label) or None
        """
        # Edge patterns with labels
        edge_patterns = [
            # With labels: A -->|Label| B
            (r'(.+?)\s+(-->)\|([^|]+)\|\s+(.+)', EdgeType.SOLID_ARROW),
            (r'(.+?)\s+(-\.->)\|([^|]+)\|\s+(.+)', EdgeType.DOTTED_ARROW),
            (r'(.+?)\s+(==>)\|([^|]+)\|\s+(.+)', EdgeType.THICK_ARROW),
            (r'(.+?)\s+(---)\|([^|]+)\|\s+(.+)', EdgeType.SOLID_LINE),
            (r'(.+?)\s+(-\.-)\|([^|]+)\|\s+(.+)', EdgeType.DOTTED_LINE),
            (r'(.+?)\s+(===)\|([^|]+)\|\s+(.+)', EdgeType.THICK_LINE),

            # Without labels: A --> B
            (r'(.+?)\s+(-->)\s+(.+)', EdgeType.SOLID_ARROW),
            (r'(.+?)\s+(-\.->)\s+(.+)', EdgeType.DOTTED_ARROW),
            (r'(.+?)\s+(==>)\s+(.+)', EdgeType.THICK_ARROW),
            (r'(.+?)\s+(---)\s+(.+)', EdgeType.SOLID_LINE),
            (r'(.+?)\s+(-\.-)\s+(.+)', EdgeType.DOTTED_LINE),
            (r'(.+?)\s+(===)\s+(.+)', EdgeType.THICK_LINE),
        ]

        for pattern, edge_type in edge_patterns:
            match = re.match(pattern, line)
            if match:
                if len(match.groups()) == 4:  # With label
                    source, arrow, label, target = match.groups()
                    return (source.strip(), target.strip(), arrow, edge_type, label.strip())
                else:  # Without label
                    source, arrow, target = match.groups()
                    return (source.strip(), target.strip(), arrow, edge_type, None)

        return None
