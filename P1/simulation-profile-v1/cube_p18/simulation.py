"""P1.8 /3 context validation: return typing, scenarios, evaluators, records.

Descriptive only. Nothing here runs a method, fetches a library entry,
verifies a digest or a witness, or scores a result.
"""
from __future__ import annotations
import copy
import re

FORMAT3 = 'aiaeao.cube.binding-context/3'
FORMAT2 = 'aiaeao.cube.binding-context/2'
V2_TOP = ('format','reference_version','context_id','source_kind','scope_ref','referents',
          'predicate_contracts','method_contracts','profile_limitations','instantiation_profiles')
V3_TOP = ('evaluation_frame','scenarios','evaluators','evaluation_records')
METHOD_EXTRA = ('return_concept_ids','return_cardinality','library_ref')
JUDGMENTS = frozenset({'X:endpoint:conclusion','X:endpoint:satisfaction','X:endpoint:completion',
                       'X:endpoint:admission','X:endpoint:authority'})
ORIGINS = ('illustrative_fixture','external_declaration_unverified')
MODES = ('simulation','replay','operative')
KINDS = ('local_script','external_simulator','proof_tool','human_review')
METHOD_ID = re.compile(r'^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*/v[1-9][0-9]*$')
SHA_HEX = re.compile(r'^[0-9a-f]{64}$')
DIGEST = re.compile(r'^sha256:[0-9a-f]{64}$')


class SimulationError(ValueError):
    """Invalid caller /3 configuration (MCP config error), never a semantic FAIL."""


def _ne(v):
    return isinstance(v,str) and bool(v) and not any(0xD800 <= ord(c) <= 0xDFFF for c in v)


def _shape(obj, allowed, needed, path):
    if not isinstance(obj,dict): raise SimulationError(path+': expected object')
    extra=set(obj)-set(allowed); missing=set(needed)-set(obj)
    if extra or missing:
        raise SimulationError(f'{path}: unknown {sorted(extra)} / missing {sorted(missing)}')


def _idlist(v, path, check=None):
    if not isinstance(v,list) or not v or not all(_ne(x) for x in v) or len(v)!=len(set(v)):
        raise SimulationError(path+': expected nonempty unique string array')
    if check:
        for x in v: check(x,path)


def project_v2(ctx):
    """Lossless view for the unchanged P1.6/P1.4 path: drop only /3 additions."""
    out=copy.deepcopy(ctx)
    out['format']=FORMAT2
    for k in V3_TOP: out.pop(k,None)
    for m in out.get('method_contracts',[]):
        if isinstance(m,dict):
            for k in METHOD_EXTRA: m.pop(k,None)
    return out


def concept_table(resolver):
    """concept_id -> instantiation, from the frozen P1.1 key table."""
    return {e['concept_id']:e['instantiation'] for e in resolver.exact.values()}


