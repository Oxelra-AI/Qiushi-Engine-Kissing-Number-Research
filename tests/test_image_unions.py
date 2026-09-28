"""Orbitwise coverage and deterministic conditional-expectation selection."""
from fractions import Fraction
from itertools import combinations, product
from math import ceil
import unittest


def action(sizes):
    orbits, offset = [], 0
    for size in sizes:
        orbits.append(tuple(range(offset, offset + size)))
        offset += size
    group = []
    for shifts in product(*(range(size) for size in sizes)):
        image = {}
        for orbit, shift in zip(orbits, shifts):
            image.update((point, orbit[(i + shift) % len(orbit)])
                         for i, point in enumerate(orbit))
        group.append(image)
    return orbits, group


class OrbitImageUnions(unittest.TestCase):
    def test_existence_and_all_maximizing_choices(self):
        for sizes in ((5,), (2, 3), (1, 3)):
            orbits, group = action(sizes)
            size = sum(sizes)
            for count in range(size + 1):
                for source in combinations(range(size), count):
                    images = [frozenset(g[x] for x in source) for g in group]
                    miss = [1 - Fraction(len(set(source) & set(orbit)), len(orbit))
                            for orbit in orbits]
                    for steps in range(1, 4):
                        expected = sum(len(orbit) * (1 - q**steps)
                                       for orbit, q in zip(orbits, miss))
                        sizes_of_unions = [len(frozenset().union(*choice))
                                          for choice in product(images, repeat=steps)]
                        self.assertEqual(Fraction(sum(sizes_of_unions), len(sizes_of_unions)),
                                         expected)
                        self.assertGreaterEqual(max(sizes_of_unions), ceil(expected))

                        states = {frozenset()}
                        for chosen in range(steps):
                            following = set()
                            for union in states:
                                before = sum(len(orbit) - q**(steps-chosen)
                                             * (len(orbit) - len(union & set(orbit)))
                                             for orbit, q in zip(orbits, miss))
                                scores = [sum(q**(steps-chosen-1)
                                              * len((image - union) & set(orbit))
                                              for orbit, q in zip(orbits, miss))
                                          for image in images]
                                for image, score in zip(images, scores):
                                    if score != max(scores):
                                        continue
                                    updated = union | image
                                    after = sum(len(orbit) - q**(steps-chosen-1)
                                                * (len(orbit) - len(updated & set(orbit)))
                                                for orbit, q in zip(orbits, miss))
                                    self.assertGreaterEqual(after, before)
                                    following.add(updated)
                            states = following
                        self.assertTrue(all(len(union) >= ceil(expected) for union in states))


if __name__ == "__main__":
    unittest.main()
