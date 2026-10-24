"""VP-03 presentation-only lens profiles over immutable VP-02 view plans.

Explicit fixture facet declarations drive emphasis. No lookup/inference of ontology
semantics, verification, provenance, actual authority or observation is attempted.
Every input node, edge, chart sample and measurement remains present at standard
granularity. XML geometry is derived entirely from the existing VP-02 printer.
"""
from __future__ import annotations
import hashlib
import json
from decimal import Decimal
from xml.etree import ElementTree as ET
from vpviews import ViewPrinter
from vpviews.printer import ViewError, exact_keys as _exact_keys, short as _short, ident as _ident
from vp2d.printer import add, rect, line, color_blend, NS

PROFILE='P2-VP-LENSES/0.3.0'
FORMAT='aiaeao.cube.vp03-lens-bundle/1'
PROFILES=(
    'cube.lens.semantics',
    'cube.lens.provenance',
    'cube.lens.execution',
    'cube.lens.governance',
    'cube.lens.epistemology',
)
LABELS={x:x.split('.')[-1].upper() for x in PROFILES}
BASE_STATUS='declared_unverified'

class LensError(ViewError):
    """Presentation lens declaration error; not a P1 semantic status."""


def require(condition,message):
    if not condition:raise LensError(message)


def exact_keys(*args,**kwargs):
    try:return _exact_keys(*args,**kwargs)
    except ViewError as error:raise LensError(str(error)) from error


def short(*args,**kwargs):
    try:return _short(*args,**kwargs)
    except ViewError as error:raise LensError(str(error)) from error


def ident(*args,**kwargs):
    try:return _ident(*args,**kwargs)
    except ViewError as error:raise LensError(str(error)) from error


