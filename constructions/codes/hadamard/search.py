#!/usr/bin/env python3
"""Reconstruct the two weight-four sources and search their coordinate pairings."""
import json
from itertools import combinations, product
from pathlib import Path


def quadruple_system():
    """Construct S(3,4,10) by a deterministic exact cover of its triples."""
    triples = list(combinations(range(10), 3))
    positions = {triple: i for i, triple in enumerate(triples)}
    blocks = list(combinations(range(10), 4))
    masks = [sum(1 << positions[t] for t in combinations(block, 3)) for block in blocks]
    candidates = [[i for i, mask in enumerate(masks) if mask >> j & 1]
                  for j in range(len(triples))]
    full = (1 << len(triples)) - 1

    def extend(covered, selected):
        if covered == full:
            return selected
        legal = None
        for j in range(len(triples)):
            if covered >> j & 1:
                continue
            available = [i for i in candidates[j] if not masks[i] & covered]
            if legal is None or len(available) < len(legal):
                legal = available
                if len(legal) <= 1:
                    break
        for i in legal:
            answer = extend(covered | masks[i], selected + [i])
            if answer is not None:
                return answer
        return None

    indices = extend(masks[0], [0])
    if indices is None:
        raise ValueError("No quadruple system found")
    result = [blocks[i] for i in indices]
    counts = {triple: 0 for triple in triples}
    for block in result:
        for triple in combinations(block, 3):
            counts[triple] += 1
    if len(result) != 30 or set(counts.values()) != {1}:
        raise ValueError("Invalid Steiner quadruple system")
    return result


def one_factors():
    """A one-factorization of K6 in the stored coordinate order."""
    order = list(range(5))
    factors = []
    for _ in range(5):
        factors.append([tuple(sorted((order[0], 5)))] +
                       [tuple(sorted((order[i], order[-i]))) for i in (1, 2)])
        order = order[-1:] + order[:-1]
    if len({edge for factor in factors for edge in factor}) != 15:
        raise ValueError("Invalid one-factorization")
    return factors


def twelve_coordinate_code():
    """The Kalbfleisch--Stanton 51-block source, from two factorizations of K6."""
    factors = one_factors()
    blocks = [tuple(sorted(set(range(6)) - set(edge))) for edge in factors[0]]
    blocks += [tuple(i + 6 for i in block) for block in blocks[:3]]
    blocks += [tuple(sorted(left + tuple(i + 6 for i in right)))
               for factor in factors for left in factor for right in factor]
    return blocks


def direct_twelve_coordinate_code():
    """Choose one colour as pairs and the other four as transverse blocks."""
    left_pairs = ((0, 1), (2, 4), (3, 5))
    factors = one_factors()
    colour = next(i for i, factor in enumerate(factors) if set(factor) == set(left_pairs))
    pairing = left_pairs + tuple((a + 6, b + 6) for a, b in left_pairs)
    blocks = [tuple(sorted(left + tuple(i + 6 for i in right)))
              for i, factor in enumerate(factors) if i != colour
              for left in factor for right in factor]
    if len(blocks) != 36 or any(len(set(a) & set(b)) > 2 for a, b in combinations(blocks, 2)):
        raise ValueError("Invalid direct transverse construction")
    if any(set(pair) <= set(block) for block in blocks for pair in pairing):
        raise ValueError("A directly selected block is not transverse")
    return pairing, blocks


def matchings(items):
    items = tuple(items)
    if not items:
        yield ()
        return
    first, rest = items[0], items[1:]
    for i, second in enumerate(rest):
        for tail in matchings(rest[:i] + rest[i + 1:]):
            yield ((first, second),) + tail


def optimize(blocks, coordinates):
    masks = [sum(1 << i for i in block) for block in blocks]
    if len(set(masks)) != len(masks) or any((a & b).bit_count() > 2
                                           for a, b in combinations(masks, 2)):
        raise ValueError("Invalid weight-four source")
    best, best_pairing, examined = [], None, 0
    for pairing in matchings(range(coordinates)):
        examined += 1
        pairs = [(1 << a) | (1 << b) for a, b in pairing]
        retained = [block for block, mask in zip(blocks, masks)
                    if all(mask & pair != pair for pair in pairs)]
        if len(retained) > len(best):
            best, best_pairing = retained, pairing
    return best_pairing, best, examined


def reconstruct(root=None):
    root = Path(root) if root else Path(__file__).resolve().parent
    results = []
    for dimension, size, blocks, expected in (
            (35, 10, quadruple_system(), 16), (36, 12, twelve_coordinate_code(), 36)):
        pairing, selected, examined = optimize(blocks, size)
        if len(selected) != expected:
            raise ValueError("Unexpected transversal count")
        if dimension == 36:
            direct_pairing, direct_blocks = direct_twelve_coordinate_code()
            if pairing != direct_pairing or set(selected) != set(direct_blocks):
                raise ValueError("Direct four-colour construction differs from the stored pairing")
        certificate = json.loads((root / "data" / f"d{dimension}_construction.json").read_text())
        region = certificate["chamber"]["W"][:size]
        pair_for = {coordinate: (a, b) for a, b in pairing for coordinate in (a, b)}
        generated = set()
        for block in selected:
            for signs in product((-1, 1), repeat=4):
                vector = [0] * dimension
                for coordinate, sign in zip(block, signs):
                    a, b = pair_for[coordinate]
                    vector[region[a]] = sign
                    vector[region[b]] = sign if coordinate == a else -sign
                support = sum(1 << i for i, value in enumerate(vector) if value)
                negative = sum(1 << i for i, value in enumerate(vector) if value < 0)
                generated.add((support, negative))
        stored = {(int(row["support_hex"], 16), int(row["sign_hex"], 16))
                  for row in certificate["added_signed_vectors"]}
        if generated != stored:
            raise ValueError("Regenerated signed code differs from the certificate")
        results.append({"dimension": dimension, "source_blocks": len(blocks),
                        "matchings_examined": examined, "transverse_blocks": len(selected),
                        "pairing": pairing, "points": len(generated),
                        "matches_certificate": True})
        if dimension == 36:
            results[-1]["direct_four_colour_construction_matches"] = True
    return results


if __name__ == "__main__":
    print(json.dumps(reconstruct(), indent=2))
