"""Functions for working with H3 cells and US states."""

from functools import cache
from importlib.resources import files

import geopandas as gpd
import h3


@cache
def load_states() -> gpd.GeoDataFrame:
    """Load US state boundaries as a GeoDataFrame."""
    path = files('h3coco.data').joinpath('us_states.json')
    return gpd.read_file(path)


def state_names() -> list[str]:
    """Return sorted list of available US state names."""
    return sorted(load_states()['NAME'].tolist())


def _geo_to_cells_safe(geometry, resolution: int) -> set[str]:
    """Convert geometry to cells, handling MultiPolygons and degenerate polygons."""
    geo = geometry.__geo_interface__

    if geo['type'] == 'Polygon':
        return h3.geo_to_cells(geo, resolution)

    if geo['type'] == 'MultiPolygon':
        cells = set()
        for poly_coords in geo['coordinates']:
            single = {'type': 'Polygon', 'coordinates': poly_coords}
            try:
                cells.update(h3.geo_to_cells(single, resolution))
            except h3.H3FailedError:
                # Skip degenerate polygons
                pass
        return cells

    raise ValueError(f'Unsupported geometry type: {geo["type"]}')


def cells_for_state(state: str, resolution: int) -> set[str]:
    """Return the set of H3 cells at the given resolution covering a US state.

    Args:
        state: US state name (e.g., 'California', 'Texas')
        resolution: H3 resolution (0-15)

    Returns:
        Set of H3 cell indices covering the state.
    """
    gdf = load_states()
    matches = gdf[gdf['NAME'].str.lower() == state.lower()]

    if matches.empty:
        raise ValueError(f'Unknown state: {state!r}. Available: {state_names()}')

    return _geo_to_cells_safe(matches.iloc[0].geometry, resolution)
