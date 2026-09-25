#!/usr/bin/env python3
"""Stream every point as an integer direction / sqrt(squared norm), exactly."""
import argparse
import itertools
import json
from pathlib import Path
from reference_checker import read_hex_file, rref, span_words

ROOT=Path(__file__).resolve().parent


def points(claim):
    n,n0=claim['dimension'],claim['top_length']
    kernel=span_words(rref(read_hex_file(ROOT/claim['kernel_file']),n0))
    for r in read_hex_file(ROOT/claim['representatives_file']):
        for word in kernel:
            yield dict(support=list(range(n0)),signs=[-1 if ((r^word)>>i)&1 else 1 for i in range(n0)],q=n0)
    for word in read_hex_file(ROOT/claim['support_file']):
        support=[i for i in range(n) if (word>>i)&1]
        for sign in range(256):
            if sign.bit_count()%2==0:
                yield dict(support=support,signs=[-1 if (sign>>i)&1 else 1 for i in range(8)],q=8)
    for i,j in itertools.combinations(range(n),2):
        for a,b in itertools.product((-1,1),repeat=2):
            yield dict(support=[i,j],signs=[a,b],q=2)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dimension',type=int,choices=[33,34,37,38,39],required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--limit',type=int,help='Preview only; omitted means all points')
    args=parser.parse_args()
    if args.limit is not None and args.limit<1:
        parser.error('--limit must be positive')
    claim=next(c for c in json.loads((ROOT/'data/claims.json').read_text()) if c['dimension']==args.dimension)
    source=points(claim)
    if args.limit is not None:
        source=itertools.islice(source,args.limit)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    count=0
    with args.output.open('x') as stream:
        stream.write(json.dumps(dict(dimension=args.dimension,representation='signed integer direction divided by sqrt(q)',
                                     preview=args.limit is not None))+'\n')
        for count,point in enumerate(source,1):
            stream.write(json.dumps(point,separators=(',',':'))+'\n')
    if args.limit is None and count!=claim['lower_bound']:
        raise ValueError('Generated point count differs from claim')
    print(json.dumps(dict(points=count,preview=args.limit is not None)))
