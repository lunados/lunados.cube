"""VP05: independent display-conformance oracle and bounded split-feasibility study.

Consumes frozen VP04 declarative requests, does not modify baseline printer.
No semantic authority, no silent aggregation, no materialization of extra SVGs.
"""
from __future__ import annotations
import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

BASE=Path(__file__).resolve().parents[2]/'visual-printer-granularity-v1'
if not BASE.is_dir():raise RuntimeError('Frozen VP04 baseline missing')
if str(BASE) not in sys.path:sys.path.insert(0,str(BASE))
from vpgranularity import GranularityPrinter, GranularityError, CAPS
from vpgranularity.printer import sha, NS

PROFILE='P2-VP-CONFORMANCE/0.5.0'
REPORT_FORMAT='aiaeao.cube.vp05-conformance-report/1'
LEVELS=('overview','standard','detail')
VIEWS=('cube.flow','cube.diagramm','cube.tree')
LENSES=('cube.lens.semantics','cube.lens.provenance','cube.lens.execution','cube.lens.governance','cube.lens.epistemology')

class ConformanceError(ValueError):pass

def demand(test,message):
    if not test:raise ConformanceError(message)

def json_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()

def ids_and_edges(plan):
    if plan['view']=='cube.diagramm':return {s['id'] for s in plan['samples']},set()
    return set(plan['order']),{'e'+str(i+1) for i in range(len(plan['edges']))}

def _split_study(printer,req,initial):
    """Probe bounded alternative focus panels, WITHOUT automatically delivering panels.

    Greedy union-cover is a *feasibility heuristic*, never a minimality proof.
    Every feasible prospective panel is rendered from the unchanged original request.
    """
    src=req['source_bundle']['view_plan'];view=src['view']
    full_items,full_edges=ids_and_edges(src)
    initial_ids=set(initial['shown_item_ids']);initial_edges={e['source_edge_id'] for e in initial['shown_edges']}
    if initial_ids==full_items and initial_edges==full_edges:
        return {'status':'NOT_REQUIRED','strategy':'focused_panels_from_immutable_source',
                'estimated_panel_count':1,'panels':[{'focus':None,'shown_item_ids':sorted(initial_ids),'shown_edge_ids':sorted(initial_edges)}],
                'uncovered_item_ids':[],'uncovered_edge_ids':[],'repeated_item_ids':[],
                'unavailable_focus_count':0,'is_minimum_proven':False,'panels_materialized':False}
    focuses=[]
    if view=='cube.diagramm':
        focuses=[{'kind':'sample','id':s['id']} for s in src['samples']]
    else:
        focuses=[{'kind':'edge','id':'e'+str(i+1)} for i in range(len(src['edges']))]
        focuses.extend({'kind':'node','id':id_} for id_ in src['order'])
    candidates=[];skipped=0
    for focus in [None]+focuses:
        q=copy.deepcopy(req);q['projection']['focus']=focus
        try:
            projection=printer.project(q)
        except GranularityError:
            skipped+=1;continue
        p=projection['plan'];items,_=ids_and_edges(p)
        edges=set(projection['edge_id_map'])
        candidates.append((focus,items,edges))
    # greedy weighted set cover; connections weighted to discourage disconnected narrative
    outstanding_items=set(full_items);outstanding_edges=set(full_edges)
    chosen=[]
    while outstanding_items or outstanding_edges:
        scored=[]
        for i,(focus,items,edges) in enumerate(candidates):
            gain_items=items&outstanding_items;gain_edges=edges&outstanding_edges
            benefit=len(gain_items)+3*len(gain_edges)
            if benefit:scored.append((benefit,-i,i))
        if not scored or len(chosen)==8:break
        _,__,index=max(scored)
        focus,items,edges=candidates[index]
        chosen.append((focus,items,edges))
        outstanding_items-=items;outstanding_edges-=edges
    counts=Counter(i for _,items,_ in chosen for i in items)
    return {'status':'FEASIBLE' if not outstanding_items and not outstanding_edges else 'NOT_FEASIBLE',
            'strategy':'focused_panels_from_immutable_source','estimated_panel_count':len(chosen),
            'panels':[{'focus':f,'shown_item_ids':sorted(items),'shown_edge_ids':sorted(edges)} for f,items,edges in chosen],
            'uncovered_item_ids':sorted(outstanding_items),'uncovered_edge_ids':sorted(outstanding_edges),
            'repeated_item_ids':sorted(k for k,v in counts.items() if v>1),
            'unavailable_focus_count':skipped,'is_minimum_proven':False,'panels_materialized':False}

