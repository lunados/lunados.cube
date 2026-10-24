#!/usr/bin/env python3
"""Deterministic VP04 fixture authoring. The inputs are the frozen VP03 examples."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from vpgranularity.printer import PROFILE,FORMAT,sha,CAPS
BASE=ROOT.parent/'visual-printer-2d-lab'

def write(name,bundle,lens,level,focus=None,budget=None,overflow='summarize'):
    view=bundle['view_plan']['view'];cap=CAPS[level][view]
    if budget is None:budget={'max_items':cap[0],'max_edges':cap[1]}
    req={'format':FORMAT,'profile':PROFILE,'reference_version':'v9.4','source_bundle':bundle,
         'source_bundle_sha256':sha(bundle),
         'projection':{'view':view,'lens':lens,'granularity':level,'focus':focus,'budget':budget,'overflow':overflow}}
    (ROOT/'fixtures'/f'{name}.json').write_text(json.dumps(req,indent=2,ensure_ascii=False)+'\n','utf8')

def main():
    for name in ('flow_migration','chart_inventory','tree_modules'):
        bundle=json.loads((BASE/'lens_bundles'/f'{name}.json').read_text('utf8'))
        for level in ('overview','standard','detail'):
            write(f'{name}__{level}',bundle,'cube.lens.provenance',level)
    # Additional fixtures make the complexity cut observable for a real 5-point line and a 6-node hierarchy.
    for viewfile,stem in [('02_cube_flow_research.json','flow_research'),('04_cube_diagramm_line.json','chart_line'),('06_cube_tree_resources.json','tree_resources')]:
        from vplenses.printer import source_digest,PROFILE as LP,FORMAT as LF
        source=json.loads((BASE/'view_fixtures'/viewfile).read_text('utf8'))
        kind='sample' if source['view']=='cube.diagramm' else 'node'
        # Manually authored facet mapping; no inferred relevance to the chosen lens.
        target=source['samples'][-1]['id'] if kind=='sample' else source['order'][-1]
        bindings=[{'lens':'cube.lens.semantics','target_kind':kind,'target_id':target,
                   'declaration_ref':f'fixture:VP04/{stem}/semantics/{target}','note':'Authored fixture emphasis',
                   'basis':'declared_unverified'}]
        bundle={'format':LF,'lens_profile':LP,'reference_version':'v9.4',
                'source_view_sha256':source_digest(source),'view_plan':source,'facet_bindings':bindings,'basis':'declared_unverified'}
        for level in ('overview','standard','detail'):
            focus={'kind':kind,'id':target} if level!='detail' and stem!='tree_resources' else None
            # Tree leaf 'source' might have ancestry > overview allowance; test such failure separately.
            if stem=='tree_resources':focus=None
            write(f'{stem}__{level}',bundle,'cube.lens.semantics',level,focus)
    # Edge focus special-case, arbitrary source edge e2, demonstrates source-to-render edge ID remap.
    source=json.loads((BASE/'lens_bundles'/'tree_modules.json').read_text('utf8'))
    write('tree_modules__focus_edge',source,'cube.lens.governance','overview',{'kind':'edge','id':'e3'})
    source=json.loads((BASE/'lens_bundles'/'chart_inventory.json').read_text('utf8'))
    write('chart_inventory__focus_metric',source,'cube.lens.provenance','overview',{'kind':'metric','id':'fixture.resource_count'})
    print('fixture files',len(list((ROOT/'fixtures').glob('*.json'))))

if __name__=='__main__':main()
