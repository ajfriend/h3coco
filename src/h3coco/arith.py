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