def validate_context_v3(ctx, v2_validator, legacy_validator, concepts):
    _shape(ctx, V2_TOP+V3_TOP, ('format','reference_version','context_id','source_kind',
                                'referents','predicate_contracts'), 'context/3')
    if ctx['format']!=FORMAT3: raise SimulationError('Unsupported context format')
    v2_validator(project_v2(ctx), legacy_validator)
    refs={r['ref']:r for r in ctx['referents']}

    def output_concept(cid,path):
        if concepts.get(cid) in (None,'not_instantiable'):
            raise SimulationError(path+': unknown or non-instantiable concept '+repr(cid))
        if cid in JUDGMENTS:
            raise SimulationError(path+': X judgment endpoints are never method/evaluator outputs (MR-4)')

    def method_id(mid,path):
        if METHOD_ID.fullmatch(mid) is None: raise SimulationError(path+': invalid method_id')

    for i,m in enumerate(ctx.get('method_contracts',[])):
        path=f'/method_contracts/{i}'
        has_ids='return_concept_ids' in m; has_card='return_cardinality' in m
        if has_ids!=has_card:
            raise SimulationError(path+': return_concept_ids and return_cardinality must be declared together')
        if has_ids:
            _idlist(m['return_concept_ids'],path+'/return_concept_ids',output_concept)
            if m['return_cardinality'] not in ('one','many'):
                raise SimulationError(path+': invalid return_cardinality')
        if 'library_ref' in m:
            lib=m['library_ref']
            _shape(lib,('library_id','entry_id','revision','sha256'),('library_id','entry_id','revision','sha256'),path+'/library_ref')
            if not all(_ne(lib[k]) for k in ('library_id','entry_id','revision')) or \
               not isinstance(lib['sha256'],str) or SHA_HEX.fullmatch(lib['sha256']) is None:
                raise SimulationError(path+': malformed library_ref')

    if 'evaluation_frame' in ctx:
        _shape(ctx['evaluation_frame'],('scenario_ref',),('scenario_ref',),'/evaluation_frame')
        if not _ne(ctx['evaluation_frame']['scenario_ref']): raise SimulationError('/evaluation_frame: invalid scenario_ref')

    seen=set()
    for i,s in enumerate(ctx.get('scenarios',[])):
        path=f'/scenarios/{i}'
        _shape(s,('scenario_id','revision','scope','origin','mode','world_refs','method_ids','parameters','assumption_refs'),
               ('scenario_id','revision','scope','origin','mode','world_refs','method_ids'),path)
        if not all(_ne(s[k]) for k in ('scenario_id','revision','scope')) or s['origin'] not in ORIGINS:
            raise SimulationError(path+': invalid scenario metadata')
        if s['scenario_id'] in seen: raise SimulationError(path+': duplicate scenario_id')
        seen.add(s['scenario_id'])
        if s['mode'] not in MODES: raise SimulationError(path+': invalid mode')
        def member(x,p):
            if x not in refs: raise SimulationError(p+': world member is not a declared referent (SC-1)')
        _idlist(s['world_refs'],path+'/world_refs',member)
        _idlist(s['method_ids'],path+'/method_ids',method_id)
        params=s.get('parameters',{})
        if not isinstance(params,dict) or len(params)>64 or not all(_ne(k) for k in params) or \
           not all(v is None or isinstance(v,(str,int,float,bool)) for v in params.values()):
            raise SimulationError(path+': parameters must be <=64 JSON scalars (SC-4)')
        for x in s.get('assumption_refs',[]):
            if x not in s['world_refs'] or refs[x]['concept_id']!='Y:identified-object:annotation':
                raise SimulationError(path+': assumption_refs must be Y Annotation world members (SC-5)')

    seen=set()
    for i,e in enumerate(ctx.get('evaluators',[])):
        path=f'/evaluators/{i}'
        _shape(e,('evaluator_id','revision','scope','origin','kind','method_ids','output_concept_ids'),
               ('evaluator_id','revision','scope','origin','kind','method_ids','output_concept_ids'),path)
        if not all(_ne(e[k]) for k in ('evaluator_id','revision','scope')) or e['origin'] not in ORIGINS or e['kind'] not in KINDS:
            raise SimulationError(path+': invalid evaluator metadata')
        if e['evaluator_id'] in seen: raise SimulationError(path+': duplicate evaluator_id')
        seen.add(e['evaluator_id'])
        _idlist(e['method_ids'],path+'/method_ids',method_id)
        _idlist(e['output_concept_ids'],path+'/output_concept_ids',output_concept)

    seen=set()
    for i,r in enumerate(ctx.get('evaluation_records',[])):
        path=f'/evaluation_records/{i}'
        _shape(r,('record_id','scenario_ref','evaluator_ref','method_id','input_digest','output_refs','witness_ref','status'),
               ('record_id','scenario_ref','evaluator_ref','method_id','input_digest','output_refs','status'),path)
        if not all(_ne(r[k]) for k in ('record_id','scenario_ref','evaluator_ref','method_id','input_digest')):
            raise SimulationError(path+': invalid record metadata')
        if r['record_id'] in seen: raise SimulationError(path+': duplicate record_id')
        seen.add(r['record_id'])
        if r['status'] not in ('declared','unresolved'): raise SimulationError(path+': invalid status (EV-6)')
        if 'witness_ref' in r and not _ne(r['witness_ref']): raise SimulationError(path+': invalid witness_ref')
        _idlist(r['output_refs'],path+'/output_refs')
    return ctx
