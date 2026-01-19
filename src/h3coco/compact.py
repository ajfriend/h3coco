"""Co-compaction for H3 cells using signed cell representation."""

from collections import defaultdict
from collections.abc import Iterable

import h3

from h3coco.arithdict import ArithDict

# Type alias for H3 cell indices (hexadecimal strings like '8049fffffffffff')
H3Cell = str


class Janus:
    """Tracks cells we want (pos) and don't want (neg) under a root cell."""

    def __init__(self, root, pos, neg):
        self.root = root
        self.pos = pos
        self.neg = neg

    @classmethod
    def included(cls, cell):
        """A cell we want."""
        return cls(cell, ArithDict.one(cell), ArithDict())

    @classmethod
    def excluded(cls, cell):
        """A cell we don't want."""
        return cls(cell, ArithDict(), ArithDict.one(cell))

    @classmethod
    def merge(cls, parent, children):
        """Merge children under a common parent, choosing compact representation."""
        # Fill in any missing children as excluded
        covered = {j.root for j in children}
        for missing in set(h3.cell_to_children(parent)) - covered:
            children.append(cls.excluded(missing))

        pos = ArithDict.sum(j.pos for j in children)
        neg = ArithDict.sum(j.neg for j in children)

        # Choose whichever representation is more compact
        if len(neg) + 1 < len(pos):
            pos = ArithDict.one(parent) - neg
        else:
            neg = ArithDict.one(parent) - pos

        return cls(parent, pos, neg)


def _bump(jani):
    """Move all Janus objects up one resolution level."""
    groups = defaultdict(list)
    for j in jani:
        groups[h3.cell_to_parent(j.root)].append(j)

    return [Janus.merge(parent, children)
            for parent, children in groups.items()]


def compact(cells: Iterable[H3Cell]) -> dict[H3Cell, int]:
    """Compact a set of H3 cells into a signed cell representation.

    Args:
        cells: Iterable of H3 cell indices (all at same resolution).
               H3Cell is a string like '8049fffffffffff'.

    Returns:
        Dict mapping H3 cell indices to signed integers (+1 or -1).
        Use uncompact to expand back to the original cells.
    """
    jani = [Janus.included(c) for c in cells]

    if not jani:
        return {}

    while h3.get_resolution(jani[0].root) > 0:
        jani = _bump(jani)

    return dict(ArithDict.sum(j.pos for j in jani))


def uncompact(cells: dict[H3Cell, int], res: int) -> set[H3Cell]:
    """Uncompact a signed cell representation to a set of cells at target resolution.

    Args:
        cells: Dict mapping H3 cell indices to signed integers (+1 or -1).
               Positive cells are included, negative cells are subtracted.
               H3Cell is a string like '8049fffffffffff'.
        res: Target H3 resolution for output cells.

    Returns:
        Set of H3 cell indices at the target resolution.
    """
    ad = ArithDict()
    for h, sign in cells.items():
        children = h3.cell_to_children(h, res)
        ad += sign * ArithDict(children)

    for k, v in ad.items():
        assert v == 1
        assert h3.get_resolution(k) == res

    out = set(ad.keys())
    assert len(out) == len(ad)

    return out
