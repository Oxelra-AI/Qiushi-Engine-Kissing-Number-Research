#!/usr/bin/env python3
"""Exact conditional-expectation selection from a finite pool of line classes."""
from collections import Counter
from fractions import Fraction
from math import comb


def incidence_counts(images):
    """Count points with each nonzero image-incidence mask."""
    membership = {}
    for i, image in enumerate(images):
        for point in set(image):
            membership[point] = membership.get(point, 0) | (1 << i)
    return dict(Counter(membership.values()))


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def select(counts, pool_size, target):
    """Choose distinct images, meeting the exact uniform-subset expectation.

    counts[mask] is the number of distinct points present in precisely the
    images indicated by mask. Every decision uses integer binomial scores.
    """
    if (not isinstance(pool_size, int) or not isinstance(target, int)
            or not 0 <= target <= pool_size):
        raise ValueError("Invalid pool size or target")
    remaining = (1 << pool_size) - 1
    if any(not isinstance(mask, int) or not 0 < mask <= remaining
           or not isinstance(count, int) or count <= 0
           for mask, count in counts.items()):
        raise ValueError("Invalid incidence table")
    denominator = choose(pool_size, target)
    expected = sum((Fraction(count * (denominator - choose(pool_size-mask.bit_count(), target)),
                             denominator) for mask, count in counts.items()), Fraction())
    uncovered = dict(counts)
    chosen, covered, history = [], 0, []
    potential = expected
    for step in range(target):
        m, h = pool_size-step, target-step
        weights = {a: choose(m-1-a, h-1) for a in range(1, m+1)}
        scores = [0] * pool_size
        for mask, count in uncovered.items():
            bits = mask & remaining
            weight = count * weights[bits.bit_count()]
            while bits:
                bit = bits & -bits
                scores[bit.bit_length()-1] += weight
                bits ^= bit
        eligible = [i for i in range(pool_size) if remaining >> i & 1]
        index = min(eligible, key=lambda i: (-scores[i], i))
        chosen.append(index)
        bit = 1 << index
        gain = sum(count for mask, count in uncovered.items() if mask & bit)
        covered += gain
        uncovered = {mask: count for mask, count in uncovered.items() if not mask & bit}
        remaining ^= bit
        denominator_next = choose(m-1, h-1)
        following = Fraction(covered) + sum((
            Fraction(count * (denominator_next - choose(m-1-(mask & remaining).bit_count(), h-1)),
                     denominator_next) for mask, count in uncovered.items()), Fraction())
        if following < potential:
            raise ArithmeticError("Conditional expectation decreased")
        history.append({"image": index, "new_points": gain,
                        "conditional_expectation": str(following)})
        potential = following
    if potential != covered or covered < expected:
        raise ArithmeticError("Final coverage does not meet the guarantee")
    return {"indices": chosen, "union": covered,
            "expected_union": str(expected),
            "guaranteed_union": -(-expected.numerator // expected.denominator),
            "steps": history}


def improve(counts, pool_size, indices):
    """Take exact improving one-image exchanges until none remains."""
    chosen = set(indices)
    if len(chosen) != len(indices) or not chosen <= set(range(pool_size)):
        raise ValueError("Invalid starting image indices")
    selected = sum(1 << i for i in chosen)
    history = []
    while True:
        covered = sum(number for mask, number in counts.items() if mask & selected)
        gain = [0] * pool_size
        loss = [0] * pool_size
        rescue = [[0] * pool_size for _ in range(pool_size)]
        for mask, number in counts.items():
            active = mask & selected
            if active and active.bit_count() > 1:
                continue
            bits = mask & ~selected
            if active:
                old = active.bit_length()-1
                loss[old] += number
            while bits:
                bit = bits & -bits
                new = bit.bit_length()-1
                if active:
                    rescue[old][new] += number
                else:
                    gain[new] += number
                bits ^= bit
        swaps = [(gain[j]+rescue[i][j]-loss[i], i, j)
                 for i in sorted(chosen) for j in range(pool_size) if j not in chosen]
        if not swaps:
            return {"indices": sorted(chosen), "union": covered,
                    "exchanges": history, "maximum_swap_gain": 0}
        delta, old, new = min(swaps, key=lambda row: (-row[0], row[1], row[2]))
        if delta <= 0:
            return {"indices": sorted(chosen), "union": covered,
                    "exchanges": history, "maximum_swap_gain": delta}
        updated = (selected ^ (1 << old)) | (1 << new)
        actual = sum(number for mask, number in counts.items() if mask & updated)
        if actual != covered+delta:
            raise ArithmeticError("Exchange gain disagrees with exact union")
        history.append({"removed": old, "inserted": new, "gain": delta})
        chosen.remove(old)
        chosen.add(new)
        selected = updated
