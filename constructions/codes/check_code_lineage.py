#!/usr/bin/env python3
"""Reconstruct the QR mother code and compare exact binary row spaces.

Bit i is the coefficient of x**i. The parity coordinate is 47. No distance
claim about the mother code is assumed by the final construction checker.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPONENTS = (0, 1, 2, 3, 5, 6, 7, 9, 10, 12, 13, 14, 18, 19, 23)


def reduce_basis(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    for bit in sorted(pivots):
        for other in pivots:
            if other > bit and (pivots[other] >> bit) & 1:
                pivots[other] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def shorten(rows, zeros, keep):
    rows = list(reduce_basis(rows))
    for bit in zeros:
        pivot = next((i for i, row in enumerate(rows) if (row >> bit) & 1), None)
        if pivot is not None:
            base = rows.pop(pivot)
            rows = [row ^ base if (row >> bit) & 1 else row for row in rows]
    return reduce_basis(sum(((row >> bit) & 1) << i for i, bit in enumerate(keep))
                        for row in rows)


def read_masks(name):
    return [int(line, 16) for line in (ROOT / 'data' / name).read_text().splitlines()
            if line.strip() and not line.startswith(('#', '$'))]


def verify():
    public_rows = [(sum(int(bit) << i for i, bit in enumerate(line.strip())))
                   for line in (ROOT/'data/cheng_sloane_codetables_matrix.txt').read_text().splitlines()
                   if line.strip() and not line.startswith('#')]
    if len(public_rows) != 17:
        raise ValueError('Incomplete public Cheng-Sloane matrix')
    for dimension in (33,34,37):
        if read_masks(f'd{dimension}_kernel.txt') != public_rows:
            raise ValueError('Stored Cheng-Sloane rows differ from the cited public matrix')
    polynomial = sum(1 << i for i in EXPONENTS)
    # Polynomial division verifies the specified degree-23 cyclic factor.
    remainder = (1 << 47) | 1
    while remainder.bit_length() >= polynomial.bit_length():
        remainder ^= polynomial << (remainder.bit_length() - polynomial.bit_length())
    if remainder:
        raise ValueError('The printed polynomial does not divide x^47 + 1')
    mother = [polynomial << i for i in range(24)]
    mother = [row | ((row.bit_count() & 1) << 47) for row in mother]
    if len(reduce_basis(mother)) != 24:
        raise ValueError('Incorrect mother-code rank')
    kernel40 = shorten(mother, list(range(40, 48)), list(range(40)))
    expected39 = shorten(kernel40, [0], list(range(1, 40)))
    expected38 = shorten(kernel40, [0, 1], list(range(2, 40)))
    actual39 = reduce_basis(read_masks('d39_kernel.txt'))
    actual38 = reduce_basis(read_masks('d38_kernel.txt'))
    if expected39 != actual39 or expected38 != actual38:
        raise ValueError('Mother-code shortening does not reproduce the stored kernels')
    if shorten(actual39, [38], list(range(38))) != actual38:
        raise ValueError('The nested 39-to-38 shortening identity failed')
    return dict(valid=True, cheng_sloane_public_matrix='17 rows equal, bit 0 is leftmost column',
                binary_cyclic_polynomial_exponents=list(EXPONENTS),
                mother_length=48, mother_dimension=24, parity_coordinate=47,
                first_zero_coordinates=list(range(40,48)), intermediate_dimension=len(kernel40),
                kernel39_zero_coordinates_in_length40=[0],
                kernel38_zero_coordinates_in_length40=[0,1],
                equality='binary row spaces, in the stated retained-coordinate order',
                nested_kernel39_to_kernel38_zero_coordinate=38,
                final_kernel_dimensions=[len(actual38),len(actual39)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(verify(), indent=2) + '\n'
    if args.output:
        args.output.write_text(result)
    print(result, end='')
