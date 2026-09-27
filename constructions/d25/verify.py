"""Run both parts of the construction verification."""
import sys
from verify_baseline import main as verify_baseline
from verify_extension import main as verify_extension

if __name__=='__main__':
    if sys.flags.optimize:
        raise SystemExit('Run without -O: verification uses assertions.')
    verify_baseline()
    verify_extension()
    print('PASS: 197580 distinct points in dimension 25; squared norm 4; pair products <= 2.')
