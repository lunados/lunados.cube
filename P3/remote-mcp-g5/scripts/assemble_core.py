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
    (OUT/'G5_SOURCE_MANIFEST.json').write_text(json.dumps({'format':'aiaeao.cube.g5-assembly/1',
         'files':manifest,'p0_snapshot_lock':report['lock_sha256']},sort_keys=True,indent=2)+'\n','utf-8')
    print('PASS G5 assembly: %d frozen source files; pinned P0 %s' % (len(manifest),report['lock_sha256']))
    print('Deployable candidate assembled at: '+str(OUT))

if __name__=='__main__': main()
