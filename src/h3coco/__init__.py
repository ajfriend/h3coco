"""h3coco - H3 geospatial indexing utilities."""

from h3coco.arithdict import ArithDict
from h3coco.compact import H3Cell, compact, uncompact
from h3coco.plotting import best_text_corner, cells_bounds, figsize_for_cells, plot_cells, plot_cocompact, plot_cocompaction, plot_compaction_comparison, plot_state
from h3coco.states import cells_for_state, load_states, state_names

__version__ = '0.1.0'
__all__ = ['ArithDict', 'H3Cell', 'best_text_corner', 'cells_bounds', 'cells_for_state', 'compact', 'figsize_for_cells', 'load_states', 'plot_cells', 'plot_cocompact', 'plot_cocompaction', 'plot_compaction_comparison', 'plot_state', 'state_names', 'uncompact']
