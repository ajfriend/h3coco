"""Test compact/uncompact roundtrip for each US state."""

import pytest

import h3coco as coco

RES = 6


@pytest.mark.parametrize('state', coco.state_names())
def test_roundtrip(state):
    cells = set(coco.cells_for_state(state, RES))
    compacted = coco.compact(cells)
    uncompacted = coco.uncompact(compacted, RES)
    assert uncompacted == cells
