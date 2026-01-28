# Excelimermaid CLI Quick Reference

## Most Common Commands

### 1. Basic Render (A* enabled by default)
```bash
excelimermaid diagram.mmd -o output.svg
```

### 2. Orthogonal Routing with A* (Best for test_crossing.mmd)
```bash
excelimermaid test_crossing.mmd -o output.svg --edge-routing orthogonal
```

### 3. Custom A* Settings
```bash
excelimermaid diagram.mmd -o output.svg \
    --edge-routing orthogonal \
    --pathfinding-algorithm astar \
    --route-offset 100
```

### 4. Adjust Hand-Drawn Style
```bash
# Subtle style (minimal hand-drawn)
excelimermaid diagram.mmd -o output.svg --sketch-style subtle --roughness 0.7

# Standard style (balanced)
excelimermaid diagram.mmd -o output.svg --sketch-style standard --roughness 1.0

# Heavy style (maximum, default)
excelimermaid diagram.mmd -o output.svg --sketch-style heavy --roughness 2.0
```

### 5. Heuristic Algorithm (Faster)
```bash
excelimermaid large_diagram.mmd -o output.svg --pathfinding-algorithm heuristic
```

### 6. Disable Obstacle Avoidance
```bash
excelimermaid diagram.mmd -o output.svg --no-avoid-obstacles
```

### 7. Multiple Formats
```bash
excelimermaid diagram.mmd -o output --formats svg,png
```

### 8. High-DPI PNG
```bash
excelimermaid diagram.mmd -o output.png --dpi 600
```

## Key Options

| Option | Common Values | Description |
|--------|--------------|-------------|
| `--edge-routing` | `orthogonal`, `curved`, `straight` | Routing style |
| `--pathfinding-algorithm` | `astar`, `heuristic` | Pathfinding method |
| `--sketch-style` | `subtle`, `standard`, `heavy` | Hand-drawn preset |
| `--roughness` | `0.7` (subtle), `1.0` (standard), `2.0` (heavy) | Roughness level |
| `--route-offset` | `60-120` | Distance around obstacles |
| `--smoothness` | `0.6-0.9` | Curve smoothness |
| `--seed` | Any integer | For reproducibility |

## Use Cases

| Task | Command |
|------|---------|
| **Long crossing edges** | `--edge-routing orthogonal --route-offset 100` |
| **Artistic diagrams** | `--edge-routing curved --smoothness 0.9 --sketch-style heavy` |
| **Technical docs** | `--edge-routing orthogonal --sketch-style subtle --roughness 0.7` |
| **Large diagrams** | `--pathfinding-algorithm heuristic` |
| **Reproducible output** | `--seed 42` |

## Installation

```bash
# Install in development mode
cd excelimermaid
pip install -e .

# Use the command
excelimermaid --help
```

## Full Help

```bash
excelimermaid --help
```
