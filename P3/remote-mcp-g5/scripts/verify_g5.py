#!/usr/bin/env python3
"""Honest local G5 gate. Does not claim Cloudflare/Pyodide or live HTTP validation."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];REPO=HERE.parents[1]

def main():
    for script in ('make_registry.py','assemble_core.py'):
        subprocess.run([sys.executable,str(HERE/'scripts'/script)],check=True)
    cp=subprocess.run(['node','--check',str(HERE/'gateway/src/index.mjs')]);assert cp.returncode==0
    cp=subprocess.run(['node','--test',str(HERE/'gateway/tests/security.test.mjs')]);assert cp.returncode==0
    sys.path.insert(0,str(HERE/'.g5-runtime'))
    from core_runtime import dispatch,wire_call
    from aiaeao_mcp_local import p0_resources
    from vpprint.core import make_job,render_job
    assert len(json.loads((HERE/'gateway/src/p0-registry.json').read_text())['resources'])==14
    assert dispatch('cube_discover_surface')['ok']
    assert dispatch('cube_read_reference',{'uri':p0_resources.INDEX_URI})['ok']
    assert dispatch('cube_read_reference',{'uri':'file:///etc/passwd'})['ok'] is False
    assert dispatch('cube_validate',{'input_text':'this is not valid ACG'})['result']['report']['overall_status']=='FAIL'
    assert dispatch('cube_validate',{'input_text':'this is not valid ACG'})['ok']
    fixture=json.loads((REPO/'P2/visual-printer-release-v1/examples/flow_provenance_standard.vp03.bundle.json').read_text())
    job=dispatch('cube_prepare_print',{'bundle':fixture,'lens':'cube.lens.provenance','granularity':'standard'})
    assert job['ok']
    remote=dispatch('cube_render_svg',{'job':job['result']});assert remote['ok']
    core_report,core_svg=render_job(job['result'])
    assert remote['result']['report']==core_report
    assert remote['result']['artifact']['svg_text'].encode('utf-8')==core_svg
    assert hashlib.sha256(core_svg).hexdigest()==remote['result']['artifact']['sha256']
    assert remote['result']['transport']=='remote_mcp_streamable_http'
    assert dispatch('cube_check_print',{'job':job['result']})['result']==core_report
    assert wire_call({'operation':'__import__','arguments':{}})['ok'] is False
    print('PASS G5 OFFLINE: 14 P0 registry entries, P1 semantic failures, exact P2 SVG/report parity, denylist input')
    subprocess.run([sys.executable,str(HERE/'scripts/check_runtime_assets.py')],check=True)
    suite=unittest.defaultTestLoader.discover(str(HERE/'tests'),pattern='test_*.py')
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
    print('NOT RE-RUN HERE: Cloudflare live runtime, npm SDK integration, remote auth, independent host acceptance')

if __name__=='__main__':main()
