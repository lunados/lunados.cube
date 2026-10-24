"""Generate release matrix from hand-authored INDEPENDENT_ORACLE expectations.
This developer helper must NOT overwrite the oracle.
"""
import copy
import json
import sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R))
from vpconformance import ConformanceAuditor, ConformanceError
from vpconformance.conformance import CAPS,sha
B=R.parent/'visual-printer-granularity-v1'
oracle=json.loads((R/'fixtures'/'INDEPENDENT_ORACLE.json').read_text('utf8'))
audit=ConformanceAuditor()
for name,data in oracle['sources'].items():
    base=json.loads((B/'fixtures'/(data['seed']+'.json')).read_text('utf8'))
    for lens in oracle['lenses']:
        for level in ('overview','standard','detail'):
            req=copy.deepcopy(base)
            req['projection']['lens']='cube.lens.'+lens
            req['projection']['granularity']=level
            cap=CAPS[level][data['view']]
            req['projection']['budget']={'max_items':cap[0],'max_edges':cap[1]}
            req['projection']['focus']=None
            req['projection']['overflow']='summarize'
            req['source_bundle_sha256']=sha(req['source_bundle'])
            expected={'source_items':data['source_items'],'shown_items':data['levels'][level][0],
                      'shown_edges':data['levels'][level][1],'completeness':data['levels'][level][2]}
            c_id=f'{name}__{lens}__{level}'
            declared={b['lens'] for b in req['source_bundle']['facet_bindings']}
            supported=('cube.lens.'+lens) in declared
            try:
                report,svg,pr=audit.audit(req,expected,include_svg=True)
            except ConformanceError as error:
                if supported:raise
                if 'selected lens has no explicit facet bindings' not in str(error):raise
                report={'format':'aiaeao.cube.vp05-expected-rejection/1','case_id':c_id,'status':'EXPECTED_REJECTION',
                        'diagnostic':'LENS_DECLARATION_MISSING','message':'selected lens has no explicit facet bindings: cannot infer relevance',
                        'content_status':'declared_unverified','semantic_conformance':'NOT_EVALUATED'}
                svg=None;pr=None
            else:
                if not supported:raise RuntimeError('missing declaration wrongly accepted: '+c_id)
            (R/'matrix'/(c_id+'.json')).write_text(json.dumps(req,ensure_ascii=False,indent=2,sort_keys=True)+'\n','utf8')
            if svg is not None:
                (R/'matrix'/(c_id+'.svg')).write_bytes(svg)
                (R/'matrix'/(c_id+'.vp04.report.json')).write_text(json.dumps(pr,ensure_ascii=False,indent=2,sort_keys=True)+'\n','utf8')
            (R/'matrix'/(c_id+'.vp05.report.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n','utf8')
print('generated',len(list((R/'matrix').glob('*.svg'))),'positive golden projections; rejected',sum('EXPECTED_REJECTION' in x.read_text('utf8') for x in (R/'matrix').glob('*.vp05.report.json')))
