# Claude Code Instructions

## Code Style

- Use single quotes for strings, not double quotes.
- But use triple double quotes for string blocks
- Import h3coco as: `import h3coco as coco`, then use `coco.function_name()`

## Testing

- Run tests using `just test`
- Always use `uv run` to run Python commands, never system `python3`
