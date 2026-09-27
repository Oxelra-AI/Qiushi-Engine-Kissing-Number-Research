"""Confirm rejection of two normalized but incompatible replacement points."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile

import verify_extension

HERE=Path(__file__).resolve().parent


def main(output=None):
    base=json.loads((HERE/'baseline-heads.json').read_text())
    direction=base['extra_equator_lean']
    cases=[('upper_minus_Q','upper',[-v for v in direction]+[4]),
           ('lower_duplicate_Q','lower',direction+[-4])]
    outcomes=[]
    original_here=verify_extension.HERE
    for name,role,vector in cases:
        with tempfile.TemporaryDirectory(prefix='kissing-certificate-') as tmp:
            dest=Path(tmp)
            for filename in ('baseline-heads.json','repair-points.json','leech.py','golay.py'):
                shutil.copy2(HERE/filename,dest/filename)
            data=json.loads((dest/'repair-points.json').read_text())
            data['points'][role]['integer_vector']=vector
            data['points'][role]['squared_norm']=sum(v*v for v in vector)
            assert data['points'][role]['squared_norm']==64
            (dest/'repair-points.json').write_text(json.dumps(data))
            verify_extension.HERE=dest
            rejected=False
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    verify_extension.main()
            except AssertionError:
                rejected=True
            finally:
                verify_extension.HERE=original_here
            assert rejected,name
            outcomes.append({'case':name,'exact_squared_norm':4,'rejected':True})
    if output is not None:
        Path(output).write_text(json.dumps(outcomes,indent=2)+'\n')
    print(json.dumps(outcomes,indent=2))
    return outcomes


if __name__=='__main__':main()
