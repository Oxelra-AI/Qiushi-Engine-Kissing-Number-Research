"""Check the rational matrix certificate; verify.py regenerates its geometry."""
import argparse, json
from fractions import Fraction
from pathlib import Path

def check():
    data=json.loads((Path(__file__).resolve().parent/'data/certificate.json').read_text())
    A=[[Fraction(x) for x in row] for row in data['A_rows']]
    b=list(map(Fraction,data['b_rhs']))
    c=list(map(Fraction,data['target_c']))
    w=list(map(Fraction,data['dual_w']))
    assert len(A)==len(b)==len(w)==43
    assert all(len(row)==len(c)==43 for row in A)
    assert all(sum(A[i][j]*w[i] for i in range(43))==c[j] for j in range(43))
    value=sum(x*y for x,y in zip(w,b))
    assert value==2553792
    return {'passed':True,'dimension':43,'lower_bound':int(value),'rows':43,'columns':43}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=check();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