def _decision(req,rep,split):
    total=rep['counts']['source_items'];omit=rep['counts']['items_omitted'];level=rep['granularity']
    selected_source_lens=[x for x in req['source_bundle']['facet_bindings'] if x['lens']==rep['lens']]
    blind=bool(selected_source_lens) and rep['lens_emphasis']=='no_visible_declared_targets'
    if omit==0 and rep['counts']['edges_omitted']==0:
        return {'action':'SINGLE_COMPLETE','rationale':'entire declared source is visible in this projection',
                'status':'descriptive_display_only'}
    pressure=(omit/total>=.60 or (level=='standard' and (rep['counts']['edges_omitted']>0 or
                    any(x['lens']==rep['lens'] for x in rep['omitted_facet_bindings']))) or blind)
    if pressure:
        if split['status']=='FEASIBLE':
            return {'action':'SPLIT_RECOMMENDED','rationale':'substantial source reduction / selected lens evidence occluded; feasible bounded focus-panel coverage',
                    'status':'proposal_not_printed'}
        return {'action':'REFOCUS_OR_RAISE_BUDGET','rationale':'projection loses important detail, but the bounded focus-panel study did not cover the whole source',
                'status':'proposal_not_printed'}
    return {'action':'SINGLE_DISCLOSED','rationale':'intentional bounded reduction with explicit item/edge disclosure',
            'status':'descriptive_display_only'}

