"""P1.6 fixture-scoped X endpoint instantiation; deliberately not an Authority oracle.

Only consumes binding-context/2, keeps binding-context/1's frozen path intact.
No external I/O except reading the pinned local P1.6 reference vocabulary.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path

VOCAB = Path(__file__).resolve().parents[1] / 'instantiation_reference_v1.json'
VOCAB_SHA256 = '58a20c38487d9b7edee2f1a5e6b69a26528957191c642e0ef50b46563e1b65f1'
ORIGINS = ('illustrative_fixture', 'external_declaration_unverified')
CODES = {
    'P1_INSTANTIATION_SLOT_MISSING': ('UNRESOLVED','Morphology v9.4 §6.2 / P1.6 required endpoint slot'),
    'P1_INSTANTIATION_SLOT_TYPE': ('FAIL','Morphology v9.4 §6.2 / P1.6 endpoint slot type constraint'),
    'P1_INSTANTIATION_SLOT_SIGNATURE': ('FAIL','P1.6 reference slot descriptor / cardinality'),
    'P1_INSTANTIATION_CONDITION': ('FAIL','Morphology v9.4 §6.2.2 / P1.6 conditional admission'),
    'P1_INSTANTIATION_CYCLE': ('FAIL','Morphology v9.4 §6.2 / P1.6 endpoint-reference cycle'),
    'P1_INSTANTIATION_PROFILE_AMBIGUOUS': ('UNRESOLVED','P1.6 scoped profile selection'),
    'P1_INSTANTIATION_PROFILE_REQUIRED': ('UNRESOLVED','Morphology v9.4 §6.2 / P1.3 endpoint binding'),
    'P1_BINDING_CONTEXT_REQUIRED': ('UNRESOLVED','P1.3 declared referent and exact binding'),
    'P1_LAYER_WITNESS_MISSING': ('UNRESOLVED','P1.3 β/ζ witness declaration'),
    'P1_SCOPE_CONFLICT': ('FAIL','P1.4 declared scope consistency'),
}

class InstantiationError(ValueError):
    """Invalid caller context/configuration (exit 3), never a semantic FAIL."""


def _nonempty(v):
    return isinstance(v,str) and bool(v) and not any(0xD800 <= ord(c) <= 0xDFFF for c in v)


def _shape(obj, allowed, needed, path):
    if not isinstance(obj,dict): raise InstantiationError(path+': expected object')
    if set(obj)-set(allowed) or set(needed)-set(obj):
        raise InstantiationError(path+': unknown or missing keys: '+str(sorted(set(obj)-set(allowed)))+' / '+str(sorted(set(needed)-set(obj))))


def reference():
    raw=VOCAB.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=VOCAB_SHA256:
        raise InstantiationError('P1.6 reference vocabulary sha256 mismatch; fail closed')
    doc=json.loads(raw)
    if len(doc.get('endpoints',[]))!=10 or doc.get('reference_version')!='v9.4':
        raise InstantiationError('Invalid P1.6 vocabulary')
    return {e['concept_id']:e for e in doc['endpoints']}


def validate_context_v2(ctx, legacy_validator):
    """Closed /2 shape with exact v1 validation of all inherited context fields.

    Does not require jsonschema in G5/P3 runtime. Profile descriptor checks
    follow INSTANTIATION_PROFILES.schema.json and enforce non-widening.
    """
    _shape(ctx, ('format','reference_version','context_id','source_kind','scope_ref','referents',
                 'predicate_contracts','method_contracts','profile_limitations','instantiation_profiles'),
           ('format','reference_version','context_id','source_kind','referents','predicate_contracts'), 'context/2')
    if ctx['format']!='aiaeao.cube.binding-context/2': raise InstantiationError('Unsupported context format')
    clean=copy.deepcopy(ctx)
    clean['format']='aiaeao.cube.binding-context/1'
    clean.pop('instantiation_profiles',None)
    for r in clean['referents']:
        if isinstance(r,dict):
            r.pop('instantiation_profile_ref',None)
            r.pop('slots',None)
    legacy_validator(clean)
    if not isinstance(ctx.get('instantiation_profiles',[]),list) or len(ctx.get('instantiation_profiles',[]))>512:
        raise InstantiationError('instantiation_profiles must be an array of <=512')
    for i,r in enumerate(ctx['referents']):
        path=f'/referents/{i}'
        _shape(r,('ref','concept_id','home','layers','provenance_status','scope_ref','witness_ref',
                  'instantiation_profile_ref','slots'),('ref','concept_id','home','layers','provenance_status'),path)
        if 'instantiation_profile_ref' in r and not _nonempty(r['instantiation_profile_ref']):
            raise InstantiationError(path+'/instantiation_profile_ref invalid')
        if 'slots' in r:
            slots=r['slots']
            if not isinstance(slots,dict) or len(slots)>32:
                raise InstantiationError(path+'/slots must be object (max 32)')
            for k,v in slots.items():
                if not _nonempty(k) or (not isinstance(v,str) and not isinstance(v,list)):
                    raise InstantiationError(path+'/slots: malformed slot value')
                if isinstance(v,list) and (not v or not all(isinstance(x,str) for x in v)):
                    raise InstantiationError(path+'/slots: malformed array slot value')
    vocab=reference()
    for i,p in enumerate(ctx.get('instantiation_profiles',[])):
        path=f'/instantiation_profiles/{i}'
        _shape(p,('profile_ref','concept_id','revision','scope','origin','slots'),
               ('profile_ref','concept_id','revision','scope','origin','slots'),path)
        if not all(_nonempty(p[k]) for k in ('profile_ref','concept_id','revision','scope')) or p['origin'] not in ORIGINS:
            raise InstantiationError(path+': invalid profile metadata')
        if p['concept_id'] not in vocab:
            raise InstantiationError(path+': profile must address one of 10 X endpoints')
        if not isinstance(p['slots'],list) or not 1 <= len(p['slots']) <= 32:
            raise InstantiationError(path+': slots must contain 1..32 descriptors')
        builtins={s['name']:s for s in vocab[p['concept_id']]['slots']}
        present={}
        for j,s in enumerate(p['slots']):
            sp=f'{path}/slots/{j}'
            if not isinstance(s,dict): raise InstantiationError(sp+': expected descriptor object')
            kind=s.get('kind')
            allowed={'ref':('name','kind','required','cardinality','concept_ids'),
                     'enum':('name','kind','required','values'),
                     'string':('name','kind','required')}.get(kind)
            if not allowed:raise InstantiationError(sp+': unknown descriptor kind')
            _shape(s,allowed,allowed,sp)
            name=s['name']
            if not _nonempty(name) or name in present or name not in builtins:
                raise InstantiationError(sp+': unknown or duplicate slot name')
            if not isinstance(s['required'],bool):raise InstantiationError(sp+': required must be bool')
            base=builtins[name]
            if kind!=base['kind'] or (base['required'] and not s['required']):
                raise InstantiationError(sp+': caller profile widens baseline slot kind/requiredness')
            if kind=='ref':
                if s['cardinality']!=base['cardinality'] or not isinstance(s['concept_ids'],list) or not s['concept_ids'] or \
                   not all(_nonempty(x) for x in s['concept_ids']) or len(s['concept_ids'])!=len(set(s['concept_ids'])) or \
                   not set(s['concept_ids']).issubset(base['concept_ids']):
                    raise InstantiationError(sp+': invalid/widening reference descriptor')
            elif kind=='enum':
                if not isinstance(s['values'],list) or not s['values'] or not all(_nonempty(x) for x in s['values']) or \
                   len(s['values'])!=len(set(s['values'])) or not set(s['values']).issubset(base['values']):
                    raise InstantiationError(sp+': invalid/widening enum descriptor')
            present[name]=s
        if any(s['required'] and s['name'] not in present for s in builtins.values()):
            raise InstantiationError(path+': caller profile drops a baseline required slot')
    return ctx


def _diag(code, path, message):
    status,rule=CODES[code]
    return {'code':code,'stage':'referent_binding',
            'severity':'error' if status=='FAIL' else 'unresolved',
            'message':message,'reference_rule':rule,'ast_path':path}


def _join(statuses):
    if 'FAIL' in statuses: return 'FAIL'
    if 'UNRESOLVED' in statuses: return 'UNRESOLVED'
    return 'PASS'


def _ptr(index,name=''):
    return f'/referents/{index}/slots'+('/'+name.replace('~','~0').replace('/','~1') if name else '')


class InstantiationCheck:
    def __init__(self, context):
        self.ctx=context
        self.vocab=reference()
        self.refs={r['ref']:(i,r) for i,r in enumerate(context['referents'])}
        self.profiles=context.get('instantiation_profiles',[])

    def run(self, refid, layer):
        result, ds=self._check(refid,layer,())
        # Diagnostic uniqueness, stable sorting (the caller's report also sorts diagnostics).
        seen=set(); uniq=[]
        for d in ds:
            k=(d['code'],d['ast_path'],d['message'])
            if k not in seen:seen.add(k);uniq.append(d)
        return result,uniq

    def _check(self,refid,layer,stack):
        if refid not in self.refs:
            return 'UNRESOLVED', [_diag('P1_BINDING_CONTEXT_REQUIRED','/', 'No declared X endpoint referent '+repr(refid))]
        i,r=self.refs[refid];base=_ptr(i)
        if r['concept_id'] not in self.vocab:
            return 'PASS',[]
        if refid in stack:
            return 'FAIL',[_diag('P1_INSTANTIATION_CYCLE',base,'Endpoint reference cycle is forbidden in this P1.6 declared fixture.')]
        if layer in ('β','ζ') and not r.get('witness_ref'):
            return 'UNRESOLVED',[_diag('P1_LAYER_WITNESS_MISSING',f'/referents/{i}/witness_ref','β/ζ requires a declared witness pointer before slots.')]
        options=[p for p in self.profiles if p['concept_id']==r['concept_id'] and p['scope']==r.get('scope_ref')]
        explicit=r.get('instantiation_profile_ref')
        if explicit:
            matching=[p for p in options if p['profile_ref']==explicit]
            if not matching:
                if any(p['profile_ref']==explicit and p['concept_id']==r['concept_id'] for p in self.profiles):
                    return 'FAIL',[_diag('P1_SCOPE_CONFLICT',f'/referents/{i}/instantiation_profile_ref','Explicit profile scope conflicts with this declared referent.')]
                return 'UNRESOLVED',[_diag('P1_INSTANTIATION_PROFILE_REQUIRED',f'/referents/{i}/instantiation_profile_ref','No matching scoped instantiation profile.')]
            options=matching
        if len(options)>1:
            return 'UNRESOLVED',[_diag('P1_INSTANTIATION_PROFILE_AMBIGUOUS',f'/referents/{i}/instantiation_profile_ref','Multiple scoped profiles without unique selection.')]
        if not options:
            return 'UNRESOLVED',[_diag('P1_INSTANTIATION_PROFILE_REQUIRED',f'/referents/{i}/instantiation_profile_ref','X endpoint lacks a declared scoped instantiation profile.')]
        p=options[0]
        vals=r.get('slots',{})
        descriptors={d['name']:d for d in p['slots']}
        statuses=[];diags=[]
        def issue(code,path,msg):
            statuses.append(CODES[code][0]);diags.append(_diag(code,path,msg))
        for name in sorted(set(vals)-set(descriptors)):
            issue('P1_INSTANTIATION_SLOT_SIGNATURE',_ptr(i,name),'Undeclared slot name.')
        for name,s in sorted(descriptors.items()):
            sp=_ptr(i,name)
            if name not in vals:
                if s['required']:
                    issue('P1_INSTANTIATION_SLOT_MISSING',sp,'Required endpoint slot absent.')
                continue
            v=vals[name]
            if s['kind']=='string':
                if not _nonempty(v):issue('P1_INSTANTIATION_SLOT_SIGNATURE',sp,'Expected nonempty string literal.')
                continue
            if s['kind']=='enum':
                if not isinstance(v,str) or v not in s['values']:
                    issue('P1_INSTANTIATION_SLOT_SIGNATURE',sp,'Enum value is outside declared profile.')
                continue
            if s['cardinality']=='one':
                if not _nonempty(v):
                    issue('P1_INSTANTIATION_SLOT_SIGNATURE',sp,'Expected one nonempty reference string.')
                    continue
                targets=[v]
            else:
                if not isinstance(v,list) or not v or not all(_nonempty(x) for x in v):
                    issue('P1_INSTANTIATION_SLOT_SIGNATURE',sp,'Expected nonempty array of reference strings.')
                    continue
                targets=v
            for j,target in enumerate(targets):
                tp=sp+('/'+str(j) if s['cardinality']=='many' else '')
                if target not in self.refs:
                    issue('P1_BINDING_CONTEXT_REQUIRED',tp,'Slot target is not a declared referent.')
                    continue
                _,t=self.refs[target]
                if t['concept_id'] not in s['concept_ids']:
                    issue('P1_INSTANTIATION_SLOT_TYPE',tp,'Slot target has a forbidden concept type.')
                    continue
                if name=='pair_scope_ref' and target != r.get('scope_ref'):
                    issue('P1_SCOPE_CONFLICT',tp,'Endpoint pair scope must match the declared scope identity.')
                    continue
                if t['concept_id'] in self.vocab:
                    status,sub=self._check(target,layer if layer in t['layers'] else t['layers'][0],stack+(refid,))
                    statuses.append(status);diags.extend(sub)
        if r['concept_id']=='X:endpoint:admission':
            decision=vals.get('decision')
            if decision=='admitted':
                if 'authority_ref' not in vals:issue('P1_INSTANTIATION_CONDITION',_ptr(i,'authority_ref'),'Admitted decision must declare authority_ref.')
                if 'refusal_ref' in vals:issue('P1_INSTANTIATION_CONDITION',_ptr(i,'refusal_ref'),'Admitted decision cannot carry refusal_ref.')
            elif decision=='refused' and 'refusal_ref' not in vals:
                issue('P1_INSTANTIATION_CONDITION',_ptr(i,'refusal_ref'),'Refused decision must declare refusal_ref.')
        return _join(statuses),diags
