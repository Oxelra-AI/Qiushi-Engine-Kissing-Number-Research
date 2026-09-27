#!/usr/bin/env python3
"""Independent exact verifier for algebraic-palette dimension-18 partial-fiber certificates.

This verifies certificates whose support fibers have integer residual coordinates
but whose hole residual coordinates may lie in Q(sqrt(3)), expressed as strings
such as 2*sqrt(3), -2/sqrt(3), or 4/sqrt(3).  A scalar is represented as
(A+B*sqrt(3))/3 with integer A,B.  Scaled inner products are compared exactly in
Q(sqrt(3)).

The supplied certificate gives K(18)>=8230.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import argparse, itertools, json, os, time
from collections import Counter, defaultdict
from typing import Iterable, Tuple, List, Dict
import numpy as np


def mask(cells: Iterable[Tuple[int, int]]) -> int:
    x=0
    for r,c in cells:
        x |= 1 << (4*r+c)
    return x

def wt(x:int)->int: return int(x).bit_count()
def inter(a:int,b:int)->int: return (int(a)&int(b)).bit_count()
def dot2(a:int,b:int)->int: return inter(a,b)&1

def bitstring(x:int)->str:
    return ''.join('1' if ((int(x)>>i)&1) else '0' for i in range(16))

def generate_C10()->List[int]:
    C=[]
    for x in range(1<<16):
        rows=[sum((x>>(4*r+c))&1 for c in range(4))&1 for r in range(4)]
        cols=[sum((x>>(4*r+c))&1 for r in range(4))&1 for c in range(4)]
        if len(set(rows))==1 and len(set(cols))==1 and rows[0]==cols[0]: C.append(x)
    return sorted(C)

def gf2_basis(words: Iterable[int])->List[int]:
    pivots: Dict[int,int]={}; indep=[]
    for w0 in sorted(int(w) for w in words):
        y=w0
        while y:
            p=y.bit_length()-1
            if p in pivots: y ^= pivots[p]
            else:
                pivots[p]=y; indep.append(w0); break
    return indep

def char_mask(q:int,basis:List[int])->int:
    m=0
    for i,b in enumerate(basis):
        if dot2(q,b): m |= 1<<i
    return m

def gf2_rank_ints(vecs: Iterable[int]) -> int:
    pivots = {}
    rank = 0
    for v0 in vecs:
        y = int(v0)
        while y:
            p = y.bit_length() - 1
            if p in pivots:
                y ^= pivots[p]
            else:
                pivots[p] = y
                rank += 1
                break
    return rank

def pair_supports()->List[int]:
    out=set()
    for rows in itertools.combinations(range(4),2): out.add(mask((r,c) for r in rows for c in range(4)))
    for cols in itertools.combinations(range(4),2): out.add(mask((r,c) for r in range(4) for c in cols))
    return sorted(out)

def square_supports()->List[int]:
    out=set(); allr=set(range(4)); allc=set(range(4))
    for rows in itertools.combinations(range(4),2):
        R=set(rows); Rc=allr-R
        for cols in itertools.combinations(range(4),2):
            C=set(cols); Cc=allc-C
            out.add(mask([(r,c) for r in R for c in C]+[(r,c) for r in Rc for c in Cc]))
    return sorted(out)

def cross_supports()->List[int]:
    out=set()
    for r0 in range(4):
        for c0 in range(4):
            out.add(mask([(r0,c) for c in range(4) if c!=c0]+[(r,c0) for r in range(4) if r!=r0]))
    return sorted(out)

def odd_minus_masks(q:int)->List[int]:
    pos=[i for i in range(16) if (q>>i)&1]
    out=[]
    for sub in range(1<<len(pos)):
        if sub.bit_count()&1:
            m=0
            for j,p in enumerate(pos):
                if (sub>>j)&1: m |= 1<<p
            out.append(m)
    return out

def sign_first_from_minus_mask(q:int, minus:int, scale:int)->np.ndarray:
    first=np.zeros(16,dtype=np.int16)
    for i in range(16):
        if (q>>i)&1:
            first[i] = -scale if ((minus>>i)&1) else scale
    return first

# Scalars in Q(sqrt(3)) are represented as (A,B) for (A+B sqrt(3))/3.
def scalar_int(n:int)->Tuple[int,int]: return (3*int(n),0)

def parse_scalar_expr(x)->Tuple[int,int]:
    if isinstance(x,(int,float)):
        if abs(float(x)-round(float(x)))>1e-12: raise ValueError(f'noninteger numeric scalar {x}')
        return scalar_int(int(round(float(x))))
    s=str(x).replace(' ','')
    table={
        '0':(0,0),'4':(12,0),'-4':(-12,0),'3':(9,0),'-3':(-9,0),'2':(6,0),'-2':(-6,0),'6':(18,0),'-6':(-18,0),'12':(36,0),'-12':(-36,0),
        '2*sqrt(3)':(0,6),'-2*sqrt(3)':(0,-6),'sqrt(3)*2':(0,6),'-sqrt(3)*2':(0,-6),
        '2/sqrt(3)':(0,2),'-2/sqrt(3)':(0,-2),'4/sqrt(3)':(0,4),'-4/sqrt(3)':(0,-4),
    }
    if s not in table:
        raise ValueError(f'unknown scalar expression {x!r}')
    return table[s]

def qsqrt3_prod_num(x:Tuple[int,int], y:Tuple[int,int])->Tuple[int,int]:
    # Returns numerator P,Q such that x*y=(P+Q sqrt(3))/9.
    A,B=x; C,D=y
    return (A*C + 3*B*D, A*D + B*C)

def residual_dot_num(Y1,Z1,Y2,Z2)->Tuple[int,int]:
    # Returns P,Q for 2Y1Y2+6Z1Z2 = (P+Q sqrt(3))/9.
    py,qy=qsqrt3_prod_num(Y1,Y2); pz,qz=qsqrt3_prod_num(Z1,Z2)
    return (2*py+6*pz, 2*qy+6*qz)

def qsqrt3_le_num(P:int,Q:int,R:int)->bool:
    """Return whether P+Q*sqrt(3) <= R, exactly over integers."""
    P=int(P); Q=int(Q); R=int(R)
    D=R-P
    if Q==0:
        return D>=0
    if Q>0:
        return D>=0 and D*D >= 3*Q*Q
    # Q<0: P-|Q|sqrt3 <= R. If D>=0 it is automatic; otherwise need -D <= |Q|sqrt3.
    return D>=0 or D*D <= 3*Q*Q

def qsqrt3_lt_num(P:int,Q:int,R:int)->bool:
    return qsqrt3_le_num(P,Q,R) and not (Q==0 and P==R)

def qsqrt3_to_float_num(P:int,Q:int)->float:
    return (P+Q*np.sqrt(3.0))/9.0

def add_vec(first16, Y_pair, Z_pair, family, info, firsts, AY, BY, AZ, BZ, fams, meta):
    firsts.append(np.array(first16,dtype=np.int16))
    AY.append(int(Y_pair[0])); BY.append(int(Y_pair[1])); AZ.append(int(Z_pair[0])); BZ.append(int(Z_pair[1]))
    fams.append(family); d={'family':family}; d.update(info or {}); meta.append(d)

def build_vectors(cert):
    firsts=[]; AY=[]; BY=[]; AZ=[]; BZ=[]; fams=[]; meta=[]
    z16=np.zeros(16,dtype=np.int16)
    # Fixed Cohn--Li core.
    for i,j in itertools.combinations(range(16),2):
        for si in (-1,1):
            for sj in (-1,1):
                first=np.zeros(16,dtype=np.int16); first[i]=12*si; first[j]=12*sj
                add_vec(first,scalar_int(0),scalar_int(0),'odd17_type1a',{'i':i,'j':j,'si':si,'sj':sj},firsts,AY,BY,AZ,BZ,fams,meta)
    for qi,q in enumerate(pair_supports()+square_supports()):
        for minus in odd_minus_masks(q):
            add_vec(sign_first_from_minus_mask(q,minus,6),scalar_int(0),scalar_int(0),'odd17_type1b',{'support_index':qi,'support':q,'minus':minus},firsts,AY,BY,AZ,BZ,fams,meta)
    for qi,q in enumerate(cross_supports()):
        for minus in odd_minus_masks(q):
            for eta in (-1,1):
                add_vec(sign_first_from_minus_mask(q,minus,6),scalar_int(6*eta),scalar_int(0),'odd17_cross',{'support_index':qi,'support':q,'minus':minus,'eta':eta},firsts,AY,BY,AZ,BZ,fams,meta)
    for eta in (-1,1):
        add_vec(z16,scalar_int(12*eta),scalar_int(0),'odd17_axis_sqrt8',{'eta':eta},firsts,AY,BY,AZ,BZ,fams,meta)
    for eta in (-1,1):
        for zeta in (-1,1):
            add_vec(z16,scalar_int(6*eta),scalar_int(6*zeta),'dim18_axis_sqrt2_sqrt6',{'eta':eta,'zeta':zeta},firsts,AY,BY,AZ,BZ,fams,meta)
    # Listed partial support fibers.
    for si,rec in enumerate(cert['supports']):
        q=int(rec['q_int']); Y0=parse_scalar_expr(rec['ell_YZ'][0]); Z0=parse_scalar_expr(rec['ell_YZ'][1])
        for minus in odd_minus_masks(q):
            add_vec(sign_first_from_minus_mask(q,minus,6),Y0,Z0,'partial_support_fiber',{'support_index':si,'support':q,'minus':minus,'orientation':int(rec['orientation']),'ell_YZ':rec['ell_YZ']},firsts,AY,BY,AZ,BZ,fams,meta)
    # Listed algebraic holes.
    for hi,rec in enumerate(cert['holes']):
        c=int(rec['c_int']); first=np.zeros(16,dtype=np.int16)
        for i in range(16): first[i] = -4 if ((c>>i)&1) else 4
        Y=parse_scalar_expr(rec.get('Y_expr',rec.get('Y'))); Z=parse_scalar_expr(rec.get('Z_expr',rec.get('Z')))
        add_vec(first,Y,Z,'partial_deep_hole',{'hole_index':hi,'c':c,'angle_index_mod12':int(rec.get('angle_index_mod12',rec.get('color',-1))),'Y_expr':rec.get('Y_expr'), 'Z_expr':rec.get('Z_expr')},firsts,AY,BY,AZ,BZ,fams,meta)
    return (np.vstack(firsts), np.array(AY,dtype=np.int16), np.array(BY,dtype=np.int16), np.array(AZ,dtype=np.int16), np.array(BZ,dtype=np.int16), fams, meta)

def exact_pair_check(F,AY,BY,AZ,BZ,fams,chunk:int=512):
    N=len(fams); F32=F.astype(np.int32); FT=F32.T.copy()
    AY64=AY.astype(np.int64); BY64=BY.astype(np.int64); AZ64=AZ.astype(np.int64); BZ64=BZ.astype(np.int64)
    norms_bad=[]
    norm_hist=Counter()
    for i in range(N):
        head=int(np.dot(F32[i],F32[i]))
        P,Q=residual_dot_num((int(AY[i]),int(BY[i])),(int(AZ[i]),int(BZ[i])),(int(AY[i]),int(BY[i])),(int(AZ[i]),int(BZ[i])))
        # Total scaled norm is head + (P+Q sqrt(3))/9, so store the
        # numerator pair (9*head+P, Q).  Norm 288 is (2592,0)/9.
        norm_hist[(9*head+P,Q)] += 1
        if Q!=0 or 9*head+P != 9*288:
            norms_bad.append([i,head,P,Q])
            if len(norms_bad)>=20: break
    bad=[]; pair_count=0; max_float=-1e100; max_record=None; fam_pair_max=defaultdict(lambda:(-1e100,None))
    hist_approx=Counter()
    for a in range(0,N,chunk):
        b=min(N,a+chunk); rows=b-a
        H=F32[a:b] @ FT
        # residual numerator arrays for block vs all columns
        P = 2*(AY64[a:b,None]*AY64[None,:] + 3*BY64[a:b,None]*BY64[None,:]) + 6*(AZ64[a:b,None]*AZ64[None,:] + 3*BZ64[a:b,None]*BZ64[None,:])
        Q = 2*(AY64[a:b,None]*BY64[None,:] + BY64[a:b,None]*AY64[None,:]) + 6*(AZ64[a:b,None]*BZ64[None,:] + BZ64[a:b,None]*AZ64[None,:])
        R = 9*(144 - H.astype(np.int64))
        col=np.arange(N)[None,:]; row=np.arange(a,b)[:,None]
        keep=col>row
        pair_count += int(keep.sum())
        D=R-P
        ok=np.zeros_like(D,dtype=bool)
        q0=(Q==0); qp=(Q>0); qn=(Q<0)
        ok[q0]=D[q0]>=0
        ok[qp]=(D[qp]>=0) & (D[qp]*D[qp] >= 3*Q[qp]*Q[qp])
        ok[qn]=(D[qn]>=0) | (D[qn]*D[qn] <= 3*Q[qn]*Q[qn])
        viol=keep & (~ok)
        if np.any(viol):
            loc=np.argwhere(viol)
            for rr,cc in loc[:20-len(bad)]:
                i=a+int(rr); j=int(cc)
                bad.append([i,j,int(H[rr,cc]),int(P[rr,cc]),int(Q[rr,cc]),int(R[rr,cc])])
            if len(bad)>=20: break
        # Approximate max for reporting only.
        Val=H.astype(np.float64)+(P.astype(np.float64)+Q.astype(np.float64)*np.sqrt(3.0))/9.0
        Val_masked=np.where(keep,Val,-1e100)
        idx=np.unravel_index(int(np.argmax(Val_masked)),Val_masked.shape)
        val=float(Val_masked[idx])
        if val>max_float:
            rr,cc=idx; max_float=val; max_record=[a+int(rr),int(cc),int(H[rr,cc]),int(P[rr,cc]),int(Q[rr,cc]),val,fams[a+int(rr)],fams[int(cc)]]
        # coarsened histogram rounded to 1e-9 string, enough to expose pair coverage not used as proof.
        # Family-pair maxima.
        for rr in range(rows):
            gi=a+rr
            for fj in sorted(set(fams)):
                pass
        # avoid expensive family loops here; compute from max records later if needed.
    return {'N':N,'pair_count':pair_count,'expected_pair_count':N*(N-1)//2,'bad_pair_prefix':bad,'bad_pair_prefix_count':len(bad),'norm_bad_prefix':norms_bad,'norms_all_scaled_288':len(norms_bad)==0,'norm_histogram_num':{str(k):int(v) for k,v in norm_hist.items()},'kissing_condition_scaled_le_144':len(bad)==0,'max_approx_scaled_inner_product':max_float,'max_record':[str(x) if isinstance(x,np.generic) else x for x in (max_record or [])]}

def check_finite(cert):
    errors=[]
    C10=generate_C10(); basis=gf2_basis(C10); C10set=set(C10)
    supports=cert['supports']; holes=cert['holes']
    if len(C10)!=1024: errors.append('C10 size not 1024')
    if len(supports)!=int(cert.get('support_count',len(supports))): errors.append('support count field mismatch')
    if len(holes)!=int(cert.get('hole_count',len(holes))): errors.append('hole count field mismatch')
    ps=pair_supports()+square_supports(); cr=cross_supports()
    support_bad=[]; char_by_orient=defaultdict(set); by_orient=defaultdict(list)
    for i,s in enumerate(supports):
        q=int(s['q_int']); o=int(s['orientation']); by_orient[o].append(q)
        ch=char_mask(q,basis); char_by_orient[o].add(ch)
        if wt(q)!=6: support_bad.append([i,'weight',wt(q)])
        if max(inter(q,p) for p in ps)>4: support_bad.append([i,'pair_square_intersection'])
        if max(inter(q,c) for c in cr)>3: support_bad.append([i,'cross_intersection'])
        if 'character_mask_on_C10_basis' in s and int(s['character_mask_on_C10_basis'])!=ch:
            support_bad.append([i,'stored_character_mismatch',int(s['character_mask_on_C10_basis']),ch])
    if support_bad: errors.append(f'support finite bad {len(support_bad)}')
    # Check support-support in integer support residuals.
    supp_pair_bad=[]; supp_hist=Counter()
    for i,a in enumerate(supports):
        Ya=parse_scalar_expr(a['ell_YZ'][0]); Za=parse_scalar_expr(a['ell_YZ'][1])
        for j in range(i+1,len(supports)):
            b=supports[j]; Yb=parse_scalar_expr(b['ell_YZ'][0]); Zb=parse_scalar_expr(b['ell_YZ'][1])
            P,Q=residual_dot_num(Ya,Za,Yb,Zb); k=inter(int(a['q_int']),int(b['q_int']))
            # compare 36k+(P+Q sqrt3)/9 <=144 -> P+Q sqrt3 <=9*(144-36k)
            supp_hist[(int(a['orientation']),int(b['orientation']),k,P,Q)] += 1
            if not qsqrt3_le_num(P,Q,9*(144-36*k)):
                supp_pair_bad.append([i,j,k,P,Q])
    if supp_pair_bad: errors.append(f'support-support bad {len(supp_pair_bad)}')
    # Check holes membership, residual norm, half-plane feasibility, one hole per word.
    hole_words=[]; hole_bad=[]; syn_counts=Counter(); angle_counts=Counter()
    for hi,h in enumerate(holes):
        c=int(h['c_int']); hole_words.append(c)
        if c not in C10set: hole_bad.append([hi,'c not in C10',c])
        Y=parse_scalar_expr(h.get('Y_expr',h.get('Y'))); Z=parse_scalar_expr(h.get('Z_expr',h.get('Z')))
        P,Q=residual_dot_num(Y,Z,Y,Z)
        if Q!=0 or P!=9*32: hole_bad.append([hi,'residual norm',P,Q,h.get('Y_expr'),h.get('Z_expr')])
        violated=sorted({int(s['orientation']) for s in supports if dot2(c,int(s['q_int']))})
        syn=''.join('1' if o in violated else '0' for o in range(4)); syn_counts[syn]+=1
        angle_counts[int(h.get('angle_index_mod12',h.get('color',-999)))] += 1
        for o in violated:
            # Need L<=0 against this half-fiber residual orientation.
            # take any support with this orientation; finite check also ensures actual pair check globally.
            s0=next(s for s in supports if int(s['orientation'])==o)
            Ys=parse_scalar_expr(s0['ell_YZ'][0]); Zs=parse_scalar_expr(s0['ell_YZ'][1])
            Lp,Lq=residual_dot_num(Y,Z,Ys,Zs)
            if not qsqrt3_le_num(Lp,Lq,0):
                hole_bad.append([hi,'halfplane failed',o,Lp,Lq])
    if len(set(hole_words))!=len(hole_words): errors.append('duplicate hole words')
    orientation_residuals={}
    for o,qs in by_orient.items():
        residuals=sorted({tuple(map(str,s['ell_YZ'])) for s in supports if int(s['orientation'])==o})
        orientation_residuals[str(o)]=residuals
        if len(residuals)!=1:
            errors.append(f'orientation {o} has nonconstant residuals {residuals}')
    active_chars=[next(iter(char_by_orient[o])) for o in sorted(char_by_orient) if len(char_by_orient[o])==1]
    if hole_bad: errors.append(f'hole finite bad {len(hole_bad)}')
    return {'C10_size':len(C10),'C10_rank':len(basis),'support_count':len(supports),'hole_count':len(holes),'support_bad_prefix':support_bad[:20],'support_pair_bad_prefix':supp_pair_bad[:20],'hole_bad_prefix':hole_bad[:20],'orientation_characters_recomputed':{str(k):sorted(map(int,v)) for k,v in sorted(char_by_orient.items())},'orientation_residuals':orientation_residuals,'active_character_rank':gf2_rank_ints(active_chars) if len(active_chars)==len(char_by_orient) else None,'hole_syndrome_counts':dict(sorted(syn_counts.items())),'hole_angle_counts':{str(k):int(v) for k,v in sorted(angle_counts.items())},'errors_prefix':errors[:40],'error_count':len(errors),'finite_checks_pass':len(errors)==0}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cert',default=str(Path(__file__).resolve().parent/'data/certificate.json'))
    ap.add_argument('--output',required=True)
    ap.add_argument('--chunk',type=int,default=512)
    args=ap.parse_args(); t0=time.time()
    cert=json.load(open(args.cert))
    finite=check_finite(cert)
    F,AY,BY,AZ,BZ,fams,meta=build_vectors(cert)
    coord=exact_pair_check(F,AY,BY,AZ,BZ,fams,chunk=args.chunk)
    counts=Counter(fams)
    expected={'odd17_type1a':480,'odd17_type1b':3840,'odd17_cross':1024,'odd17_axis_sqrt8':2,'dim18_axis_sqrt2_sqrt6':4,'partial_support_fiber':32*len(cert['supports']),'partial_deep_hole':len(cert['holes'])}
    unique=len({(tuple(map(int,F[i])),int(AY[i]),int(BY[i]),int(AZ[i]),int(BZ[i])) for i in range(len(fams))})==len(fams)
    out={'input_certificate':Path(args.cert).name,'input_sha256':hashlib.sha256(Path(args.cert).read_bytes()).hexdigest(),'finite_checks':finite,'coordinate_checks':coord,'family_counts':{str(k):int(v) for k,v in sorted(counts.items())},'expected_family_counts':expected,'family_counts_match_expected':dict(counts)==expected,'unique_vectors':unique,'expected_total_formula':5350+32*len(cert['supports'])+len(cert['holes']),'verified_lower_bound':len(fams),'previous_Cohn_Li_K18':7654,'improvement_over_7654':len(fams)-7654,'improvement_over_8166':len(fams)-8166,'overall_verified':bool(finite['finite_checks_pass'] and coord['norms_all_scaled_288'] and coord['kissing_condition_scaled_le_144'] and coord['pair_count']==coord['expected_pair_count'] and unique and dict(counts)==expected and len(fams)==int(cert['lower_bound'])),'runtime_sec':time.time()-t0}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    json.dump(out,open(args.output,'w'),indent=2,sort_keys=True)
    print(json.dumps({'output':args.output,'N':len(fams),'overall_verified':out['overall_verified'],'finite_checks_pass':finite['finite_checks_pass'],'active_character_rank':finite['active_character_rank'],'norms_all_scaled_288':coord['norms_all_scaled_288'],'unique_vectors':unique,'max_approx_scaled_inner_product':coord['max_approx_scaled_inner_product'],'bad_pair_prefix_count':coord['bad_pair_prefix_count'],'pair_count':coord['pair_count'],'expected_pair_count':coord['expected_pair_count'],'improvement_over_8166':out['improvement_over_8166'],'runtime_sec':out['runtime_sec']},indent=2,sort_keys=True))

    if not out['overall_verified']:
        raise SystemExit(1)

if __name__=='__main__': main()
