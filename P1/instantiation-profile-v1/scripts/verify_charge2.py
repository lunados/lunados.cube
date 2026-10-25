#!/usr/bin/env python3
"""P1.6 Charge 2 gate: new tests plus full frozen P1.5 integrity regression."""
import os,subprocess,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[3]
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
steps=[
 ('P1.6 new schema/runtime/independent oracle', [sys.executable,'-m','unittest','discover','-s','P1/instantiation-profile-v1/tests','-v']),
 ('P1.5 frozen full release integrity', [sys.executable,'P1/release-v1/scripts/verify_p15.py']),
]
for name,args in steps:
    print('RUN:',name,flush=True)
    x=subprocess.run(args,cwd=repo,env=env)
    if x.returncode:
        print('FAIL:',name,flush=True)
        raise SystemExit(x.returncode)
print('PASS: P1.6 CHARGE 2 local implementation + P1.1–P1.5 frozen release gates',flush=True)
