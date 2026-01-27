"""Plotting functions for H3 cells."""

import h3
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

from h3coco.states import load_states


def _savefig(path):
    """Save figure with reproducible output (no date metadata, deterministic IDs)."""
    # Set hashsalt for deterministic SVG element IDs
    old_hashsalt = plt.rcParams.get('svg.hashsalt', None)
    plt.rcParams['svg.hashsalt'] = 'h3coco'
    try:
        plt.savefig(path, bbox_inches='tight', dpi=150, metadata={'Date': None})
    finally:
        if old_hashsalt is None:
            plt.rcParams['svg.hashsalt'] = ''
        else:
            plt.rcParams['svg.hashsalt'] = old_hashsalt


def cells_bounds(cells):
    """Compute the bounding box of a set of H3 cells.

    Args:
        cells: Iterable of H3 cell indices, or dict (uses keys).

    Returns:
        Tuple of (min_lng, min_lat, max_lng, max_lat).
    """
    if isinstance(cells, dict):
        cells = cells.keys()

    min_lng = float('inf')
    min_lat = float('inf')
    max_lng = float('-inf')
    max_lat = float('-inf')

    for cell in cells:
        boundary = h3.cell_to_boundary(cell)
        for lat, lng in boundary:
            min_lng = min(min_lng, lng)
            max_lng = max(max_lng, lng)
            min_lat = min(min_lat, lat)
            max_lat = max(max_lat, lat)

    return (min_lng, min_lat, max_lng, max_lat)


def best_text_corner(cells):
    """Find the best corner for placing text labels.

    Determines which corner of the bounding box has the fewest cells,
    making it the best location for text labels.

    Args:
        cells: Iterable of H3 cell indices, or dict (uses keys).

    Returns:
        Dict with keys 'x', 'y', 'ha', 'va' for use with ax.text().
        Example: {'x': 0.95, 'y': 0.95, 'ha': 'right', 'va': 'top'}
    """
    if isinstance(cells, dict):
        cells = list(cells.keys())
    else:
        cells = list(cells)

    min_lng, min_lat, max_lng, max_lat = cells_bounds(cells)
    mid_lng = (min_lng + max_lng) / 2
    mid_lat = (min_lat + max_lat) / 2

    # Count cells in each quadrant based on cell centroids
    quadrants = {
        'upper_right': 0,
        'upper_left': 0,
        'lower_right': 0,
        'lower_left': 0,
    }

    for cell in cells:
        lat, lng = h3.cell_to_latlng(cell)
        if lat >= mid_lat:
            if lng >= mid_lng:
                quadrants['upper_right'] += 1
            else:
                quadrants['upper_left'] += 1
        else:
            if lng >= mid_lng:
                quadrants['lower_right'] += 1
            else:
                quadrants['lower_left'] += 1

    # Find quadrant with fewest cells
    best = min(quadrants, key=quadrants.get)

    corners = {
        'upper_right': {'x': 0.95, 'y': 0.95, 'ha': 'right', 'va': 'top'},
        'upper_left': {'x': 0.05, 'y': 0.95, 'ha': 'left', 'va': 'top'},
        'lower_right': {'x': 0.95, 'y': 0.05, 'ha': 'right', 'va': 'bottom'},
        'lower_left': {'x': 0.05, 'y': 0.05, 'ha': 'left', 'va': 'bottom'},
    }

    return corners[best]


def figsize_for_cells(cells, width=12, nrows=1, ncols=1):
    """Compute figure size based on cell bounds and subplot grid.

    Args:
        cells: Iterable of H3 cell indices, or dict (uses keys).
        width: Desired figure width (default: 12).
        nrows: Number of subplot rows (default: 1).
        ncols: Number of subplot columns (default: 1).

    Returns:
        Tuple of (width, height) for figsize.
    """
    min_lng, min_lat, max_lng, max_lat = cells_bounds(cells)
    geo_width = max_lng - min_lng
    geo_height = max_lat - min_lat

    aspect = geo_width / geo_height
    fig_width = width
    fig_height = width / aspect * (nrows / ncols)

    return (fig_width, fig_height)


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

    # Get boundaries as (lng, lat) for plotting, sorted for reproducibility
    polygons = []
    for cell in sorted(cells):
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
    show='both',
    outline=False,
    outline_color='black',
    outline_linewidth=2,
    _outline_geo=None,
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
        show: Which cells to plot: 'both', 'include' (+1 only), or 'exclude' (-1 only).
        outline: If True, plot the outline of the uncompacted cells.
        outline_color: Color for the outline (default: black).
        outline_linewidth: Line width for the outline (default: 2).
        _outline_geo: Pre-computed outline GeoJSON (internal use for efficiency).

    Returns:
        The matplotlib axes.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 10))

    # Save original cells for outline before filtering
    original_cells = cells

    # Filter cells based on show parameter
    if show == 'include':
        cells = {k: v for k, v in cells.items() if v > 0}
    elif show == 'exclude':
        cells = {k: v for k, v in cells.items() if v < 0}
    elif show != 'both':
        raise ValueError(f"show must be 'both', 'include', or 'exclude', got {show!r}")

    # Sort cells by resolution (ascending = larger cells first), then by cell key for reproducibility
    sorted_cells = sorted(cells.items(), key=lambda x: (h3.get_resolution(x[0]), x[0]))

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

    # Plot outline of the full uncompacted region
    if outline:
        if _outline_geo is None:
            from h3coco.compact import uncompact
            uncompacted = uncompact(original_cells, res)
            shape = h3.cells_to_h3shape(uncompacted)
            geo = shape.__geo_interface__
        else:
            geo = _outline_geo

        if geo['type'] == 'Polygon':
            _plot_polygon_coords(ax, geo['coordinates'], 'none', 1.0, outline_color, outline_linewidth)
        elif geo['type'] == 'MultiPolygon':
            for poly_coords in geo['coordinates']:
                _plot_polygon_coords(ax, poly_coords, 'none', 1.0, outline_color, outline_linewidth)

    ax.autoscale_view()
    ax.set_aspect('equal')

    if savefig:
        _savefig(savefig)

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


