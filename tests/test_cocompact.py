import h3
import h3coco as coco


def test_cocompact():
    cells = (
        set(h3.cell_to_children('8049fffffffffff', 2))
        - set(h3.cell_to_children('81483ffffffffff'))
    ) | {'824807fffffffff'}

    result = coco.compact(cells)

    expected = {
        '8049fffffffffff': 1,
        '81483ffffffffff': -1,
        '824807fffffffff': 1,
    }

    assert result == expected

    # Verify round-trip
    assert coco.uncompact(result, 2) == cells


def test2():
    h = '81483ffffffffff'
    cells = h3.cell_to_children(h)
    out = coco.compact(cells)

    assert out == {h: 1}

def test3():
    a = {'81483ffffffffff': 1, '824837fffffffff': -1}
    cells = coco.uncompact(a, 2)
    expected = {
        '824807fffffffff',
        '82480ffffffffff',
        '824817fffffffff',
        '82481ffffffffff',
        '824827fffffffff',
        '82482ffffffffff',
    }

    assert cells == expected

    assert coco.compact(cells) == a


def test4():
    cells0 = {
        '824807fffffffff': 1,
        '82480ffffffffff': 1,
        '824817fffffffff': 1,
        '82481ffffffffff': 1,
        '824837fffffffff': 1,
        '8448201ffffffff': 1,
    }

    cells4 = coco.uncompact(cells0, 4)

    expected = {'81483ffffffffff': 1, '824827fffffffff': -1, '8448201ffffffff': 1, '82482ffffffffff': -1}
    assert coco.uncompact(expected, 4) == cells4

    out = coco.compact(cells4)
    assert out == expected


def test_merge_chooses_pos_and_neg_independently():
    # 6 complete children of a res-1 cell, plus 4 of the 7 grandchildren
    # under the remaining child. Coupling the pos/neg choice in
    # Janus.merge used to give 6 entries; the minimum is 4.
    parent = h3.cell_to_parent(h3.latlng_to_cell(40.69, -73.98, 1), 1)
    kids = sorted(h3.cell_to_children(parent))
    cells = {c for k in kids[:6] for c in h3.cell_to_children(k)}
    cells |= set(sorted(h3.cell_to_children(kids[6]))[:4])
    assert len(cells) == 46

    result = coco.compact(cells)

    assert len(result) == 4
    assert coco.uncompact(result, 3) == cells
