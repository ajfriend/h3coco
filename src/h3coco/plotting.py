"""Plotting functions for H3 cells."""

import h3
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection


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

    kwargs.setdefault("facecolor", "steelblue")
    kwargs.setdefault("edgecolor", "white")
    kwargs.setdefault("alpha", 0.7)
    kwargs.setdefault("linewidth", 0.5)

    # Get boundaries as (lng, lat) for plotting
    polygons = []
    for cell in cells:
        boundary = h3.cell_to_boundary(cell)
        # boundary is [(lat, lng), ...], flip to (lng, lat) for x, y plotting
        polygons.append([(lng, lat) for lat, lng in boundary])

    collection = PolyCollection(polygons, **kwargs)
    ax.add_collection(collection)
    ax.autoscale_view()
    ax.set_aspect("equal")

    return collection
