#!/usr/bin/env python3
"""Compare h3.compact_cells vs coco.compact across US states."""

import argparse
import json
from importlib.resources import files

import h3
import pandas as pd
from tabulate import tabulate

import h3coco as coco


def get_state_names():
    """Get list of US state names from the GeoJSON data."""
    data = files('h3coco.data').joinpath('us_states.json').read_text()
    geojson = json.loads(data)
    return sorted(f['properties']['NAME'] for f in geojson['features'])


def compare_state(state: str, res: int) -> dict:
    """Compare compaction methods for a single state."""
    # Get cells for state (convert to set for comparison)
    cells = set(coco.cells_for_state(state, res))
    original_count = len(cells)

    # h3 compact
    h3_compacted = h3.compact_cells(cells)
    h3_count = len(h3_compacted)

    # Verify h3 round-trip
    h3_uncompacted = set(h3.uncompact_cells(h3_compacted, res))
    assert h3_uncompacted == cells, f'h3 round-trip failed for {state}'

    # coco compact
    coco_compacted = coco.compact(cells)
    coco_count = len(coco_compacted)

    # Verify coco round-trip
    coco_uncompacted = coco.uncompact(coco_compacted, res)
    assert coco_uncompacted == cells, f'coco round-trip failed for {state}'

    # Compute % reduction from h3 to coco
    reduction = (h3_count - coco_count) / h3_count * 100 if h3_count > 0 else 0

    return {
        'resolution': res,
        'state': state,
        'original': original_count,
        'h3_compact': h3_count,
        'coco_compact': coco_count,
        'reduction': reduction,
    }


def generate_markdown_table(df: pd.DataFrame) -> str:
    """Generate a markdown table from DataFrame."""
    df = df.copy()
    df['reduction'] = df['reduction'].apply(lambda x: f'-{x:.1f}%' if x > 0 else '0%')
    table = tabulate(
        df[['state', 'resolution', 'original', 'h3_compact', 'coco_compact', 'reduction']],
        headers=['State', 'Res', '# Cells', 'h3.compact', 'coco.compact', 'Reduction'],
        tablefmt='github',
        showindex=False,
        intfmt=',',
        colalign=('left', 'right', 'right', 'right', 'right', 'right'),
    )
    return table


def main():
    parser = argparse.ArgumentParser(description='Compare H3 compaction methods')
    parser.add_argument('--res', type=int, default=6, help='H3 resolution (default: 6)')
    args = parser.parse_args()

    states = get_state_names()
    results = []

    for state in states:
        print(f'Processing {state}...', flush=True)
        try:
            result = compare_state(state, args.res)
            results.append(result)
        except Exception as e:
            print(f'  Error: {e}')

    df = pd.DataFrame(results)
    df = df.sort_values('reduction', ascending=False)

    print()
    print(generate_markdown_table(df))


if __name__ == '__main__':
    main()
