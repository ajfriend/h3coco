# h3coco

"Dual" compaction (or co-compaction) for H3 cells.

## Idea

If your uncompaction operation can both add and remove cells, then you can
store a "co-compacted" set of H3 cells more tersely than if
you can just add cells (standard H3 uncompaction).

This repo provides proof-of-concept implementations for `h3coco.compact`
and `h3coco.uncompact`.

A co-compacted set is a collection of cells
marked for addition or subtraction, which we represent here with a `dict[str, int]`
like:

```python
{'8049fffffffffff': 1, '8048fffffffffff': -1, ...}
```

(You could alternatively store positive and negative cell sets.)

We're seeing around 25% to 45% reduction in number of cells needed, compared
to standard H3 compaction.

Here's California:

![California co-compaction example](california_6.svg)


## Why?

Standard `h3.compact_cells` only merges cells when all 7 children are present. This leaves gaps at boundaries.

`coco.compact` uses a signed representation: positive cells are included, negative cells are subtracted. This allows representing "parent minus some children" which often yields 25-45% fewer cells.

## Usage

```python
import h3coco as coco

# Get cells for a region
cells = coco.cells_for_state('California', res=6)

# Compact to signed representation
compacted = coco.compact(cells)
# Returns: {'8049fffffffffff': 1, '8048fffffffffff': -1, ...}

# Uncompact back to original cells
original = coco.uncompact(compacted, res=6)
assert original == set(cells)
```

## Data format

- Input to `compact`: iterable of H3 cell strings at the same resolution
- Output from `compact`: `dict[str, int]` where values are +1 (include) or -1 (exclude)
- Input to `uncompact`: the dict from `compact`, plus target resolution
- Output from `uncompact`: `set[str]` of H3 cells at target resolution

## Comparison with h3.compact

| State                |   Res |   # Cells |   h3.compact |   coco.compact |   Reduction |
|----------------------|-------|-----------|--------------|----------------|-------------|
| Georgia              |     7 |    31,596 |        1,344 |            770 |      -42.7% |
| South Carolina       |     7 |    17,620 |        1,000 |            580 |      -42.0% |
| Nebraska             |     7 |    37,691 |        1,343 |            785 |      -41.5% |
| Delaware             |     8 |     7,305 |          813 |            483 |      -40.6% |
| New York             |     7 |    23,527 |        1,633 |            973 |      -40.4% |
| Louisiana            |     7 |    22,147 |        1,807 |          1,079 |      -40.3% |
| West Virginia        |     7 |    12,609 |        1,161 |            695 |      -40.1% |
| Pennsylvania         |     7 |    22,512 |        1,014 |            608 |      -40.0% |
| Illinois             |     7 |    28,815 |        1,353 |            813 |      -39.9% |
| Kentucky             |     7 |    21,376 |        1,384 |            842 |      -39.2% |
| New Mexico           |     7 |    53,115 |        1,539 |            937 |      -39.1% |
| Virginia             |     7 |    21,629 |        1,775 |          1,085 |      -38.9% |
| New Jersey           |     7 |     3,917 |          527 |            323 |      -38.7% |
| Minnesota            |     7 |    40,334 |        1,700 |          1,044 |      -38.6% |
| Mississippi          |     7 |    23,171 |        1,343 |            827 |      -38.4% |
| Alabama              |     7 |    26,201 |        1,199 |            739 |      -38.4% |
| Texas                |     7 |   116,680 |        3,610 |          2,228 |      -38.3% |
| North Dakota         |     7 |    34,547 |        1,199 |            743 |      -38.0% |
| Wisconsin            |     7 |    26,918 |        1,394 |            864 |      -38.0% |
| Missouri             |     7 |    34,493 |        1,511 |            939 |      -37.9% |
| Arizona              |     7 |    49,850 |        1,490 |            928 |      -37.7% |
| South Dakota         |     7 |    38,756 |        1,340 |            836 |      -37.6% |
| Idaho                |     7 |    42,368 |        1,862 |          1,162 |      -37.6% |
| Florida              |     7 |    31,358 |        2,198 |          1,372 |      -37.6% |
| Montana              |     7 |    76,431 |        2,043 |          1,279 |      -37.4% |
| Tennessee            |     7 |    21,997 |        1,369 |            859 |      -37.3% |
| Wyoming              |     7 |    47,720 |        1,412 |            888 |      -37.1% |
| Colorado             |     7 |    47,881 |        1,387 |            873 |      -37.1% |
| Indiana              |     7 |    18,580 |        1,078 |            680 |      -36.9% |
| Nevada               |     7 |    52,210 |        1,582 |            998 |      -36.9% |
| Vermont              |     7 |     4,547 |          515 |            325 |      -36.9% |
| New Hampshire        |     7 |     4,408 |          526 |            332 |      -36.9% |
| Rhode Island         |     8 |     3,815 |          749 |            475 |      -36.6% |
| California           |     7 |    74,445 |        2,601 |          1,651 |      -36.5% |
| North Carolina       |     7 |    27,806 |        1,946 |          1,238 |      -36.4% |
| Arkansas             |     7 |    25,391 |        1,157 |            737 |      -36.3% |
| Alaska               |     6 |    44,878 |        5,242 |          3,346 |      -36.2% |
| District of Columbia |    10 |    12,107 |          791 |            507 |      -35.9% |
| Iowa                 |     7 |    28,395 |        1,167 |            749 |      -35.8% |
| Hawaii               |     7 |     2,785 |          709 |            457 |      -35.5% |
| Michigan             |     7 |    27,703 |        2,419 |          1,561 |      -35.5% |
| Ohio                 |     7 |    20,894 |        1,022 |            660 |      -35.4% |
| Washington           |     7 |    37,717 |        2,113 |          1,371 |      -35.1% |
| Maine                |     7 |    15,311 |        1,199 |            783 |      -34.7% |
| Oklahoma             |     7 |    32,054 |        1,610 |          1,052 |      -34.7% |
| Oregon               |     7 |    50,532 |        1,518 |            992 |      -34.7% |
| Massachusetts        |     7 |     4,010 |          704 |            464 |      -34.1% |
| Maryland             |     7 |     5,391 |        1,167 |            773 |      -33.8% |
| Connecticut          |     7 |     2,454 |          318 |            214 |      -32.7% |
| Puerto Rico          |     7 |     2,431 |          367 |            247 |      -32.7% |
| Utah                 |     7 |    39,272 |        1,280 |            862 |      -32.7% |
| Kansas               |     7 |    38,756 |        1,214 |            826 |      -32.0% |
