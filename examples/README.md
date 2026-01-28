# Example Diagrams

This directory contains example Mermaid flowcharts demonstrating various use cases and patterns.

## Examples

### Basic Examples

- **01_simple_workflow.mmd** - Simple workflow with decision point
- **13_basic_debug.mmd** - Basic debug loop pattern

### Business Process Examples

- **02_data_pipeline.mmd** - Data processing pipeline
- **03_authentication_flow.mmd** - User authentication flow
- **06_request_lifecycle.mmd** - HTTP request/response lifecycle
- **14_api_request.mmd** - Complex API request handling with error recovery
- **15_auth_flow.mmd** - User login authentication with permissions

### Architecture Examples

- **04_microservices.mmd** - Microservices architecture
- **05_ci_cd_pipeline.mmd** - CI/CD deployment pipeline
- **11_network_architecture.mmd** - Network infrastructure layout
- **12_event_driven.mmd** - Event-driven architecture

### Decision & Control Flow

- **07_decision_tree.mmd** - Multi-branch decision tree (order processing)
- **08_parallel_processing.mmd** - Parallel batch processing
- **09_error_handling.mmd** - Error handling with retry logic

### Machine Learning

- **10_ml_pipeline.mmd** - Machine learning pipeline with training loop

## Rendering Examples

To render any example:

```bash
# SVG output
python -m excelimermaid.cli examples/01_simple_workflow.mmd --output examples/01_simple_workflow.svg

# PNG output
python -m excelimermaid.cli examples/01_simple_workflow.mmd --output examples/01_simple_workflow.png

# Custom roughness
python -m excelimermaid.cli examples/01_simple_workflow.mmd --output output.svg --roughness 0.5
```

## Features Demonstrated

- **Shape variety**: Rectangles, diamonds (decision nodes), cylinders (databases), circles
- **Edge types**: Solid arrows, labeled edges, decision branches
- **Flow directions**: TD (top-down), LR (left-right)
- **Complex routing**: Obstacle avoidance, curved paths, feedback loops
- **Labels**: Edge labels for decision branches and conditions

All examples are rendered with:
- Adaptive arrow sizing based on path length
- Intelligent attachment point selection (closest edges)
- Flow-direction aware routing
- Smooth corner rounding for major turns
- Gentle curves on straight segments
