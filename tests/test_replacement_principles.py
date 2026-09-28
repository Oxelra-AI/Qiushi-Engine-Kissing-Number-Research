"""Exact finite checks of replacement and shell-completion principles."""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def subsets(values):
    return (frozenset(part) for size in range(len(values) + 1)
            for part in combinations(values, size))


def signed_words(support, parity=None):
    """Represent a signed word by its support and negative-coordinate masks."""
    support = tuple(support)
    mask = sum(1 << i for i in support)
    for signs in range(1 << len(support)):
        if parity is None or signs.bit_count() % 2 == parity:
            negative = sum(1 << i for j, i in enumerate(support) if signs >> j & 1)
            yield mask, negative


def signed_dot(x, y):
    common = x[0] & y[0]
    return common.bit_count() - 2 * ((x[1] ^ y[1]) & common).bit_count()


def one_factors(t):
    """Round-robin one-factorization of the complete graph on 2t vertices."""
    ring = list(range(2 * t - 1))
    factors = []
    for _ in range(2 * t - 1):
        factors.append([(ring[0], 2 * t - 1)] +
                       [(ring[i], ring[-i]) for i in range(1, t)])
        ring = ring[-1:] + ring[:-1]
    return factors


def factors_with_pairs(pairs):
    """Relabel a round-robin factorization so factor zero is prescribed."""
    factors = one_factors(len(pairs))
    labels = {old: new for edge, pair in zip(factors[0], pairs)
              for old, new in zip(edge, pair)}
    return [tuple(frozenset(labels[i] for i in edge) for edge in factor)
            for factor in factors]


def transverse_family(left_pairs, right_pairs):
    left, right = factors_with_pairs(left_pairs), factors_with_pairs(right_pairs)
    edges_left = tuple(e for factor in left[1:] for e in factor)
    edges_right = tuple(e for factor in right[1:] for e in factor)
    family = frozenset((e, f) for a, b in zip(left[1:], right[1:])
                       for e in a for f in b)
    return edges_left, edges_right, family


def fibres(family, edges, side):
    return {edge: frozenset(pair[1-side] for pair in family if pair[side] == edge)
            for edge in edges}


def is_matching(edges):
    vertices = [v for edge in edges for v in edge]
    return len(vertices) == len(set(vertices))


def matching_number(edges):
    edges = frozenset(edges)

    @lru_cache(None)
    def visit(vertices):
        if not vertices:
            return 0
        v = min(vertices)
        choices = [visit(vertices - {v})]
        choices.extend(1 + visit(vertices - edge) for edge in edges
                       if v in edge and edge <= vertices)
        return max(choices)

    return visit(frozenset(v for edge in edges for v in edge))


def exchange_matching(neighbours):
    """Maximum bipartite matching and its alternating-path deficiency set."""
    right_to_left = {}

    def augment(left, seen):
        for right in sorted(neighbours[left]):
            if right in seen:
                continue
            seen.add(right)
            if right not in right_to_left or augment(right_to_left[right], seen):
                right_to_left[right] = left
                return True
        return False

    for left in neighbours:
        augment(left, set())
    reached_left = set(neighbours) - set(right_to_left.values())
    reached_right = set()
    pending = list(reached_left)
    while pending:
        left = pending.pop()
        for right in neighbours[left] - reached_right:
            reached_right.add(right)
            if right in right_to_left and right_to_left[right] not in reached_left:
                reached_left.add(right_to_left[right])
                pending.append(right_to_left[right])
    return right_to_left, reached_left, reached_right


