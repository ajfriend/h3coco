import h3
import h3coco as coco


def test_cocompact():
    cells = (
        set(h3.cell_to_children('8049fffffffffff', 2))
        - set(h3.cell_to_children('81483ffffffffff'))
    ) | {'824807fffffffff'}

    result = coco.cocompact(cells)

    expected = {
        '8049fffffffffff': 1,
        '81483ffffffffff': -1,
        '824807fffffffff': 1,
    }

    assert result == expected

    # Verify round-trip
    assert coco.co_uncompact(result, 2) == cells


def test2():
    h = '81483ffffffffff'
    cells = h3.cell_to_children(h)
    out = coco.cocompact(cells)

    assert out == {h: 1}

def test3():
    a = {'81483ffffffffff': 1, '824837fffffffff': -1}
    cells = coco.co_uncompact(a, 2)
    expected = {
        '824807fffffffff',
        '82480ffffffffff',
        '824817fffffffff',
        '82481ffffffffff',
        '824827fffffffff',
        '82482ffffffffff',
    }

    assert cells == expected

    assert coco.cocompact(cells) == a


def test4():
    cells0 = {
        '824807fffffffff',
        '82480ffffffffff',
        '824817fffffffff',
        '82481ffffffffff',
        '824837fffffffff',
        '8448201ffffffff',
    }
    cells0 = coco.ArithDict(cells0)
    cells4 = coco.co_uncompact(cells0, 4)

    expected = {'81483ffffffffff': 1, '824827fffffffff': -1, '8448201ffffffff': 1, '82482ffffffffff': -1}
    assert coco.co_uncompact(expected, 4) == cells4

    out = coco.cocompact(cells4)
    assert out == expected
