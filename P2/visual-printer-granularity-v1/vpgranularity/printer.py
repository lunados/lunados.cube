"""VP-04: bounded, declarative reductions of immutable VP-03 lens bundles.

This package never synthesizes a typed relationship, a measurement, or a canonical
identity. All dropped source IDs are disclosed in SVG and a machine-readable report.
"""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

BASE=Path(__file__).resolve().parents[2]/'visual-printer-2d-lab'
if not BASE.is_dir(): raise RuntimeError('VP-03 immutable baseline missing: '+str(BASE))
if str(BASE) not in sys.path:sys.path.insert(0,str(BASE))
from vplenses import LensPrinter, PROFILES
from vplenses.printer import LensError, source_digest, cjson, FORMAT as VP03_FORMAT
from vpviews import ViewPrinter
from vpviews.printer import ViewError
from vp2d.printer import NS, add, rect, text

PROFILE='P2-VP-GRANULARITY/0.4.0'
FORMAT='aiaeao.cube.vp04-projection-request/1'
REPORT_FORMAT='aiaeao.cube.vp04-print-report/1'
LEVELS=('overview','standard','detail')
CAPS={
    'overview':{'cube.flow':(2,1),'cube.diagramm':(2,0),'cube.tree':(3,2)},
    'standard':{'cube.flow':(4,4),'cube.diagramm':(4,0),'cube.tree':(5,4)},
    'detail':{'cube.flow':(4,8),'cube.diagramm':(6,0),'cube.tree':(7,6)},
}
MAX_CANVAS_BYTES=1024*1024

class GranularityError(ValueError):
    """Error in the projection request or its presentation budget; not a P1 verdict."""

def need(ok,message):
    if not ok:raise GranularityError(message)

def exact(value,required,context):
    need(type(value) is dict,context+' must be an object')
    need(set(value)==set(required),context+' requires exactly '+','.join(sorted(required)))

def sha(value):return hashlib.sha256(cjson(value).encode('utf-8')).hexdigest()

def edge_id(index):return 'e'+str(index+1)

def target_refs(plan):
    if plan['view']=='cube.diagramm':return [('sample',s['id']) for s in plan['samples']]
    return [('node',id_) for id_ in plan['order']]