def paired_images(blocks, coordinate_pairs):
    """Transfer source axes 2i,2i+1 to the supplied output pair i."""
    images = set()
    for block in blocks:
        for signs in product((-1, 1), repeat=4):
            support = negative = 0
            for axis, sign in zip(sorted(block), signs):
                a, b = coordinate_pairs[axis//2]
                support |= (1 << a) | (1 << b)
                if sign < 0:
                    negative |= 1 << a
                if sign * (-1 if axis % 2 else 1) < 0:
                    negative |= 1 << b
            images.add((support, negative))
    return images


class ReplacementPrinciples(unittest.TestCase):
    def test_exact_parity_bundle_boundary(self):
        candidates = list(signed_words(range(8)))
        for overlap in range(9):
            support = tuple(range(overlap)) + tuple(range(8, 16 - overlap))
            for parity in (0, 1):
                with self.subTest(overlap=overlap, parity=parity):
                    bundle = set(signed_words(support, parity))
                    self.assertEqual(len(bundle), 128)
                    for q in candidates:
                        maximum = max(signed_dot(q, s) for s in bundle)
                        expected = overlap if overlap < 8 else (
                            8 if q[1].bit_count() % 2 == parity else 6)
                        self.assertEqual(maximum, expected)
                        compatible = all(signed_dot(q, s) <= 4 for s in bundle - {q})
                        additive_count = len(bundle | {q}) == len(bundle) + 1
                        self.assertEqual(compatible and additive_count, overlap <= 4)

        even = set(signed_words(range(8), parity=0))
        duplicate, opposite_parity = (255, 0), (255, 1)
        self.assertIn(duplicate, even)
        self.assertEqual(max(signed_dot(duplicate, s) for s in even - {duplicate}), 4)
        self.assertEqual(max(signed_dot(opposite_parity, s) for s in even), 6)

    def test_selected_support_can_fit_a_nonisolated_region(self):
        region = set(range(12))
        old_support = {0, 1, 2, 3, 4, 12, 13, 14}
        new_support = {0, 1, 2, 3, 5, 6, 7, 8}
        self.assertEqual(len(region & old_support), 5)
        self.assertEqual(len(new_support & old_support), 4)
        self.assertTrue(new_support <= region)
        self.assertEqual(max(signed_dot(q, s)
                             for q in signed_words(new_support)
                             for s in signed_words(old_support, parity=0)), 4)

    def test_one_factorization_family(self):
        for t, expected in ((2, 128), (3, 576), (4, 1536)):
            with self.subTest(t=t):
                factors = one_factors(t)
                for factor in factors:
                    self.assertCountEqual([i for edge in factor for i in edge], range(2*t))
                self.assertEqual({frozenset(edge) for factor in factors for edge in factor},
                                 {frozenset(edge) for edge in combinations(range(2*t), 2)})
                pairing = factors[0] + [(a + 2*t, b + 2*t) for a, b in factors[0]]
                pair_for = {i: (a, b) for a, b in pairing for i in (a, b)}
                blocks = [left + tuple(i + 2*t for i in right)
                          for factor in factors[1:] for left in factor for right in factor]
                self.assertEqual(len(blocks), (2*t - 2)*t*t)
                self.assertLessEqual(max(len(set(a) & set(b))
                                         for a, b in combinations(blocks, 2)), 2)
                images = set()
                for block in blocks:
                    self.assertEqual(len({pair_for[i] for i in block}), 4)
                    for signs in product((-1, 1), repeat=4):
                        vector = [0] * (4*t)
                        for i, sign in zip(block, signs):
                            a, b = pair_for[i]
                            vector[a], vector[b] = sign, sign if i == a else -sign
                        images.add((sum(1 << i for i, v in enumerate(vector) if v),
                                    sum(1 << i for i, v in enumerate(vector) if v < 0)))
                self.assertEqual(len(images), expected)
                self.assertEqual(expected, 32*t*t*(t - 1))
                self.assertTrue(all(mask.bit_count() == 8 for mask, _ in images))
                self.assertLessEqual(max(signed_dot(a, b) for a, b in combinations(images, 2)), 4)

    def test_sharp_transverse_fibres(self):
        for t in (2, 3, 4):
            pairs = [(2*i, 2*i+1) for i in range(2*t)]
            left, right, family = transverse_family(pairs[:t], pairs[t:])
            with self.subTest(t=t):
                self.assertEqual(len(left), 2*t*(t-1))
                self.assertEqual(len(family), 2*t*t*(t-1))
                for edge_set, side in ((left, 0), (right, 1)):
                    for fibre in fibres(family, edge_set, side).values():
                        self.assertTrue(is_matching(fibre))
                        self.assertEqual(len(fibre), t)
                reduced = family - {next(iter(family))}
                self.assertFalse(all(len(f) == t for f in fibres(reduced, left, 0).values()))
                extra = next(p for p in product(left, right) if p not in family)
                enlarged = family | {extra}
                self.assertTrue(any(not is_matching(f)
                                    for f in fibres(enlarged, left, 0).values()))
                self.assertGreater(max(len((e | f) & (g | h))
                                       for (e, f), (g, h) in combinations(enlarged, 2)), 2)

        # Exhaustive equivalence and optimum in the smallest unrestricted model.
        left, right, _ = transverse_family([(0, 1), (2, 3)], [(4, 5), (6, 7)])
        maximum = 0
        for family in subsets(tuple(product(left, right))):
            direct = all(len((e | f) & (g | h)) <= 2
                         for (e, f), (g, h) in combinations(family, 2))
            local = all(is_matching(f) for f in fibres(family, left, 0).values()) and all(
                is_matching(f) for f in fibres(family, right, 1).values())
            self.assertEqual(direct, local)
            if direct:
                maximum = max(maximum, len(family))
        self.assertEqual(maximum, 8)

    def test_boundary_matching_and_mixed_cover(self):
        left, right, _ = transverse_family([(0, 1), (2, 3)], [(4, 5), (6, 7)])
        e0, f0 = left[0], right[0]
        allowed = {(e0, f) for f in right if f != f0} | {
            (e, f0) for e in left if e != e0}
        a = {e: matching_number(f) for e, f in fibres(allowed, left, 0).items()}
        b = {f: matching_number(e) for f, e in fibres(allowed, right, 1).items()}
        self.assertEqual((sum(a.values()), sum(b.values())), (5, 5))
        bounds = []
        for cover_left in subsets(left):
            cover_right = {f for e, f in allowed if e not in cover_left}
            bounds.append(sum(a[e] for e in cover_left) + sum(b[f] for f in cover_right))
        self.assertEqual(min(bounds), 4)
        optimum = max(len(family) for family in subsets(tuple(allowed))
                      if all(is_matching(f) for f in fibres(family, left, 0).values())
                      and all(is_matching(f) for f in fibres(family, right, 1).values()))
        self.assertEqual(optimum, 4)

    def test_local_perfect_matchings_do_not_ensure_global_equality(self):
        left, right, _ = transverse_family([(0, 1), (2, 3)], [(4, 5), (6, 7)])
        # The first two and last two edges are the two nonzero factors.
        allowed = {(left[0], f) for f in right[:2]} | {
            (left[1], f) for f in right[2:]} | {
            (e, f) for e in left[2:] for f in right}
        self.assertTrue(all(matching_number(f) == 2 for f in fibres(allowed, left, 0).values()))
        self.assertTrue(all(matching_number(e) == 2 for e in fibres(allowed, right, 1).values()))
        optimum = max(len(family) for family in subsets(tuple(allowed))
                      if all(is_matching(f) for f in fibres(family, left, 0).values())
                      and all(is_matching(e) for e in fibres(family, right, 1).values()))
        self.assertEqual(optimum, 6)
        self.assertLess(optimum, 8)

    def test_forbidden_pair_type_and_d37_fixed_boundary(self):
        data = ROOT / "constructions/codes/data"
        patch = json.loads((data / "d37_signed_patch.json").read_text())
        pairs = [tuple(i-1 for i in pair) for pair in patch["pair_coordinates_1indexed"]]
        old = [sum(1 << i for i, bit in enumerate(line.strip()) if bit == "1")
               for line in (data / "d37_supports_binary.txt").read_text().splitlines()
               if line.strip() and not line.startswith("#")]
        retained = [mask for i, mask in enumerate(old) if i not in patch["triple_indices_0based"]]
        pair_masks = [sum(1 << i for i in pair) for pair in pairs]
        all_types = set(combinations(range(6), 4))
        allowed_types = {kind for kind in all_types
                         if all((sum(pair_masks[i] for i in kind) & mask).bit_count() <= 4
                                for mask in retained)}
        forbidden_omissions = {frozenset(range(6)) - set(kind)
                               for kind in all_types - allowed_types}
        self.assertEqual(len(allowed_types), 12)
        self.assertEqual(forbidden_omissions,
                         {frozenset((0, 2)), frozenset((0, 5)), frozenset((2, 4))})
        region = sum(pair_masks)
        self.assertEqual(max((region & mask).bit_count() for mask in retained), 5)
        for half in combinations(range(6), 3):
            self.assertTrue(any(len(set(half) & edge) == 1 for edge in forbidden_omissions))

        left_indices, right_indices = (0, 2, 4), (1, 3, 5)
        source_pairs = [(2*i, 2*i+1) for i in range(6)]
        left, right, full = transverse_family([source_pairs[i] for i in left_indices],
                                               [source_pairs[i] for i in right_indices])
        type_of = lambda e, f: tuple(sorted({i//2 for i in e | f}))
        allowed = {(e, f) for e in left for f in right if type_of(e, f) in allowed_types}
        family = full & allowed
        self.assertEqual(len(full), 36)
        self.assertEqual(len(family), 32)
        row_capacities = [matching_number(f) for f in fibres(allowed, left, 0).values()]
        self.assertCountEqual(row_capacities, [2]*4 + [3]*8)
        self.assertEqual(sum(row_capacities), len(family))
        images = paired_images([e | f for e, f in family], pairs)
        self.assertEqual(len(images), 512)
        self.assertTrue(all(mask.bit_count() == 8 for mask, _ in images))
        self.assertLessEqual(max(signed_dot(x, y) for x, y in combinations(images, 2)), 4)
        self.assertTrue(all((support & mask).bit_count() <= 4
                            for support in {mask for mask, _ in images} for mask in retained))
        stored_types = {tuple(sorted({i//2 for i in row})) for row in patch["selected_yblocks"]}
        self.assertEqual(len(stored_types), 10)
        self.assertTrue(stored_types <= allowed_types)
        self.assertFalse(any(all(sum(i//2 in half for i in row) == 2
                                 for row in patch["selected_yblocks"])
                             for half in combinations(range(6), 3)))

    def test_exchange_matching_deficiency_exhaustively(self):
        edges = tuple(product(range(3), range(3)))
        for chosen in subsets(edges):
            neighbours = {i: {j for a, j in chosen if a == i} for i in range(3)}
            matching, reached, conflicts = exchange_matching(neighbours)
            optimum = max(len(pool) - len({j for i in pool for j in neighbours[i]})
                          for pool in subsets(tuple(neighbours)))
            self.assertEqual(optimum, 3 - len(matching))
            self.assertEqual(conflicts, {j for i in reached for j in neighbours[i]})
            self.assertEqual(len(reached) - len(conflicts), optimum)
        # Candidate-candidate conflicts invalidate the attainment assertion.
        neighbours = {0: {0}, 1: {0}}
        self.assertEqual(2-len(exchange_matching(neighbours)[0]), 1)
        self.assertEqual(max(len(pool)-len({j for i in pool for j in neighbours[i]})
                             for pool in (set(), {0}, {1})), 0)

    def test_stored_support_exchange_matching_certificates(self):
        root = ROOT / "constructions/codes"
        ledger = json.loads((root / "data/exchanges/exchanges.json").read_text())
        for entry in ledger["exchanges"]:
            with self.subTest(dimension=entry["dimension"]):
                old = {int(line, 16) for line in (root / entry["parent"]).read_text().splitlines()
                       if line.strip() and not line.lstrip().startswith(("#", "$"))}
                added = {int(mask, 16) for mask in entry["added_hex"]}
                removed = {int(mask, 16) for mask in entry["removed_hex"]}
                self.assertTrue(all((a & b).bit_count() <= 4 for a, b in combinations(added, 2)))
                neighbours = {a: {b for b in old if (a & b).bit_count() > 4} for a in sorted(added)}
                self.assertEqual({b for values in neighbours.values() for b in values}, removed)
                matching, pool, conflicts = exchange_matching(neighbours)
                self.assertEqual(len(matching), len(removed))
                self.assertEqual(len(pool)-len(conflicts), entry["final_size"]-entry["parent_size"])

    def test_shared_deletion_cost(self):
        half = Fraction(1, 2)
        old = frozenset(((1, 0), (-1, 0)))
        upper = (Fraction(3, 5), Fraction(4, 5))
        lower = (Fraction(3, 5), Fraction(-4, 5))
        close = (Fraction(4, 5), Fraction(3, 5))
        candidates = (upper, lower, close)
        weights = {(1, 0): 3, (-1, 0): 5, upper: 2, lower: 2, close: 2}
        weight = lambda points: sum(weights[p] for p in points)
        compatible = lambda points: all(dot(a, b) <= half for a, b in combinations(points, 2))
        conflicts = {q: {x for x in old if dot(q, x) > half} for q in candidates}
        self.assertTrue(set(candidates).isdisjoint(old))
        self.assertTrue(all(dot(p, p) == 1 for p in old | set(candidates)))
        self.assertTrue(compatible(old))
        self.assertEqual(conflicts[upper], conflicts[lower])
        shared = conflicts[upper] | conflicts[lower]
        self.assertEqual(shared, {(1, 0)})
        self.assertEqual(2 - len(shared), 1)
        self.assertEqual(sum(len(conflicts[q]) for q in (upper, lower)), 2)
        self.assertEqual(weight({upper, lower}) - weight(shared), 1)
        self.assertTrue(all(weight({q}) - weight(conflicts[q]) < 0 for q in (upper, lower)))

        for chosen in subsets(candidates):
            forbidden = {x for q in chosen for x in conflicts[q]}
            gains = []
            for deleted in subsets(old):
                result = (old - deleted) | chosen
                valid = compatible(result)
                self.assertEqual(valid, compatible(chosen) and forbidden <= deleted)
                if valid:
                    self.assertEqual(len(result) - len(old), len(chosen) - len(deleted))
                    gains.append(weight(result) - weight(old))
            if compatible(chosen):
                self.assertEqual(max(gains), weight(chosen) - weight(forbidden))
            else:
                self.assertFalse(gains)

    def test_automatic_shell_window(self):
        for scale in (1, 2):
            minimum = scale * scale
            heads = [tuple(scale * sign if i == axis else 0 for i in range(3))
                     for axis in range(3) for sign in (-1, 1)]
            vectors = [tuple(scale * x for x in row) for row in product(range(-2, 3), repeat=3)]
            for q in range(2 * minimum, 6 * minimum, minimum):
                self.assertGreater(Fraction(q - minimum, q), 0)
                for v in vectors:
                    b = dot(v, v)
                    if not minimum < b <= q:
                        continue
                    for u in heads:
                        self.assertLessEqual(2 * abs(dot(u, v)), b)
                        squared_product = Fraction(dot(u, v)**2, b * q)
                        self.assertLessEqual(squared_product, Fraction(1, 4))
                        if b < q:
                            self.assertLess(squared_product, Fraction(1, 4))
        self.assertEqual(Fraction(dot((1, 0), (1, 1))**2, 2 * 2), Fraction(1, 4))

    def test_shell_window_counterexamples(self):
        q, u = 2, (1,)
        for v, b in (((1,), 1), ((2,), 4)):
            with self.subTest(shell_norm=b):
                self.assertEqual(dot(v, v), b)
                self.assertFalse(1 < b <= q)
                self.assertGreater(Fraction(dot(u, v)**2, b * q), Fraction(1, 4))


if __name__ == "__main__":
    unittest.main()
