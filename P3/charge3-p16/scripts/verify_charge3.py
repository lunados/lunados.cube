#!/usr/bin/env python3
"""Full offline Charge 3 release gate (NO Cloudflare/remote host claims)."""
import os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
REPO=HERE.parents[1]
ENV=os.environ.copy();ENV['PYTHONDONTWRITEBYTECODE']='1'
STEPS=[
 ('Charge 3 overlay SHA-256',[sys.executable,'P3/charge3-p16/scripts/verify_sources.py']),
 ('P1.6 Charge 2 and frozen P1.5 gate',[sys.executable,'P1/instantiation-profile-v1/scripts/verify_charge2.py']),
 ('G4 local MCP and frozen G0-G3 gates',[sys.executable,'P3/adapters/mcp-local/scripts/verify_g4.py']),
 ('G5 offline including worker bundling and existing tests',[sys.executable,'P3/remote-mcp-g5/scripts/verify_g5.py']),
 ('Charge 3 local MCP tests',[sys.executable,'-m','unittest','discover','-s','P3/charge3-p16/tests','-p','test_*.py','-v']),
 ('Charge 3 isolated staged Worker parity',[sys.executable,'P3/charge3-p16/scripts/verify_staged_g5.py']),
]
for name,cmd in STEPS:
 print('RUN',name,flush=True)
 result=subprocess.run(cmd,cwd=REPO,env=ENV,timeout=420)
 if result.returncode:
    raise SystemExit('FAIL '+name)
print('PASS: P1.6 CHARGE 3 OFFLINE integration + frozen gates (NO remote proof, NO production approval)')
