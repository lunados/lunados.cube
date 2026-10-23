"""P1.3 deterministic concept + declared-referent resolver. No semantic truth or authority."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from cube_parser.parser import parse_result, validate_ast, json_dump

HERE = Path(__file__).resolve().parents[1]
BASE = HERE / "baseline"
P11 = BASE / "P1_1_Contract_Freeze"
P0 = BASE / "P0_reference"

STAGES = ("syntax", "structure", "concept_resolution", "referent_binding",
          "predicate_typing", "method_typing", "qualifier_typing", "scope_consistency")
STATUSES = ("PASS", "FAIL", "UNRESOLVED", "NOT_EVALUATED")

class ContractError(ValueError):
    """Missing or modified fixed reference files; fail closed."""

class ContextError(ValueError):
    """Malformed, ambiguous or nonconforming declared context; not a semantic status."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def reject_duplicate_pairs(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise ContextError('Duplicate JSON object key: '+k)
        obj[k] = v
    return obj


def _object(value, fields, required, where):
    if not isinstance(value, dict):
        raise ContextError(f'{where} must be an object')
    extra = value.keys()-set(fields)
    missing = set(required)-value.keys()
    if extra or missing:
        raise ContextError(f'{where}: unexpected fields {sorted(extra)} or missing fields {sorted(missing)}')


def _nonempty(x):
    return isinstance(x,str) and bool(x) and not any(0xD800 <= ord(c) <= 0xDFFF for c in x)


def _strlist(x, where, *, unique=False, minlen=0):
    if not isinstance(x,list) or len(x)<minlen or not all(_nonempty(y) for y in x):
        raise ContextError(f'{where} must be a list of nonempty strings')
    if unique and len(x)!=len(set(x)):
        raise ContextError(f'{where} must contain unique entries')


def validate_context(ctx: Any) -> dict:
    """Stdlib implementation of the P1.1 context schema plus deterministic uniqueness.

    Does NOT infer any authority, attest provenance or execute a predicate.
    Invalid caller payloads are input errors, not semantic unknowns.
    """
    _object(ctx, ('format','reference_version','context_id','source_kind','scope_ref','referents',
                  'predicate_contracts','method_contracts','profile_limitations'),
            ('format','reference_version','context_id','source_kind','referents','predicate_contracts'),'context')
    if ctx['format']!='aiaeao.cube.binding-context/1' or ctx['reference_version']!='v9.4':
        raise ContextError('Unsupported context format or reference_version')
    if not _nonempty(ctx['context_id']): raise ContextError('context_id required')
    if ctx['source_kind'] not in ('illustrative_fixture','external_declaration_unverified'):
        raise ContextError('Unsupported source_kind')
    if 'scope_ref' in ctx and not isinstance(ctx['scope_ref'],str):
        raise ContextError('scope_ref must be string')
    if 'profile_limitations' in ctx:
        _strlist(ctx['profile_limitations'],'profile_limitations')
    for name,maximum in [('referents',10000),('predicate_contracts',512),('method_contracts',512)]:
        if not isinstance(ctx.get(name,[]),list) or len(ctx.get(name,[]))>maximum:
            raise ContextError(f'{name} must be an array of <= {maximum} entries')
    refids=set()
    for i,ref in enumerate(ctx['referents']):
        label=f'referents[{i}]'
        _object(ref,('ref','concept_id','home','layers','provenance_status','scope_ref','witness_ref'),
                ('ref','concept_id','home','layers','provenance_status'),label)
        if not _nonempty(ref['ref']) or not _nonempty(ref['concept_id']):
            raise ContextError(label+': ref and concept_id must be nonempty')
        if ref['home'] not in ('X','Y','Z') or ref['provenance_status']!='declared_unverified':
            raise ContextError(label+': invalid home or provenance_status')
        if not isinstance(ref['layers'],list) or not ref['layers'] or any(v not in ('α','β','ζ') for v in ref['layers']):
            raise ContextError(label+': invalid layers')
        if len(ref['layers'])!=len(set(ref['layers'])):
            raise ContextError(label+': duplicate layers')
        if 'scope_ref' in ref and not isinstance(ref['scope_ref'],str): raise ContextError(label+': scope_ref must be string')
        if 'witness_ref' in ref and not _nonempty(ref['witness_ref']): raise ContextError(label+': invalid witness_ref')
        if ref['ref'] in refids: raise ContextError(label+': duplicate referent identifier (ambiguous)')
        refids.add(ref['ref'])
    # P1.3 does not type-check predicate/method contracts, but refuses invalid input context shape.
    for name,fields,required in [
        ('predicate_contracts',('predicate_id','revision','scope','origin','subject_concept_ids','object_concept_ids','direction','required_qualifiers','additional_constraints'),
         ('predicate_id','revision','scope','origin','subject_concept_ids','object_concept_ids','direction')),
        ('method_contracts',('method_id','revision','scope','origin','argument_min','argument_max','argument_concept_ids','effect_class'),
         ('method_id','revision','scope','origin','argument_min','argument_max'))]:
        for i,entry in enumerate(ctx.get(name,[])):
            label=f'{name}[{i}]'; _object(entry,fields,required,label)
            for attr in required:
                if attr in ('argument_min','argument_max','subject_concept_ids','object_concept_ids'): continue
                if not _nonempty(entry[attr]): raise ContextError(label+': invalid '+attr)
            if entry['origin'] not in ('illustrative_fixture','external_declaration_unverified'):
                raise ContextError(label+': invalid origin')
            if name=='predicate_contracts':
                if entry['direction']!='subject_to_object': raise ContextError(label+': invalid direction')
                for attr in ('subject_concept_ids','object_concept_ids'):
                    _strlist(entry[attr],label+'.'+attr,unique=True,minlen=1)
                if 'required_qualifiers' in entry:
                    _strlist(entry['required_qualifiers'],label+'.required_qualifiers',unique=True)
                    if any(x not in ('T','F','M','O') for x in entry['required_qualifiers']): raise ContextError(label+': invalid qualifier')
                if 'additional_constraints' in entry: _strlist(entry['additional_constraints'],label+'.additional_constraints')
            else:
                if re.fullmatch(r'[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*/v[1-9][0-9]*', entry['method_id']) is None:
                    raise ContextError(label+': invalid method_id')
                if not isinstance(entry['argument_min'],int) or isinstance(entry['argument_min'],bool) or entry['argument_min']<0 or not isinstance(entry['argument_max'],int) or isinstance(entry['argument_max'],bool) or entry['argument_max']<0:
                    raise ContextError(label+': argument bounds must be nonnegative integers')
                if 'argument_concept_ids' in entry: _strlist(entry['argument_concept_ids'],label+'.argument_concept_ids')
                if 'effect_class' in entry and entry['effect_class'] not in ('pure_declarative','unknown','effectful_declared'):
                    raise ContextError(label+': invalid effect_class')
    return ctx


