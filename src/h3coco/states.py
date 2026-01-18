"""Functions for working with H3 cells and US states."""

import json
from importlib.resources import files

import h3


def _load_state_boundaries() -> dict:
    """Load US state boundary data from bundled GeoJSON."""
    data_file = files("h3coco.data").joinpath("us_states.json")
    return json.loads(data_file.read_text())


def _get_state_geometry(state: str) -> dict:
    """Get the GeoJSON geometry for a US state."""
    boundaries = _load_state_boundaries()
    state_lower = state.lower()

    for feature in boundaries['features']:
        name = feature['properties']['NAME']
        if name.lower() == state_lower:
            return feature['geometry']

    available = sorted(f['properties']['NAME'] for f in boundaries['features'])
    raise ValueError(f'Unknown state: {state!r}. Available: {available}')


def _geo_to_cells_safe(geometry: dict, resolution: int) -> set[str]:
    """Convert geometry to cells, handling MultiPolygons and degenerate polygons."""
    if geometry['type'] == 'Polygon':
        return h3.geo_to_cells(geometry, resolution)

    if geometry['type'] == 'MultiPolygon':
        cells = set()
        for poly_coords in geometry['coordinates']:
            single = {'type': 'Polygon', 'coordinates': poly_coords}
            try:
                cells.update(h3.geo_to_cells(single, resolution))
            except h3.H3FailedError:
                # Skip degenerate polygons
                pass
        return cells

    raise ValueError(f'Unsupported geometry type: {geometry["type"]}')


def cells_for_state(state: str, resolution: int) -> set[str]:
    """Return the set of H3 cells at the given resolution covering a US state.

    Args:
        state: US state name (e.g., "California", "Texas")
        resolution: H3 resolution (0-15)

    Returns:
        Set of H3 cell indices covering the state.
    """
    geometry = _get_state_geometry(state)
    return _geo_to_cells_safe(geometry, resolution)
