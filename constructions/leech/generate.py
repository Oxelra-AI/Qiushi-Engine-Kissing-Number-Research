#!/usr/bin/env python3
"""Stream exact unit coordinates over Q(sqrt(2),sqrt(3)) as JSON lines.

Each coordinate is a four-entry rational string tuple in basis
(1,sqrt(2),sqrt(3),sqrt(6)). No decimal approximation is emitted.
"""
import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path
import verify as v

ROOT = Path(__file__).resolve().parent


def points(dimension):
    data = ROOT / 'data'
    code, _, _ = v.build_code(data/'golay_generator.txt')
    shell = sorted(v.shell_from_code(code))
    zero = v.q()
    if dimension == 25:
        block = v.rows(data/'s496.txt',24)
        used = set(block)
        for r in shell:
            if r not in used:
                yield [(F(0),F(x,8),F(0),F(0)) for x in r]+[zero]
        for h in [F(1,2), F(-1,2)]:
            for r in block:
                yield [(F(0),F(0),F(0),F(x,16)) for x in r]+[v.q(h)]
        for h in [1,-1]:
            yield [zero]*24+[v.q(h)]
    elif dimension == 27:
        blocks = [v.rows(data/f'block{i}.txt',24) for i in range(4)]
        used = set(itertools.chain.from_iterable(blocks))
        tails = json.loads((data/'tails.json').read_text())
        for r in shell:
            if r not in used:
                yield [(F(0),F(x,8),F(0),F(0)) for x in r]+[zero]*3
        for block, labels in zip(blocks,tails['partition']):
            for label in labels:
                for r in block:
                    yield [(F(0),F(0),F(x,12),F(0)) for x in r]+tails['mixed'][label]
        for tail in tails['pure']:
            yield [zero]*24+tail
    else:
        raise ValueError('Only dimensions 25 and 27 are in this project')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dimension',type=int,choices=[25,27],required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--limit',type=int,help='Preview only; omitted means every point')
    args=parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error('--limit must be positive')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    source=points(args.dimension)
    if args.limit is not None:
        source=itertools.islice(source,args.limit)
    count=0
    with args.output.open('x') as stream:
        stream.write(json.dumps(dict(dimension=args.dimension,basis=['1','sqrt(2)','sqrt(3)','sqrt(6)'],
                                     preview=args.limit is not None))+'\n')
        for count,row in enumerate(source,1):
            stream.write(json.dumps([[str(c) for c in x] for x in row],separators=(',',':'))+'\n')
    print(json.dumps(dict(points=count,preview=args.limit is not None)))