class GranularityPrinter:
    def __init__(self):
        self.lens_printer=LensPrinter()
        self.view_printer=ViewPrinter()

    def validate(self,req):
        exact(req,('format','profile','reference_version','source_bundle','source_bundle_sha256','projection'),'VP-04 request')
        need(req['format']==FORMAT,'wrong VP-04 format')
        need(req['profile']==PROFILE,'wrong VP-04 profile')
        need(req['reference_version']=='v9.4','reference version must be v9.4')
        bundle=req['source_bundle']
        need(type(bundle) is dict,'source_bundle must be object')
        need(req['source_bundle_sha256']==sha(bundle),'VP-03 bundle source checksum mismatch')
        p=req['projection'];exact(p,('view','lens','granularity','focus','budget','overflow'),'projection')
        need(p['lens'] in PROFILES,'unknown or unauthorized lens')
        need(p['granularity'] in LEVELS,'granularity must be overview, standard, detail')
        need(p['overflow'] in ('summarize','reject'),'overflow must be summarize or reject')
        exact(p['budget'],('max_items','max_edges'),'budget')
        # Strict bool rejection (bool is int subclass).
        for k in ('max_items','max_edges'):need(type(p['budget'][k]) is int and p['budget'][k]>=0,'budget '+k+' requires a nonnegative integer')
        try:d=self.lens_printer.validate(bundle,p['lens'])
        except (LensError,ViewError) as e:raise GranularityError('invalid VP-03 source: '+str(e)) from e
        plan=d['plan'];view=plan['view'];need(view==p['view'],'requested view differs from source view')
        n=len(plan['samples']) if view=='cube.diagramm' else len(plan['nodes'])
        e=0 if view=='cube.diagramm' else len(plan['edges'])
        limitems,limedges=CAPS[p['granularity']][view]
        minitems=2
        minedges=0 if view=='cube.diagramm' else 1
        need(minitems<=p['budget']['max_items']<=limitems,'max_items exceeds selected level/view range')
        need(minedges<=p['budget']['max_edges']<=limedges,'max_edges exceeds selected level/view range')
        focus=p['focus']
        if focus is not None:
            exact(focus,('kind','id'),'focus')
            kind=focus['kind'];fid=focus['id']
            need(type(fid) is str and bool(re.fullmatch('[A-Za-z][A-Za-z0-9_.:-]{0,99}',fid)),'invalid focus ID')
            if view=='cube.diagramm':need(kind in ('sample','metric'),'chart focus must be sample or metric')
            else:need(kind in ('node','edge'),'graph focus must be node or edge')
            if kind=='sample':need(fid in {s['id'] for s in plan['samples']},'focus sample not in source')
            if kind=='metric':need(fid==plan['metric']['id'],'focus metric not in source')
            if kind=='node':need(fid in set(plan['order']),'focus node not in source')
            if kind=='edge':need(fid in [edge_id(i) for i in range(e)],'focus edge not in source')
        if p['granularity']=='detail':
            need(p['budget']['max_items']>=n and p['budget']['max_edges']>=e,'detail cannot omit source items or edges; increase budget (within layout cap)')
        if p['overflow']=='reject':need(n<=p['budget']['max_items'] and e<=p['budget']['max_edges'],'overflow=reject: source exceeds budget')
        return d

    def _select_flow(self,plan,selected,budget,focus):
        order=plan['order'];edges=plan['edges'];n=min(len(order),budget['max_items'])
        required=set()
        forced_edge=None
        if focus:
            if focus['kind']=='node':required.add(focus['id'])
            elif focus['kind']=='edge':
                i=int(focus['id'][1:])-1
                required.update((edges[i]['from'],edges[i]['to']))
                forced_edge=i
        priority_nodes={b['target_id'] for b in selected if b['target_kind']=='node'}
        priority_edges={b['target_id'] for b in selected if b['target_kind']=='edge'}
        options=[]
        for indices in itertools.combinations(range(len(order)),n):
            ids={order[i] for i in indices}
            if not required<=ids:continue
            available=[i for i,e in enumerate(edges) if e['from'] in ids and e['to'] in ids]
            if not available or (forced_edge is not None and forced_edge not in available):continue
            # Original authored edge order remains primary, highlighted/focused edges preferentially retained.
            eligible=sorted(available,key=lambda i:(i!=forced_edge,edge_id(i) not in priority_edges,i))
            kept=sorted(eligible[:budget['max_edges']])
            if forced_edge is not None and forced_edge not in kept:continue
            score=(len(kept),sum(order[i] in priority_nodes for i in indices),sum(edge_id(i) in priority_edges for i in kept),tuple(-i for i in indices))
            options.append((score,set(ids),kept))
        need(bool(options),'no declared connected subset fits flow budget/focus; cannot fabricate an edge')
        _,ids,kept=max(options,key=lambda a:a[0])
        return ids,kept

    def _select_tree(self,plan,selected,budget,focus):
        order=plan['order'];root=plan['root_id'];edges=plan['edges'];n=min(len(order),budget['max_items'],budget['max_edges']+1)
        parents={e['to']:e['from'] for e in edges}
        required={root}
        if focus:
            fid=focus['id']
            if focus['kind']=='edge':fid=edges[int(fid[1:])-1]['to']
            while fid not in required:
                required.add(fid);fid=parents.get(fid,root)
        need(len(required)<=n,'focus ancestry exceeds tree budget; increase max_items/max_edges')
        priority={b['target_id'] for b in selected if b['target_kind']=='node'}
        priority_edges={b['target_id'] for b in selected if b['target_kind']=='edge'}
        candidates=[]
        rest=[x for x in order if x!=root]
        for comb in itertools.combinations(rest,n-1):
            ids=set(comb)|{root}
            if not required<=ids or any(parents.get(x) not in ids for x in ids-{root}):continue
            kept=[i for i,e in enumerate(edges) if e['from'] in ids and e['to'] in ids]
            if len(kept)!=len(ids)-1:continue
            score=(sum(x in priority for x in ids),sum(edge_id(i) in priority_edges for i in kept),tuple(-order.index(x) for x in order if x in ids))
            candidates.append((score,ids,kept))
        need(bool(candidates),'no ancestor-closed subset fits tree budget/focus')
        _,ids,kept=max(candidates,key=lambda a:a[0]);return ids,kept

    def _select_chart(self,plan,selected,budget,focus):
        samples=plan['samples'];n=min(len(samples),budget['max_items'])
        focus_sample=focus['id'] if focus and focus['kind']=='sample' else None
        priorities={b['target_id'] for b in selected if b['target_kind']=='sample'}
        max_value=max(s['value'] for s in samples)
        # For bars, retain a maximal sample so zero-based scale remains comparable.
        peak_index=next(i for i,s in enumerate(samples) if s['value']==max_value)
        indices=[]
        if plan['plot']=='line':
            # Never connect non-adjacent retained points (false intermediate segment).
            for start in range(len(samples)-n+1):
                group=list(range(start,start+n))
                if focus_sample and focus_sample not in {samples[i]['id'] for i in group}:continue
                score=(sum(samples[i]['id'] in priorities for i in group),peak_index in group,-start)
                indices.append((score,group))
        else:
            for group in itertools.combinations(range(len(samples)),n):
                if focus_sample and focus_sample not in {samples[i]['id'] for i in group}:continue
                if peak_index not in group:continue
                score=(sum(samples[i]['id'] in priorities for i in group),tuple(-i for i in group))
                indices.append((score,list(group)))
        need(bool(indices),'chart focus/scale cannot fit budget')
        _,kept=max(indices,key=lambda x:x[0]);return {samples[i]['id'] for i in kept}

    def project(self,req):
        d=self.validate(req);plan=d['plan'];p=req['projection'];view=plan['view'];budget=p['budget'];focus=p['focus']
        selected=d['selected']
        projected=copy.deepcopy(plan)
        original_items=[x['id'] for x in plan['samples']] if view=='cube.diagramm' else plan['order'][:]
        old_edges=plan.get('edges',[])
        if view=='cube.diagramm':
            ids=self._select_chart(plan,selected,budget,focus)
            projected['samples']=[s for s in plan['samples'] if s['id'] in ids]
            kept_edges=[]
        else:
            if view=='cube.flow':ids,kept_edges=self._select_flow(plan,selected,budget,focus)
            else:ids,kept_edges=self._select_tree(plan,selected,budget,focus)
            projected['nodes']=[node for node in plan['nodes'] if node['id'] in ids]
            projected['order']=[node_id for node_id in plan['order'] if node_id in ids]
            projected['edges']=[copy.deepcopy(old_edges[i]) for i in kept_edges]
        omitted_items=[i for i in original_items if i not in ids]
        edge_mapping={edge_id(old):edge_id(new) for new,old in enumerate(kept_edges)}
        omitted_edges=[]
        for i,e in enumerate(old_edges):
            if i not in kept_edges:
                omitted_edges.append({'source_edge_id':edge_id(i),'from':e['from'],'to':e['to'],
                    'predicate_id':e['predicate_id'],'declaration_ref':e['declaration_ref'],
                    'reason':'endpoint_omitted' if (e['from'] not in ids or e['to'] not in ids) else 'edge_budget'})
        vis=[];hidden=[]
        for b in d['all_bindings']:
            keep=(b['target_kind']=='metric' or (b['target_kind']=='node' and b['target_id'] in ids) or
                  (b['target_kind']=='sample' and b['target_id'] in ids) or
                  (b['target_kind']=='edge' and b['target_id'] in edge_mapping))
            if keep:
                new=copy.deepcopy(b)
                if b['target_kind']=='edge':new['target_id']=edge_mapping[b['target_id']]
                vis.append(new)
            else:hidden.append(copy.deepcopy(b))
        need(len(projected['nodes'])>=2 if view!='cube.diagramm' else len(projected['samples'])>=2,'too few display items')
        try:self.view_printer.validate(projected)
        except ViewError as error:raise GranularityError('projection invalid under VP-02 contract: '+str(error)) from error
        reduced=copy.deepcopy(req['source_bundle']);reduced['view_plan']=projected
        reduced['source_view_sha256']=source_digest(projected)
        reduced['facet_bindings']=vis
        lens_present=any(x['lens']==p['lens'] for x in vis)
        if lens_present:
            try:self.lens_printer.validate(reduced,p['lens'])
            except LensError as error:raise GranularityError('projected lens invalid: '+str(error)) from error
        axis_rescaled=(view=='cube.diagramm' and self.view_printer._max_tick([self.view_printer._validate_chart(plan)['values'][i] for i in range(len(plan['samples']))]) !=
                       self.view_printer._max_tick(self.view_printer._validate_chart(projected)['values']))
        summary={'items_omitted':len(omitted_items),'edges_omitted':len(omitted_edges),'facet_bindings_omitted':len(hidden),
                 'items_shown':len(ids),'edges_shown':len(kept_edges)}
        return {'plan':projected,'original':plan,'reduced_bundle':reduced,'lens_present':lens_present,'omitted_item_ids':omitted_items,
                'omitted_edges':omitted_edges,'visible_bindings':vis,'omitted_bindings':hidden,
                'edge_id_map':edge_mapping,'axis_rescaled':axis_rescaled,'summary':summary,
                'source_bundle_sha256':req['source_bundle_sha256']}

    def _assemble(self,req,proj):
        p=req['projection'];base=self.lens_printer.render(proj['reduced_bundle'],p['lens']) if proj['lens_present'] else self.view_printer.render(proj['plan'])
        need(len(base)<=MAX_CANVAS_BYTES,'SVG exceeds maximum canvas bytes')
        root=ET.fromstring(base)
        original_height=int(root.get('height'))
        # Extend canvas rather than overwrite VP-02 footnotes.
        footer_h=95
        root.set('height',str(original_height+footer_h))
        root.set('viewBox',f'0 0 1200 {original_height+footer_h}')
        # Preserve the original white background on the extended SVG canvas.
        # Otherwise transparency in raster previews can misleadingly appear black.
        background=next((child for child in root if child.tag==f'{{{NS}}}rect'
                         and child.get('x')=='0' and child.get('y')=='0'
                         and child.get('width')=='1200'),None)
        if background is not None:background.set('height',str(original_height+footer_h))
        root.set('data-vp04-printer-profile',PROFILE)
        root.set('data-vp04-granularity',p['granularity'])
        root.set('data-vp04-source-bundle-sha256',req['source_bundle_sha256'])
        root.set('data-vp04-reduced-view-sha256',source_digest(proj['plan']))
        focus=p['focus']
        if focus is not None:
            root.set('data-vp04-focus-kind',focus['kind'])
            root.set('data-vp04-focus-id',focus['id'])
        for el in root.iter(f'{{{NS}}}g'):
            e=el.get('data-edge-id')
            if e:
                inverse={v:k for k,v in proj['edge_id_map'].items()}
                if e in inverse:el.set('data-source-edge-id',inverse[e])
        # Decoration is a footnote only, NEVER a synthetic typed node or edge.
        g=add(root,'g',**{'data-vp04-complexity-ledger':'display-only','aria-label':'Projection completeness disclosure'})
        rect(g,48,original_height+10,1104,72,stroke='#94A3B8',fill='#F1F5F9',radius=9)
        s=proj['summary']
        text(g,65,original_height+34,'VP-04 · '+p['granularity'].upper()+' · DISPLAY BUDGET · NOT A SEMANTIC VERDICT',13,'#334155','bold')
        message=(f"Shown {s['items_shown']} items / {s['edges_shown']} edges  ·  omitted {s['items_omitted']} items / {s['edges_omitted']} edges")
        text(g,65,original_height+57,message,13,'#475569')
        if proj['axis_rescaled']:
            text(g,772,original_height+57,'CHART AXIS RESCALED',12,'#B45309','bold')
        if not proj['lens_present']:
            text(g,770,original_height+33,'LENS HAS NO VISIBLE DECLARED TARGETS',11,'#9A3412','bold')
        meta=add(root,'metadata',id='vp04-source-and-reduction-ledger')
        meta.text=cjson({'source_bundle_sha256':req['source_bundle_sha256'],'projection':p,'reduced_view_sha256':source_digest(proj['plan']),
                         'omitted_item_ids':proj['omitted_item_ids'],'omitted_edges':proj['omitted_edges'],
                         'omitted_facet_bindings':proj['omitted_bindings'],'edge_id_map':proj['edge_id_map'],
                         'axis_rescaled':proj['axis_rescaled'],'status':'declared_unverified',
                         'nonimplications':['truth','causality','authority','admission','completeness']})
        return ET.tostring(root,encoding='utf-8',xml_declaration=True,short_empty_elements=True)+b'\n'

    def render(self,req):
        return self._assemble(req,self.project(req))

    def report(self,req,svg):
        proj=self.project(req)
        expected=self._assemble(req,proj)
        need(svg==expected,'SVG/report mismatch: exact rendered bytes required')
        view=proj['plan']['view'];s=proj['summary']
        return {'format':REPORT_FORMAT,'profile':PROFILE,'reference_version':'v9.4','render_status':'PASS',
                'view':view,'lens':req['projection']['lens'],'granularity':req['projection']['granularity'],
                'focus':req['projection']['focus'],'budget':req['projection']['budget'],'overflow':req['projection']['overflow'],
                'source_bundle_sha256':req['source_bundle_sha256'],'source_view_sha256':req['source_bundle']['source_view_sha256'],
                'reduced_view_sha256':source_digest(proj['plan']),'svg_sha256':hashlib.sha256(svg).hexdigest(),
                'counts':{'source_items':len(proj['original']['samples']) if view=='cube.diagramm' else len(proj['original']['nodes']),
                          'source_edges':len(proj['original'].get('edges',[])),**s},
                'shown_item_ids':[x['id'] for x in proj['plan']['samples']] if view=='cube.diagramm' else proj['plan']['order'],
                'shown_edges':[{'source_edge_id':k,'projected_edge_id':v} for k,v in proj['edge_id_map'].items()],
                'omitted_item_ids':proj['omitted_item_ids'],'omitted_edges':proj['omitted_edges'],
                'displayed_facet_bindings':proj['visible_bindings'],'omitted_facet_bindings':proj['omitted_bindings'],
                'lens_emphasis':'declared_unverified' if proj['lens_present'] else 'no_visible_declared_targets',
                'chart_axis_rescaled':proj['axis_rescaled'],
                'chart_window':'contiguous_window_only' if view=='cube.diagramm' and proj['plan']['plot']=='line' else 'not_applicable',
                'completeness':'PARTIAL_EXPLICIT' if proj['omitted_item_ids'] or proj['omitted_edges'] else 'COMPLETE_INPUT_VIEW',
                'content_status':'declared_unverified','semantic_conformance':'NOT_EVALUATED','epistemic_warrant':'NOT_EVALUATED',
                'current_authority':'NOT_EVALUATED','canonical_admission':'NOT_EVALUATED',
                'notices':['Aggregated count is display-only: no virtual entity, predicate or measurement was synthesized.',
                           'Every omitted element and edge is retained by identifier in this report and SVG metadata.',
                           'Chart subset scaling must not be compared across levels unless chart_axis_rescaled=false.',
                           'Layouts, lens markers, focus and filtering never imply verified truth or granted authority.']}
