"""VP-02: three local deterministic diagram layouts, deliberately no app or 3D.

A view projects *declared* data. It never infers P1 conformance, authority,
provenance verification, causality, time truth, or a canonical Y/Z total order.
"""
from __future__ import annotations
import json
import hashlib
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree as ET
from vp2d.printer import (Printer, PrintError, add, line, rect, text,
                           color_blend)

PROFILE='P2-VP-VIEWS/0.2.0'
ALLOWED_VIEWS=('cube.flow','cube.diagramm','cube.tree')
COMMON={'printer_profile','reference_version','view','lens','granularity','title','subtitle'}
COLOR='#475569'
STROKE='#64748B'
LABEL=re.compile(r'^[a-zA-Z][a-zA-Z0-9_.:-]{0,99}$')
HERE=Path(__file__).resolve().parents[1]

class ViewError(PrintError):
    """The declared view is invalid or unsupported; never a semantic verdict."""


def require(flag,message):
    if not flag:raise ViewError(message)

def exact_keys(obj, required, allowed=None, context='object'):
    require(isinstance(obj,dict),context+' must be an object')
    allowed=required if allowed is None else allowed
    require(required <= obj.keys(),context+' missing fields: '+','.join(sorted(required-set(obj))))
    require(obj.keys() <= allowed,context+' unexpected fields: '+','.join(sorted(set(obj)-allowed)))

def short(value,name,maxlen=80):
    require(isinstance(value,str) and bool(value) and len(value)<=maxlen and not any(ord(c)<32 for c in value),f'{name} must be nonempty clean text up to {maxlen} chars')
    return value

def ident(value,name):
    require(isinstance(value,str) and LABEL.fullmatch(value) is not None,name+' must be a stable ASCII ID')

def decimal_number(value):
    require(not isinstance(value,bool) and isinstance(value,(int,float,Decimal)), 'chart value must be numeric, never boolean or string')
    try: d=Decimal(str(value))
    except InvalidOperation:raise ViewError('invalid numeric chart value')
    require(d.is_finite() and d>=0 and d<=Decimal('1000000000'),'chart value must be finite nonnegative and <= 1e9')
    require(d.as_tuple().exponent>=-3,'chart value supports at most 3 decimal places')
    return d

def fmt(v):
    if not isinstance(v,Decimal):v=Decimal(str(v))
    return format(v.quantize(Decimal('0.001')).normalize(),'f')

def excerpt(s,limit=32):
    return s if len(s)<=limit else s[:limit-1].rstrip()+'…'

def wrap_label(s,max_chars=23):
    """Two fixed lines, ellipsize remaining content visibly; SVG title holds full label."""
    words=s.split(' ')
    lines=[];current=''
    for word in words:
        joined=(current+' '+word).strip()
        if len(joined)<=max_chars:current=joined
        elif current:
            lines.append(current);current=word
        else:
            lines.append(excerpt(word,max_chars));current=''
        if len(lines)==2:break
    if len(lines)<2 and current:lines.append(excerpt(current,max_chars))
    original=' '.join(words)
    if len(original)>sum(len(x) for x in lines)+max(0,len(lines)-1):
        if lines:lines[-1]=excerpt(lines[-1],max_chars-1).rstrip('…')+'…'
    return lines[:2]

