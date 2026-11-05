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
 'P1/comparison-profile-v1/cube_p19':'*',
 'P1/migration-profile-v1/cube_p110':'*',
 'P1/migration-profile-v2/cube_p1101':'*',
 'P1/migration-methods-v1/cube_p111':'*',
 'P1/coverage-instance-profile-v1/cube_p112':'*',
 'P1/control-flow-profile-v1/cube_p113':'*',
 'P1/relation-origin-profile-v1/cube_p114':'*',
 'P1/scope-nesting-profile-v1/cube_p115':'*',
 'P2/visual-printer-release-v1/vpprint':'*',
 'P2/visual-printer-conformance-v1/vpconformance':'*',
 'P2/visual-printer-granularity-v1/vpgranularity':'*',
 'P2/visual-printer-2d-lab/vp2d':'*',
 'P2/visual-printer-2d-lab/vplenses':'*',
 'P2/visual-printer-2d-lab/vpviews':'*',
 'P2/visual-printer-2d-lab/reference':'*',
 # R5 (MILE-010): the plan printers of G6 (VP-07…VP-11), staged unchanged
 'P2/visual-printer-migration-v1/vpmigration':'*',
 'P2/visual-printer-sequence-v1/vpsequence':'*',
 'P2/visual-printer-axes-v1/vpaxes':'*',
 'P2/visual-printer-cells-v1/vpcells':'*',
 'P2/visual-printer-instances-v1/vpinstances':'*',
 # R10 (MILE-016): VP-12 landscape printer, staged unchanged
 'P2/visual-printer-landscape-v1/vplandscape':'*',
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
    # P1.6 reads exactly one immutable SHA-pinned JSON vocabulary at runtime; P1.15 (R9) its pinned reference v2.
    for rel in ('P1/instantiation-profile-v1/instantiation_reference_v1.json',
                'P1/scope-nesting-profile-v1/instantiation_reference_v2.json'):
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
    cvec={c['id']:c for c in json.loads((REPO/'P1/comparison-profile-v1/fixtures/c01_c20_materialized.json').read_text('utf-8'))['cases']}
    for cid,want in (('C-12','PASS'),('C-16','PASS'),('C-05','FAIL')):
        p19=dispatch('cube_validate',{'input_text':cvec[cid]['input_text'],'context':cvec[cid]['context']})
        assert p19['ok'] and p19['result']['report']['overall_status']==want,(cid,p19)
        assert p19['result']['comparison_profile']=='P1.9/comparison-profile-v1',p19
    assert dispatch('cube_discover_surface')['result']['p19_comparison']['profile']=='P1.9/comparison-profile-v1'
    mvec={c['id']:c for c in json.loads((REPO/'P1/migration-profile-v1/fixtures/m01_m22_materialized.json').read_text('utf-8'))['cases']}
    for mid,want in (('M-01','PASS'),('M-18','PASS'),('M-17','FAIL'),('M-10','UNRESOLVED')):
        p110=dispatch('cube_validate',{'input_text':mvec[mid]['input_text'],'context':mvec[mid]['context'],
                                       'qualification_profiles':mvec[mid].get('qualification_profiles')})
        assert p110['ok'] and p110['result']['report']['overall_status']==want,(mid,p110)
        assert p110['result']['migration_profile']=='P1.10/migration-profile-v1',p110
        assert p110['result']['evaluation_performed_by_cube'] is False,p110
    assert dispatch('cube_validate',{'input_text':mvec['M-02']['input_text'],'context':mvec['M-02']['context']})['ok'] is False
    gold={c['id']:c for c in json.loads((REPO/'P1/migration-profile-v1/fixtures/golden_migration_synthetic.json').read_text('utf-8'))['cases']}
    for gid,c in gold.items():
        g=dispatch('cube_validate',{'input_text':c['input_text'],'context':c['context'],'qualification_profiles':c['qualification_profiles']})
        assert g['ok'] and g['result']['report']['overall_status']==c['expected_overall'],(gid,g)
    assert dispatch('cube_discover_surface')['result']['p110_migration']['profile']=='P1.10/migration-profile-v1'
    gvec={c['id']:c for c in json.loads((REPO/'P1/migration-profile-v2/fixtures/g01_g10_materialized.json').read_text('utf-8'))['cases']}
    for gid,want in (('G-01','UNRESOLVED'),('G-02','PASS'),('G-09','FAIL'),('G-10','PASS')):
        r=dispatch('cube_validate',{'input_text':gvec[gid]['input_text'],'context':gvec[gid]['context']})
        assert r['ok'] and r['result']['report']['overall_status']==want,(gid,r)
    gg={c['id']:c for c in json.loads((REPO/'P1/migration-profile-v2/fixtures/golden_gap_synthetic.json').read_text('utf-8'))['cases']}
    for gid,c in gg.items():
        r=dispatch('cube_validate',{'input_text':c['input_text'],'context':c['context'],'qualification_profiles':c['qualification_profiles']})
        assert r['ok'] and r['result']['report']['overall_status']==c['expected_overall'],(gid,r)
        assert r['result']['migration_profile']=='P1.10.1/migration-profile-v2',r
    assert dispatch('cube_discover_surface')['result']['p1101_migration']['profile']=='P1.10.1/migration-profile-v2'
    fvec={c['id']:c for c in json.loads((REPO/'P1/migration-methods-v1/fixtures/f01_f16_materialized.json').read_text('utf-8'))['cases']}
    for fid,want in (('F-01','PASS'),('F-05','PASS'),('F-06','UNRESOLVED'),('F-10','FAIL'),('F-14','PASS'),('F-15','UNRESOLVED')):
        c=fvec[fid];r=dispatch('cube_validate',{'input_text':c['input_text'],'context':c['context'],**({'qualification_profiles':c['qualification_profiles']} if 'qualification_profiles' in c else {})})
        assert r['ok'] and r['result']['report']['overall_status']==want,(fid,r)
        assert r['result']['migration_profile']=='P1.11/migration-methods-v1' and r['result']['method_execution_by_cube'] is False,r
    for fid in ('F-02','F-04','F-16'):
        r=dispatch('cube_validate',{'input_text':fvec[fid]['input_text'],'context':fvec[fid]['context']})
        assert not r['ok'] and r['diagnostic']['code']=='P1_MCP_CONFIG_INVALID',(fid,r)
    assert dispatch('cube_discover_surface')['result']['p111_migration_methods']['profile']=='P1.11/migration-methods-v1'
    kvec={c['id']:c for c in json.loads((REPO/'P1/coverage-instance-profile-v1/fixtures/k01_k21_materialized.json').read_text('utf-8'))['cases']}
    for kid,c in kvec.items():
        r=dispatch('cube_validate',{'input_text':c['input_text'],'context':c['context']})
        assert r['ok'] and r['result']['report']['overall_status']==c['expected_overall'],(kid,r)
        codes={d['code'] for d in r['result']['report']['diagnostics']}
        assert set(c['required_codes'])<=codes and not set(c['forbidden_codes'])&codes,(kid,codes)
        assert r['result']['coverage_profile']=='P1.12/coverage-instance-profile-v1' and r['result']['population_evaluation_by_cube'] is False,r
    k7=json.loads(json.dumps(kvec['K-08']['context']));k7['format']='aiaeao.cube.binding-context/7'
    r=dispatch('cube_validate',{'input_text':kvec['K-08']['input_text'],'context':k7})
    assert not r['ok'] and r['diagnostic']['code']=='P1_MCP_CONFIG_INVALID',r
    assert dispatch('cube_discover_surface')['result']['p112_coverage_instance']['profile']=='P1.12/coverage-instance-profile-v1'
    # R5 (MILE-010, ST-3): binding-context/9 through P1.13 and one chain per plan view through the core
    for c in json.loads((REPO/'P1/control-flow-profile-v1/fixtures/kf01_kf09_materialized.json').read_text('utf-8'))['cases']:
        r=dispatch('cube_validate',{'input_text':c['input_text'],'context':c['context']})
        assert r['ok'] and r['result']['report']['overall_status']==c['expected_overall'],(c['id'],r)
        if c['context']['format'].endswith('/9'):
            assert r['result']['control_flow_profile']=='P1.13/control-flow-profile-v1' and r['result']['trace_evaluation_by_cube'] is False,(c['id'],r)
    surf=dispatch('cube_discover_surface')['result']
    assert surf['p113_control_flow']['binding_context_formats']==['aiaeao.cube.binding-context/9'],surf['p113_control_flow']
    assert surf['domains']['P2']['plan_views']['remote_available'] is True and len(surf['domains']['P2']['plan_views']['views'])==7
    # R9 (MILE-015): binding-context/11 through P1.15, all SN vectors against their committed oracle
    for c in json.loads((REPO/'P1/scope-nesting-profile-v1/fixtures/sn01_sn14_materialized.json').read_text('utf-8'))['cases']:
        r=dispatch('cube_validate',{'input_text':c['input_text'],'input_format':c['input_format'],'context':c['context']})
        assert r['ok'] and r['result']['report']['overall_status']==c['expected_overall'],(c['id'],r)
        codes={d['code'] for d in r['result']['report']['diagnostics']}
        assert set(c['required_codes'])<=codes and not set(c['forbidden_codes'])&codes,(c['id'],codes)
        assert r['result']['scope_nesting_profile']=='P1.15/scope-nesting-profile-v1' and r['result']['policy_narrowing_checked_by_cube'] is False,r
    assert dispatch('cube_discover_surface')['result']['p115_scope_nesting']['binding_context_formats']==['aiaeao.cube.binding-context/11']
    # R10 (MILE-016): VP-12 cube.landscape and VP-09.3 with its pinned de locale through the core
    land={c['id']:c for c in json.loads((REPO/'P2/visual-printer-landscape-v1/fixtures/l01_l14_materialized.json').read_text('utf-8'))['cases']}
    c=land['L-04']
    src=dispatch('cube_plan_source',{'context':c['context'],'plan_id':'pm-ls','printer':'vplandscape','layers':c['layers'],'steps':'current,mvp,beta'})
    assert src['ok'],src
    v=dispatch('cube_plan_views',{'source':src['result']['source'],'view':'cube.landscape','granularity':'detail','locale':'de'})
    assert v['ok'] and 'Y × Z über T · abgeleitet · Morphologie 01.3' in v['result']['panels'][0]['svg'],v.get('diagnostic')
    assert dispatch('cube_plan_check',{'result':v['result']})['result']['status']=='PASS'
    sys.path.insert(0,str(HERE/'scripts'))
    import r5_calls
    one={'P-K01-phases','P-K07-flow','P-K08-sequence','P-K09-axes','P-S-04','P-I-22'}
    for call in (c for c in r5_calls.calls() if c['id'] in one):
        steps=r5_calls.run_chain(call,lambda op,a:(lambda r:(not r['ok'],r.get('result',r.get('diagnostic'))))(dispatch(op,a)))
        assert len(steps)==len(call['steps']) and not any(e for e,_ in steps) and steps[-1][1]['status']=='PASS',(call['id'],steps[-1])
    (OUT/'G5_SOURCE_MANIFEST.json').write_text(json.dumps({'format':'aiaeao.cube.g5-assembly/1',
         'files':manifest,'p0_snapshot_lock':report['lock_sha256']},sort_keys=True,indent=2)+'\n','utf-8')
    print('PASS G5 assembly: %d staged source files (frozen P0/P1.1-P1.5/P2 + P1.6 + P1.8 + P1.9 + P1.10 + P1.10.1 + P1.11 + P1.12 + P1.13 + R6: P1.14, plan printers VP-07…VP-11 + R9: P1.15 + R10: VP-12); pinned P0 %s' % (len(manifest),report['lock_sha256']))
    print('Deployable candidate assembled at: '+str(OUT))

if __name__=='__main__': main()
