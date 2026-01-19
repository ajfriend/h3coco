# h3coco

Co-compaction for H3 cells using signed cell representation.

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

| State                |   Res |   # Cells |   h3.compact |   coco.compact | Reduction |
|----------------------|-------|-----------|--------------|----------------|-----------|
| Arkansas             |     6 |     3,615 |          435 |            243 |    -44.1% |
| New Jersey           |     6 |       557 |          185 |            105 |    -43.2% |
| New York             |     6 |     3,369 |          555 |            323 |    -41.8% |
| New Mexico           |     6 |     7,587 |          573 |            343 |    -40.1% |
| Missouri             |     6 |     4,936 |          532 |            320 |    -39.8% |
| South Dakota         |     6 |     5,536 |          502 |            302 |    -39.8% |
| Georgia              |     6 |     4,503 |          417 |            251 |    -39.8% |
| Colorado             |     6 |     6,841 |          523 |            315 |    -39.8% |
| North Carolina       |     6 |     3,960 |          642 |            388 |    -39.6% |
| Florida              |     6 |     4,491 |          735 |            449 |    -38.9% |
| Vermont              |     6 |       649 |          175 |            107 |    -38.9% |
| Pennsylvania         |     6 |     3,216 |          366 |            224 |    -38.8% |
| South Carolina       |     6 |     2,522 |          344 |            212 |    -38.4% |
| Kentucky             |     6 |     3,056 |          470 |            290 |    -38.3% |
| Texas                |     6 |    16,666 |        1,168 |            722 |    -38.2% |
| Virginia             |     6 |     3,090 |          588 |            364 |    -38.1% |
| Montana              |     6 |    10,916 |          752 |            466 |    -38.0% |
| Minnesota            |     6 |     5,763 |          579 |            363 |    -37.3% |
| Tennessee            |     6 |     3,146 |          464 |            292 |    -37.1% |
| Idaho                |     6 |     6,051 |          693 |            437 |    -36.9% |
| Wisconsin            |     6 |     3,845 |          473 |            299 |    -36.8% |
| Mississippi          |     6 |     3,312 |          420 |            266 |    -36.7% |
| Kansas               |     6 |     5,534 |          476 |            302 |    -36.6% |
| Alaska               |     6 |    44,878 |        5,242 |          3,346 |    -36.2% |
| West Virginia        |     6 |     1,804 |          352 |            226 |    -35.8% |
| Wyoming              |     6 |     6,816 |          510 |            330 |    -35.3% |
| Ohio                 |     6 |     2,982 |          360 |            234 |    -35.0% |
| North Dakota         |     6 |     4,937 |          431 |            281 |    -34.8% |
| Iowa                 |     6 |     4,047 |          381 |            249 |    -34.6% |
| Oregon               |     6 |     7,219 |          547 |            359 |    -34.4% |
| Nebraska             |     6 |     5,389 |          457 |            301 |    -34.1% |
| Nevada               |     6 |     7,458 |          588 |            392 |    -33.3% |
| Indiana              |     6 |     2,653 |          343 |            229 |    -33.2% |
| Arizona              |     6 |     7,130 |          530 |            354 |    -33.2% |
| Washington           |     6 |     5,397 |          645 |            431 |    -33.2% |
| Louisiana            |     6 |     3,179 |          509 |            341 |    -33.0% |
| Alabama              |     6 |     3,742 |          388 |            260 |    -33.0% |
| Maine                |     6 |     2,194 |          370 |            248 |    -33.0% |
| Illinois             |     6 |     4,117 |          433 |            291 |    -32.8% |
| California           |     6 |    10,635 |          903 |            607 |    -32.8% |
| Rhode Island         |     6 |        73 |           43 |             29 |    -32.6% |
| Oklahoma             |     6 |     4,577 |          503 |            341 |    -32.2% |
| Michigan             |     6 |     3,957 |          747 |            507 |    -32.1% |
| Utah                 |     6 |     5,609 |          521 |            365 |    -29.9% |
| Maryland             |     6 |       773 |          347 |            245 |    -29.4% |
| New Hampshire        |     6 |       627 |          159 |            113 |    -28.9% |
| Massachusetts        |     6 |       567 |          207 |            151 |    -27.1% |
| Hawaii               |     6 |       398 |          194 |            144 |    -25.8% |
| Connecticut          |     6 |       350 |          110 |             84 |    -23.6% |
| Puerto Rico          |     6 |       341 |          113 |             87 |    -23.0% |
| Delaware             |     6 |       150 |           72 |             56 |    -22.2% |
| District of Columbia |     6 |         5 |            5 |              5 |        0% |
