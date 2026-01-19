"""Arithmetic dictionary and compact/uncompact operations for H3 cells."""

import h3


class ArithDict:
    """A dictionary that supports arithmetic operations with integer values.

    Values are automatically removed when they become zero.
    Missing keys return 0.
    """

    __slots__ = ('_d',)

    def __init__(self, data=None):
        self._d = {}

        if data is None:
            return

        # Mapping: {'a': 3, 'b': -1}
        if hasattr(data, 'items'):
            for k, v in data.items():
                v = int(v)
                if v != 0:
                    self._d[k] = v
            return

        # Iterable of keys: ['a', 'b', 'a']
        for k in data:
            self._d[k] = self._d.get(k, 0) + 1
            if self._d[k] == 0:
                del self._d[k]

    # --- dict behavior ---
    def __getitem__(self, k):
        return self._d.get(k, 0)

    def __setitem__(self, k, v):
        v = int(v)
        if v == 0:
            self._d.pop(k, None)
        else:
            self._d[k] = v

    def __delitem__(self, k):
        self._d.pop(k, None)

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def items(self):
        return self._d.items()

    def to_dict(self):
        return dict(self._d)

    # --- arithmetic ---
    def _combine(self, other, op):
        out = {}
        keys = set(self._d) | set(other)
        for k in keys:
            v = op(self[k], other.get(k, 0))
            if v != 0:
                out[k] = v
        return ArithDict(out)

    def __add__(self, other):
        return self._combine(other, lambda a, b: a + b)

    def __sub__(self, other):
        return self._combine(other, lambda a, b: a - b)

    def __iadd__(self, other):
        for k in set(self._d) | set(other):
            v = self[k] + other.get(k, 0)
            if v == 0:
                self._d.pop(k, None)
            else:
                self._d[k] = v
        return self

    def __isub__(self, other):
        for k in set(self._d) | set(other):
            v = self[k] - other.get(k, 0)
            if v == 0:
                self._d.pop(k, None)
            else:
                self._d[k] = v
        return self

    def __neg__(self):
        return ArithDict({k: -v for k, v in self._d.items()})

    def __mul__(self, scalar):
        if not isinstance(scalar, int):
            return NotImplemented
        if scalar == 0:
            return ArithDict()
        return ArithDict({k: v * scalar for k, v in self._d.items()})

    __rmul__ = __mul__

    @classmethod
    def sum(cls, iterable):
        """Sum an iterable of items, applying ArithDict constructor to each."""
        result = cls()
        for item in iterable:
            result += cls(item)
        return result

    def __repr__(self):
        return f'ArithDict({self._d})'

    def get(self, k, default=0):
        return self._d.get(k, default)

    def keys(self):
        return self._d.keys()

    def values(self):
        return self._d.values()


from collections import defaultdict
from dataclasses import dataclass


@dataclass
class _Janus:
    """Internal helper for cocompact algorithm."""
    root: str
    child_res: int
    local_target_cells: set[str]
    pos: ArithDict
    neg: ArithDict

    @classmethod
    def from_cell(cls, h: str):
        return cls(
            root=h,
            child_res=h3.get_resolution(h),
            local_target_cells={h},
            pos=ArithDict({h: 1}),
            neg=ArithDict(),
        )


def _from_cells(cells):
    return {c: _Janus.from_cell(c) for c in cells}


def _process_children(parent: str, children: list[_Janus]) -> _Janus:
    pos = ArithDict.sum(j.pos for j in children)
    neg = ArithDict.sum(j.neg for j in children)
    child_res = children[0].child_res
    local_target = set.union(*[c.local_target_cells for c in children])

    # Decide: direct representation vs complement
    if len(neg) + 1 < len(pos):
        pos = ArithDict([parent]) - neg
    else:
        neg = ArithDict([parent]) - pos

    return _Janus(
        root=parent,
        child_res=child_res,
        local_target_cells=local_target,
        pos=pos,
        neg=neg,
    )


def _bump(janni: dict[str, _Janus]) -> dict[str, _Janus]:
    groups = defaultdict(list)
    for c, j in janni.items():
        p = h3.cell_to_parent(c)
        groups[p].append(j)

    # Fill in missing children with Janus objects that exclude the entire cell
    for parent, children in groups.items():
        child_res = children[0].child_res
        covered = {j.root for j in children}
        all_children = set(h3.cell_to_children(parent))
        for missing in all_children - covered:
            children.append(_Janus(
                root=missing,
                child_res=child_res,
                local_target_cells=set(),
                pos=ArithDict(),
                neg=ArithDict({missing: 1}),
            ))

    return {h: _process_children(h, children) for h, children in groups.items()}


def cocompact(cells) -> dict[str, int]:
    """Compact a set of H3 cells into a signed cell representation.

    Args:
        cells: Iterable of H3 cell indices (all at same resolution).

    Returns:
        Dict mapping H3 cell indices to signed integers (+1 or -1).
        Use co_uncompact to expand back to the original cells.
    """
    cells = list(cells)
    res = h3.get_resolution(cells[0])
    for c in cells:
        assert h3.get_resolution(c) == res

    janni = _from_cells(cells)
    while res > 0:
        janni = _bump(janni)
        res -= 1

    out = ArithDict.sum(j.pos for j in janni.values())
    return dict(out)


def co_uncompact(cells: dict[str, int], res: int) -> set[str]:
    """Uncompact a signed cell representation to a set of cells at target resolution.

    Args:
        cells: Dict mapping H3 cell indices to signed integers (+1 or -1).
               Positive cells are included, negative cells are subtracted.
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
