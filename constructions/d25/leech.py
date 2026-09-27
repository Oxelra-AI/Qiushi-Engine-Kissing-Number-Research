"""Leech lattice minimal vectors, norm^2 = 32 (Cohn's scaling)."""
import numpy as np, itertools, collections, os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from golay import golay24

_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'leech196560.npy')

def build():
    G = golay24()
    assert dict(collections.Counter(G.sum(1).tolist())) == {0:1,8:759,12:2576,16:759,24:1}
    octads = G[G.sum(1)==8]
    out = []
    for i,j in itertools.combinations(range(24),2):
        for si in (4,-4):
            for sj in (4,-4):
                v=np.zeros(24,dtype=np.int8); v[i]=si; v[j]=sj; out.append(v)
    signs = [m for m in range(256) if bin(m).count('1')%2==0]
    for oc in octads:
        pos=np.nonzero(oc)[0]
        for m in signs:
            v=np.zeros(24,dtype=np.int8)
            for t,p in enumerate(pos): v[p] = -2 if (m>>t)&1 else 2
            out.append(v)
    base_all = np.where(G==1, -1, 1).astype(np.int8)
    for ci in range(4096):
        base = base_all[ci]; c = G[ci]
        for j in range(24):
            v = base.copy()
            v[j] = 3 if c[j]==1 else -3
            out.append(v)
    A = np.array(out, dtype=np.int8)
    assert A.shape == (196560,24), A.shape
    n2 = (A.astype(np.int32)**2).sum(1)
    assert (n2==32).all()
    assert len(set(map(tuple,A.tolist())))==196560
    return A

def load():
    if os.path.exists(_CACHE):
        return np.load(_CACHE)
    A = build()
    os.makedirs(os.path.dirname(_CACHE), exist_ok=True)
    np.save(_CACHE, A)
    return A

if __name__=="__main__":
    A=load()
    print("shape",A.shape)
    # inner product distribution from a fixed vector
    for idx in (0, 2000, 150000):
        d = A.astype(np.int32) @ A[idx].astype(np.int32)
        print(idx, sorted(collections.Counter(d.tolist()).items()))
