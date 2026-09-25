"""Check the 32- and 37-dimensional support and signed constructions."""
from pathlib import Path
from itertools import combinations, product
import argparse, hashlib, json
import reference_checker
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
report={}
top=reference_checker.verify_top(32,DATA/'d33_kernel.txt',DATA/'d33_representatives.txt')
assert top['valid_top_sign_code'] and top['top_size']==2**17 and top['top_min_distance']==8
def supports(path, n):
    rows = [s.strip() for s in path.read_text().splitlines() if s.strip() and not s.startswith('#')]
    assert all(len(s)==n and set(s)<=set('01') for s in rows)
    masks = [int(s,2) for s in rows]
    assert len(set(masks)) == len(masks) and all(x.bit_count()==8 for x in masks)
    hist = [0]*9
    for i,x in enumerate(masks):
        for y in masks[:i]:
            hist[(x&y).bit_count()] += 1
    assert sum(hist[5:]) == 0
    return masks, {'n':n,'count':len(masks),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'intersection_histogram':hist,'verified':True}

m32, report['d32'] = supports(DATA/'d32_supports_binary.txt',32)
assert len(m32)==1676
report['d32']['bound']=2**17+128*len(m32)+2*32*31

m37, report['d37'] = supports(DATA/'d37_supports_binary.txt',37)
patch=json.loads((DATA/'d37_signed_patch.json').read_text())
assert patch['base_seed_sha256']==report['d37']['sha256']
# Coordinates are numbered left to right in the binary support string.
base=[{i+1 for i,c in enumerate(format(x,'037b')) if c=='1'} for x in m37]
deleted=set(patch['triple_indices_0based']); assert len(deleted)==3
assert len(m37)==2845 and all(0<=i<len(base) for i in deleted)
Q=[]
for r in patch['vectors']:
    s=set(r['support_1indexed']);minus=set(r['negative_1indexed'])
    assert len(s)==8 and minus<=s and s<=set(range(1,38))
    Q.append(tuple(-1 if i in minus else 1 if i in s else 0 for i in range(1,38)))
assert len(Q)==len(set(Q))==512

# Rebuild the signed vectors from the stored transverse four-subsets.
pairs=patch['pair_coordinates_1indexed']
block=patch['block_1indexed']
assert len(pairs)==6 and all(len(pair)==2 for pair in pairs)
assert sorted(c for pair in pairs for c in pair)==sorted(block)
assert len(block)==len(set(block))==12 and set(block)<=set(range(1,38))
assert set().union(*(base[i] for i in deleted))==set(block)
yblocks=[tuple(row) for row in patch['selected_yblocks']]
assert len(yblocks)==len(set(yblocks))==32
for row in yblocks:
    assert len(row)==len(set(row))==4 and set(row)<=set(range(12))
    assert len({i//2 for i in row})==4
assert all(len(set(a)&set(b))<=2 for a,b in combinations(yblocks,2))
generated=[]
for row in yblocks:
    for signs in product((-1,1),repeat=4):
        vector=[0]*37
        for axis,sign in zip(row,signs):
            a,b=pairs[axis//2]
            vector[a-1]=sign
            vector[b-1]=sign if axis%2==0 else -sign
        generated.append(tuple(vector))
assert len(generated)==len(set(generated))==512 and set(generated)==set(Q)
assert all(sum(a*b for a,b in zip(x,y))<=4 for x,y in combinations(Q,2))
for q in Q:
    s={i+1 for i,x in enumerate(q) if x}
    assert all(len(s&b)<=4 for j,b in enumerate(base) if j not in deleted)
report['d37'].update(patch_points=len(Q),removed_bundles=len(deleted),bound=2**17+128*(len(m37)-3)+512+2*37*36,patch_verified=True,
                    hadamard_transverse_supports=len(yblocks),hadamard_generated_points=len(generated),
                    hadamard_reconstruction_matches=True)

args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
