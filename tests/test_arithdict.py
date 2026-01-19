"""Examples demonstrating ArithDict behavior."""

from h3coco import ArithDict


def test_missing_keys_return_zero():
    ad = ArithDict({'a': 1})
    assert ad['a'] == 1
    assert ad['missing'] == 0


def test_zeros_are_removed():
    ad = ArithDict({'a': 1, 'b': 0, 'c': -1})
    assert set(ad.keys()) == {'a', 'c'}


def test_from_iterable_counts_occurrences():
    ad = ArithDict(['a', 'b', 'a', 'a'])
    assert ad['a'] == 3
    assert ad['b'] == 1


def test_addition():
    a = ArithDict({'x': 2, 'y': 1})
    b = ArithDict({'x': 1, 'z': 3})
    result = a + b
    assert result['x'] == 3
    assert result['y'] == 1
    assert result['z'] == 3


def test_subtraction():
    a = ArithDict({'x': 5})
    b = ArithDict({'x': 3})
    assert (a - b)['x'] == 2
    assert (b - a)['x'] == -2  # negative values are preserved


def test_subtraction_removes_zeros():
    a = ArithDict({'x': 3})
    b = ArithDict({'x': 3})
    result = a - b
    assert 'x' not in result.keys()
    assert len(result) == 0


def test_scalar_multiplication():
    ad = ArithDict({'a': 2, 'b': -1})
    result = 3 * ad
    assert result['a'] == 6
    assert result['b'] == -3


def test_one():
    ad = ArithDict.one('cell')
    assert ad['cell'] == 1
    assert len(ad) == 1


def test_sum():
    items = [{'a': 1}, {'a': 2, 'b': 1}, {'b': -1}]
    result = ArithDict.sum(items)
    assert result['a'] == 3
    assert 'b' not in result.keys()  # 1 + (-1) = 0, removed
