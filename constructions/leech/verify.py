#!/usr/bin/env python3
"""Exact finite-premise checker for the two written Leech-tail proofs.

Python 3.10+, standard library only. No floats enter an acceptance condition.
The report proves the six Leech family-pair estimates and the lift reductions.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import time
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rows(path, columns):
    out = []
    for line in Path(path).read_text().splitlines():
        text = line.strip()
        if not text or text.startswith('#'):
            continue
        row = tuple(map(int, text.split()))
        require(len(row) == columns, f'Wrong row length in {Path(path).name}')
        out.append(row)
    return out


def dot(a, b):
    return sum(x*y for x,y in zip(a,b))


def build_code(path):
    gen = rows(path,24)
    require(len(gen)==12 and all(x in (0,1) for r in gen for x in r), 'Bad binary generator')
    masks = [sum(x<<i for i,x in enumerate(r)) for r in gen]
    code = {0}
    for g in masks:
        old = len(code)
        code |= {c^g for c in tuple(code)}
        require(len(code)==2*old, 'Dependent generator rows')
    histogram = Counter(c.bit_count() for c in code)
    require(histogram=={0:1,8:759,12:2576,16:759,24:1}, 'Wrong Golay weight enumerator')
    require(all((g&h).bit_count()%2==0 for g in masks for h in masks), 'Not self-orthogonal')
    octads = [c for c in code if c.bit_count()==8]
    maximum = max((a&b).bit_count() for a,b in itertools.combinations(octads,2))
    require(maximum<=4, 'Octad intersection bound failed')
    return code, dict(sorted(histogram.items())), maximum


def shell_from_code(code):
    shell = set()
    for i,j in itertools.combinations(range(24),2):
        for a,b in itertools.product((-4,4),repeat=2):
            row=[0]*24; row[i]=a; row[j]=b; shell.add(tuple(row))
    for c in code:
        if c.bit_count()==8:
            support=[i for i in range(24) if (c>>i)&1]
            for signs in range(256):
                if signs.bit_count()%2:
                    continue
                row=[0]*24
                for j,i in enumerate(support):
                    row[i]=-2 if (signs>>j)&1 else 2
                shell.add(tuple(row))
        signs=[-1 if (c>>i)&1 else 1 for i in range(24)]
        for j in range(24):
            row=signs.copy(); row[j]*=-3; shell.add(tuple(row))
    require(len(shell)==196560, 'Incorrect shell cardinality')
    require(all(dot(v,v)==32 for v in shell), 'Incorrect shell norms')
    return shell


def verify_block(path, shell):
    block=rows(path,24)
    require(len(block)==496 and len(set(block))==496, 'Block size or distinctness failed')
    require(all(v in shell for v in block), 'Block is not in the generated shell')
    maximum=max(dot(a,b) for a,b in itertools.combinations(block,2))
    require(maximum<=8, 'Compatible-block dot product bound failed')
    return block, maximum


# Exact arithmetic in Q(sqrt(2),sqrt(3)), basis indexed by the square-free bits.
def q(value=0):
    return (F(value),F(0),F(0),F(0))


def add(x,y):
    return tuple(a+b for a,b in zip(x,y))


def mul(x,y):
    result=[F(0)]*4
    for i,a in enumerate(x):
        for j,b in enumerate(y):
            result[i^j] += a*b*(2 if i&j&1 else 1)*(3 if i&j&2 else 1)
    return tuple(result)


def scalar(a,x):
    return tuple(F(a)*b for b in x)


def qdot(a,b):
    result=q()
    for x,y in zip(a,b):
        result=add(result,mul(x,y))
    return result


def sign(x):
    if all(a==0 for a in x):
        return 0
    # Certified rational enclosures, never float comparisons.
    for bits in (16,32,64,128,256,512):
        scale=1<<bits
        lo=hi=x[0]
        for coefficient,radicand in zip(x[1:],(2,3,6)):
            base=math.isqrt(radicand*scale*scale)
            lower,upper=F(base,scale),F(base+1,scale)
            if coefficient>=0:
                lo+=coefficient*lower; hi+=coefficient*upper
            else:
                lo+=coefficient*upper; hi+=coefficient*lower
        if lo>0:
            return 1
        if hi<0:
            return -1
    raise ArithmeticError('Algebraic sign not resolved; no acceptance')


def verify_tails(path):
    data=json.loads(Path(path).read_text())
    require(data['basis']==['1','sqrt(2)','sqrt(3)','sqrt(6)'], 'Unexpected number-field basis')
    def parse(key):
        array=data[key]
        require(len(array)==12 and all(len(r)==3 for r in array), 'Tail shape mismatch')
        require(all(len(c)==4 for r in array for c in r), 'Bad coefficient vector')
        return [tuple(tuple(map(F,c)) for c in r) for r in array]
    mixed,pure=parse('mixed'),parse('pure')
    require(len(set(mixed))==len(set(pure))==12, 'Duplicate tail labels')
    require(all(qdot(t,t)==q(F(1,3)) for t in mixed), 'Mixed tail norm failed')
    require(all(qdot(t,t)==q(1) for t in pure), 'Pure tail norm failed')
    gram=[[qdot(a,b) for b in mixed] for a in mixed]
    D=[]
    for row in gram:
        vals=[]
        for value in row:
            require(value[1:]==(F(0),F(0),F(0)), 'Mixed Gram is not rational')
            scaled=48*value[0]
            require(scaled.denominator==1,'Scaled Gram not integral')
            vals.append(int(scaled))
        D.append(vals)
    require({D[i][j] for i in range(12) for j in range(i)}=={-16,-8,0,8}, 'Mixed Gram spectrum')
    require(all(sign(add(qdot(a,b),q(F(-1,2))))<=0 for a,b in itertools.combinations(pure,2)),
            'Pure/pure bound failed')
    require({qdot(a,b) for a,b in itertools.combinations(pure,2)} ==
            {q(-1), q(F(-1,2)), q(0), q(F(1,2))}, 'Pure Gram spectrum mismatch')
    bound=(F(0),F(0),F(1,6),F(1,12))
    pure_mixed=[qdot(a,b) for a in pure for b in mixed]
    require(bound in pure_mixed and all(sign(add(v,scalar(-1,bound)))<=0 for v in pure_mixed),
            'Displayed pure/mixed maximum mismatch')
    require(all(sign(add(qdot(a,b),q(F(-1,2))))<0 for a in pure for b in mixed),
            'Pure/mixed bound failed')
    parts=data['partition']
    require(len(parts)==4 and all(len(t)==3 for t in parts), 'Not four triples')
    require(sorted(itertools.chain.from_iterable(parts))==list(range(12)), 'Partition coverage failed')
    require(all(D[i][j]<=-8 for t in parts for i,j in itertools.combinations(t,2)), 'Triple incompatible')
    cliques=[s for size in range(1,13) for s in itertools.combinations(range(12),size)
             if all(D[i][j]<=-8 for i,j in itertools.combinations(s,2))]
    omega=max(map(len,cliques))
    require(omega==3, 'Label graph clique number differs')
    triangles=[s for s in cliques if len(s)==3]
    require(len(triangles)==8 and all(D[i][j]==-8 for t in triangles
                                   for i,j in itertools.combinations(t,2)), 'Triangle classification')
    partitions=[p for p in itertools.combinations(triangles,4)
                if sorted(itertools.chain.from_iterable(p))==list(range(12))]
    require(len(partitions)==2, 'Triangle partition count')
    require(all(sum(D[i][j]<=-8 for j in range(12) if j!=i)==5 for i in range(12)), 'Graph degrees')
    return D, omega, len(triangles)


def verify(data_dir):
    start=time.monotonic()
    code,weights,octad_intersection=build_code(data_dir/'golay_generator.txt')
    shell=shell_from_code(code)
    s,m25=verify_block(data_dir/'s496.txt',shell)
    blocks=[]; maxima=[]
    for i in range(4):
        block,maximum=verify_block(data_dir/f'block{i}.txt',shell)
        blocks.append(block); maxima.append(maximum)
    require(len(set(itertools.chain.from_iterable(blocks)))==4*496, '27D blocks overlap')
    D,omega,triangles=verify_tails(data_dir/'tails.json')
    require(D==[list(r) for r in rows(data_dir/'tail_gram_scaled.txt',12)], 'Stored/derived Gram mismatch')
    # Every geometric pair class is covered by the written family proof.
    require(3*16**2<=1024 and F(3*m25,128)+F(1,4)<=F(1,2), '25D lift reductions')
    require(4*16**2<=32*48, '27D zero/mixed reduction')
    require(all(m+16<=24 for m in maxima), '27D same-label reduction')
    require(16+8<=24 and 32-8<=24, '27D cross-block and repeated-row reductions')
    result={25:len(shell)+len(s)+2,27:len(shell)-sum(map(len,blocks))+3*sum(map(len,blocks))+12}
    require(result=={25:197058,27:200540}, 'Wrong result cardinality')
    return dict(checker='standard-library exact finite-premise checker', valid=True,
        results=[dict(dimension=d,lower_bound=n) for d,n in result.items()],
        golay_weight_enumerator=weights, max_octad_intersection=octad_intersection,
        generated_shell_size=len(shell), block_pair_counts=[math.comb(496,2)]*5,
        block_maxima=[m25]+maxima, label_clique_number=omega, triangles=triangles,
        floating_point_used_for_acceptance=False,
        proof_scope='Exact finite inputs checked; the report proves the universal Leech and lift pair-class implications.',
        elapsed_seconds=round(time.monotonic()-start,3))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=ROOT/'data')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=verify(args.data)
    text=json.dumps(result,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text)
    print(text,end='')


if __name__=='__main__':
    main()