class ViewPrinter:
    def __init__(self, reference_dir=None):
        self.base=Printer(reference_dir)

    def _common(self,p):
        require(isinstance(p,dict),'plan must be an object')
        require(p.get('printer_profile')==PROFILE,'unsupported view printer profile')
        require(p.get('reference_version')=='v9.4','reference_version must be v9.4')
        require(p.get('view') in ALLOWED_VIEWS,'view must be cube.flow, cube.diagramm, or cube.tree (not Planner views)')
        require(p.get('lens')=='neutral','VP-02 freezes lens=neutral; lens profiles belong to VP-03')
        require(p.get('granularity')=='standard','VP-02 freezes granularity=standard; budgets belong to later package')
        short(p.get('title'),'title',78)
        if 'subtitle' in p:short(p['subtitle'],'subtitle',95)

    def _node(self, n):
        # Reuse P1 presentation binding validation; never NFKC glyph -> identity.
        try:self.base._node(n)
        except PrintError as e:raise ViewError(str(e)) from e
        short(n['label'],'node label',60)
        return n

    def _nodes(self,p,minimum,maximum):
        ns=p.get('nodes')
        require(isinstance(ns,list) and minimum<=len(ns)<=maximum,f'view node budget: {minimum}..{maximum}')
        ids=[]
        for n in ns:
            self._node(n);ids.append(n['id'])
        require(len(ids)==len(set(ids)),'duplicate node ID')
        order=p.get('order')
        require(isinstance(order,list) and len(order)==len(ns) and all(isinstance(i,str) for i in order),'explicit full node order required')
        require(len(set(order))==len(order) and set(order)==set(ids),'order must be a permutation of node IDs; no inferred Y/Z ordering')
        return {n['id']:n for n in ns}

    def _edges(self, p, node_ids, kind):
        edges=p.get('edges')
        require(isinstance(edges,list) and edges and len(edges)<=8,'edges must contain 1..8 declared relationships')
        signatures=set()
        for e in edges:
            exact_keys(e,{'from','to','predicate_id','declaration_ref','arrow_anchor_id'},context='relationship')
            require(isinstance(e['from'],str) and isinstance(e['to'],str) and e['from'] in node_ids and e['to'] in node_ids,'unknown relationship endpoint')
            require(e['from']!=e['to'],'self-loop not supported in this fixed layout')
            for k in ('predicate_id','declaration_ref'):short(e[k],k,140)
            require(e['arrow_anchor_id']=='relation-arrows.reference','neutral registered Unicode reference arrow required; no inferred causality')
            require((e['from'],e['to'],e['predicate_id'],e['declaration_ref']) not in signatures,'duplicate declared edge')
            signatures.add((e['from'],e['to'],e['predicate_id'],e['declaration_ref']))
        return edges

    def _validate_flow(self,p):
        required=COMMON|{'nodes','edges','order','direction','declaration_status'}
        exact_keys(p,required,required|{'subtitle'},'cube.flow')
        nodes=self._nodes(p,2,4)
        require(p['direction'] in ('left-to-right','top-down'),'unsupported cube.flow direction')
        require(p['declaration_status']=='declared_unverified','flow assertions must be qualified as declared_unverified')
        edges=self._edges(p,set(nodes),'flow')
        return {'nodes':nodes,'edges':edges}

    def _validate_tree(self,p):
        required=COMMON|{'nodes','edges','order','root_id','declaration_status'}
        exact_keys(p,required,required|{'subtitle'},'cube.tree')
        nodes=self._nodes(p,2,7)
        require(p['declaration_status']=='declared_unverified','tree assertions must be qualified as declared_unverified')
        require(p['root_id'] in nodes,'declared root not in nodes')
        edges=self._edges(p,set(nodes),'tree')
        require(len(edges)==len(nodes)-1,'tree must have exactly n-1 relations')
        children={i:[] for i in nodes};parent={}
        order_index={key:i for i,key in enumerate(p['order'])}
        for e in edges:
            source,target=e['from'],e['to']
            require(target not in parent,'ambiguous multi-parent hierarchy: use cube.flow or reject')
            parent[target]=source
            children[source].append(target)
        require(p['root_id'] not in parent,'root cannot have a parent')
        require(set(parent)==set(nodes)-{p['root_id']},'orphan or disconnected tree')
        for xs in children.values():xs.sort(key=lambda i:order_index[i])
        levels=[];front=[p['root_id']];visited=set()
        while front:
            require(len(levels)<4,'tree budget exceeded: max 4 levels including root')
            require(not any(n in visited for n in front),'cycle in tree')
            require(len(front)<=5,'tree width budget exceeded: 5 siblings per level')
            visited.update(front);levels.append(front)
            front=[child for n in front for child in children[n]]
        require(len(visited)==len(nodes),'disconnected/cyclic tree not supported')
        require(p['order']==[k for level in levels for k in level],'tree order must be declared breadth-first with stable sibling order')
        return {'nodes':nodes,'edges':edges,'levels':levels}

    def _validate_chart(self,p):
        required=COMMON|{'plot','metric','samples'}
        exact_keys(p,required,required|{'subtitle'},'cube.diagramm')
        require(p['plot'] in ('bar','line'),'cube.diagramm plot must be bar or line')
        m=p['metric']
        exact_keys(m,{'id','unit','scale','declaration_ref','evidence_status'},context='metric')
        ident(m['id'],'metric.id')
        short(m['unit'],'unit',24)
        require(m['scale']=='linear_zero_based','only zero-based linear comparable measures accepted')
        short(m['declaration_ref'],'measurement declaration',180)
        require(m['evidence_status']=='declared_unverified','chart values must be marked declared_unverified')
        samples=p['samples']
        require(isinstance(samples,list) and 2<=len(samples)<=6,'chart budget: 2..6 comparable samples')
        ids=[];values=[]
        for s in samples:
            exact_keys(s,{'id','label','value'},context='sample')
            ident(s['id'],'sample.id');short(s['label'],'sample.label',24)
            ids.append(s['id']);values.append(decimal_number(s['value']))
        require(len(set(ids))==len(ids),'duplicate sample id')
        # Explicit sample array order is presentation order, never an inferred time axis.
        return {'values':values}

    def validate(self,plan):
        self._common(plan)
        v=plan['view']
        return {'cube.flow':self._validate_flow,'cube.diagramm':self._validate_chart,'cube.tree':self._validate_tree}[v](plan)

    def _root(self,plan,height):
        # inherit accessible title, footer, text/symbol decisions from VP-01.
        root=self.base._root({'view_id':plan['view'],'title':plan['title'],'subtitle':plan.get('subtitle','v9.4 · VP-02 · declared display-only projection')},height)
        root.set('data-printer-profile',PROFILE)
        root.set('data-cube-view',plan['view'])
        return root

    def _card(self,p,item,x,y,w,h=90):
        a=self.base.by_id[item['anchor_id']]
        accent=self.base.colors.get(item.get('color_token'),'#64748B')
        g=add(p,'g',**{'data-item-id':item['id'],'data-anchor-id':item['anchor_id'],'data-form-id':item['form_id']})
        if item.get('semantic_ref'):g.set('data-semantic-ref',item['semantic_ref'])
        if item.get('qualified_state_witness_ref'):g.set('data-witness-ref',item['qualified_state_witness_ref'])
        desc=add(g,'title');desc.text=item['label']+' · '+item['anchor_id']
        if item['form_id']=='form.lens-marker':
            add(g,'circle',cx=x+35,cy=y+37,r=28,stroke=accent,stroke_width=2,fill=color_blend(accent))
        elif item['form_id']!='form.glyph-only':
            rect(g,x,y,w,h,accent,color_blend(accent),9,dashed=item['form_id']=='form.boundary-frame')
        text(g,x+34,y+43,a['unicode'],28,'#0F172A',anchor='middle',glyph=True)
        for j,s in enumerate(wrap_label(item['label'],max(13,int((w-87)/8.1)))):
            text(g,x+72,y+29+j*19,s,14,'#0F172A','bold')
        text(g,x+72,y+h-13,excerpt(item['anchor_id'],max(14,int((w-88)/6.9))),10,'#64748B')
        return g

    def _arrow(self,p,x,y,direction):
        # Line geometry is a *depiction* of an explicitly declared edge.
        if direction=='down':
            add(p,'path',d=f'M{x-5} {y-6} L{x} {y} L{x+5} {y-6}',stroke=STROKE,stroke_width=2,fill='none')
        elif direction=='up':
            add(p,'path',d=f'M{x-5} {y+6} L{x} {y} L{x+5} {y+6}',stroke=STROKE,stroke_width=2,fill='none')
        elif direction=='right':
            add(p,'path',d=f'M{x-6} {y-5} L{x} {y} L{x-6} {y+5}',stroke=STROKE,stroke_width=2,fill='none')
        elif direction=='left':
            add(p,'path',d=f'M{x+6} {y-5} L{x} {y} L{x+6} {y+5}',stroke=STROKE,stroke_width=2,fill='none')

    def _edge(self,p,e,i,from_x,from_y,to_x,to_y):
        g=add(p,'g',**{'data-predicate-id':e['predicate_id'],'data-declaration-ref':e['declaration_ref'],'data-edge-id':f'e{i+1}'})
        add(g,'title').text=f"{e['from']} → {e['to']} | {e['predicate_id']} | {e['declaration_ref']}"
        line(g,from_x,from_y,to_x,to_y,STROKE)
        self._arrow(g,to_x,to_y,'right' if to_x>=from_x else 'left')
        return g

    def _flow(self,p,plan,derived):
        ns=derived['nodes'];keys=plan['order'];dir=plan['direction']
        text(p,60,129,'CUBE.FLOW · DECLARED RELATIONSHIPS · no inferred chronology or causality',13,COLOR,'bold')
        pos={}
        if dir=='left-to-right':
            n=len(keys);gap=35;w=(1080-(n-1)*gap)/n;y=191
            for i,key in enumerate(keys):
                x=60+i*(w+gap);pos[key]=(x,y,w,88)
                self._card(p,ns[key],x,y,w,88)
            for i,e in enumerate(derived['edges']):
                # Distinct deterministic under-card routing tracks, preserving edge direction.
                a=pos[e['from']];b=pos[e['to']];track=326+i*32
                ax=a[0]+a[2]/2;bx=b[0]+b[2]/2
                g=add(p,'g',**{'data-predicate-id':e['predicate_id'],'data-declaration-ref':e['declaration_ref'],'data-edge-id':f'e{i+1}'})
                add(g,'title').text=f"{e['from']} → {e['to']} | {e['predicate_id']} | {e['declaration_ref']}"
                line(g,ax,a[1]+88,ax,track,STROKE)
                line(g,ax,track,bx,track,STROKE)
                line(g,bx,track,bx,b[1]+88,STROKE)
                self._arrow(g,bx,b[1]+88,'up')
                text(g,ax+8,track-6,'e'+str(i+1),12,COLOR)
            notes_y=365+len(derived['edges'])*32
        else:
            for i,key in enumerate(keys):
                x=105;y=179+i*119;pos[key]=(x,y,370,88)
                self._card(p,ns[key],x,y,370,88)
            for i,e in enumerate(derived['edges']):
                a=pos[e['from']];b=pos[e['to']];track=545+i*45
                ay=a[1]+44;by=b[1]+44
                g=add(p,'g',**{'data-predicate-id':e['predicate_id'],'data-declaration-ref':e['declaration_ref'],'data-edge-id':f'e{i+1}'})
                add(g,'title').text=f"{e['from']} → {e['to']} | {e['predicate_id']} | {e['declaration_ref']}"
                line(g,475,ay,track,ay,STROKE)
                line(g,track,ay,track,by,STROKE)
                line(g,track,by,475,by,STROKE)
                self._arrow(g,478,by,'left')
                text(g,track+7,min(ay,by)+18,'e'+str(i+1),12,COLOR)
            notes_y=207+len(keys)*119
        text(p,62,notes_y,'DECLARATION LEDGER · each edge is a fixture assertion, not P1 proof',13,COLOR,'bold')
        for i,e in enumerate(derived['edges']):
            text(p,68,notes_y+29+i*29,f"e{i+1} · {excerpt(e['from'],17)} → {excerpt(e['to'],17)}  ·  {excerpt(e['predicate_id'],28)}",13,'#334155')
            text(p,590,notes_y+29+i*29,excerpt(e['declaration_ref'],71),11,COLOR)

    def _tree(self,p,plan,derived):
        levels=derived['levels'];nodes=derived['nodes'];positions={}
        text(p,60,132,'CUBE.TREE · single-root declared hierarchy · no synthesized parentage',13,COLOR,'bold')
        for depth,keys in enumerate(levels):
            n=len(keys);cell=1080/n;w=min(230,cell-20);y=177+depth*139
            for i,key in enumerate(keys):
                x=60+i*cell+(cell-w)/2;positions[key]=(x,y,w,90)
        for i,e in enumerate(derived['edges']):
            source,target=positions[e['from']],positions[e['to']]
            ax=source[0]+source[2]/2;bx=target[0]+target[2]/2
            ay=source[1]+90;by=target[1]
            mid=(ay+by)/2
            g=add(p,'g',**{'data-predicate-id':e['predicate_id'],'data-declaration-ref':e['declaration_ref'],'data-edge-id':f'e{i+1}'})
            add(g,'title').text=f"{e['from']} → {e['to']} | {e['predicate_id']} | {e['declaration_ref']}"
            line(g,ax,ay,ax,mid,STROKE)
            line(g,ax,mid,bx,mid,STROKE)
            line(g,bx,mid,bx,by,STROKE)
            self._arrow(g,bx,by,'down')
        for k in plan['order']:
            x,y,w,h=positions[k];self._card(p,nodes[k],x,y,w,h)
        y=190+len(levels)*139
        text(p,62,y,'DECLARED LINKS · references retained in SVG metadata and the print report',13,COLOR,'bold')
        for i,e in enumerate(derived['edges']):
            text(p,70,y+27+i*23,f"e{i+1} · {excerpt(e['from'],20)} → {excerpt(e['to'],20)} · {excerpt(e['predicate_id'],24)}",12,COLOR)

    @staticmethod
    def _max_tick(values):
        maximum=max(values)
        if maximum==0:return Decimal('1')
        x=maximum/Decimal(4)
        power=Decimal(10)**x.adjusted()
        ratio=x/power
        step=next((v for v in [Decimal(1),Decimal(2),Decimal(5),Decimal(10)] if ratio<=v),Decimal(10))*power
        return step*4

    def _chart(self,p,plan,derived):
        data=plan['samples'];values=derived['values'];peak=self._max_tick(values)
        x0=135;y0=175;h=347;w=974
        text(p,66,128,'CUBE.DIAGRAMM · DECLARED NUMBERS · NOT EMPIRICAL VERIFICATION',13,COLOR,'bold')
        text(p,66,155,f"Measure: {plan['metric']['id']}   ·   Unit: {plan['metric']['unit']}   ·   linear zero-based",12,COLOR)
        for i in range(5):
            v=peak*Decimal(i)/Decimal(4)
            yy=y0+h-float(Decimal(i)*Decimal(h)/Decimal(4))
            line(p,x0,yy,x0+w,yy,'#E2E8F0')
            text(p,x0-13,yy+5,fmt(v),12,COLOR,anchor='end')
        line(p,x0,y0,x0,y0+h,STROKE)
        line(p,x0,y0+h,x0+w,y0+h,STROKE)
        count=len(data);step=w/count
        pts=[]
        for i,(row,v) in enumerate(zip(data,values)):
            cx=x0+(i+.5)*step;yy=y0+h-float(v/peak)*h
            pts.append((cx,yy))
            label=excerpt(row['label'],19)
            text(p,cx,y0+h+27,label,13,'#334155',anchor='middle')
            if plan['plot']=='bar':
                bw=min(90,step*.50)
                rect(p,cx-bw/2,yy,bw,y0+h-yy,'#64748B',color_blend('#2563EB'),5)
                text(p,cx,yy-10,fmt(v),13,'#334155',anchor='middle')
        if plan['plot']=='line':
            # Line order is explicitly the authored sample array order; NOT time.
            path=' '.join(('M' if i==0 else 'L')+f' {fmt(Decimal(str(cx)))} {fmt(Decimal(str(yy)))}' for i,(cx,yy) in enumerate(pts))
            add(p,'path',d=path,fill='none',stroke='#2563EB',stroke_width=2.5,stroke_linecap='round')
            for (cx,yy),v in zip(pts,values):
                add(p,'circle',cx=fmt(Decimal(str(cx))),cy=fmt(Decimal(str(yy))),r=5,fill='#FFFFFF',stroke='#2563EB',stroke_width=2.5)
                text(p,cx,yy-14,fmt(v),13,'#334155',anchor='middle')
        text(p,67,600,'Source declaration: '+excerpt(plan['metric']['declaration_ref'],100),12,COLOR)
        text(p,67,625,'Sample order is supplied by the fixture; not a verified temporal or causal relation.',12,COLOR)

    def render(self,plan):
        d=self.validate(plan)
        if plan['view']=='cube.diagramm':height=718
        elif plan['view']=='cube.flow':
            height=max(535,445+len(plan['edges'])*61) if plan['direction']=='left-to-right' else (305+len(plan['nodes'])*119+len(plan['edges'])*29)
        else:height=290+len(d['levels'])*139+len(plan['edges'])*23
        root=self._root(plan,height)
        if plan['view']=='cube.flow':self._flow(root,plan,d)
        elif plan['view']=='cube.tree':self._tree(root,plan,d)
        else:self._chart(root,plan,d)
        return ET.tostring(root,encoding='utf-8',xml_declaration=True,short_empty_elements=True)+b'\n'

    def report(self,plan,svg):
        self.validate(plan)
        out={'format':'aiaeao.cube.vp02-print-report/1',
             'printer_profile':PROFILE,'reference_version':'v9.4','view':plan['view'],
             'lens':'neutral','granularity':'standard','render_status':'PASS',
             'svg_sha256':hashlib.sha256(svg).hexdigest(),
             'semantic_conformance':'NOT_EVALUATED','epistemic_warrant':'NOT_EVALUATED',
             'current_authority':'NOT_EVALUATED','canonical_admission':'NOT_EVALUATED',
             'content_status':'declared_unverified',
             'notices':['All source declarations are unverified presentation inputs.',
                        'Layout order, geometry, color and arrowheads do not assert semantic typing, causation or time truth.']}
        if plan['view'] in ('cube.flow','cube.tree'):
            out['displayed_item_ids']=plan['order']
            out['displayed_edges']=[{'from':e['from'],'to':e['to'],'predicate_id':e['predicate_id'],'declaration_ref':e['declaration_ref']} for e in plan['edges']]
        else:
            out['sample_ids']=[x['id'] for x in plan['samples']]
            out['measurement_ref']=plan['metric']['declaration_ref']
            out['unit']=plan['metric']['unit']
        return out
