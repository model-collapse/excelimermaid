"""Command-line interface for Exceli-Mermaid."""

import click
import logging
from pathlib import Path
from typing import Optional

from . import MermaidRenderer, __version__


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '-o', '--output',
    type=click.Path(path_type=Path),
    required=True,
    help='Output file path (.svg or .png)'
)
@click.option(
    '--formats',
    type=str,
    default=None,
    help='Comma-separated list of formats (e.g., "svg,png"). Requires -o without extension.'
)
@click.option(
    '--roughness',
    type=float,
    default=2.0,
    help='Hand-drawn roughness level (0.0-2.0, default: 2.0)'
)
@click.option(
    '--bowing',
    type=float,
    default=1.0,
    help='Line curvature/bowing (0.0-10.0, default: 1.0)'
)
@click.option(
    '--seed',
    type=int,
    default=None,
    help='Random seed for reproducibility'
)
@click.option(
    '--dpi',
    type=int,
    default=300,
    help='DPI for PNG output (default: 300)'
)
@click.option(
    '--background',
    type=str,
    default='white',
    help='Background color (default: white)'
)
@click.option(
    '--node-spacing',
    type=int,
    default=80,
    help='Horizontal spacing between nodes (default: 80)'
)
@click.option(
    '--rank-spacing',
    type=int,
    default=100,
    help='Vertical spacing between ranks (default: 100)'
)
@click.option(
    '--edge-routing',
    type=click.Choice(['curved', 'straight', 'orthogonal'], case_sensitive=False),
    default='curved',
    help='Edge routing style (default: curved)'
)
@click.option(
    '--no-avoid-obstacles',
    is_flag=True,
    default=False,
    help='Disable automatic obstacle avoidance for edges'
)
@click.option(
    '--route-margin',
    type=float,
    default=15.0,
    help='Margin around nodes for collision detection in pixels (default: 15.0)'
)
@click.option(
    '--smoothness',
    type=float,
    default=0.8,
    help='Curve smoothness 0.0-1.0 (default: 0.8, higher = more rounded)'
)
@click.option(
    '--route-offset',
    type=float,
    default=60.0,
    help='Distance to offset when routing around obstacles in pixels (default: 60.0)'
)
@click.option(
    '--pathfinding-algorithm',
    type=click.Choice(['astar', 'heuristic'], case_sensitive=False),
    default='astar',
    help='Pathfinding algorithm for obstacle avoidance (default: astar)'
)
@click.option(
    '--pathfinding-cell-size',
    type=int,
    default=10,
    help='Grid cell size for A* pathfinding in pixels (default: 10)'
)
@click.option(
    '--sketch-style',
    type=click.Choice(['subtle', 'standard', 'heavy'], case_sensitive=False),
    default='heavy',
    help='Hand-drawn style preset (default: heavy)'
)
@click.option(
    '--no-multi-stroke',
    is_flag=True,
    default=False,
    help='Disable multi-stroke drawing (use single stroke per shape)'
)
@click.option(
    '--log-level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False),
    default=None,
    help='Enable logging at specified level (shows pathfinding progress and failures)'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    default=False,
    help='Enable INFO level logging (shortcut for --log-level INFO)'
)
@click.option(
    '--debug',
    is_flag=True,
    default=False,
    help='Enable DEBUG level logging (shortcut for --log-level DEBUG)'
)
@click.version_option(version=__version__)
def main(
    input_file: Path,
    output: Path,
    formats: Optional[str],
    roughness: float,
    bowing: float,
    seed: Optional[int],
    dpi: int,
    background: str,
    node_spacing: int,
    rank_spacing: int,
    edge_routing: str,
    no_avoid_obstacles: bool,
    route_margin: float,
    smoothness: float,
    route_offset: float,
    pathfinding_algorithm: str,
    pathfinding_cell_size: int,
    sketch_style: str,
    no_multi_stroke: bool,
    log_level: Optional[str],
    verbose: bool,
    debug: bool
):
    """
    Render Mermaid flowcharts with Excalidraw style.

    INPUT_FILE: Path to Mermaid (.mmd) file

    Examples:

        # Render to SVG (uses A* pathfinding by default)
        excelimermaid diagram.mmd -o output.svg

        # Render to PNG with high DPI
        excelimermaid diagram.mmd -o output.png --dpi 300

        # Render to both formats
        excelimermaid diagram.mmd -o output --formats svg,png

        # Adjust hand-drawn style
        excelimermaid diagram.mmd -o output.svg --roughness 2.0 --seed 42

        # Use orthogonal routing with A* pathfinding (recommended for obstacle avoidance)
        excelimermaid diagram.mmd -o output.svg --edge-routing orthogonal

        # Customize A* pathfinding
        excelimermaid diagram.mmd -o output.svg --pathfinding-algorithm astar --pathfinding-cell-size 10

        # Use heuristic pathfinding (faster but less optimal)
        excelimermaid diagram.mmd -o output.svg --pathfinding-algorithm heuristic

        # Disable obstacle avoidance (direct lines)
        excelimermaid diagram.mmd -o output.svg --no-avoid-obstacles

        # Customize routing behavior
        excelimermaid diagram.mmd -o output.svg --smoothness 0.8 --route-offset 80

        # Change hand-drawn style preset
        excelimermaid diagram.mmd -o output.svg --sketch-style subtle
        excelimermaid diagram.mmd -o output.svg --sketch-style standard
        excelimermaid diagram.mmd -o output.svg --sketch-style heavy

        # Enable logging (see pathfinding progress and failures)
        excelimermaid diagram.mmd -o output.svg --verbose
        excelimermaid diagram.mmd -o output.svg --debug
        excelimermaid diagram.mmd -o output.svg --log-level INFO
    """
    # Configure logging if requested
    if debug:
        log_level = 'DEBUG'
    elif verbose:
        log_level = 'INFO'

    if log_level:
        level = getattr(logging, log_level.upper())
        logging.basicConfig(
            level=level,
            format='%(levelname)s: %(message)s'
        )
        # Enable detailed pathfinding logs
        logging.getLogger('excelimermaid.layout.pathfinding_v2').setLevel(level)
        click.echo(f"Logging enabled at {log_level} level", err=True)
    else:
        # Disable all logging by default (set to CRITICAL to suppress everything)
        logging.basicConfig(level=logging.CRITICAL)
        logging.getLogger('excelimermaid').setLevel(logging.CRITICAL)

    try:
        # Read input file
        mermaid_script = input_file.read_text(encoding='utf-8')

        # Create renderer
        renderer = MermaidRenderer(
            roughness=roughness,
            bowing=bowing,
            seed=seed,
            background_color=background,
            node_spacing=node_spacing,
            rank_spacing=rank_spacing,
            edge_routing=edge_routing,
            avoid_obstacles=not no_avoid_obstacles,
            route_margin=route_margin,
            smoothness=smoothness,
            route_offset=route_offset,
            pathfinding_algorithm=pathfinding_algorithm,
            pathfinding_cell_size=pathfinding_cell_size,
            sketch_style=sketch_style,
            multi_stroke=not no_multi_stroke
        )

        # Parse and layout
        click.echo("Parsing Mermaid script...")
        diagram = renderer.parse(mermaid_script)

        click.echo("Applying layout...")
        diagram.layout()

        # Handle multiple formats
        if formats:
            format_list = [f.strip().lower() for f in formats.split(',')]
            base_path = output
            for fmt in format_list:
                if fmt not in ['svg', 'png']:
                    raise click.BadParameter(f"Unsupported format: {fmt}")

                output_path = base_path.with_suffix(f'.{fmt}')
                click.echo(f"Rendering {fmt.upper()}...")
                if fmt == 'png':
                    diagram.export(str(output_path), dpi=dpi)
                else:
                    diagram.export(str(output_path))
                click.echo(f"✓ Saved to {output_path}")
        else:
            # Single format based on extension
            if not output.suffix:
                raise click.BadParameter("Output path must have .svg or .png extension")

            fmt = output.suffix.lstrip('.')
            click.echo(f"Rendering {fmt.upper()}...")

            if fmt == 'png':
                diagram.export(str(output), dpi=dpi)
            elif fmt == 'svg':
                diagram.export(str(output))
            else:
                raise click.BadParameter(f"Unsupported format: {fmt}")

            click.echo(f"✓ Saved to {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()
