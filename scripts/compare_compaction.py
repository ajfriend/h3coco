"""Compare h3.compact_cells vs coco.compact across US states."""

import h3
from tabulate import tabulate

import h3coco as coco


def get_state_names():
    """Get list of US state names from the GeoJSON data."""
    import json
    from importlib.resources import files

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

    # Compute improvement ratio
    ratio = h3_count / coco_count if coco_count > 0 else 0

    return {
        'state': state,
        'original': original_count,
        'h3': h3_count,
        'coco': coco_count,
        'ratio': ratio,
    }


def generate_markdown_table(results: list[dict], res: int) -> str:
    """Generate a markdown table from results."""
    # Build table data
    headers = ['State', 'Original', 'h3.compact', 'coco.compact', 'Ratio']
    rows = [
        [r['state'], f"{r['original']:,}", f"{r['h3']:,}", f"{r['coco']:,}", f"{r['ratio']:.2f}x"]
        for r in results
    ]

    # Add totals
    total_original = sum(r['original'] for r in results)
    total_h3 = sum(r['h3'] for r in results)
    total_coco = sum(r['coco'] for r in results)
    total_ratio = total_h3 / total_coco if total_coco > 0 else 0
    rows.append(['**Total**', f'**{total_original:,}**', f'**{total_h3:,}**', f'**{total_coco:,}**', f'**{total_ratio:.2f}x**'])

    table = tabulate(rows, headers=headers, tablefmt='github', colalign=('left', 'right', 'right', 'right', 'right'))
    return f'## Compaction comparison at resolution {res}\n\n{table}'



RES = 6

states = get_state_names()
results = []

for state in states:
    print(f'Processing {state}...', flush=True)
    try:
        result = compare_state(state, RES)
        results.append(result)
    except Exception as e:
        print(f'  Error: {e}')

# Sort by ratio descending
results.sort(key=lambda r: r['ratio'], reverse=True)

print()
print(generate_markdown_table(results, RES))

