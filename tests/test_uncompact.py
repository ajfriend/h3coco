import h3coco as coco


def test_uncompact():
    cells = {
        '8049fffffffffff': +1,
        '81483ffffffffff': -1,
        '824807fffffffff': +1,
    }
    result = coco.uncompact(cells, 2)

    expected = {
        '824807fffffffff',
        '824847fffffffff',
        '82484ffffffffff',
        '824857fffffffff',
        '82485ffffffffff',
        '824867fffffffff',
        '82486ffffffffff',
        '824877fffffffff',
        '824887fffffffff',
        '82488ffffffffff',
        '824897fffffffff',
        '82489ffffffffff',
        '8248a7fffffffff',
        '8248affffffffff',
        '8248b7fffffffff',
        '8248c7fffffffff',
        '8248cffffffffff',
        '8248d7fffffffff',
        '8248dffffffffff',
        '8248e7fffffffff',
        '8248effffffffff',
        '8248f7fffffffff',
        '824907fffffffff',
        '82490ffffffffff',
        '824917fffffffff',
        '82491ffffffffff',
        '824927fffffffff',
        '82492ffffffffff',
        '824937fffffffff',
        '824947fffffffff',
        '82494ffffffffff',
        '824957fffffffff',
        '82495ffffffffff',
        '824967fffffffff',
        '82496ffffffffff',
        '824977fffffffff',
        '824987fffffffff',
        '82498ffffffffff',
        '824997fffffffff',
        '82499ffffffffff',
        '8249a7fffffffff',
        '8249affffffffff',
        '8249b7fffffffff',
    }

    assert result == expected
