"""Regenerate the rational 45-dimensional projection certificate.

The minimum-six QR neighbour is checked by ../qr/verify.py.
"""
from pathlib import Path
from itertools import combinations, product
from functools import lru_cache
import argparse, hashlib, json
from sage.all import Matrix, QQ, ZZ, vector
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
args=p.parse_args();report={}
compact=json.loads((DATA/'compact.json').read_text())
record=json.loads((DATA/'record.json').read_text())
G=Matrix(ZZ,json.loads((DATA/'gram.json').read_text())['ambient_G'])
T=Matrix(ZZ,compact['section_basis_T_rows']); H=T*G*T.transpose()
assert H==Matrix(ZZ,[[6,-2,-2],[-2,6,-2],[-2,-2,6]])
assert Matrix(ZZ,compact['projection_witness_rows_W'])*G*T.transpose()==Matrix.identity(ZZ,3)
ws=record['t_witness_vectors']; assert len(ws)==len(set(map(tuple,ws)))==298
for w in ws:
    v=vector(ZZ,w)
    assert v*G*v==6 and list(T*G*v)==[-2,-2,3]

# Reconstruct every allowed section signature from minimum 6; no cached domain.
inv=H.inverse()
section=[vector(ZZ,z) for z in product(range(-1,2),repeat=3) if vector(ZZ,z)*H*vector(ZZ,z)==6]
assert len(section)==8
exceptional={tuple(H*z) for z in section}
domain=[]
for y in product(range(-6,7),repeat=3):
    v=vector(ZZ,y)
    if v*inv*v>6: continue
    if y in exceptional or all(abs(v*z)<=3 for z in section):domain.append(y)
assert set(domain)=={tuple(-a for a in y) for y in domain}
canon=lambda y:min(tuple(y),tuple(-a for a in y))
free=sorted({canon(y) for y in domain if y not in exceptional})
alphas=[a for a in product(range(11),repeat=3) if sum(a)<=10 and sum(a)%2==0]
@lru_cache(None)
def pairing(indices):
    if not indices:return ZZ(1)
    return sum(H[indices[0],indices[j]]*pairing(indices[1:j]+indices[j+1:]) for j in range(1,len(indices)))
def mono(y,a):
    return QQ.prod(QQ(y[i])**a[i] for i in range(3))
rows=[];rhs=[]
for a in alphas:
    indices=tuple(i for i in range(3) for _ in range(a[i]));m=len(indices)//2
    denominator=ZZ.prod(48+2*j for j in range(m))
    moment=QQ((52416000*6**m,denominator))*pairing(indices)
    rows.append([(1 if y==(0,0,0) else 2)*mono(y,a) for y in free])
    rhs.append(moment-sum(mono(y,a) for y in exceptional))
A=Matrix(QQ,rows);b=vector(QQ,rhs)
# Fibres with signatures e1,e2,e3 project to equal-length kissing points.
c=vector(QQ,[sum(y==canon(e) for e in [(1,0,0),(0,1,0),(0,0,1)])-9*(y==canon((-2,-2,3))) for y in free])
dual_path=DATA/'dual.json'
saved=json.loads(dual_path.read_text())
assert saved['signature_representatives']==[list(y) for y in free]
assert saved['moment_multi_indices']==[list(a) for a in alphas]
assert saved['constant']==7377408 and saved['target']=='sum_i f(e_i) - 9 f(-2,-2,3)'
assert len(saved['dual'])==A.nrows()
dual=vector(QQ,[QQ(x) for x in saved['dual']])
assert sum(x!=0 for x in dual)==107
assert all(x>=0 for x in c-A.transpose()*dual) and dual*b==7377408
report['d45']={'verified':True,'witnesses':298,'bound':7377408+9*298,'section_gram':[list(map(int,r)) for r in H.rows()],
               'signature_count':len(domain),'free_antipodal_orbits':len(free),'moment_rows':len(alphas),
               'exact_bound':'f(e1)+f(e2)+f(e3)-9*f(-2,-2,3)>=7377408',
               'dual_nonzero':sum(x!=0 for x in dual),'ambient_minimum_verifier':'../qr/verify.py',
               'stored_dual_checked':True,'dual_sha256':hashlib.sha256(dual_path.read_bytes()).hexdigest()}
certificate={'signature_representatives':free,'moment_multi_indices':alphas,'dual':[str(x) for x in dual],'constant':7377408,'target':'sum_i f(e_i) - 9 f(-2,-2,3)'}

result=report['d45'];result['rational_certificate']=certificate
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(report,indent=2))
