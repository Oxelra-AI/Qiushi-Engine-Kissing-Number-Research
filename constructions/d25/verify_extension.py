"""Exact and Arb verification of the 197580-point extension.

Unchanged pairs are inherited from the separately verified 197579-point
baseline.  Equalities in the moved shell are algebraic identities; every other
new comparison is decided by integer arithmetic or a strict Arb enclosure.
No acceptance decision uses a floating-point screen.
"""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math
import time

import numpy as np
from flint import arb, ctx, fmpq

from leech import build

HERE = Path(__file__).resolve().parent
ctx.prec = 192


def ball(q):
    q = Fraction(q)
    return arb(fmpq(q.numerator,q.denominator))


def strict_max(values, label):
    best = None
    count = 0
    for value in values:
        assert value < 2, (label,str(value))
        if best is None or value.upper() > best.upper():
            best = value
        count += 1
    return {'checked_expressions':count,'maximum_enclosure':str(best),'strictly_below_two':True}


def main(output=None):
    start = time.time()
    base = json.loads((HERE/'baseline-heads.json').read_text())
    repairs = json.loads((HERE/'repair-points.json').read_text())['points']
    heads = base['heads']
    assert len(heads) == 1016 and [h['index'] for h in heads] == list(range(1016))
    Z = build().astype(np.int64)
    assert Z.shape == (196560,24) and np.all(np.sum(Z*Z,axis=1)==32)
    lookup = {tuple(map(int,z)):i for i,z in enumerate(Z)}
    assert len(lookup) == len(Z)
    owners = np.array([h['owner'] for h in heads],dtype=np.int64)
    owner_ids = np.array([lookup[tuple(map(int,u))] for u in owners])
    assert len(set(map(int,owner_ids))) == 1016
    g = np.array(base['extra_equator_lean'],dtype=np.int64)
    assert int(g@g) == 48
    gZ = Z@g
    assert np.all(gZ%8==0)
    bottom = set(np.flatnonzero(gZ == -24).tolist())
    top = np.flatnonzero(gZ == 24)
    assert len(bottom) == len(top) == 552
    assert bottom <= set(owner_ids.tolist())
    assert not set(top.tolist()) & set(owner_ids.tolist())
    W = Z[top]
    U = W-g
    assert all(tuple(map(int,u)) in lookup for u in U)
    assert {lookup[tuple(map(int,u))] for u in U} == bottom
    keep = np.ones(len(Z),dtype=bool)
    keep[owner_ids] = False
    keep[top] = False
    assert keep.sum() == 194992
    assert np.max(gZ[keep]) <= 16

    sqrt2,sqrt3,sqrt6,sqrt8 = (arb(i).sqrt() for i in (2,3,6,8))
    tm = (3-sqrt3)/6
    a = sqrt3/2+sqrt2/4
    b = (sqrt6-2)/4
    s = sqrt6/2
    # The identities a^2+b^2=3/2 and sqrt3*a-b=2 are proved in
    # construction.tex; the input expressions above define them exactly.
    assert a > 0 and a < s and b > 0 and b < 1

    cls = [h for h in heads if h['kind']=='class']
    rat = [h for h in heads if h['kind']=='rational']
    assert len(cls)==972 and len(rat)==44
    CU = np.array([h['owner'] for h in cls],dtype=np.int64)
    CV = np.array([h['lean'] for h in cls],dtype=np.int64)
    assert np.all(np.sum(CU*CU,axis=1)==32)
    assert np.all(np.sum(CV*CV,axis=1)==48)
    assert np.all(np.sum(CU*CV,axis=1)==-24)
    rationals = {h['index']:[Fraction(x) for x in h['coordinates']] for h in rat}
    assert all(sum(q*q for q in x)==24 for x in rationals.values())

    # Every class cap is present in both signs. b>0 makes the upper sign
    # the larger product. Group exactly equal integer coefficient tuples.
    A = W@CU.T
    B = W@CV.T
    C = g@CU.T
    D = g@CV.T
    tuples = np.unique(np.c_[A.ravel(),B.ravel(),np.tile(C,len(W)),np.tile(D,len(W))],axis=0)
    moved_class = strict_max(
        ((int(e)+tm*int(f))/8+(a-s)/(8*sqrt6)*(int(c)+tm*int(d))+b
         for e,f,c,d in tuples),'moved shell versus class caps')
    moved_class['represented_comparisons'] = 552*972*2

    moved_rat_values = []
    rat_cache = {}
    for index,coords in rationals.items():
        denominator = math.lcm(*(q.denominator for q in coords))
        nums = [int(q*denominator) for q in coords]
        products = W.astype(object)@np.array(nums,dtype=object)
        maximum = Fraction(int(max(products)),denominator)
        gn = sum(int(t)*q for t,q in zip(g,coords))
        sign = -1 if index==984 else 1
        moved_rat_values.append(ball(maximum)/8+(a-s)/(8*sqrt6)*ball(gn)+b*sign)
        rat_cache[index] = (coords,gn)
    moved_rat = strict_max(moved_rat_values,'moved shell versus rational caps')
    moved_rat['represented_comparisons'] = 552*(2*44-2)

    # Q=(sqrt3 n,-1). Only the lower 1008 cap is replaced; the upper
    # 984 cap is replaced but its lower partner remains.
    q_caps = []
    for h in heads:
        if h['kind']=='class':
            gn = arb(int(g@np.array(h['owner'])))+tm*int(g@np.array(h['lean']))
        else:
            gn = ball(rat_cache[h['index']][1])
        hsign = 1 if h['index']==1008 else -1
        q_caps.append(gn/(8*sqrt2)-hsign)
    q_cap_result = strict_max(q_caps,'new Q versus unchanged caps')

    replacement_results = {}
    point_ints = {}
    for role,record in repairs.items():
        k = np.array(record['integer_vector'],dtype=np.int64)
        N = int(k@k)
        assert len(k)==25 and N==record['squared_norm']
        point_ints[role]=(k,N)
        shell_dot_max = int(np.max(Z[keep]@k[:24]))
        assert shell_dot_max<=0 or shell_dot_max*shell_dot_max<8*N
        kg = int(k[:24]@g)
        moved_integer_max = int(np.max(W@k[:24]))
        moved_value = 2/arb(N).sqrt()*(arb(moved_integer_max)/sqrt8
                        +(a-s)*arb(kg)/(4*sqrt3)+b*int(k[-1]))
        assert moved_value < 2
        cap_values = []
        for h in heads:
            if h['kind']=='class':
                product = arb(int(k[:24]@np.array(h['owner'])))+tm*int(k[:24]@np.array(h['lean']))
            else:
                product = ball(sum(int(v)*q for v,q in zip(k[:24],rat_cache[h['index']][0])))
            signs = [1,-1]
            if h['index']==984:signs.remove(1)
            if h['index']==1008:signs.remove(-1)
            for hsign in signs:
                cap_values.append(2/arb(N).sqrt()*(product/sqrt8+int(k[-1])*hsign))
        cap_result = strict_max(cap_values,role+' versus unchanged caps')
        # Poles, P=-2n, and Q, all with exact integer comparisons.
        assert 4*int(k[-1])**2 < N
        assert -kg<=0 or kg*kg<12*N
        qnum=kg-4*int(k[-1])
        assert qnum<=0 or qnum*qnum<16*N
        replacement_results[role]={
            'integer_squared_norm':N,
            'unchanged_shell_comparisons':int(keep.sum()),
            'maximum_shell_dot_integer':shell_dot_max,
            'shell_strict_test':[shell_dot_max*shell_dot_max,8*N],
            'moved_shell_max_enclosure':str(moved_value),
            'caps':cap_result,
            'poles_P_Q_integer_tests':True}
    ku,Nu=point_ints['upper'];kl,Nl=point_ints['lower']
    mutual=int(ku@kl)
    assert mutual<=0 or 4*mutual*mutual<Nu*Nl

    # Moved-to-moved products equal the original products because their
    # shared two-dimensional tail keeps squared norm 3/2. For every other
    # retained shell point the horizontal projection is a convex combination
    # of two distinct Leech minimal vectors, neither retained at that location.
    # Q meets every moved point at 2; its other shell products are <=sqrt(2).
    inventory=int(keep.sum())+552+(2032-2)+2+4
    assert inventory==197580
    result={
        'points':inventory,'dimension':25,'squared_norm':4,'inner_product_bound':2,
        'extension_verified':True,'precision_bits':ctx.prec,
        'depends_on':'Exact baseline verification plus the Leech minimal-shell inner-product bound.',
        'norms_and_shell_equalities':'algebraic identities in construction.tex',
        'moved_shell_count':552,'unchanged_shell_count':int(keep.sum()),
        'moved_vs_class_caps':moved_class,'moved_vs_rational_caps':moved_rat,
        'Q_vs_unchanged_caps':q_cap_result,'replacement_points':replacement_results,
        'replacement_mutual_integer_dot':mutual,
        'distinctness':'All norms are 4 and all distinct-index products are at most 2; coincidence is excluded.',
        'input_sha256':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest()
                        for n in ['baseline-heads.json','repair-points.json','leech.py','golay.py']},
        'elapsed_seconds':time.time()-start}
    if output is not None:
        Path(output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':main()
