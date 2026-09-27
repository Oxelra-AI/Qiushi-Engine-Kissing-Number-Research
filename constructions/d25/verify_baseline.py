"""Verify the inherited 197579-point configuration using exact arithmetic."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math
import time

import numpy as np
from leech import build

HERE = Path(__file__).resolve().parent


def radical_le(p,q):
    """p+q*sqrt(3) <= 0, for rational p,q."""
    if q==0:return p<=0
    if q>0:return p<0 and p*p>=3*q*q
    return p<=0 or p*p<=3*q*q


def radical_array_le(p,q):
    p=np.asarray(p,dtype=np.int64);q=np.asarray(q,dtype=np.int64)
    assert max(int(np.abs(p).max()),int(np.abs(q).max()))<10**8
    out=np.zeros(p.shape,dtype=bool)
    zero=q==0;positive=q>0;negative=q<0
    out[zero]=p[zero]<=0
    out[positive]=(p[positive]<0)&(p[positive]*p[positive]>=3*q[positive]*q[positive])
    out[negative]=(p[negative]<=0)|(p[negative]*p[negative]<=3*q[negative]*q[negative])
    return out


def radical36_nonnegative(a,b,c):
    """a+b*sqrt(3)+c*sqrt(6) >= 0 by rational interval refinement."""
    if not b and not c:return a>=0
    for bits in (32,64,128,256,512,1024):
        scale=1<<bits
        s3=math.isqrt(3*scale*scale);s6=math.isqrt(6*scale*scale)
        lower=a*scale+b*(s3 if b>=0 else s3+1)+c*(s6 if c>=0 else s6+1)
        upper=a*scale+b*(s3+1 if b>=0 else s3)+c*(s6+1 if c>=0 else s6)
        if lower>=0:return True
        if upper<0:return False
    raise ArithmeticError('radical sign unresolved')


def main(output=None):
    started=time.time()
    source=HERE/'baseline-heads.json'
    data=json.loads(source.read_text())
    heads=data['heads']
    assert len(heads)==1016 and [h['index'] for h in heads]==list(range(1016))
    M=build().astype(np.int64)
    assert M.shape==(196560,24) and np.all(np.sum(M*M,axis=1)==32)
    lookup={tuple(map(int,row)):i for i,row in enumerate(M)}
    assert len(lookup)==len(M)
    owners=np.array([h['owner'] for h in heads],dtype=np.int64)
    owner_ids=np.array([lookup[tuple(map(int,u))] for u in owners])
    assert len(set(owner_ids.tolist()))==1016
    classes=[h for h in heads if h['kind']=='class']
    rats=[h for h in heads if h['kind']=='rational']
    assert len(classes)==972 and len(rats)==44
    U=np.array([h['owner'] for h in classes],dtype=np.int64)
    V=np.array([h['lean'] for h in classes],dtype=np.int64)
    assert np.all(np.sum(U*U,axis=1)==32)
    assert np.all(np.sum(V*V,axis=1)==48)
    assert np.all(np.sum(U*V,axis=1)==-24)
    assert all(tuple(map(int,w)) in lookup for w in U+V)
    # t^2=t-1/6 proves each class head has Cohn squared norm 24.
    for start in range(0,972,16):
        A=U[start:start+16]@M.T;B=V[start:start+16]@M.T
        assert np.all(A%8==0) and np.all(B%8==0)
        A//=8;B//=8
        valid=radical_array_le(6*A+3*B-12,-B)
        for row,head in zip(valid,classes[start:start+16]):
            owner=owner_ids[head['index']]
            assert not row[owner]
            row[owner]=True
        assert np.all(valid)
    A=U@U.T;B=U@V.T+V@U.T;C=V@V.T
    assert np.all(A%8==0) and np.all(B%8==0) and np.all(C%8==0)
    A//=8;B//=8;C//=8
    valid=radical_array_le(6*A+3*B+2*C-6,-B-C)
    np.fill_diagonal(valid,True)
    assert np.all(valid)

    nums=[];dens=[]
    scale=1<<40
    positive=np.maximum(M,0).sum(1)
    near_checks=0
    for head in rats:
        coordinates=[Fraction(q) for q in head['coordinates']]
        assert len(coordinates)==24
        denominator=math.lcm(*(q.denominator for q in coordinates))
        numerator=[int(q*denominator) for q in coordinates]
        assert sum(x*x for x in numerator)==24*denominator*denominator
        nums.append(numerator);dens.append(denominator)
        floors=np.array([(x*scale)//denominator for x in numerator],dtype=np.int64)
        assert int(np.abs(floors).max())*int(np.abs(M).sum(1).max())<2**62
        # Each coordinate lies in [floor/scale,(floor+1)/scale].
        upper=M@floors+positive
        possible=np.flatnonzero(upper>16*scale)
        owner=owner_ids[head['index']]
        assert owner in set(possible.tolist())
        for row in possible:
            product=sum(x*int(z) for x,z in zip(numerator,M[row]))
            if row==owner:assert product>16*denominator
            else:assert product<=16*denominator
        near_checks+=len(possible)
    for i in range(44):
        for j in range(i):
            assert sum(x*y for x,y in zip(nums[i],nums[j]))<=8*dens[i]*dens[j]
    for p,q in zip(nums,dens):
        for u,v in zip(U,V):
            a=sum(x*int(y) for x,y in zip(p,u))
            b=sum(x*int(y) for x,y in zip(p,v))
            assert radical_le(6*a+3*b-48*q,-b)

    g=np.array(data['extra_equator_lean'],dtype=np.int64)
    assert int(g@g)==48 and any(np.array_equal(g,v) for v in V)
    values=M@g
    assert np.all(values%8==0)
    assert values.min()==-24 and values.max()==24
    deleted=np.flatnonzero(values==-24)
    assert len(deleted)==552 and set(deleted.tolist())<=set(owner_ids.tolist())
    for u,v in zip(U,V):
        au=int(g@u);bv=int(g@v)
        assert au%8==0 and bv%8==0
        aa=au//8;bb=bv//8
        assert radical36_nonnegative(6*aa+3*bb,-bb,6)
    for p,q in zip(nums,dens):
        product=-sum(x*int(y) for x,y in zip(p,g))
        assert product<=0 or product*product<=384*q*q
    # All horizontal heads have norm^2 3 and same-cap products <=1.
    # Opposite-cap products <=2 follow from Cauchy; poles are direct.
    result={
        'baseline_verified':True,'points':197579,'class_heads':972,'rational_heads':44,
        'class_shell_comparisons':972*196560,'rational_shell_comparisons':44*196560,
        'rational_big_integer_checks':near_checks,
        'class_class_pairs':972*971//2,'rational_class_pairs':44*972,
        'rational_rational_pairs':44*43//2,'extra_equator_deletions':552,
        'shell_basis':'Golay enumeration of the Leech minimal shell; its lattice minimum gives mutual compatibility.',
        'floating_point_acceptance_decisions':0,
        'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'elapsed_seconds':time.time()-started}
    if output is not None:
        Path(output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':main()
