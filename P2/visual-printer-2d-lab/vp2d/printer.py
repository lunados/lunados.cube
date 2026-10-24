"""Deterministic, no-network, no-side-effects SVG 2D rendering experiment.

Projection only. A valid render plan does NOT mean a valid ACG assertion,
verified witness, admitted action or recognized ontology instance.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

PROFILE="P2-VP-2D/0.1.0"
NS="http://www.w3.org/2000/svg"
ET.register_namespace('', NS)
FONT="DejaVu Sans, Noto Sans Symbols 2, Apple Symbols, Segoe UI Symbol, sans-serif"
GLYPH_FONT="FreeSerif, Noto Sans Math, Noto Sans Symbols 2, Apple Symbols, serif"
HERE=Path(__file__).resolve().parents[1]
HEX=re.compile(r'^#[0-9A-Fa-f]{6}$')
KEY=re.compile(r'^[A-Za-z][A-Za-z0-9_.:-]{0,99}$')

class PrintError(ValueError):
    """A presentation-plan error, not a P1 semantic diagnostic."""


def add(p,name,**attrs):
    return ET.SubElement(p,f'{{{NS}}}{name}',{str(k).replace('_','-'):str(v) for k,v in attrs.items()})

def text(p,x,y,value,size=17,color='#111827',weight='normal',anchor=None,glyph=False):
    attrs=dict(x=x,y=y,fill=color,font_family=GLYPH_FONT if glyph else FONT,font_size=size,font_weight=weight)
    if anchor:attrs['text_anchor']=anchor
    e=add(p,'text',**attrs);e.text=value
    return e

def line(p,x1,y1,x2,y2,color='#64748B',dashed=False):
    attrs=dict(x1=x1,y1=y1,x2=x2,y2=y2,stroke=color,stroke_width=1.6)
    if dashed:attrs['stroke_dasharray']='5 7'
    return add(p,'line',**attrs)

def rect(p,x,y,w,h,stroke='#CBD5E1',fill='#FFFFFF',radius=8,dashed=False):
    a=dict(x=x,y=y,width=w,height=h,rx=radius,stroke=stroke,stroke_width=1.8,fill=fill)
    if dashed:a['stroke_dasharray']='6 5'
    return add(p,'rect',**a)

def color_blend(accent):
    """Very light fill, using only source token-derived RGB and white."""
    rgb=[int(accent[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join(f'{round(.09*v+.91*255):02X}' for v in rgb)

class Printer:
    def __init__(self, reference_dir=None):
        ref=Path(reference_dir) if reference_dir else HERE/'reference'
        self.symbols=json.loads((ref/'p0-symbols-v9.4.json').read_text('utf8'))
        self.pairs=json.loads((ref/'p0-core-v9.4.json').read_text('utf8'))['ontology']['X']['pairs']
        self.concepts=json.loads((ref/'p0-concepts-v9.4.json').read_text('utf8'))['concepts']
        self.anchors=json.loads((ref/'p1-anchors.json').read_text('utf8'))['entries']
        self.rules=json.loads((ref/'p1-form-color.json').read_text('utf8'))
        self.by_id={a['anchor_id']:a for a in self.anchors}
        self.p0_by_id={a['id']:a for a in self.symbols['anchors']}
        self.concept_by_id={a['id']:a for a in self.concepts}
        self.colors={k:v['hex'] for k,v in self.rules['colors'].items()}
        self.forms={v['id'] for v in self.rules['forms']}
        if len(self.by_id)!=129 or len(self.p0_by_id)!=129:
            raise PrintError('P0/P1 symbol registry count differs from expected 129')
        for a in self.anchors:
            if self.p0_by_id.get(a['anchor_id'],{}).get('glyph')!=a['unicode']:
                raise PrintError('P0/P1 symbol registry mismatch')

    def _node(self,item):
        if not isinstance(item,dict): raise PrintError('item must be an object')
        allowed={'id','anchor_id','label','form_id','color_token','semantic_ref','qualified_state_witness_ref','time_label'}
        if set(item)-allowed:raise PrintError('unknown item property')
        for k in ('id','anchor_id','label','form_id'):
            if k not in item or not isinstance(item[k],str) or not item[k]:raise PrintError('missing item field: '+k)
        if not KEY.fullmatch(item['id']):raise PrintError('invalid item id')
        if len(item['label'])>68: raise PrintError('label too long (max 68 chars)')
        a=self.by_id.get(item['anchor_id'])
        if not a:raise PrintError('unknown canonical visual anchor: '+item['anchor_id'])
        if item['form_id'] not in self.forms:raise PrintError('unknown form')
        if item['form_id'] not in (a['form_suggestion'],a['form_default']):
            raise PrintError('form not recommended for anchor: '+item['anchor_id'])
        c=item.get('color_token')
        if c:
            if c not in self.colors:raise PrintError('unknown color token')
            if a['color_policy']=='none_for_operators':raise PrintError('operator color forbidden')
            if c.startswith('domain.') and c!=a['domain_accent_token']:
                raise PrintError('wrong domain accent for anchor')
            if c.startswith('status.') and not item.get('qualified_state_witness_ref'):
                raise PrintError('status accent without qualified witness reference')
            if c.startswith('status.') and a['may_use_status_accent']!='context_only':
                raise PrintError('status accent not allowed for anchor')
        if item.get('qualified_state_witness_ref') and not isinstance(item['qualified_state_witness_ref'],str):
            raise PrintError('witness reference must be string')
        if item.get('semantic_ref') and not isinstance(item['semantic_ref'],str):
            raise PrintError('semantic reference must be string')
        if 'time_label' in item and (not isinstance(item['time_label'],str) or len(item['time_label'])>40):
            raise PrintError('time label invalid')
        return a

    def validate(self,plan):
        if not isinstance(plan,dict):raise PrintError('plan must be object')
        required={'printer_profile','reference_version','view_id','title','template','items'}
        allowed=required|{'links','order','sequence_basis','subtitle'}
        if set(plan)-allowed:raise PrintError('unexpected plan property')
        if not required.issubset(plan):raise PrintError('missing plan fields')
        if plan['printer_profile']!=PROFILE or plan['reference_version']!='v9.4':
            raise PrintError('wrong profile/version')
        if plan['template'] not in ('contract_pairs','relation_graph','sequence_thread','topology_blocks'):
            raise PrintError('unsupported 2D template')
        if not isinstance(plan['view_id'],str) or not KEY.fullmatch(plan['view_id']):
            raise PrintError('invalid view id')
        if not isinstance(plan['title'],str) or not 1<=len(plan['title'])<=72:
            raise PrintError('title required, maximum 72')
        if not isinstance(plan['items'],list):raise PrintError('items must be an array')
        if plan.get('subtitle') is not None and (not isinstance(plan['subtitle'],str) or len(plan['subtitle'])>105):
            raise PrintError('subtitle must be max 105 chars')
        items=plan['items']
        if plan['template']=='contract_pairs':
            if items:raise PrintError('contract_pairs uses canonical P0 pair registry; items must be []')
            if any(k in plan for k in ('links','order','sequence_basis')):raise PrintError('extra template fields')
        elif plan['template']=='relation_graph':
            if len(items)!=2:raise PrintError('prototype relation template needs exactly two items')
            links=plan.get('links')
            if not isinstance(links,list) or len(links)!=1:raise PrintError('prototype relation template needs one declared link')
            e=links[0]
            if not isinstance(e,dict) or set(e)!={'from','to','arrow_anchor_id','predicate_id','declaration_ref'}:
                raise PrintError('link must include declared predicate and declaration_ref')
            if e['arrow_anchor_id'] not in self.by_id or self.by_id[e['arrow_anchor_id']]['visual_role']!='relation_operator':
                raise PrintError('link needs canonical Unicode relation operator')
            if e['arrow_anchor_id']!='relation-arrows.reference':
                raise PrintError('prototype supports only neutral registered reference operator')
            for k in ('predicate_id','declaration_ref'):
                if not isinstance(e[k],str) or not e[k] or len(e[k])>130:raise PrintError('missing declaration metadata')
            if any(k in plan for k in ('order','sequence_basis')):raise PrintError('wrong template fields')
        elif plan['template']=='sequence_thread':
            if not 2<=len(items)<=5:raise PrintError('sequence supports 2..5 items')
            if plan.get('sequence_basis')!='explicit_fixture_order_unverified':
                raise PrintError('sequence must explicitly declare unverified ordering')
            if plan.get('order')!=[v.get('id') for v in items]:
                raise PrintError('sequence order must match explicit items')
            if 'links' in plan:raise PrintError('no semantic edges supported in sequence')
        else:
            if not 2<=len(items)<=5:raise PrintError('topology supports 2..5 items')
            if any(k in plan for k in ('links','order','sequence_basis')):raise PrintError('no semantic edges supported in topology')
        ids=[]
        for item in items:
            self._node(item);ids.append(item['id'])
        if len(ids)!=len(set(ids)):raise PrintError('duplicate item id')
        if plan['template']=='relation_graph':
            e=plan['links'][0]
            if e['from'] not in ids or e['to'] not in ids or e['from']==e['to']:
                raise PrintError('invalid relation endpoints')
        return True

    def _root(self,plan,height):
        w=1200
        root=ET.Element(f'{{{NS}}}svg',dict(version='1.1',width=str(w),height=str(height),viewBox=f'0 0 {w} {height}',role='img',**{'aria-labelledby':'svg-title svg-desc','data-printer-profile':PROFILE,'data-view-id':plan['view_id']}))
        t=add(root,'title',id='svg-title');t.text=plan['title']
        d=add(root,'desc',id='svg-desc');d.text='Experimental display-only AIAEAO v9.4 projection. Geometry and colors cannot imply verification, permission, admission, successful execution or semantic validation.'
        rect(root,0,0,w,height,stroke='#FFFFFF',fill='#FFFFFF',radius=0)
        rect(root,0,0,w,9,stroke='#111827',fill='#111827',radius=0)
        text(root,42,48,plan['title'],27,'#111827','bold')
        text(root,42,75,plan.get('subtitle','v9.4 · P1-VG-basic/1.0.0 · P2 2D experimental projection'),14,'#475569')
        line(root,42,93,w-42,93,color='#E2E8F0')
        line(root,42,height-49,w-42,height-49,color='#E2E8F0')
        text(root,42,height-25,'DISPLAY-ONLY · not an ACG validation, warrant or authority decision',13,'#475569')
        text(root,w-42,height-25,plan['view_id'],12,'#64748B',anchor='end')
        return root

    def _draw_item(self,p,item,x,y,w,h):
        a=self.by_id[item['anchor_id']]
        accent=self.colors.get(item.get('color_token'), '#64748B')
        # Never infer semantic type, witness authenticity or independent evidence.
        g=add(p,'g',**{'data-anchor-id':item['anchor_id'],'data-item-id':item['id'],'data-form-id':item['form_id']})
        if item.get('semantic_ref'): g.set('data-semantic-ref',item['semantic_ref'])
        if item.get('qualified_state_witness_ref'): g.set('data-witness-ref',item['qualified_state_witness_ref'])
        tt=add(g,'title');tt.text=item['label']+' — '+item['anchor_id']
        form=item['form_id'];fill=color_blend(accent)
        if form=='form.lens-marker':
            c=add(g,'circle',cx=x+44,cy=y+h/2,r=min(h/2-10,31),fill=fill,stroke=accent,stroke_width=2)
            line(g,x+84,y+10,x+84,y+h-10,'#E2E8F0')
        elif form=='form.glyph-only':
            pass
        else:
            rad=18 if form in ('form.state-badge','form.identity-chip') else 9 if form in ('form.module-block','form.contract-anchor','form.planning-node') else 2
            rect(g,x,y,w,h,accent,fill,rad,dashed=form=='form.boundary-frame')
        text(g,x+42,y+h/2+8,a['unicode'],28,'#0F172A',anchor='middle',glyph=True)
        # Simple deterministic fixed positions; longer labels use 13 px rather than floating wrapping.
        size=14 if len(item['label'])>24 else 17
        text(g,x+80,y+h/2+5,item['label'],size,'#0F172A','bold')
        display_id=item['anchor_id'] if len(item['anchor_id'])<=31 else item['anchor_id'][:29]+'…'
        text(g,x+80,y+h/2+24,display_id,11,'#475569')
        return g

    def _pairs(self,p):
        descs=['Epistemology / Observation','Governance / Policy','Semantics / Conversation','Execution / Contract','Provenance / Event']
        text(p,80,130,'X · DIMENSION',13,'#475569','bold')
        text(p,420,130,'OPENING',13,'#475569','bold')
        text(p,820,130,'COMPLEMENT',13,'#475569','bold')
        for n,pair in enumerate(self.pairs):
            y=151+n*108
            dim=self.concept_by_id[pair['dimension']]
            op=self.concept_by_id[pair['opening']]
            co=self.concept_by_id[pair['complement']]
            accent_token='domain.'+dim['label'].lower()
            lens=dict(id='dim_'+str(n),anchor_id=dim['visual_semantic_id'],label=dim['label'],form_id='form.lens-marker',color_token=accent_token,semantic_ref=dim['id'])
            left=dict(id='open_'+str(n),anchor_id=op['visual_semantic_id'],label=op['label'],form_id='form.contract-anchor',color_token=accent_token,semantic_ref=op['id'])
            right=dict(id='comp_'+str(n),anchor_id=co['visual_semantic_id'],label=co['label'],form_id='form.contract-anchor',color_token=accent_token,semantic_ref=co['id'])
            for it in [lens,left,right]:self._node(it)
            self._draw_item(p,lens,66,y,274,72)
            self._draw_item(p,left,396,y,323,72)
            self._draw_item(p,right,802,y,323,72)
            line(p,724,y+36,795,y+36,'#94A3B8')
            text(p,759,y+24,'pair',11,'#64748B',anchor='middle')
            if n!=len(self.pairs)-1:line(p,64,y+89,1132,y+89,'#EEF2F7')

    def _relation(self,p,plan):
        ia,ib=plan['items']; edge=plan['links'][0]
        assert edge['from']!=edge['to']
        d={x['id']:x for x in (ia,ib)}
        s,t=d[edge['from']],d[edge['to']]
        text(p,64,146,'SUBJECT · DECLARED',14,'#475569','bold')
        text(p,754,146,'OBJECT · DECLARED',14,'#475569','bold')
        self._draw_item(p,s,62,196,408,104)
        self._draw_item(p,t,728,196,408,104)
        op=self.by_id[edge['arrow_anchor_id']]['unicode']
        line(p,470,242,568,242,'#475569')
        text(p,596,251,op,29,'#334155',anchor='middle',glyph=True)
        line(p,625,242,728,242,'#475569')
        text(p,596,285,edge['predicate_id']+' · declared',13,'#475569',anchor='middle')
        rect(p,62,345,1074,95,'#E2E8F0','#F8FAFC',6)
        text(p,80,376,'Declaration pointer: '+edge['declaration_ref'],13,'#475569')
        text(p,80,408,'Typed relation was NOT checked by this printer. Run P1 independently.',13,'#475569')

    def _sequence(self,p,plan):
        items=plan['items']
        text(p,80,135,'EXPLICIT FIXTURE ORDER · not observed time / causality',14,'#475569','bold')
        for i,item in enumerate(items):
            y=171+108*i
            if i:
                line(p,105,y-36,105,y-10,'#94A3B8',True)
            add(p,'circle',cx=105,cy=y+34,r=16,stroke='#475569',stroke_width=2,fill='#FFFFFF')
            text(p,105,y+39,str(i+1),15,'#334155','bold',anchor='middle')
            self._draw_item(p,item,172,y,600,70)
            if item.get('time_label'):
                text(p,825,y+40,item['time_label'],14,'#475569')
        text(p,80,171+108*len(items)+21,'Ordinal placement only; no witness validity or event occurrence inferred.',13,'#475569')

    def _topology(self,p,plan):
        n=len(plan['items'])
        rect(p,68,140,1065,405,'#64748B','#F8FAFC',12,True)
        text(p,92,178,'ILLUSTRATIVE Z / Y PLACEMENT',17,'#334155','bold')
        text(p,92,207,'Dashed boundary depicts grouping only; not governance Admission.',13,'#64748B')
        cols=3
        for i,item in enumerate(plan['items']):
            col,row=i%cols,i//cols
            x=94+col*350;y=249+row*155
            self._draw_item(p,item,x,y,312,97)
        text(p,92,515,'No host/adapter connectivity or authority is inferred from proximity.',13,'#475569')

    def render(self,plan):
        self.validate(plan)
        t=plan['template'];height={
            'contract_pairs':766,
            'relation_graph':534,
            'topology_blocks':636
        }.get(t,188+len(plan['items'])*108+123)
        root=self._root(plan,height)
        {'contract_pairs':lambda:self._pairs(root),
         'relation_graph':lambda:self._relation(root,plan),
         'sequence_thread':lambda:self._sequence(root,plan),
         'topology_blocks':lambda:self._topology(root,plan)}[t]()
        raw=ET.tostring(root,encoding='utf-8',xml_declaration=True,short_empty_elements=True)
        return raw+b'\n'

    @staticmethod
    def sha256(data):return hashlib.sha256(data).hexdigest()
