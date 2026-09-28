"""Exact capacity for all twelve-coordinate pair-type boundaries."""
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
import unittest

from constructions.codes.hadamard.boundary import solve_type_boundary
from test_replacement_principles import (
    exchange_matching, fibres, matching_number, paired_images,
    signed_dot, subsets, transverse_family,
)


PAIR_TYPES = tuple(frozenset(pair) for pair in combinations(range(3), 2))
CELLS = tuple(product(range(3), repeat=2))
SOURCE_PAIRS = tuple((2*i, 2*i+1) for i in range(6))
LEFT, RIGHT, FULL_FAMILY = transverse_family(SOURCE_PAIRS[:3], SOURCE_PAIRS[3:])


def cell_of(left, right):
    return (PAIR_TYPES.index(frozenset(i//2 for i in left)),
            PAIR_TYPES.index(frozenset(i//2-3 for i in right)))


def double_cover(allowed):
    return {cell: {other for other in allowed if other != cell
                   and (other[0] == cell[0] or other[1] == cell[1])}
            for cell in sorted(allowed)}


def boundary_solution(allowed):
    """Maximum matching, minimum cover, and the associated 0/1/2 cells."""
    graph = double_cover(allowed)
    matching, reached_left, reached_right = exchange_matching(graph)
    cover_left, cover_right = set(allowed) - reached_left, reached_right
    weights = {cell: 2 - int(cell in cover_left) - int(cell in cover_right)
               for cell in allowed}
    return matching, cover_left, cover_right, weights


def source_from_weights(weights):
    blocks = {left | right for left, right in FULL_FAMILY
              if weights.get(cell_of(left, right)) == 1}
    for (row, col), weight in weights.items():
        if weight != 2:
            continue
        pairs = sorted(PAIR_TYPES[row]) + [i+3 for i in sorted(PAIR_TYPES[col])]
        blocks.update(frozenset(2*pair + bit for pair, bit in zip(pairs, bits))
                      for bits in product((0, 1), repeat=4) if sum(bits) % 2 == 0)
    return blocks


def block_cell(block):
    return cell_of(frozenset(i for i in block if i < 6),
                   frozenset(i for i in block if i >= 6))


def matching_normal_form_optimum(allowed):
    """An independent enumeration of all at most 34 type-level matchings."""
    best = 0
    for size in range(4):
        for doubled in combinations(allowed, size):
            rows, cols = {a for a, _ in doubled}, {b for _, b in doubled}
            if len(rows) != size or len(cols) != size:
                continue
            remaining = {(a, b) for a, b in allowed if a not in rows and b not in cols}
            best = max(best, 8*size + 4*len(remaining))
    return best


class TransverseTypeCapacity(unittest.TestCase):
    def test_all_512_type_boundaries(self):
        self.assertEqual(Counter(cell_of(e, f) for e, f in FULL_FAMILY),
                         Counter({cell: 4 for cell in CELLS}))
        for allowed in subsets(CELLS):
            matching, cover_left, cover_right, weights = boundary_solution(allowed)
            graph = double_cover(allowed)
            expected = 8*len(allowed) - 4*len(matching)
            with self.subTest(allowed=sorted(allowed)):
                self.assertEqual(len(cover_left) + len(cover_right), len(matching))
                self.assertTrue(all(a in cover_left or b in cover_right
                                    for a, neighbours in graph.items() for b in neighbours))
                self.assertTrue(all(weights[a] + weights[b] <= 2
                                    for a, neighbours in graph.items() for b in neighbours))
                self.assertTrue(all(weights[b] == 0 for a in allowed if weights[a] == 2
                                    for b in graph[a]))
                blocks = source_from_weights(weights)
                counts = Counter(block_cell(block) for block in blocks)
                self.assertEqual(counts, Counter({a: 4*s for a, s in weights.items() if s}))
                self.assertEqual(len(blocks), expected)
                self.assertEqual(expected, matching_normal_form_optimum(allowed))
                self.assertTrue(all(len(block) == 4 and len({i//2 for i in block}) == 4
                                    for block in blocks))
                self.assertTrue(all(len(a & b) <= 2 for a, b in combinations(blocks, 2)))
                # All summands of the matching upper bound are tight.
                self.assertTrue(all(counts[a] + counts[b] == 8 for b, a in matching.items()))
                self.assertTrue(all(counts[a] == 8 for a in allowed - set(matching.values())))
                self.assertTrue(all(counts[a] == 8 for a in allowed - set(matching)))
                self.assertLessEqual(expected, 36 if len(allowed) == 9 else 32)
                if len(allowed) == 8:
                    self.assertEqual(expected, 32)

                # Check the reusable implementation against the independent
                # matching/normal-form computations and all geometric pairs.
                result = solve_type_boundary(sorted(allowed))
                actual = {frozenset(block) for block in result["blocks"]}
                self.assertEqual(result["capacity"], expected)
                self.assertEqual(result["signed_capacity"], 16*expected)
                self.assertEqual(len(actual), expected)
                self.assertEqual(Counter(block_cell(block) for block in actual),
                                 Counter({a: 4*s for a, s in result["weights"].items() if s}))
                self.assertTrue(all(len(block) == 4 and len({i//2 for i in block}) == 4
                                    for block in actual))
                self.assertTrue(all(len(a & b) <= 2 for a, b in combinations(actual, 2)))
                certificate = result["matching"]
                self.assertEqual(len(certificate), len(matching))
                self.assertEqual(len({a for a, _ in certificate}), len(certificate))
                self.assertEqual(len({b for _, b in certificate}), len(certificate))
                self.assertTrue(all(b in graph[a] for a, b in certificate))
                c_left, c_right = set(result["cover_left"]), set(result["cover_right"])
                self.assertEqual(len(c_left) + len(c_right), len(certificate))
                self.assertTrue(all(a in c_left or b in c_right
                                    for a, neighbours in graph.items() for b in neighbours))

    def test_double_star_strictly_improves_previous_cover_bound(self):
        allowed = {(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)}
        matching, _, _, weights = boundary_solution(allowed)
        blocks = source_from_weights(weights)
        self.assertEqual((len(matching), len(blocks)), (5, 20))
        incidences = {(e, f) for e in LEFT for f in RIGHT if cell_of(e, f) in allowed}
        left_cap = {e: matching_number(f) for e, f in fibres(incidences, LEFT, 0).items()}
        right_cap = {f: matching_number(e) for f, e in fibres(incidences, RIGHT, 1).items()}
        self.assertEqual((sum(left_cap.values()), sum(right_cap.values())), (28, 28))
        covers = []
        for chosen_left in subsets(LEFT):
            chosen_right = {f for e, f in incidences if e not in chosen_left}
            covers.append(sum(left_cap[e] for e in chosen_left) +
                          sum(right_cap[f] for f in chosen_right))
        self.assertEqual(min(covers), 24)
        images = paired_images(blocks, SOURCE_PAIRS)
        self.assertEqual(len(images), 320)
        self.assertLessEqual(max(signed_dot(x, y) for x, y in combinations(images, 2)), 4)

    def test_doubled_cells_and_factorization_cells_coexist(self):
        allowed = {(0, 0), (1, 1), (1, 2), (2, 1), (2, 2)}
        _, _, _, weights = boundary_solution(allowed)
        self.assertEqual(weights[(0, 0)], 2)
        self.assertTrue(all(weights[a] == 1 for a in allowed - {(0, 0)}))
        blocks = source_from_weights(weights)
        self.assertEqual(len(blocks), 24)
        self.assertTrue(all(len(a & b) <= 2 for a, b in combinations(blocks, 2)))
        images = paired_images(blocks, SOURCE_PAIRS)
        self.assertEqual(len(images), 384)
        self.assertLessEqual(max(signed_dot(x, y) for x, y in combinations(images, 2)), 4)

    def test_all_d37_pair_divisions(self):
        root = Path(__file__).resolve().parents[1] / "constructions/codes/data"
        patch = json.loads((root / "d37_signed_patch.json").read_text())
        physical_pairs = [tuple(i-1 for i in pair) for pair in patch["pair_coordinates_1indexed"]]
        old = [sum(1 << i for i, bit in enumerate(row.strip()) if bit == "1")
               for row in (root / "d37_supports_binary.txt").read_text().splitlines()
               if row.strip() and not row.startswith("#")]
        retained = [mask for i, mask in enumerate(old) if i not in patch["triple_indices_0based"]]
        capacities = Counter()
        for left in combinations(range(6), 3):
            if 0 not in left:  # Identify a division with its left/right reversal.
                continue
            right = tuple(i for i in range(6) if i not in left)
            order = left + right
            pairs = [physical_pairs[i] for i in order]
            allowed = set()
            for row, col in CELLS:
                source_pair_indices = list(PAIR_TYPES[row]) + [i+3 for i in PAIR_TYPES[col]]
                support = sum(1 << axis for i in source_pair_indices for axis in pairs[i])
                if all((support & mask).bit_count() <= 4 for mask in retained):
                    allowed.add((row, col))
            matching, _, _, _ = boundary_solution(allowed)
            result = solve_type_boundary(sorted(allowed))
            blocks = result["blocks"]
            self.assertEqual(len(blocks), 8*len(allowed)-4*len(matching))
            images = paired_images(blocks, pairs)
            self.assertEqual(len(images), 16*len(blocks))
            self.assertLessEqual(max(signed_dot(x, y) for x, y in combinations(images, 2)), 4)
            self.assertTrue(all((support & mask).bit_count() <= 4
                                for support in {support for support, _ in images} for mask in retained))
            capacities[len(images)] += 1
        self.assertEqual(capacities, Counter({512: 4, 448: 4, 384: 2}))

    def test_input_domain(self):
        for invalid in ([(3, 0)], [(-1, 0)], [(0,)], [(0, 1, 2)], [(True, 1)], ["01"]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                solve_type_boundary(invalid)
        self.assertEqual(solve_type_boundary([])["capacity"], 0)
        self.assertEqual(solve_type_boundary([(0, 0), (0, 0)])["capacity"], 8)


if __name__ == "__main__":
    unittest.main()
