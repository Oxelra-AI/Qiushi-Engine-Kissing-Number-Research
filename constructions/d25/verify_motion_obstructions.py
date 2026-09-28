"""Certify the two necessary cap changes in the fixed-Q chord family."""
from fractions import Fraction
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from flint import arb, ctx, fmpq

from leech import build

HERE = Path(__file__).resolve().parent


def check():
    ctx.prec = 192
    source = HERE / 'baseline-heads.json'
    data = json.loads(source.read_text())
    g = np.array(data['extra_equator_lean'], dtype=np.int64)
    shell = build().astype(np.int64)
    top = shell[shell @ g == 24]
    if top.shape != (552, 24):
        raise ValueError('Unexpected complete contact layer')
    sqrt2, sqrt3, sqrt6 = (arb(i).sqrt() for i in (2, 3, 6))
    a, b, h = sqrt3/2 + sqrt2/4, (sqrt6-2)/4, sqrt6/2

    def ball(value):
        q = Fraction(value)
        return arb(fmpq(q.numerator, q.denominator))

    obstructions = {}
    for index in (984, 1008):
        head = data['heads'][index]
        if head['index'] != index or head['kind'] != 'rational':
            raise ValueError('Unexpected head identity')
        coords = list(map(Fraction, head['coordinates']))
        if sum(q*q for q in coords) != 24:
            raise ValueError('Unexpected cap-head norm')
        g_dot = sum(int(v)*q for v, q in zip(g, coords))
        products = [sum(int(v)*q for v, q in zip(row, coords)) for row in top]
        maximum = max(products)
        moved = ball(maximum)/8 + (a-h)*ball(g_dot)/(8*sqrt6)+b
        inserted = ball(g_dot)/(8*sqrt2)+1
        if index == 984 and not moved > ball(Fraction(201, 100)):
            raise ValueError('Upper cap obstruction failed')
        if index == 1008 and not inserted > ball(Fraction(231, 100)):
            raise ValueError('Lower cap obstruction failed')
        obstructions[str(index)] = {
            'anchor_head_product': str(g_dot),
            'maximum_top_head_product': str(maximum),
            'moved_upper_at_contact': str(moved),
            'inserted_point_lower_product': str(inserted),
        }
    if not 1-sqrt6/5 > 0:
        raise ValueError('Monotonicity bound failed')
    return {'passed': True, 'minimum_cap_changes': 2, 'precision_bits': ctx.prec,
            'scope': 'Fixed inserted Q and the complete coordinated chord layer',
            'head_data_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'obstructions': obstructions}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = check()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
