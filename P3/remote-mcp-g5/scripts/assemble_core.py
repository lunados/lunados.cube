#!/usr/bin/env python3
"""Stage existing frozen P0/P1/P2 packages without rewriting source files.

Invoke from any cwd: python3 P3/remote-mcp-g5/scripts/assemble_core.py
Result lives under P3/remote-mcp-g5/.g5-runtime (gitignored).
"""
from __future__ import annotations
import hashlib, json, shutil, sys
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
REPO=HERE.parents[1]
OUT=HERE/'.g5-runtime'
FILES={
 'P3/adapters/mcp-local/aiaeao_mcp_local': '*',
 'P3/adapters/mcp-local/p0_snapshot':'*',
 'P1/semantic-validator-v1/cube_parser':'*',
 'P1/semantic-validator-v1/cube_resolver':'*',
 'P1/semantic-validator-v1/cube_semantic':'*',
 'P1/semantic-validator-v1/baseline':'*',
 'P1/instantiation-profile-v1/cube_p16':'*',
 'P1/simulation-profile-v1/cube_p18':'*',
 'P2/visual-printer-release-v1/vpprint':'*',
 'P2/visual-printer-conformance-v1/vpconformance':'*',
 'P2/visual-printer-granularity-v1/vpgranularity':'*',
 'P2/visual-printer-2d-lab/vp2d':'*',
 'P2/visual-printer-2d-lab/vplenses':'*',
 'P2/visual-printer-2d-lab/vpviews':'*',
 'P2/visual-printer-2d-lab/reference':'*',
}
KEEP={'.py','.json','.md','.ebnf','.txt'}

def main():
    if not (REPO/'P3/adapters/mcp-local/aiaeao_mcp_local/surface.py').exists():
        raise SystemExit('ERROR: run within a repo that has G4 local MCP sources')
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    manifest=[]
    for folder in FILES:
        src=REPO/folder
        if not src.is_dir():raise SystemExit('Missing frozen reference: '+folder)
        for f in sorted(src.rglob('*')):
            if f.is_symlink():raise SystemExit('Refusing symlink in source: '+str(f))
            if not f.is_file() or f.suffix not in KEEP:continue
            rel=f.relative_to(REPO)
            dest=OUT/rel;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(f,dest)
            manifest.append({'path':str(rel),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    # P1.6 reads exactly one immutable SHA-pinned JSON vocabulary at runtime.
    for rel in ('P1/instantiation-profile-v1/instantiation_reference_v1.json',):
        src=REPO/rel
        if not src.is_file():raise SystemExit('Missing P1.6 vocabulary: '+rel)
        dest=OUT/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dest)
        manifest.append({'path':rel,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    for fname in ('entry.py','core_runtime.py','wrangler.jsonc','pyproject.toml'):
        shutil.copyfile(HERE/'python-core'/fname,OUT/fname)
    # Byte-level verification of full P0 source snapshot before acceptance.
    sys.path.insert(0,str(OUT/'P3/adapters/mcp-local'))
    from aiaeao_mcp_local.p0_resources import verify_snapshot
    report=verify_snapshot()
    sys.path.insert(0,str(OUT))
    from core_runtime import dispatch
    assert dispatch('cube_discover_surface')['ok']
    assert dispatch('cube_validate',{'input_text':'this is not valid ACG'})['result']['report']['overall_status']=='FAIL'
    fixture=json.loads((REPO/'P1/instantiation-profile-v1/fixtures/valid_conclusion_context_v2.json').read_text('utf-8'))
    p16=dispatch('cube_validate',{'input_text':'X:α:Conclusion["c1"]','context':fixture})
    assert p16['ok'] and p16['result']['report']['overall_status']=='PASS',p16
    vectors=json.loads((REPO/'P1/simulation-profile-v1/fixtures/s01_s17_materialized.json').read_text('utf-8'))['cases']
    s16=next(c for c in vectors if c['id']=='S-16')
    p18=dispatch('cube_validate',{'input_text':s16['input_text'],'context':s16['context']})
    assert p18['ok'] and p18['result']['report']['overall_status']=='PASS',p18
    assert p18['result']['evaluation_performed_by_cube'] is False,p18
    assert dispatch('cube_discover_surface')['result']['p18_simulation']['profile']=='P1.8/simulation-profile-v1'
    (OUT/'G5_SOURCE_MANIFEST.json').write_text(json.dumps({'format':'aiaeao.cube.g5-assembly/1',
         'files':manifest,'p0_snapshot_lock':report['lock_sha256']},sort_keys=True,indent=2)+'\n','utf-8')
    print('PASS G5 assembly: %d staged source files (frozen P0/P1.1-P1.5/P2 + P1.6 + P1.8); pinned P0 %s' % (len(manifest),report['lock_sha256']))
    print('Deployable candidate assembled at: '+str(OUT))

if __name__=='__main__': main()