def plot_cocompaction(cells, width=12, savefig=None):
    """Plot the co-compaction result for a set of cells.

    Args:
        cells: Set of H3 cell indices (all at same resolution).
        width: Figure width (default: 12).
        savefig: If provided, save figure to this path.

    Returns:
        Tuple of (fig, ax) - the figure and axes.
    """
    from h3coco.compact import compact

    # Sort cells for reproducibility
    cells = sorted(set(cells))
    res = h3.get_resolution(cells[0])

    # Compact
    compacted = compact(cells)

    # Auto-size figure based on cell bounds
    figsize = figsize_for_cells(compacted, width=width, nrows=1, ncols=1)
    fig, ax = plt.subplots(figsize=figsize)

    plot_cocompact(compacted, res=res, show='both', ax=ax, outline=True, outline_linewidth=0.5)
    ax.set_xticks([])
    ax.set_yticks([])

    fig.tight_layout()

    if savefig:
        _savefig(savefig)

    return fig, ax


def plot_compaction_comparison(cells, width=12, fontsize=12, savefig=None):
    """Plot a 2x2 comparison of standard vs co-compaction.

    Creates a figure with four subplots:
    1. Standard h3.compact_cells result
    2. Co-compaction result (positive + negative cells)
    3. Positive cells only
    4. Negative cells only

    Args:
        cells: Set of H3 cell indices (all at same resolution).
        width: Figure width (default: 12).
        fontsize: Font size for labels (default: 12).
        savefig: If provided, save figure to this path.

    Returns:
        Tuple of (fig, axs) - the figure and flattened array of axes.
    """
    from h3coco.compact import compact

    # Sort cells for reproducibility
    cells = sorted(set(cells))
    res = h3.get_resolution(cells[0])

    # Compact with both methods
    compacted = compact(cells)
    h3_compacted = h3.compact_cells(cells)

    # Count cells
    n_total = len(compacted)
    n_pos = sum(1 for v in compacted.values() if v > 0)
    n_neg = sum(1 for v in compacted.values() if v < 0)
    n_h3 = len(h3_compacted)
    reduction_pct = (n_h3 - n_total) / n_h3 * 100

    # Auto-size figure based on cell bounds
    figsize = figsize_for_cells(compacted, width=width, nrows=2, ncols=2)
    fig, axs = plt.subplots(2, 2, figsize=figsize, sharex=True, sharey=True)
    axs = axs.flatten()

    # Find best corner for text
    corner = best_text_corner(compacted)

    # Pre-compute outline (same for all plots since they represent the same region)
    outline_shape = h3.cells_to_h3shape(cells)
    outline_geo = outline_shape.__geo_interface__

    # Standard compaction
    ax = axs[0]
    h3_compacted_dict = {cell: 1 for cell in sorted(h3_compacted)}
    plot_cocompact(h3_compacted_dict, res=res, ax=ax, outline=True, outline_linewidth=0.5, include_color='forestgreen', _outline_geo=outline_geo)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(corner['x'], corner['y'], f'standard compaction\n{n_h3} cells\nresolution {res}', transform=ax.transAxes, ha=corner['ha'], va=corner['va'], fontsize=fontsize)

    # Co-compacted
    ax = axs[1]
    plot_cocompact(compacted, res=res, show='both', ax=ax, outline=True, outline_linewidth=0.5, _outline_geo=outline_geo)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(corner['x'], corner['y'], f'co-compaction\n{n_total} cells\n({reduction_pct:.1f}% reduction)', transform=ax.transAxes, ha=corner['ha'], va=corner['va'], fontsize=fontsize)

    # Positive elements
    ax = axs[2]
    plot_cocompact(compacted, res=res, show='include', ax=ax, outline=True, outline_linewidth=0.5, _outline_geo=outline_geo)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(corner['x'], corner['y'], f'{n_pos} positive cells', transform=ax.transAxes, ha=corner['ha'], va=corner['va'], fontsize=fontsize)

    # Negative elements
    ax = axs[3]
    plot_cocompact(compacted, res=res, show='exclude', ax=ax, outline=True, outline_linewidth=0.5, _outline_geo=outline_geo)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(corner['x'], corner['y'], f'{n_neg} negative cells', transform=ax.transAxes, ha=corner['ha'], va=corner['va'], fontsize=fontsize)

    fig.tight_layout()

    if savefig:
        _savefig(savefig)

    return fig, axs
