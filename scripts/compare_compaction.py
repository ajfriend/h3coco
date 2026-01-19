#!/usr/bin/env python3
"""Compare h3.compact_cells vs coco.compact across US states."""

import h3
import pandas as pd
from tabulate import tabulate

import h3coco as coco


def compare_state(state: str, res: int) -> dict:
    """Compare compaction methods for a single state."""
    print(f'Processing {state}...', flush=True)
    cells = set(coco.cells_for_state(state, res))

    # h3 compact
    h3_compacted = h3.compact_cells(cells)
    h3_uncompacted = set(h3.uncompact_cells(h3_compacted, res))
    assert h3_uncompacted == cells, f'h3 round-trip failed for {state}'

    # coco compact
    coco_compacted = coco.compact(cells)
    coco_uncompacted = coco.uncompact(coco_compacted, res)
    assert coco_uncompacted == cells, f'coco round-trip failed for {state}'

    # Compute % reduction from h3 to coco
    h3_count = len(h3_compacted)
    coco_count = len(coco_compacted)
    reduction = (h3_count - coco_count) / h3_count * 100 if h3_count > 0 else 0

    return {
        'state': state,
        'resolution': res,
        'original': len(cells),
        'h3_compact': h3_count,
        'coco_compact': coco_count,
        'reduction': reduction,
    }


def generate_markdown_table(df: pd.DataFrame) -> str:
    """Generate a markdown table from DataFrame."""
    df = df.copy()
    df['reduction'] = df['reduction'].apply(lambda x: f'-{x:.1f}%' if x > 0 else '0%')
    return tabulate(
        df[['state', 'resolution', 'original', 'h3_compact', 'coco_compact', 'reduction']],
        headers=['State', 'Res', '# Cells', 'h3.compact', 'coco.compact', 'Reduction'],
        tablefmt='github',
        showindex=False,
        intfmt=',',
        colalign=('left', 'right', 'right', 'right', 'right', 'right'),
    )


RES = 6

results = [
    compare_state(state, RES)
    for state in coco.state_names()
]

df = pd.DataFrame(results)
df = df.sort_values('reduction', ascending=False)

print()
print(generate_markdown_table(df))
