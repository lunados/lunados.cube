"""Generates the machine-readable VP-02 input schema, no external dependencies."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ref='#/$defs/'
s={
 '$schema':'https://json-schema.org/draft/2020-12/schema',
 '$id':'urn:aiaeao:vp02:view-plan:0.2.0',
 'title':'AIAEAO Cube VP-02 view-plan / 0.2.0',
 'description':'Presentational-only P2 experiment; schema validates structure, Python printer additionally validates graph/tree invariants and P1 anchor compatibility.',
 'oneOf':[{'$ref':ref+'flow'},{'$ref':ref+'chart'},{'$ref':ref+'tree'}],
 '$defs':{}
}
common={
 'printer_profile':{'const':'P2-VP-VIEWS/0.2.0'},
 'reference_version':{'const':'v9.4'},
 'lens':{'const':'neutral'},
 'granularity':{'const':'standard'},
 'title':{'type':'string','minLength':1,'maxLength':78},
 'subtitle':{'type':'string','minLength':1,'maxLength':95}
}
idpat={'type':'string','pattern':'^[A-Za-z][A-Za-z0-9_.:-]{0,99}$'}
node={'type':'object','additionalProperties':False,'required':['id','anchor_id','label','form_id'],
'properties':{
 'id':idpat,'anchor_id':{'type':'string','minLength':1},
 'label':{'type':'string','minLength':1,'maxLength':60},
 'form_id':{'type':'string','pattern':'^form\\.'},
 'semantic_ref':{'type':'string','minLength':1},
 'qualified_state_witness_ref':{'type':'string','minLength':1},
 'time_label':{'type':'string','maxLength':40},
 'color_token':{'type':'string','minLength':1}
}}
edge={'type':'object','additionalProperties':False,
'required':['from','to','predicate_id','declaration_ref','arrow_anchor_id'],
'properties':{'from':idpat,'to':idpat,'predicate_id':{'type':'string','minLength':1,'maxLength':140},
'declaration_ref':{'type':'string','minLength':1,'maxLength':140},'arrow_anchor_id':{'const':'relation-arrows.reference'}}}
sample={'type':'object','additionalProperties':False,'required':['id','label','value'],
'properties':{'id':idpat,'label':{'type':'string','minLength':1,'maxLength':24},'value':{'type':'number','minimum':0,'maximum':1000000000}}}
metric={'type':'object','additionalProperties':False,
'required':['id','unit','scale','declaration_ref','evidence_status'],
'properties':{'id':idpat,'unit':{'type':'string','minLength':1,'maxLength':24},
'scale':{'const':'linear_zero_based'},'declaration_ref':{'type':'string','minLength':1,'maxLength':180},'evidence_status':{'const':'declared_unverified'}}}
for kind,view,other in (
 ('flow','cube.flow',{'nodes':{'type':'array','minItems':2,'maxItems':4,'items':node},
                      'edges':{'type':'array','minItems':1,'maxItems':8,'items':edge},
                      'order':{'type':'array','minItems':2,'maxItems':4,'items':idpat,'uniqueItems':True},
                      'direction':{'enum':['left-to-right','top-down']},
                      'declaration_status':{'const':'declared_unverified'}}),
 ('tree','cube.tree',{'nodes':{'type':'array','minItems':2,'maxItems':7,'items':node},
                      'edges':{'type':'array','minItems':1,'maxItems':8,'items':edge},
                      'order':{'type':'array','minItems':2,'maxItems':7,'items':idpat,'uniqueItems':True},
                      'root_id':idpat,'declaration_status':{'const':'declared_unverified'}}),
 ('chart','cube.diagramm',{'plot':{'enum':['bar','line']},'metric':metric,
                         'samples':{'type':'array','minItems':2,'maxItems':6,'items':sample}})):
 props={**common,'view':{'const':view},**other}
 s['$defs'][kind]={'type':'object','additionalProperties':False,'required':[x for x in props if x!='subtitle'],'properties':props}
(R/'VIEW_PLAN.schema.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n','utf8')

rp={'$schema':'https://json-schema.org/draft/2020-12/schema',
     '$id':'urn:aiaeao:vp02:print-report:1',
     'title':'AIAEAO VP-02 print report / 1',
     'type':'object','additionalProperties':False,
     'required':['format','printer_profile','reference_version','view','lens','granularity','render_status','svg_sha256','semantic_conformance','epistemic_warrant','current_authority','canonical_admission','content_status','notices'],
     'properties':{
        'format':{'const':'aiaeao.cube.vp02-print-report/1'},
        'printer_profile':{'const':'P2-VP-VIEWS/0.2.0'},
        'reference_version':{'const':'v9.4'},
        'view':{'enum':['cube.flow','cube.diagramm','cube.tree']},
        'lens':{'const':'neutral'},'granularity':{'const':'standard'},
        'render_status':{'const':'PASS'},'svg_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},
        'semantic_conformance':{'const':'NOT_EVALUATED'},
        'epistemic_warrant':{'const':'NOT_EVALUATED'},
        'current_authority':{'const':'NOT_EVALUATED'},
        'canonical_admission':{'const':'NOT_EVALUATED'},
        'content_status':{'const':'declared_unverified'},
        'notices':{'type':'array','items':{'type':'string'},'minItems':2},
        'displayed_item_ids':{'type':'array','items':idpat},
        'displayed_edges':{'type':'array','items':{'type':'object','additionalProperties':False,
           'required':['from','to','predicate_id','declaration_ref'],
           'properties':{'from':idpat,'to':idpat,'predicate_id':{'type':'string'},'declaration_ref':{'type':'string'}}}},
        'sample_ids':{'type':'array','items':idpat},
        'measurement_ref':{'type':'string'},'unit':{'type':'string'}
     },
     'allOf':[
       {'if':{'properties':{'view':{'const':'cube.diagramm'}}},
        'then':{'required':['sample_ids','measurement_ref','unit']},
        'else':{'required':['displayed_item_ids','displayed_edges']}}
     ]}
(R/'PRINT_REPORT.schema.json').write_text(json.dumps(rp,ensure_ascii=False,indent=2)+'\n','utf8')
print('Wrote schemas')
