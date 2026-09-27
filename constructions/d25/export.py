"""Export the exact construction to a numerical NumPy array."""
import argparse
from fractions import Fraction
import json
from pathlib import Path

import numpy as np
from leech import build

HERE=Path(__file__).resolve().parent


def configuration():
    data=json.loads((HERE/'baseline-heads.json').read_text())
    repairs=json.loads((HERE/'repair-points.json').read_text())['points']
    shell=build()
    owners={tuple(h['owner']) for h in data['heads']}
    keep=np.array([tuple(map(int,z)) not in owners for z in shell])
    Z=shell[keep].astype(float)/np.sqrt(8)
    g=np.array(data['extra_equator_lean'],dtype=np.int64)
    n=g/np.sqrt(48)
    moved=np.abs(Z@n-np.sqrt(1.5))<1e-10
    assert moved.sum()==552
    a=np.sqrt(3)/2+np.sqrt(2)/4
    b=(np.sqrt(6)-2)/4
    Z[moved]+=(a-np.sqrt(1.5))*n
    shell25=np.c_[Z,np.where(moved,b,0)]
    heads=[]
    for h in data['heads']:
        if h['kind']=='class':
            row=np.array(h['owner'])+(3-np.sqrt(3))/6*np.array(h['lean'])
        else:
            row=np.array([float(Fraction(q)) for q in h['coordinates']])
        heads.append(row/np.sqrt(8))
    X=np.array(heads)
    caps=np.r_[np.c_[X,np.ones(1016)],np.c_[X,-np.ones(1016)]]
    for role,index in [('upper',984),('lower',2024)]:
        r=repairs[role]
        caps[index]=2*np.array(r['integer_vector'])/np.sqrt(r['squared_norm'])
    poles=np.zeros((2,25));poles[0,-1]=2;poles[1,-1]=-2
    points=np.r_[shell25,caps,np.r_[-2*n,0][None,:],poles,np.r_[g/4,-1][None,:]]
    assert points.shape==(197580,25)
    return points


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('output',type=Path,help='Destination .npy file')
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    np.save(args.output,configuration())
    print(f'Wrote 197580 by 25 numerical coordinates to {args.output}')
