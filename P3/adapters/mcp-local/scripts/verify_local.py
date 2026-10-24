"""Offline bridge verifier. SDK smoke must be run separately on a machine with MCP installed."""
import subprocess
import sys
from pathlib import Path
base=Path(__file__).resolve().parents[1]
cmd=[sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v']
print('CMD:', ' '.join(cmd),flush=True)
raise SystemExit(subprocess.call(cmd,cwd=base))
