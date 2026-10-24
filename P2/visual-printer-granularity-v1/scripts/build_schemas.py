"""Publish full VP04 projection envelope and report schemas; full VP03 bundle
validity is checked by the embedded frozen VP03 Python oracle, not guessed here."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
fields={'format':{'const':'aiaeao.cube.vp04-projection-request/1'},'profile':{'const':'P2-VP-GRANULARITY/0.4.0'},'reference_version':{'const':'v9.4'},'source_bundle':{'type':'object','required':['format','lens_profile','reference_version','source_view_sha256','view_plan','facet_bindings','basis']},'source_bundle_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},
  'projection':{'type':'object','additionalProperties':False,'required':['view','lens','granularity','focus','budget','overflow'],'properties':{
     'view':{'enum':['cube.flow','cube.diagramm','cube.tree']},
     'lens':{'enum':['cube.lens.semantics','cube.lens.provenance','cube.lens.execution','cube.lens.governance','cube.lens.epistemology']},
     'granularity':{'enum':['overview','standard','detail']},
     'focus':{'oneOf':[{'type':'null'},{'type':'object','required':['kind','id'],'additionalProperties':False,'properties':{'kind':{'enum':['node','edge','sample','metric']},'id':{'type':'string','pattern':'^[A-Za-z][A-Za-z0-9_.:-]{0,99}$'}}}]},
     'budget':{'type':'object','additionalProperties':False,'required':['max_items','max_edges'],'properties':{'max_items':{'type':'integer','minimum':2,'maximum':7},'max_edges':{'type':'integer','minimum':0,'maximum':8}}},
     'overflow':{'enum':['summarize','reject']}
  }}}
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:aiaeao:vp04:projection-request:0.4.0',
 'title':'AIAEAO VP-04 Projection Request','description':'Standalone envelope. The frozen VP03 bundle contract, cross-field budget ranges, source locks and graph invariants are validated programmatically by vpgranularity.',
 'type':'object','additionalProperties':False,'required':list(fields),'properties':fields}
(ROOT/'PROJECTION_REQUEST.schema.json').write_text(json.dumps(schema,indent=2,ensure_ascii=False)+'\n','utf8')
counts={'source_items':{'type':'integer','minimum':2},'source_edges':{'type':'integer','minimum':0},'items_omitted':{'type':'integer','minimum':0},'edges_omitted':{'type':'integer','minimum':0},'facet_bindings_omitted':{'type':'integer','minimum':0},'items_shown':{'type':'integer','minimum':2},'edges_shown':{'type':'integer','minimum':0}}
props={'format':{'const':'aiaeao.cube.vp04-print-report/1'},'profile':{'const':'P2-VP-GRANULARITY/0.4.0'},'reference_version':{'const':'v9.4'},'render_status':{'const':'PASS'},
'view':{'enum':['cube.flow','cube.diagramm','cube.tree']},'lens':fields['projection']['properties']['lens'],
'granularity':fields['projection']['properties']['granularity'],'focus':fields['projection']['properties']['focus'],
'budget':fields['projection']['properties']['budget'],'overflow':fields['projection']['properties']['overflow'],
'source_bundle_sha256':fields['source_bundle_sha256'],'source_view_sha256':fields['source_bundle_sha256'],'reduced_view_sha256':fields['source_bundle_sha256'],'svg_sha256':fields['source_bundle_sha256'],
'counts':{'type':'object','additionalProperties':False,'required':list(counts),'properties':counts},
'shown_item_ids':{'type':'array','uniqueItems':True,'items':{'type':'string'}},
'shown_edges':{'type':'array','items':{'type':'object','additionalProperties':False,'required':['source_edge_id','projected_edge_id'],'properties':{'source_edge_id':{'type':'string','pattern':'^e[1-8]$'},'projected_edge_id':{'type':'string','pattern':'^e[1-8]$'}}}},
'omitted_item_ids':{'type':'array','uniqueItems':True,'items':{'type':'string'}},
'omitted_edges':{'type':'array','items':{'type':'object','additionalProperties':False,'required':['source_edge_id','from','to','predicate_id','declaration_ref','reason'],
 'properties':{'source_edge_id':{'type':'string'},'from':{'type':'string'},'to':{'type':'string'},'predicate_id':{'type':'string'},'declaration_ref':{'type':'string'},'reason':{'enum':['endpoint_omitted','edge_budget']}}}},
'displayed_facet_bindings':{'type':'array','items':{'type':'object'}},'omitted_facet_bindings':{'type':'array','items':{'type':'object'}},
'lens_emphasis':{'enum':['declared_unverified','no_visible_declared_targets']},'chart_axis_rescaled':{'type':'boolean'},
'chart_window':{'enum':['contiguous_window_only','not_applicable']},'completeness':{'enum':['COMPLETE_INPUT_VIEW','PARTIAL_EXPLICIT']},
'content_status':{'const':'declared_unverified'},
**{x:{'const':'NOT_EVALUATED'} for x in ['semantic_conformance','epistemic_warrant','current_authority','canonical_admission']},
'notices':{'type':'array','minItems':3,'items':{'type':'string'}}}
schema2={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:aiaeao:vp04:print-report:0.4.0','title':'AIAEAO VP04 Print Report',
 'type':'object','additionalProperties':False,'required':list(props),'properties':props}
(ROOT/'PRINT_REPORT_VP04.schema.json').write_text(json.dumps(schema2,indent=2,ensure_ascii=False)+'\n','utf8')
print('schemas built')
