import h3coco as coco


def test_maryland():
    cells = coco.cells_for_state('Maryland', 5)
    assert len(cells) > 0
