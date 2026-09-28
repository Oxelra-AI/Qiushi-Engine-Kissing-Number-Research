"""Solve every twelve-coordinate transverse 2+2 pair-type boundary.

The source pairs are (0,1), (2,3), ..., (10,11); the first three are
the left half. Pair types 0,1,2 mean (0,1), (0,2), (1,2) within a half.
An allowed type (i,j) permits all sixteen blocks choosing one coordinate
from each pair of left type i and right type j.

Only this complete-type, complete-sign model is optimized. Physical old
supports must first be used to determine the allowed types. No claim
about unrestricted signed codes is made.
"""
from itertools import combinations, product


PAIR_TYPES = tuple(combinations(range(3), 2))


def _factorization_blocks():
    """Four synchronized factors of K6 minus the three prescribed pairs."""
    blocks = []
    for a, b in product((0, 1), repeat=2):
        c = a ^ b
        factor = ((a, 2+b), (1-a, 4+c), (3-b, 5-c))
        blocks.extend(tuple(sorted(left + tuple(i+6 for i in right)))
                      for left in factor for right in factor)
    return blocks


def _type_of(block):
    left = tuple(sorted(i//2 for i in block if i < 6))
    right = tuple(sorted(i//2-3 for i in block if i >= 6))
    return PAIR_TYPES.index(left), PAIR_TYPES.index(right)


def solve_type_boundary(allowed_types):
    """Return an optimal source family and independently checkable certificates.

    Input: iterable of (left_type, right_type), both integers in {0,1,2}.
    Repeated types are ignored. The returned dictionary contains:
      capacity / signed_capacity: source and complete-sign image counts;
      blocks: attaining four-subsets of source axes 0,...,11;
      weights: type weights 0,1,2, contributing 0,4,8 source blocks;
      matching: maximum double-cover matching, as (minus_type, plus_type);
      cover_left / cover_right: a minimum cover of the double cover.

    All computations use Python integers and the nine possible type cells.
    """
    allowed = set()
    for cell in allowed_types:
        if (not isinstance(cell, (tuple, list)) or len(cell) != 2 or
                any(type(i) is not int or not 0 <= i < 3 for i in cell)):
            raise ValueError("Each allowed type must be a pair of integers in {0,1,2}")
        allowed.add(tuple(cell))
    graph = {a: tuple(b for b in sorted(allowed) if a != b and
                     (a[0] == b[0] or a[1] == b[1])) for a in sorted(allowed)}
    matched = {}

    def augment(left, seen):
        for right in graph[left]:
            if right in seen:
                continue
            seen.add(right)
            if right not in matched or augment(matched[right], seen):
                matched[right] = left
                return True
        return False

    for left in graph:
        augment(left, set())
    reached_left = allowed - set(matched.values())
    reached_right = set()
    pending = list(reached_left)
    while pending:
        for right in graph[pending.pop()]:
            if right in reached_right:
                continue
            reached_right.add(right)
            if right in matched and matched[right] not in reached_left:
                reached_left.add(matched[right])
                pending.append(matched[right])
    cover_left, cover_right = allowed - reached_left, reached_right
    weights = {a: 2-int(a in cover_left)-int(a in cover_right) for a in sorted(allowed)}

    blocks = {block for block in _factorization_blocks() if weights.get(_type_of(block)) == 1}
    for (row, col), weight in weights.items():
        if weight == 2:
            pairs = PAIR_TYPES[row] + tuple(i+3 for i in PAIR_TYPES[col])
            blocks.update(tuple(sorted(2*pair+bit for pair, bit in zip(pairs, bits)))
                          for bits in product((0, 1), repeat=4) if sum(bits) % 2 == 0)
    capacity = 8*len(allowed)-4*len(matched)
    return {"capacity": capacity, "signed_capacity": 16*capacity,
            "blocks": tuple(sorted(blocks)), "weights": weights,
            "matching": tuple(sorted((left, right) for right, left in matched.items())),
            "cover_left": tuple(sorted(cover_left)), "cover_right": tuple(sorted(cover_right))}
