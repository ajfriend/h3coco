"""Plotting functions for H3 cells."""

import h3
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

from h3coco.states import load_states


def plot_state(state, ax=None, **kwargs):
    """Plot the raw boundary polygon for a US state.

    Args:
        state: US state name (e.g., 'California', 'Texas')
        ax: Matplotlib axes to plot on. If None, uses current axes.
        **kwargs: Passed to geopandas plot (e.g., facecolor, edgecolor, alpha).

    Returns:
        The matplotlib axes.
    """
    if ax is None:
        ax = plt.gca()

    kwargs.setdefault('facecolor', 'none')
    kwargs.setdefault('edgecolor', 'black')
    kwargs.setdefault('linewidth', 1)

    gdf = load_states()
    matches = gdf[gdf['NAME'].str.lower() == state.lower()]

    if matches.empty:
        from h3coco.states import state_names
        raise ValueError(f'Unknown state: {state!r}. Available: {state_names()}')

    matches.plot(ax=ax, **kwargs)
    ax.set_aspect('equal')

    return ax


def plot_cells(cells, ax=None, **kwargs):
    """Plot a set of H3 cells.

    Args:
        cells: Iterable of H3 cell indices.
        ax: Matplotlib axes to plot on. If None, uses current axes.
        **kwargs: Passed to PolyCollection (e.g., facecolor, edgecolor, alpha).

    Returns:
        The PolyCollection added to the axes.
    """
    if ax is None:
        ax = plt.gca()

    kwargs.setdefault('facecolor', 'steelblue')
    kwargs.setdefault('edgecolor', 'white')
    kwargs.setdefault('alpha', 0.7)
    kwargs.setdefault('linewidth', 0.5)

    # Get boundaries as (lng, lat) for plotting
    polygons = []
    for cell in cells:
        boundary = h3.cell_to_boundary(cell)
        # boundary is [(lat, lng), ...], flip to (lng, lat) for x, y plotting
        polygons.append([(lng, lat) for lat, lng in boundary])

    collection = PolyCollection(polygons, **kwargs)
    ax.add_collection(collection)
    ax.autoscale_view()
    ax.set_aspect('equal')

    return collection


def plot_cocompact(
    cells: dict[str, int],
    res: int,
    ax=None,
    include_color='steelblue',
    exclude_color='indianred',
    alpha=0.5,
    linewidth=0.5,
    edgecolor='white',
    savefig=None,
):
    """Plot a co-compacted H3 cell set.

    Plots included (+1) cells in blue and excluded (-1) cells in red,
    with lower resolution (larger) cells drawn first.

    Args:
        cells: Dict mapping H3 cell indices to +1 (include) or -1 (exclude).
        res: Target resolution to uncompact cells to for plotting.
        ax: Matplotlib axes to plot on. If None, creates new figure.
        include_color: Color for +1 cells (default: steelblue).
        exclude_color: Color for -1 cells (default: indianred).
        alpha: Transparency for polygons (default: 0.5).
        linewidth: Width of polygon edges (default: 0.5).
        edgecolor: Color of polygon edges (default: white).
        savefig: If provided, save figure to this path (supports .png, .svg).

    Returns:
        The matplotlib axes.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 10))

    # Sort cells by resolution (ascending = larger cells first)
    sorted_cells = sorted(cells.items(), key=lambda x: h3.get_resolution(x[0]))

    for cell, sign in sorted_cells:
        # Uncompact this cell to target resolution
        children = h3.cell_to_children(cell, res)
        if not children:
            # Cell is already at or below target res, use it directly
            children = {cell}

        # Convert cells to a polygon using h3's built-in function
        shape = h3.cells_to_h3shape(children)
        geo = shape.__geo_interface__

        # Choose color based on sign
        facecolor = include_color if sign > 0 else exclude_color

        # Handle both Polygon and MultiPolygon
        if geo['type'] == 'Polygon':
            _plot_polygon_coords(ax, geo['coordinates'], facecolor, alpha, edgecolor, linewidth)
        elif geo['type'] == 'MultiPolygon':
            for poly_coords in geo['coordinates']:
                _plot_polygon_coords(ax, poly_coords, facecolor, alpha, edgecolor, linewidth)

    ax.autoscale_view()
    ax.set_aspect('equal')

    if savefig:
        plt.savefig(savefig, bbox_inches='tight', dpi=150)

    return ax


def _plot_polygon_coords(ax, coords, facecolor, alpha, edgecolor, linewidth):
    """Plot a polygon from GeoJSON coordinates."""
    # coords is [exterior, *holes] where each is [(lng, lat), ...]
    exterior = coords[0]
    holes = coords[1:] if len(coords) > 1 else []

    # Create polygon vertices (exterior ring)
    verts = [(lng, lat) for lng, lat in exterior]

    # For polygons with holes, we need to use PathPatch
    if holes:
        from matplotlib.patches import PathPatch
        from matplotlib.path import Path

        # Build path codes for exterior
        codes = [Path.MOVETO] + [Path.LINETO] * (len(exterior) - 2) + [Path.CLOSEPOLY]
        all_verts = list(exterior)

        # Add holes
        for hole in holes:
            codes += [Path.MOVETO] + [Path.LINETO] * (len(hole) - 2) + [Path.CLOSEPOLY]
            all_verts += list(hole)

        path = Path(all_verts, codes)
        patch = PathPatch(
            path,
            facecolor=facecolor,
            alpha=alpha,
            edgecolor=edgecolor,
            linewidth=linewidth,
        )
        ax.add_patch(patch)
    else:
        from matplotlib.patches import Polygon as MplPolygon
        patch = MplPolygon(
            verts,
            facecolor=facecolor,
            alpha=alpha,
            edgecolor=edgecolor,
            linewidth=linewidth,
        )
        ax.add_patch(patch)
