from h3coco import cells_for_state


def test_maryland():
    cells = cells_for_state('Maryland', 5)
    assert len(cells) > 0
