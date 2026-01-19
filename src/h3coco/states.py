"""Functions for working with H3 cells and US states."""

from functools import cache
from importlib.resources import files

import geopandas as gpd
import h3


@cache
def load_states() -> gpd.GeoDataFrame:
    """Load US state boundaries as a GeoDataFrame."""
    path = files('h3coco.data').joinpath('us_states.json')
    gdf = gpd.read_file(path)
    # buffer(0) cleans up degenerate polygons that cause h3 to fail
    gdf['geometry'] = gdf['geometry'].buffer(0)
    return gdf


def state_names() -> list[str]:
    """Return sorted list of available US state names."""
    return sorted(load_states()['NAME'].tolist())


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

    geometry = matches.iloc[0].geometry
    return h3.geo_to_cells(geometry.__geo_interface__, resolution)
