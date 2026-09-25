#!/usr/bin/env python3
"""Exact 35D/36D signed construction check.

Only Python integers and the supplied finite inputs are used.
"""
import argparse
from datetime import datetime, timezone
from itertools import combinations, product
from math import comb
from pathlib import Path
import hashlib
import json
from search import reconstruct


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(root):
    data = root / 'data'
    source_reconstruction = reconstruct(root)
    generators = json.loads((data/'generators.json').read_text())['dimensions']
    top = json.loads((data/'top_code.json').read_text())
    rows = top['generator_matrix']
    require(len(rows) == 17 and all(len(r) == 32 and all(type(b) is int and b in (0,1) for b in r) for r in rows), 'Bad top generator')
    words = {0}
    for row in rows:
        mask = sum(b << j for j,b in enumerate(row))
        words |= {w ^ mask for w in words}
    require(len(words) == 2**17, 'Top rank is not 17')
    distance = min(w.bit_count() for w in words if w)
    require(distance >= 8, 'Top minimum distance below 8')
    results = []
    for dim, expected in [(35,409676),(36,484760)]:
        path = data/f'd{dim}_construction.json'
        cert = json.loads(path.read_text())
        old = [int(x,16) for x in cert['old_supports_hex']]
        raw_path = Path(cert['source_support_file'])
        require(not raw_path.is_absolute() and '..' not in raw_path.parts, 'Bad source path')
        raw = (root/raw_path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == cert['source_support_sha256'], 'Source hash mismatch')
        parsed = [int(s.strip(),16) for s in raw.decode().splitlines() if s.strip() and not s.strip().startswith(('$','#'))]
        require(parsed == old and len(set(old)) == len(old), 'Support list mismatch or duplicates')
        require(all(0 <= u < 1 << dim and u.bit_count()==8 for u in old), 'Illegal old support')
        old_ip = max((u&v).bit_count() for u,v in combinations(old,2))
        require(old_ip <= 4, 'Old support intersection exceeds 4')
        W = cert['chamber']['W']
        require(len(set(W)) == len(W) and set(W) <= set(range(dim)), 'Bad chamber')
        Wmask = sum(1 << i for i in W)
        deleted = set(cert['chamber']['delete_old_support_indices'])
        require(deleted == {i for i,u in enumerate(old) if u&~Wmask==0}, 'Wrong deleted supports')
        retained = [u for i,u in enumerate(old) if i not in deleted]
        require(max((u&Wmask).bit_count() for u in retained) <= 4, 'Chamber not isolated')
        new = [(int(v['support_hex'],16),int(v['sign_hex'],16)) for v in cert['added_signed_vectors']]
        require(len(set(new)) == len(new), 'Duplicate new vectors')
        require(all(0 <= u < 1<<dim and u.bit_count()==8 and u&~Wmask==0 and s>=0 and s&~u==0 for u,s in new), 'Illegal new vectors')
        generator = generators[str(dim)]
        pairs = generator['coordinate_pairs_zero_based']
        used = [i for pair in pairs for i in pair]
        require(all(len(pair)==2 for pair in pairs) and len(used)==len(set(used)), 'Coordinate pairing')
        require(set(used)<=set(W), 'Paired coordinates outside the local region')
        require(sorted(set(W)-set(used))==generator['unused_chamber_coordinates'], 'Unused coordinates')
        four_subsets = [tuple(row) for row in generator['transverse_supports']]
        require(len(four_subsets)==len(set(four_subsets))=={35:16,36:36}[dim], 'Transverse support count')
        require(all(len(row)==len(set(row))==4 and set(row)<=set(range(len(used)))
                    and len({i//2 for i in row})==4 for row in four_subsets), 'Transversality')
        require(all(len(set(a)&set(b))<=2 for a,b in combinations(four_subsets,2)), 'Weight-four intersection')
        generated = set()
        for support in four_subsets:
            for signs in product((-1,1), repeat=4):
                values = [0]*dim
                for axis, sign in zip(support, signs):
                    a,b = pairs[axis//2]
                    values[a],values[b] = sign, sign if axis%2==0 else -sign
                mask = sum(1<<i for i,v in enumerate(values) if v)
                negative = sum(1<<i for i,v in enumerate(values) if v<0)
                generated.add((mask,negative))
        require(len(generated)==16*len(four_subsets) and generated==set(new), 'Hadamard reconstruction')
        new_ip = max((u&v).bit_count()-2*((s^t)&u&v).bit_count() for (u,s),(v,t) in combinations(new,2))
        cross = max((u&v).bit_count() for u,s in new for v in retained)
        require(new_ip <= 4 and cross <= 4, 'New pair incompatibility')
        require(not {u for u,s in new}.intersection(retained), 'New vectors duplicate retained layer')
        # All actual vectors have norm^2=32: top has 32 entries +/-1,
        # middle has eight +/-2, bottom has two +/-4. Retained middle
        # supports use all 128 even-parity sign words (distance >=2).
        # The bounds below cover every same-layer and cross-layer pair.
        bounds = {'top_top':32-2*distance, 'same_retained_support':32-8*2,
                  'different_retained_supports':4*old_ip, 'new_new':4*new_ip,
                  'new_retained':4*cross, 'bottom_bottom':16,
                  'top_middle':8*2, 'top_bottom':2*4, 'middle_bottom':2*2*4}
        require(max(bounds.values()) <= 16, 'Kissing condition failed')
        baseline = len(words)+128*len(old)+4*comb(dim,2)
        total = len(words)+128*len(retained)+len(new)+4*comb(dim,2)
        require(total == expected == cert['arithmetic']['new_total'], 'Wrong cardinality')
        results.append({'dimension':dim,'points':total,'baseline':baseline,'gain':total-baseline,
                        'transverse_supports':len(four_subsets),'hadamard_reconstruction_matches':True,
                        'removed':128*len(deleted),'added':len(new),'all_checks_pass':True,
                        'old_support_pairs':comb(len(old),2),'new_pairs':comb(len(new),2),
                        'new_retained_support_pairs':len(new)*len(retained),
                        'pair_inner_product_upper_bounds':bounds})
    return {'checked_at_utc':datetime.now(timezone.utc).isoformat(),'all_checks_pass':True,
            'source_reconstruction':source_reconstruction,
            'top_code':{'size':len(words),'minimum_distance':distance},'results':results,
            'scope':'Exact verification of the two supplied signed constructions.'}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parent
    if args.output.resolve().is_relative_to(root):
        parser.error('Write verification output outside the frozen package')
    result=verify(root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result,stream,indent=2)
    print(json.dumps(result,indent=2))
