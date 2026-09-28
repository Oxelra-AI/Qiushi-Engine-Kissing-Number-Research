"""Check endpoint contacts and the norm-64 obstruction without changing data."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'tools'))
from verify_dimension38 import golay_words, leech_membership, shell


def check():
    data = HERE / 'base-data'
    vectors, _ = shell(data)
    added_path = HERE / 'added-lines.txt'
    added = np.loadtxt(added_path, dtype=np.int64)
    if added.shape != (144, 24) or not np.all(np.sum(added*added, axis=1) == 48):
        raise ValueError('Unexpected added-line data')
    code = {tuple(map(int, row)) for row in golay_words(data)}
    if not all(leech_membership(v, code) for v in added):
        raise ValueError('Added line is outside the lattice')
    checked = 0
    for start in range(0, len(added), 16):
        rows = added[start:start+16]
        products = vectors @ rows.T
        if np.max(np.abs(products)) > 24 or np.any(products % 8):
            raise ValueError('Unexpected cross-shell inner product')
        normalized = products // 8
        for power, expected in ((2, 196560), (4, 544320), (6, 2332800)):
            if not np.all(np.sum(normalized**power, axis=0) == expected):
                raise ValueError('Spherical moment failed')
        for j, v in enumerate(rows):
            contacts = vectors[products[:, j] == 24]
            values = {tuple(map(int, u)) for u in contacts}
            partners = {tuple(map(int, v-u)) for u in contacts}
            if len(values) != 552 or values != partners:
                raise ValueError('Contact count or involution failed')
            if np.any(np.all(2*contacts == v, axis=1)):
                raise ValueError('Contact involution has a fixed point')
            checked += 1

    # General norm-eight moment calculation in the minimum-four scaling.
    moments, denominator, odd_factorial = {}, 1, 1
    for j in range(1, 5):
        denominator *= 24+2*(j-1)
        odd_factorial *= 2*j-1
        moments[2*j] = Fraction(196560*32**j*odd_factorial, denominator)
    expected_moments = {2: 262080, 4: 967680, 6: 5529600, 8: 41287680}
    if moments != expected_moments:
        raise ValueError('Norm-eight design moments failed')
    numerator = moments[8]-14*moments[6]+49*moments[4]-36*moments[2]
    if numerator != 1854720 or numerator/40320 != 46:
        raise ValueError('Norm-eight contact filter failed')

    # Independent finite check for one valid norm-64 vector; the design
    # argument, not this example, proves the result for every such vector.
    example = np.array([8]+[0]*23, dtype=np.int64)
    if not leech_membership(example, code):
        raise ValueError('Norm-64 example is outside the lattice')
    products = vectors @ example
    if any(np.sum((products//8)**power) != value
           for power, value in expected_moments.items()):
        raise ValueError('Norm-64 example moments failed')
    if np.count_nonzero(products == 32) != 46 or np.count_nonzero(products == -32) != 46:
        raise ValueError('Norm-64 example contact counts failed')
    return {'passed': True, 'checked_lines': checked,
            'contact_heads_per_oriented_line': 552,
            'old_cap_contacts_per_added_point': 1656,
            'total_new_point_old_cap_contacts': 2*checked*1656,
            'moments': {'2': 196560, '4': 544320, '6': 2332800},
            'norm64_obstruction': {
                'general_design_moments': expected_moments,
                'filter_numerator': 1854720, 'filter_denominator': 40320,
                'positive_extreme_heads': 46, 'negative_extreme_heads': 46,
                'old_cap_conflicts_per_endpoint': 138,
                'finite_example': example.tolist(),
                'finite_example_checked': True,
                'universal_scope': 'Spherical 11-design argument, not example enumeration'},
            'added_lines_sha256': hashlib.sha256(added_path.read_bytes()).hexdigest(),
            'golay_basis_sha256': hashlib.sha256((data/'golay_basis.txt').read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = check()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
