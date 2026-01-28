# Implementation Guide

This document outlines the steps to complete the Exceli-Mermaid implementation.

## Current Status

✅ **Completed**:
- Project structure and directory layout
- Core data models (Node, Edge, Diagram, Point, etc.)
- Rough drawing algorithms (hand-drawn style)
- Base layout engine interface
- Hierarchical layout stub using grandalf
- SVG and PNG exporter stubs
- CLI interface
- Example Mermaid files
- Test infrastructure

⚠️ **Needs Implementation**:
1. Mermaid parser (pyparsing grammar)
2. Complete layout engine
3. Font bundling (Virgil font)
4. Additional shape types
5. Comprehensive tests

## Implementation Order

### Phase 1: Parser Implementation (High Priority)

The parser is the foundation. Implement in `src/excelimermaid/parser/mermaid_parser.py`.

**Tasks**:
1. Define pyparsing grammar for:
   - Node shapes: `[Text]`, `(Text)`, `{Text}`, etc.
   - Edge types: `-->`, `.->`, `==>`, etc.
   - Edge labels: `-->|Label|`
   - Comments: `%%`

2. Implement shape type detection:
   ```python
   def _parse_node_shape(self, node_def: str) -> tuple[str, str, ShapeType]:
       # Match patterns like:
       # A[Text] -> rectangle
       # B(Text) -> rounded
       # C{Text} -> diamond
   ```

3. Implement edge parsing:
   ```python
   def _parse_edge(self, edge_def: str) -> tuple[str, str, EdgeType, str | None]:
       # Parse: A -->|Label| B
       # Return: ("A", "B", EdgeType.SOLID_ARROW, "Label")
   ```

4. Build complete `parse()` method that:
   - Parses line by line
   - Builds node dictionary
   - Creates edge list
   - Returns Diagram object

**Test with**:
```python
parser = MermaidParser()
diagram = parser.parse("""
flowchart TD
    A[Start] --> B[End]
""")
assert len(diagram.nodes) == 2
assert len(diagram.edges) == 1
```

### Phase 2: Layout Completion (High Priority)

Complete the hierarchical layout in `src/excelimermaid/layout/hierarchical.py`.

**Tasks**:
1. Verify grandalf integration works correctly
2. Test with simple graphs
3. Adjust node spacing and rank spacing
4. Implement edge routing (currently just straight lines)
5. Handle edge cases (cycles, disconnected components)

**Test with**:
```python
layout = HierarchicalLayout()
diagram = layout.layout(diagram)
# Verify all nodes have positions
assert all(node.position is not None for node in diagram.nodes)
```

### Phase 3: Font Integration (Medium Priority)

Bundle Virgil font for hand-drawn text appearance.

**Tasks**:
1. Download Virgil font (from Excalidraw repo or find alternative)
   - URL: https://github.com/excalidraw/excalidraw/tree/master/public/fonts
   - Files: Virgil.woff2, Virgil.ttf

2. Add fonts to `src/excelimermaid/fonts/`

3. Update SVG exporter to:
   - Embed font in SVG or
   - Use @font-face with data URI

4. Verify license compatibility (Virgil is likely OFL/MIT)

### Phase 4: Shape Completion (Medium Priority)

Implement remaining shapes in `rough_drawing.py` and `svg_exporter.py`.

**Shapes to implement**:
- Rounded rectangle
- Stadium/Pill shape
- Subroutine (rectangle with double border)
- Cylindrical (database)
- Hexagon
- Parallelogram variants
- Trapezoid variants

**Pattern**:
```python
def rough_rounded_rectangle(self, x, y, width, height, radius=10):
    # Create path with rounded corners
    # Add roughness to each segment
    pass
```

### Phase 5: Testing (Ongoing)

Write comprehensive tests in `tests/`.

**Test files needed**:
- `test_parser.py`: Parser with various Mermaid syntax
- `test_layout.py`: Layout algorithms
- `test_renderer.py`: Rough drawing generation
- `test_exporters.py`: SVG and PNG export
- `test_integration.py`: End-to-end tests

**Example integration test**:
```python
def test_end_to_end():
    script = """
    flowchart TD
        A[Start] --> B[End]
    """
    renderer = MermaidRenderer()
    diagram = renderer.parse(script)
    diagram.layout()

    # Export to temp file
    with tempfile.NamedTemporaryFile(suffix='.svg') as f:
        diagram.export(f.name)
        # Verify file exists and has content
        assert os.path.exists(f.name)
        assert os.path.getsize(f.name) > 0
```

### Phase 6: Documentation (Low Priority)

1. Add docstrings to all public methods
2. Create usage examples in `examples/`
3. Add tutorial to README
4. Create API reference documentation

## Quick Start for Development

### 1. Set up environment
```bash
cd /home/ubuntu/excelimermaid
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 2. Run tests
```bash
pytest
```

### 3. Test CLI
```bash
excelimermaid examples/basic_flowchart.mmd -o test_output.svg
```

### 4. Development workflow
1. Pick a task from Phase 1-6
2. Write tests first (TDD)
3. Implement the feature
4. Run tests
5. Commit changes

## Implementation Tips

### Parser Implementation
- Start with simple cases (rectangle nodes, solid arrows)
- Use pyparsing's debugging: `parser.setDebug()`
- Test incrementally with `parser.parseString()`

### Layout Implementation
- Use NetworkX for graph analysis
- Test with small graphs first (2-3 nodes)
- Visualize intermediate steps for debugging

### Rendering
- Test rough drawing with simple shapes first
- Adjust roughness parameters to match Excalidraw
- Use reproducible seeds for consistent output

### Font Handling
- Start with system fonts as fallback
- Add Virgil font later for polish
- Test on different platforms

## Performance Targets

- Parse 100-line Mermaid script: < 100ms
- Layout 50-node graph: < 2 seconds
- Render to SVG: < 1 second
- Convert SVG to PNG: < 3 seconds

## Known Limitations

Current implementation is MVP focused on:
- Flowchart diagrams only
- Basic shapes (rectangle, circle, diamond)
- Simple edges (solid, dotted, thick)

Not yet supported:
- Subgraphs
- Custom styling/colors
- Other diagram types (sequence, class, etc.)
- Interactive features

## Troubleshooting

### Import errors
```bash
# Ensure package is installed in development mode
pip install -e .
```

### Parser errors
```python
# Enable debug mode
parser = MermaidParser()
parser.parser.setDebug(True)
```

### Layout issues
```python
# Visualize graph structure
import networkx as nx
G = layout._build_networkx_graph(diagram)
nx.draw(G, with_labels=True)
```

## Next Steps

1. **Start with Phase 1 (Parser)**: This is the critical path
2. **Validate with examples**: Use `examples/*.mmd` files for testing
3. **Iterate on quality**: Adjust roughness, spacing, fonts
4. **Add more shapes**: Expand shape library as needed
5. **Optimize performance**: Profile and optimize bottlenecks

## Resources

- **Mermaid.js docs**: https://mermaid.js.org/
- **Pyparsing docs**: https://pyparsing-docs.readthedocs.io/
- **Rough.js algorithm**: https://github.com/rough-stuff/rough/wiki/Algorithms
- **Excalidraw repo**: https://github.com/excalidraw/excalidraw
- **Grandalf docs**: https://github.com/bdcht/grandalf
