"""Check the original P48 block construction and its ambient lattice."""
import argparse, hashlib, json, os, subprocess, tempfile
from pathlib import Path
import verify_ambient
ROOT=Path(__file__).resolve().parent

def check():
    with tempfile.TemporaryDirectory(prefix='kissing-p48-check-') as name:
        binary=Path(name)/'check_blocks'
        subprocess.run([os.environ.get('CXX','c++'),'-O3','-std=c++17',str(ROOT/'check_blocks.cpp'),'-o',str(binary)],check=True)
        out=subprocess.run([str(binary),str(ROOT/'data/blocks.txt')],capture_output=True,text=True,check=True)
        finite=json.loads(out.stdout)
    assert finite['valid_finite_blocks'] is True
    expected=json.loads((ROOT/'data/historical_summary.json').read_text())
    digest=hashlib.sha256((ROOT/'data/blocks.txt').read_bytes()).hexdigest()
    assert digest==expected['sha256'] and finite['sizes_desc']==expected['block_sizes_desc']
    ambient=verify_ambient.check()
    assert ambient['valid'] is True
    assert finite['chi']==ambient['characteristic'] and finite['glue']==ambient['glue']
    sizes=finite['sizes_desc'];rows=[]
    for n,m,t,expected in [(49,1,2,52425977),(50,3,6,52445822),(51,6,12,52475564),(52,12,24,52534909),(53,20,40,52613892),(54,36,72,52771283),(55,63,126,53034779)]:
        count=52416000+sum(sizes[:m])+t
        assert count==expected
        rows.append({'dimension':n,'lower_bound':count,'blocks':m,'tail_points':t})
    return {'passed':True,'finite':finite,'ambient':ambient,'input_sha256':digest,'results':rows}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=check();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'results':result['results']},indent=2))