def source_digest(plan):
    """SHA-256 of stable Unicode JSON, not source text formatting."""
    return hashlib.sha256(json.dumps(plan,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')).hexdigest()


def cjson(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


class LensPrinter:
    def __init__(self,reference_dir=None):
        self.base=ViewPrinter(reference_dir)
        colors=self.base.base.colors
        self.accents={name:colors['domain.'+name.rsplit('.',1)[-1]] for name in PROFILES}
        if len(set(self.accents.values()))!=5:
            raise LensError('P1 domain-accent tokens are missing or duplicated')

    def validate(self,bundle,lens):
        require(lens in PROFILES,'unsupported cube.lens.* profile')
        exact_keys(bundle,{'format','lens_profile','reference_version','source_view_sha256','view_plan','facet_bindings','basis'},context='VP-03 lens bundle')
        require(bundle['format']==FORMAT,'wrong VP-03 bundle format')
        require(bundle['lens_profile']==PROFILE,'wrong VP-03 profile')
        require(bundle['reference_version']=='v9.4','wrong morphology reference')
        require(bundle['basis']==BASE_STATUS,'lens facet basis must be declared_unverified')
        plan=bundle['view_plan']
        try:self.base.validate(plan)  # immutable VP-02 checks, including fixed neutral lens
        except ViewError as error:raise LensError(str(error)) from error
        require(bundle['source_view_sha256']==source_digest(plan),'source view checksum differs from unchanged VP-02 plan')
        if plan['view']=='cube.diagramm':
            targets={'sample':{s['id'] for s in plan['samples']},'metric':{plan['metric']['id']}}
        else:
            targets={'node':{n['id'] for n in plan['nodes']},'edge':{f'e{i+1}' for i,_ in enumerate(plan['edges'])}}
        bindings=bundle['facet_bindings']
        require(isinstance(bindings,list) and 1<=len(bindings)<=75,'facet_bindings must have 1..75 entries')
        seen=set();selected=[]
        for b in bindings:
            exact_keys(b,{'lens','target_kind','target_id','declaration_ref','note','basis'},context='facet binding')
            require(b['lens'] in PROFILES,'unsupported facet lens')
            require(b['target_kind'] in targets,'facet target kind not present in this view')
            ident(b['target_id'],'facet target_id')
            require(b['target_id'] in targets[b['target_kind']],'unknown facet target')
            short(b['declaration_ref'],'facet declaration_ref',180)
            require(b['declaration_ref'].startswith('fixture:') or b['declaration_ref'].startswith('decl:'),'facet declaration must be explicitly scoped as fixture: or decl:')
            short(b['note'],'facet note',80)
            require(b['basis']==BASE_STATUS,'facet binding has unsupported evidence status')
            key=(b['lens'],b['target_kind'],b['target_id'])
            require(key not in seen,'duplicate facet target for same lens')
            seen.add(key)
            if b['lens']==lens:selected.append(b)
        require(selected,'selected lens has no explicit facet bindings: cannot infer relevance')
        return {'plan':plan,'targets':targets,'selected':selected,'all_bindings':bindings}

    def _emphasize_cards(self,root,kind,ident_,accent):
        group=next((g for g in root.iter(f'{{{NS}}}g') if g.get('data-item-id')==ident_),None)
        require(group is not None,'renderer did not produce declared node')
        group.set('data-vp03-lens-focus','declared')
        group.set('data-vp03-focus-purpose','visual-only')
        shape=next((x for x in group if x.tag in (f'{{{NS}}}rect',f'{{{NS}}}circle')),None)
        require(shape is not None,'renderer node has no geometric carrier')
        if shape.tag==f'{{{NS}}}rect':
            add(group,'rect',x=shape.get('x'),y=shape.get('y'),width=shape.get('width'),height=shape.get('height'),rx=shape.get('rx','9'),fill='none',stroke=accent,stroke_width='3',stroke_dasharray='7 4',pointer_events='none')
        else:
            add(group,'circle',cx=shape.get('cx'),cy=shape.get('cy'),r=shape.get('r'),fill='none',stroke=accent,stroke_width='3',stroke_dasharray='7 4',pointer_events='none')

    def _emphasize_edge(self,root,ident_,accent):
        group=next((g for g in root.iter(f'{{{NS}}}g') if g.get('data-edge-id')==ident_),None)
        require(group is not None,'renderer did not produce declared edge')
        group.set('data-vp03-lens-focus','declared')
        group.set('data-vp03-focus-purpose','visual-only')
        for el in group:
            if el.tag in (f'{{{NS}}}line',f'{{{NS}}}path'):
                el.set('stroke',accent)
                el.set('stroke-width','2.8')

    def _emphasize_chart_sample(self,root,plan,ident_,accent):
        data=plan['samples'];index=next((i for i,x in enumerate(data) if x['id']==ident_),None)
        require(index is not None,'unknown chart sample')
        x=135+(index+.5)*974/len(data)
        # A deliberately additive label marker: no bars/values/measurements altered.
        mark=add(root,'g',**{'data-sample-id':ident_,'data-vp03-lens-focus':'declared','data-vp03-focus-purpose':'visual-only'})
        add(mark,'line',x1=round(x-27,2),y1=563,x2=round(x+27,2),y2=563,stroke=accent,stroke_width=4,stroke_linecap='round')

    def _emphasize_metric(self,root,ident_,accent):
        mark=add(root,'g',**{'data-metric-id':ident_,'data-vp03-lens-focus':'declared','data-vp03-focus-purpose':'visual-only'})
        add(mark,'line',x1=128,y1=176,x2=128,y2=521,stroke=accent,stroke_width=3,stroke_dasharray='7 5')

    def render(self,bundle,lens):
        derived=self.validate(bundle,lens)
        plan=derived['plan'];selected=derived['selected'];accent=self.accents[lens]
        base_svg=self.base.render(plan)
        root=ET.fromstring(base_svg)
        root.set('data-vp03-printer-profile',PROFILE)
        root.set('data-vp03-lens',lens)
        root.set('data-vp03-basis',BASE_STATUS)
        root.set('data-vp03-source-sha256',bundle['source_view_sha256'])
        for binding in selected:
            kind= binding['target_kind'];target=binding['target_id']
            if kind=='node':self._emphasize_cards(root,kind,target,accent)
            elif kind=='edge':self._emphasize_edge(root,target,accent)
            elif kind=='sample':self._emphasize_chart_sample(root,plan,target,accent)
            elif kind=='metric':self._emphasize_metric(root,target,accent)
        # Explicitly display which perspective is selected. The base view still
        # displays ALL original source objects and edges/samples.
        label=LABELS[lens]+'  ·  '+str(len(selected))+' DECLARED FOCUS'
        g=add(root,'g',**{'data-vp03-legend':'display-only','data-vp03-domain-token':'domain.'+lens.rsplit('.',1)[-1]})
        rect(g,832,104,326,49,stroke=accent,fill=color_blend(accent),radius=8)
        tx=add(g,'text',x=845,y=122,fill=accent,font_size=13,font_family='DejaVu Sans, sans-serif',font_weight='bold');tx.text=label
        tx=add(g,'text',x=845,y=139,fill='#475569',font_size=10,font_family='DejaVu Sans, sans-serif');tx.text='DECLARED DISPLAY FOCUS · NOT A VERDICT'
        # machine-readable metadata: exact binding pointers, no hidden semantic interpretation
        md=add(root,'metadata',id='vp03-focus-provenance')
        md.text=cjson({'profile':PROFILE,'lens':lens,'reference_version':'v9.4','source_view_sha256':bundle['source_view_sha256'],'status':BASE_STATUS,'bindings':selected,'nonimplication':['semantic_conformance','epistemic_warrant','current_authority','canonical_admission']})
        return ET.tostring(root,encoding='utf-8',xml_declaration=True,short_empty_elements=True)+b'\n'

    def report(self,bundle,lens,svg):
        d=self.validate(bundle,lens)
        plan=d['plan'];selected=d['selected']
        # Preserve unchanged data ledger by embedding original VP-02 report verbatim.
        base_svg=self.base.render(plan)
        base_report=self.base.report(plan,base_svg)
        return {'format':'aiaeao.cube.vp03-print-report/1','lens_profile':PROFILE,
                'reference_version':'v9.4','view':plan['view'],'lens':lens,'granularity':'standard',
                'source_view_sha256':bundle['source_view_sha256'],
                'base_view_svg_sha256':hashlib.sha256(base_svg).hexdigest(),
                'svg_sha256':hashlib.sha256(svg).hexdigest(),
                'render_status':'PASS','focus_status':'declared_unverified',
                'highlighted':[dict(x) for x in selected],
                'original_vp02_report':base_report,
                'content_status':'declared_unverified',
                'semantic_conformance':'NOT_EVALUATED',
                'epistemic_warrant':'NOT_EVALUATED',
                'current_authority':'NOT_EVALUATED',
                'canonical_admission':'NOT_EVALUATED',
                'notices':['Every source element remains visible; VP-03 changes visual emphasis only.',
                           'Facet bindings are authored display declarations, not evidence of operational facts.',
                           'Lens color, form, layout and focus neither grant authority nor assert truth.']}