def load_context_bytes(raw: bytes) -> dict:
    if len(raw)>16*1024*1024: raise ContextError('Context exceeds 16 MiB input limit')
    try:
        ctx=json.loads(raw.decode('utf-8-sig'),object_pairs_hook=reject_duplicate_pairs)
    except (ValueError, UnicodeError, RecursionError) as e:
        raise ContextError('Cannot decode context JSON: '+str(e)[:140]) from e
    return validate_context(ctx)


class Resolver:
    def __init__(self):
        lock=read_json(P11/'contract'/'source_lock.json')
        sha_expected={x['name']:x['sha256'] for x in lock['sources']}
        catalog=P0/'grammar'/'concepts.json'
        expected=sha_expected['P0/v9.4/grammar/concepts.json']
        if hashlib.sha256(catalog.read_bytes()).hexdigest()!=expected:
            raise ContractError('P0 concept catalog differs from frozen v9.4 source-lock')
        keys_path=P11/'contract'/'concept_keys.json'
        if hashlib.sha256(keys_path.read_bytes()).hexdigest()!='7bb0962eb2bc169b31462b0cfa672d4d3b54989adf4290c85c229a30adcfec6b':
            raise ContractError('Frozen P1.1 concept-key table differs from approved implementation snapshot')
        keys=read_json(keys_path)
        if keys.get('catalog_entry_count')!=80 or keys.get('semantic_notation_alias_count')!=5 or len(keys.get('entries',[]))!=85:
            raise ContractError('P1.1 concept-key count changed')
        catalog_entries=read_json(catalog)['concepts']
        self.catalog={x['id']:x for x in catalog_entries}
        if len(self.catalog)!=80: raise ContractError('Unexpected P0 catalog size')
        self.exact={};self.by_key={}
        alias_count=0;catalog_count=0
        for e in keys['entries']:
            pair=(e['home'],e['concept_key'])
            if pair in self.exact: raise ContractError('Ambiguous (home,concept_key): '+str(pair))
            self.exact[pair]=e
            self.by_key.setdefault(e['concept_key'],set()).add(e['home'])
            c=self.catalog.get(e['concept_id'])
            if not c or c['home']!=e['home'] or c['kind']!=e['kind']:
                raise ContractError('P1.1 key resolves to absent/incompatible P0 concept')
            if e.get('alias_kind'):
                if e.get('alias_kind')!='semantic_notation' or e['concept_key'] not in 'ΨΓΣΞΠ' or e['instantiation']!='not_instantiable':
                    raise ContractError('Unsupported alias entry')
                alias_count+=1
            else:
                catalog_count+=1
        if alias_count!=5 or catalog_count!=80 or {e['concept_id'] for e in keys['entries'] if not e.get('alias_kind')}!=set(self.catalog):
            raise ContractError('Incorrect keys/aliases or incomplete catalog mapping')
        self.diag_contract={e['code']:e for e in read_json(P11/'contract'/'diagnostics.json')['codes']}

    def _diagnostic(self,code: str,path: str,message: str) -> dict:
        rule=self.diag_contract[code]
        return {'code':code,'stage':rule['stage'],
                'severity':'error' if rule['default_status']=='FAIL' else 'unresolved',
                'message':message,'reference_rule':rule['reference_rule'],'ast_path':path}

    @staticmethod
    def _walk(node: dict, path: str=''):
        kind=node['kind']
        if kind=='reference':
            yield path or '/',node
        elif kind=='qualified':
            yield from Resolver._walk(node['expression'],path+'/expression')
        elif kind=='relation':
            yield from Resolver._walk(node['subject'],path+'/subject')
            yield from Resolver._walk(node['object'],path+'/object')
        elif kind=='application':
            for i,arg in enumerate(node['arguments']):
                yield from Resolver._walk(arg,path+'/arguments/'+str(i))

    def resolve_ast(self, ast: dict, context: dict | None = None) -> dict:
        """Resolve P1.3 stages only. AST must have P1.2 structural PASS."""
        validate_ast(ast)
        if context is not None: validate_context(context)
        by_ref={r['ref']:r for r in context['referents']} if context is not None else {}
        bindings=[]; diagnostics=[]
        for path,node in self._walk(ast):
            addr=node['address']; key=addr['concept_key']; home=addr['home']; layer=addr['layer']; refid=node['referent_ref']
            e=self.exact.get((home,key))
            res={'ast_path':path,'home':home,'layer':layer,'concept_key':key,
                 'referent_ref':refid,'concept_resolution':'PASS','referent_binding':'NOT_EVALUATED'}
            if e is None:
                if key in self.by_key:
                    res['concept_resolution']='FAIL'
                    diagnostics.append(self._diagnostic('P1_WRONG_HOME',path+'/address',
                        f'Known concept key {key!r} belongs to home(s) {", ".join(sorted(self.by_key[key]))}, not {home}.'))
                else:
                    res['concept_resolution']='UNRESOLVED'
                    diagnostics.append(self._diagnostic('P1_UNKNOWN_CONCEPT',path+'/address',
                        f'No exact P1.1 concept entry for {home}:{key}.'))
                bindings.append(res);continue
            res['concept_id']=e['concept_id'];res['instantiation']=e['instantiation']
            if e['instantiation']=='not_instantiable':
                res['concept_resolution']='FAIL'
                diagnostics.append(self._diagnostic('P1_NON_INSTANTIABLE',path+'/address',
                    f'{e["concept_id"]} is a non-instantiable semantic dimension or relation viewpoint.'))
                bindings.append(res);continue
            if 'concept_id' in addr and addr['concept_id']!=e['concept_id']:
                res['referent_binding']='FAIL'
                diagnostics.append(self._diagnostic('P1_REFERENT_MISMATCH',path+'/address/concept_id',
                    'Explicit address.concept_id contradicts the exact v9.4 concept-key mapping.'))
                bindings.append(res);continue
            if e['instantiation']=='requires_binding_profile':
                res['referent_binding']='UNRESOLVED'
                diagnostics.append(self._diagnostic('P1_INSTANTIATION_PROFILE_REQUIRED',path,
                    'This endpoint/zone requires an explicit instantiation profile not defined by binding-context/1.'))
                bindings.append(res);continue
            if context is None or refid not in by_ref:
                res['referent_binding']='UNRESOLVED'
                if layer in ('β','ζ'):
                    diagnostics.append(self._diagnostic('P1_LAYER_WITNESS_MISSING',path,
                        'No declared β/ζ referent and temporal/observer witness were provided.'))
                else:
                    diagnostics.append(self._diagnostic('P1_BINDING_CONTEXT_REQUIRED',path,
                        'No exact declared referent binding available in the supplied context.'))
                bindings.append(res);continue
            b=by_ref[refid]
            res['declaration_origin']=context['source_kind']
            res['provenance_status']=b['provenance_status']
            res['declared_layers']=list(b['layers'])
            if b['concept_id']!=e['concept_id'] or b['home']!=home or layer not in b['layers']:
                res['referent_binding']='FAIL'
                diagnostics.append(self._diagnostic('P1_REFERENT_MISMATCH',path,
                    'Declared referent concept_id/home/layer contradicts the requested address.'))
                bindings.append(res);continue
            scope=context.get('scope_ref')
            if scope and b.get('scope_ref') and b['scope_ref']!=scope:
                res['referent_binding']='FAIL'
                diagnostics.append(self._diagnostic('P1_REFERENT_MISMATCH',path,
                    'Declared referent scope differs from the context scope.'))
                bindings.append(res);continue
            if layer in ('β','ζ') and not b.get('witness_ref'):
                res['referent_binding']='UNRESOLVED'
                diagnostics.append(self._diagnostic('P1_LAYER_WITNESS_MISSING',path,
                    'Layer β/ζ requires an explicit context witness reference; a layer token alone proves nothing.'))
                bindings.append(res);continue
            res['referent_binding']='PASS'
            if layer in ('β','ζ'):
                res['declared_witness_ref']=b['witness_ref']
                res['witness_truth']='NOT_EVALUATED'
            bindings.append(res)
        concept_status=self._combine([x['concept_resolution'] for x in bindings])
        referent_status=self._combine([x['referent_binding'] for x in bindings])
        return {'bindings':bindings,'diagnostics':diagnostics,
                'concept_status':concept_status,'referent_status':referent_status}

    @staticmethod
    def _combine(statuses: list[str]) -> str:
        if 'FAIL' in statuses: return 'FAIL'
        if 'UNRESOLVED' in statuses: return 'UNRESOLVED'
        if 'PASS' in statuses: return 'PASS'
        return 'NOT_EVALUATED'

    def resolve_bytes(self, raw: bytes, *, input_format: str='acg_text', context: dict|None=None) -> dict:
        if context is not None: validate_context(context)
        p=parse_result(raw,input_format=input_format)
        initial={stage:{'status':'NOT_EVALUATED','reason':'Not implemented in P1.3; reserved for P1.4/P1.5.'} for stage in STAGES}
        initial['syntax']={'status':p['syntax_status'],
                           'reason':'Source grammar parsed.' if p['syntax_status']=='PASS' else 'No original source text or parser rejection.'}
        initial['structure']={'status':p['structure_status'],
                              'reason':'AST passed P1.2 structural checks.' if p['structure_status']=='PASS' else 'Invalid or unavailable AST.'}
        result={'format':'aiaeao.cube.resolution-result/1','reference_version':'v9.4',
                'profile':'P1-VC/1.0.0','component':'P1.3','input_format':input_format,
                'input_sha256':hashlib.sha256(raw).hexdigest(),
                'context_id':context['context_id'] if context is not None else None,
                'resolution_status':'UNRESOLVED','checks':initial,'bindings':[],
                'diagnostics':list(p['diagnostics']),
                'epistemic_warrant':'NOT_EVALUATED','current_authority':'NOT_EVALUATED',
                'canonical_admission':'NOT_EVALUATED',
                'semantic_typing':'NOT_EVALUATED',
                'limitations':['P1.3-only status: predicate/method/qualifier/scope typing deferred.',
                               'Context declarations are untrusted, including ζ witness pointers.']}
        if p['structure_status']!='PASS':
            result['resolution_status']='FAIL'
            return result
        rr=self.resolve_ast(p['ast'],context)
        result['bindings']=rr['bindings'];result['diagnostics']+=rr['diagnostics']
        for stage,k in [('concept_resolution','concept_status'),('referent_binding','referent_status')]:
            result['checks'][stage]={'status':rr[k],
               'reason':('Every resolved reference passed this descriptive stage.' if rr[k]=='PASS' else
                         'One or more references failed this stage.' if rr[k]=='FAIL' else
                         'One or more reference bindings remain unresolved.' if rr[k]=='UNRESOLVED' else
                         'No applicable references or blocked by earlier checks.')}
        result['resolution_status']=self._combine([x for x in (rr['concept_status'],rr['referent_status']) if x!='NOT_EVALUATED'])
        if result['resolution_status']=='NOT_EVALUATED': result['resolution_status']='UNRESOLVED'
        return result
