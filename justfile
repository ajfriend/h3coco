export UV_NO_EDITABLE := "1"
export UV_OFFLINE := "0"  # toggle on when offline to avoid failures

lab:
    uv run jupyter lab

install:
    uv sync

test: purge
    uv run pytest

purge:
    just _rm .venv
    just _rm '*.pytest_cache'
    just _rm .DS_Store
    just _rm '*.egg-info'
    just _rm dist
    just _rm .claude
    just _rm '*.ipynb_checkpoints'
    just _rm __pycache__
    just _rm uv.lock
    uv cache clean h3coco

_rm pattern:
    -@find . -name "{{pattern}}" -prune -exec rm -rf {} +
