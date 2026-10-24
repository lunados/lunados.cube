#!/usr/bin/env python3
"""Authoritative VP-03 fixture generator; never infers facets from names."""
import json
from pathlib import Path
from vplenses.printer import LensPrinter, source_digest, PROFILES, FORMAT, PROFILE
ROOT=Path(__file__).resolve().parents[1]

# All entries are explicitly fictional/illustrative perspectives supplied here.
# target_kind,target_id,note (always declared_unverified)
SPEC={
 'flow_migration':{
  'source':'01_cube_flow_migration',
  'semantics':[('node','artifact','Declared Artifact concept'),('node','resource','Declared Resource concept'),('edge','e1','Declared references predicate')],
  'provenance':[('node','artifact','Review the declared source artifact'),('edge','e1','Review the reference declaration')],
  'execution':[('node','resource','Illustrative target for a possible operation')],
  'governance':[('node','artifact','Inspect scope of declared object'),('edge','e1','Inspect declaration boundary, not grant')],
  'epistemology':[('node','resource','Illustrative knowledge claim under review')]
 },
 'chart_inventory':{
  'source':'03_cube_diagramm_bar',
  'semantics':[('metric','fixture.resource_count','Compare the declared metric definition'),('sample','artifact','Declared category identity')],
  'provenance':[('metric','fixture.resource_count','Inspect source and declared unit'),('sample','source','Declared source category')],
  'execution':[('sample','revisions','Illustrative operational-planning emphasis')],
  'governance':[('sample','evidence','Illustrative audit focus, no policy evaluation')],
  'epistemology':[('sample','artifact','Illustrative data quality focus'),('sample','evidence','Declared evidence category, not confirmed proof')]
 },
 'tree_modules':{
  'source':'05_cube_tree_modules',
  'semantics':[('node','core','Authored structural concept'),('node','adapter','Declared module kind')],
  'provenance':[('node','connector','Inspect declared connector role'),('edge','e3','Inspect authored hierarchy pointer')],
  'execution':[('node','runtime','Conceptual runtime module, not executed'),('node','toolbox','Conceptual tool collection')],
  'governance':[('node','core','Illustrative boundary of the group'),('edge','e2','Inspect the declared grouping link')],
  'epistemology':[('node','connector','Open design assumption for review')]
 }
}

def dump(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=False)+'\n','utf-8')

def main():
    printer=LensPrinter()
    for kind,spec in SPEC.items():
        base=json.loads((ROOT/'view_fixtures'/(spec['source']+'.json')).read_text('utf-8'))
        bindings=[]
        for l in PROFILES:
            name=l.rsplit('.',1)[-1]
            for cat,target,note in spec[name]:
                bindings.append({'lens':l,'target_kind':cat,'target_id':target,
                                 'declaration_ref':f'fixture:VP03/{kind}/{name}/{cat}/{target}',
                                 'note':note,'basis':'declared_unverified'})
        bundle={'format':FORMAT,'lens_profile':PROFILE,'reference_version':'v9.4',
                'source_view_sha256':source_digest(base),'view_plan':base,
                'facet_bindings':bindings,'basis':'declared_unverified'}
        dump(ROOT/'lens_bundles'/(kind+'.json'),bundle)
        for lens in PROFILES:
            name=lens.rsplit('.',1)[-1]
            stem=kind+'__'+name
            svg=printer.render(bundle,lens)
            (ROOT/'lens_outputs'/(stem+'.svg')).write_bytes(svg)
            dump(ROOT/'lens_outputs'/(stem+'.report.json'),printer.report(bundle,lens,svg))
    print('Generated 3 unchanged-source bundles, 15 lens SVGs and 15 reports')
if __name__=='__main__':main()