class ConformanceAuditor:
    def __init__(self):self.printer=GranularityPrinter()

    def audit(self,req,expected=None,include_svg=False):
        """Return report (optionally also SVG). Independent invariants are checked
        against the FULL authored source and VP04 report rather than trusting a PASS string.
        """
        try:
            svg=self.printer.render(req)
            rep=self.printer.report(req,svg)
        except (GranularityError,KeyError,ValueError,TypeError) as error:
            raise ConformanceError('VP04 rejected input: '+str(error)) from error
        p=req['projection'];full=req['source_bundle']['view_plan']
        view=full['view'];focus=p['focus']
        all_items,all_edges=ids_and_edges(full)
        shown=set(rep['shown_item_ids']);omitted=set(rep['omitted_item_ids'])
        e_shown={e['source_edge_id'] for e in rep['shown_edges']}
        e_omitted={e['source_edge_id'] for e in rep['omitted_edges']}
        invariants=[]
        def verify(test,identifier):
            demand(test,'conformance invariant failed: '+identifier)
            if identifier not in invariants:invariants.append(identifier)
        verify(req['source_bundle_sha256']==sha(req['source_bundle'])==rep['source_bundle_sha256'],'SOURCE_SHA256_LOCK')
        verify(view in VIEWS and view==rep['view']==p['view'],'CUBE_VIEW_NAMESPACE')
        verify(p['lens'] in LENSES and p['lens']==rep['lens'],'DECLARED_LENS_ONLY')
        verify(p['granularity'] in LEVELS and p['granularity']==rep['granularity'],'GRANULARITY_SCOPE')
        verify(shown|omitted==all_items and not shown&omitted,'EXACT_ITEM_PARTITION')
        verify(e_shown|e_omitted==all_edges and not e_shown&e_omitted,'EXACT_EDGE_PARTITION')
        verify(rep['counts']['items_shown']==len(shown) and rep['counts']['items_omitted']==len(omitted) and
               rep['counts']['edges_shown']==len(e_shown) and rep['counts']['edges_omitted']==len(e_omitted),'LOSS_LEDGER_BALANCED')
        projected=self.printer.project(req)['plan']
        src_items={x['id']:x for x in full.get('samples',full.get('nodes',[]))}
        kept_items=projected.get('samples',projected.get('nodes',[]))
        verify(all(src_items.get(x['id'])==x for x in kept_items),'ORIGINAL_ITEMS_UNCHANGED')
        if view=='cube.diagramm':
            if full['plot']=='line':
                idx=[next(i for i,s in enumerate(full['samples']) if s['id']==x['id']) for x in projected['samples']]
                verify(idx==list(range(min(idx),max(idx)+1)),'LINE_WINDOW_CONTIGUOUS')
            else:
                peak=max(s['value'] for s in full['samples'])
                verify(any(s['value']==peak for s in projected['samples']),'BAR_MAXIMUM_PRESERVED')
            verify(rep['chart_window']==('contiguous_window_only' if full['plot']=='line' else 'not_applicable'),'CHART_WINDOW_DECLARED')
        else:
            original={('e'+str(i+1)):e for i,e in enumerate(full['edges'])}
            mapped=[]
            for item in rep['shown_edges']:
                e=original[item['source_edge_id']];j=int(item['projected_edge_id'][1:])-1
                mapped.append(projected['edges'][j]==e and e['from'] in shown and e['to'] in shown)
            verify(all(mapped),'ORIGINAL_EDGES_UNCHANGED')
            if view=='cube.tree':
                root=full['root_id'];parents={e['to']:e['from'] for e in full['edges']}
                verify(root in shown and all(parents[x] in shown for x in shown if x!=root),'TREE_ANCESTOR_CLOSURE')
        if focus is not None:
            if focus['kind']=='node' or focus['kind']=='sample':verify(focus['id'] in shown,'FOCUS_RETAINED')
            elif focus['kind']=='edge':verify(focus['id'] in e_shown,'FOCUS_EDGE_RETAINED')
            else:verify(focus['kind']=='metric' and focus['id']==full['metric']['id'],'FOCUS_METRIC_RETAINED')
        displayed=rep['displayed_facet_bindings'];hidden=rep['omitted_facet_bindings']
        allbind=req['source_bundle']['facet_bindings']
        # Compare multisets of original declarations after reversing projected e1/e2 remapping.
        reverse={x['projected_edge_id']:x['source_edge_id'] for x in rep['shown_edges']}
        restored=[]
        for b in displayed:
            c=copy.deepcopy(b)
            if c['target_kind']=='edge':
                verify(c['target_id'] in reverse,'LENS_EDGE_REMAP_DECLARED')
                c['target_id']=reverse[c['target_id']]
            restored.append(c)
        encoded=lambda seq:Counter(json.dumps(x,sort_keys=True,ensure_ascii=False) for x in seq)
        verify(encoded(restored+hidden)==encoded(allbind),'EXACT_LENS_BINDING_PARTITION')
        root=ET.fromstring(svg)
        verify(root.tag==f'{{{NS}}}svg' and root.get('data-vp04-source-bundle-sha256')==req['source_bundle_sha256'],'SVG_SOURCE_LOCK')
        forbidden={'script','foreignObject','image','use','animate','set','iframe'}
        verify(not any(x.tag.rsplit('}',1)[-1] in forbidden for x in root.iter()) and
               not any(k.lower().startswith('on') or k in ('href','xlink:href') for x in root.iter() for k in x.attrib),'NO_ACTIVE_SVG_CONTENT')
        blocks=[x for x in root.iter() if x.get('id')=='vp04-source-and-reduction-ledger']
        verify(len(blocks)==1,'ONE_EMBEDDED_LOSS_LEDGER')
        meta=json.loads(blocks[0].text)
        verify(meta['omitted_item_ids']==rep['omitted_item_ids'] and meta['omitted_edges']==rep['omitted_edges'] and
               meta['omitted_facet_bindings']==hidden,'EMBEDDED_REPORT_MATCH')
        verify(all(rep[key]=='NOT_EVALUATED' for key in ('semantic_conformance','epistemic_warrant','current_authority','canonical_admission')),
               'NO_SEMANTIC_AUTHORITY_PROMOTION')
        verify(rep['content_status']=='declared_unverified','SOURCE_IS_DECLARED_UNVERIFIED')
        if expected is not None:
            for k,v in expected.items():
                if k=='source_items':observed=rep['counts']['source_items']
                elif k=='shown_items':observed=rep['counts']['items_shown']
                elif k=='shown_edges':observed=rep['counts']['edges_shown']
                elif k=='completeness':observed=rep['completeness']
                else:raise ConformanceError('unknown independent oracle field: '+k)
                verify(observed==v,'INDEPENDENT_ORACLE_'+k.upper())
        split=_split_study(self.printer,req,rep)
        decision=_decision(req,rep,split)
        result={
            'format':REPORT_FORMAT,'profile':PROFILE,'reference_version':'v9.4',
            'status':'PASS','dimensions':{'view':view,'lens':p['lens'],'granularity':p['granularity']},
            'source_bundle_sha256':req['source_bundle_sha256'],
            'svg_sha256':hashlib.sha256(svg).hexdigest(),
            'vp04_report_sha256':json_sha(rep),
            'invariants_passed':invariants,'displayed_item_ids':rep['shown_item_ids'],
            'omitted_item_ids':rep['omitted_item_ids'],
            'displayed_source_edge_ids':sorted(e_shown),'omitted_source_edge_ids':sorted(e_omitted),
            'displayed_lens_declarations':len(displayed),
            'omitted_lens_declarations':len(hidden),
            'chart_axis_rescaled':rep['chart_axis_rescaled'],
            'completeness':rep['completeness'],'decision':decision,'split_feasibility':split,
            'epistemic_warrant':'NOT_EVALUATED','current_authority':'NOT_EVALUATED',
            'canonical_admission':'NOT_EVALUATED','source_status':'declared_unverified',
            'limits':['Split feasibility is a heuristic, not a generated multi-page export or optimal partition',
                      'Glyph rendering varies with installed fonts','P1 semantic conformance is not evaluated by the SVG printer']}
        return (result,svg,rep) if include_svg else result
