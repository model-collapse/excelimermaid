# Summary: Logging Integrated into CLI

## What Was Done

Integrated logging options directly into the main `excelimermaid` CLI command instead of just test scripts.

## Changes Made

### File Modified
**`src/excelimermaid/cli.py`**

### Added CLI Options

1. **`--log-level LEVEL`** - Set logging level (DEBUG, INFO, WARNING, ERROR)
2. **`--verbose` / `-v`** - Enable INFO logging (shortcut)
3. **`--debug`** - Enable DEBUG logging (shortcut)

### Implementation

```python
# Added logging configuration at start of main()
if debug:
    log_level = 'DEBUG'
elif verbose:
    log_level = 'INFO'

if log_level:
    # Enable logging at requested level
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    logging.getLogger('excelimermaid.layout.pathfinding_v2').setLevel(level)
else:
    # Disable logging by default (silent)
    logging.basicConfig(level=logging.CRITICAL)
    logging.getLogger('excelimermaid').setLevel(logging.CRITICAL)
```

## Usage

### Silent (Default)
```bash
excelimermaid diagram.mmd -o output.svg
```
Clean output, no logging.

### Verbose
```bash
excelimermaid diagram.mmd -o output.svg --verbose
# or
excelimermaid diagram.mmd -o output.svg -v
```
Shows pathfinding progress, failures, retries.

### Debug
```bash
excelimermaid diagram.mmd -o output.svg --debug
```
Shows all details including per-edge routing.

## Examples

### Example 1: Silent Rendering
```bash
$ excelimermaid test_crossing.mmd -o output.svg
Parsing Mermaid script...
Applying layout...
Rendering SVG...
✓ Saved to output.svg
```

### Example 2: Verbose Rendering
```bash
$ excelimermaid test_crossing.mmd -o output.svg --verbose
Logging enabled at INFO level
Parsing Mermaid script...
Applying layout...
INFO: Starting adaptive A* pathfinding for 10 edges, 8 nodes
INFO: Adaptive parameters: margin=16.9px, cell_size=16px, grid=44x32
WARNING: A* pathfinding FAILED: [E → G] No path found...
WARNING: A* pathfinding FAILED: [A → C] No path found...
INFO: [E → H] Retry with smaller cells SUCCEEDED: Found path with 4 waypoints
INFO: Adaptive A* pathfinding complete: 10 edges routed successfully
✓ Saved to output.svg
```

### Example 3: Debug Rendering
```bash
$ excelimermaid test_crossing.mmd -o output.svg --debug
Logging enabled at DEBUG level
...
DEBUG: [1/10] Routing edge E → G (length=80.0px)
DEBUG: [1/10] Edge E → G routed: 2 waypoints
DEBUG: [2/10] Routing edge C → E (length=101.2px)
...
```

## Help Output

```bash
$ excelimermaid --help
...
  --log-level [debug|info|warning|error]
                                  Enable logging at specified level (shows
                                  pathfinding progress and failures)
  -v, --verbose                   Enable INFO level logging (shortcut for
                                  --log-level INFO)
  --debug                         Enable DEBUG level logging (shortcut for
                                  --log-level DEBUG)
...
```

## Key Features

✅ **Silent by default** - Clean output, no clutter
✅ **Easy to enable** - Single flag (`--verbose` or `--debug`)
✅ **Node IDs included** - All failures show `[source → target]`
✅ **Three log levels** - Silent, INFO, DEBUG
✅ **Easy to filter** - Pipe to grep, save to file
✅ **No performance impact** - Logging only when requested
✅ **Backward compatible** - All existing commands work

## Common Use Cases

### Debug Routing Issues
```bash
# See which edges fail
excelimermaid diagram.mmd -o output.svg --verbose 2>&1 | grep FAILED

# Find problem nodes
excelimermaid diagram.mmd -o output.svg --verbose 2>&1 | grep FAILED | sed 's/.*\[\(.*\) →.*/\1/' | sort | uniq -c
```

### Save Logs
```bash
# Save to file
excelimermaid diagram.mmd -o output.svg --verbose 2>&1 | tee render.log

# Save only errors
excelimermaid diagram.mmd -o output.svg --verbose 2>&1 | grep WARNING > errors.log
```

### CI/CD Integration
```bash
# Check for failures in CI
if excelimermaid diagram.mmd -o output.svg --verbose 2>&1 | grep -q FAILED; then
    echo "Some edges failed routing"
    exit 1
fi
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v
```
✅ All 35 tests passing

## Documentation

- **`CLI_LOGGING.md`** - Comprehensive guide with examples
- **`CLI_LOGGING_SUMMARY.md`** - This summary

## Comparison: Before vs After

### Before (Test Scripts Only)
```python
# Had to write custom Python script
import logging
logging.basicConfig(level=logging.INFO)
from excelimermaid import MermaidRenderer
renderer = MermaidRenderer()
# ... rest of code
```

### After (CLI Integration)
```bash
# Just add a flag!
excelimermaid diagram.mmd -o output.svg --verbose
```

## Benefits

1. **No scripting needed** - Just add `--verbose` or `--debug`
2. **Immediate feedback** - See pathfinding issues in real-time
3. **Easy debugging** - Node IDs in all messages
4. **Production ready** - Silent by default, enable when needed
5. **Script friendly** - Easy to pipe/grep/filter output
6. **CI/CD ready** - Perfect for automated pipelines

## Summary

**Request:** "logging should be with the main CLI"

**Delivered:**
- ✅ Added `--verbose`, `--debug`, `--log-level` to CLI
- ✅ Silent by default (no output clutter)
- ✅ Shows node IDs in all failure messages
- ✅ Easy to use (`--verbose` or `-v`)
- ✅ Comprehensive documentation
- ✅ All tests passing

**Result:** Logging fully integrated into CLI - just add `--verbose` to any command!

## Quick Reference

```bash
# Silent (default)
excelimermaid diagram.mmd -o output.svg

# Verbose (INFO)
excelimermaid diagram.mmd -o output.svg --verbose
excelimermaid diagram.mmd -o output.svg -v

# Debug (DEBUG)
excelimermaid diagram.mmd -o output.svg --debug

# Custom level
excelimermaid diagram.mmd -o output.svg --log-level WARNING
```

Done! Logging is now fully integrated into the main CLI. ✅
