"""P1.4 scoped, deterministic semantic typing atop P1.2/P1.3.

This is descriptive typing only: no fact checking, evidence authentication,
permission decision, method execution, or production Core state change.
"""
from __future__ import annotations
import hashlib
import json
import re
from typing import Any
from cube_parser.parser import parse_result
from cube_resolver.resolver import Resolver, validate_context, ContextError, STAGES

T_ROLES = frozenset(('occurrence','recording','observation','assessment',
                     'effective-interval','freshness','historicity','scheduling'))
METHOD_ID = re.compile(r'^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*/v[1-9][0-9]*$')
PARAM_NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
CHECKS = tuple(STAGES)

class ProfileError(ValueError):
    """Invalid P1.4 optional fixture-scoped qualifier profile."""


def _list_strings(value: Any, field: str, *, allow_empty=True):
    if not isinstance(value, list) or (not allow_empty and not value) or not all(isinstance(v,str) and v for v in value) or len(value)!=len(set(value)):
        raise ProfileError(f'{field}: expected unique nonempty strings')
    return value


def validate_qualification_profiles(doc: dict) -> dict:
    """Local P1.4 extension, not a modification of P1.1 binding-context/1."""
    if not isinstance(doc, dict) or set(doc) != {'format','reference_version','profile_id','scope','origin','witness_refs','qualifiers'}:
        raise ProfileError('Profile requires exactly format/reference_version/profile_id/scope/origin/witness_refs/qualifiers')
    if doc['format']!='aiaeao.cube.qualifier-profiles/1' or doc['reference_version']!='v9.4':
        raise ProfileError('Unsupported profile format/reference')
    if not all(isinstance(doc[k],str) and doc[k] for k in ('profile_id','scope')):
        raise ProfileError('profile_id and scope must be nonempty strings')
    if doc['origin'] not in ('illustrative_fixture','external_declaration_unverified'):
        raise ProfileError('Only unverified caller declarations are allowed')
    _list_strings(doc['witness_refs'],'witness_refs')
    if not isinstance(doc['qualifiers'],list) or len(doc['qualifiers'])>128:
        raise ProfileError('qualifiers must be array of <= 128 profiles')
    identifiers=set()
    for i,item in enumerate(doc['qualifiers']):
        path=f'qualifiers[{i}]'
        if not isinstance(item,dict) or set(item) != {'profile_ref','coordinate','required_parameters','allowed_parameters','allowed_values','requires_witness'}:
            raise ProfileError(path+': invalid keys')
        if not isinstance(item['profile_ref'],str) or not item['profile_ref'] or item['profile_ref'] in identifiers:
            raise ProfileError(path+': duplicate or empty profile_ref')
        identifiers.add(item['profile_ref'])
        if item['coordinate'] not in ('T','F','M','O'): raise ProfileError(path+': invalid coordinate')
        req=_list_strings(item['required_parameters'],path+'.required_parameters')
        allowed=_list_strings(item['allowed_parameters'],path+'.allowed_parameters')
        if set(req)-set(allowed): raise ProfileError(path+': required parameters not in allowed_parameters')
        if any(PARAM_NAME.fullmatch(x) is None for x in allowed): raise ProfileError(path+': invalid parameter name')
        if not isinstance(item['allowed_values'],dict) or set(item['allowed_values'])-set(allowed):
            raise ProfileError(path+': invalid allowed_values')
        for k,v in item['allowed_values'].items():
            _list_strings(v,path+'.allowed_values.'+k,allow_empty=False)
        if not isinstance(item['requires_witness'],bool):raise ProfileError(path+': requires_witness must be bool')
        if item['coordinate'] in ('T','O') and not item['requires_witness']:
            raise ProfileError(path+': T/O profile must require a witness pointer')
        if item['requires_witness'] and 'witness_ref' not in req:
            raise ProfileError(path+': witness_ref must be required')
        # A scoped profile cannot invent a ninth canonical temporal facet.
        if item['coordinate']=='T' and 'role' in item['allowed_values'] and not set(item['allowed_values']['role'])<=T_ROLES:
            raise ProfileError(path+': unsupported temporal role')
    return doc


def _pairs_no_duplicates(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ProfileError('Duplicate qualifier JSON key '+key)
        result[key]=value
    return result


def load_qualification_profiles_bytes(raw: bytes) -> dict:
    if len(raw)>1024*1024: raise ProfileError('Qualification profile exceeds 1 MiB')
    try:
        text=raw.decode('utf-8')
        if text.startswith('\ufeff'): raise ProfileError('No BOM allowed')
        doc=json.loads(text,object_pairs_hook=_pairs_no_duplicates)
    except (UnicodeError, ValueError, RecursionError) as e:
        raise ProfileError('Invalid qualification profile JSON: '+str(e)[:180]) from e
    return validate_qualification_profiles(doc)


def join(statuses: list[str]) -> str:
    if 'FAIL' in statuses: return 'FAIL'
    if 'UNRESOLVED' in statuses: return 'UNRESOLVED'
    if 'PASS' in statuses: return 'PASS'
    return 'NOT_EVALUATED'


def nodes(node: dict, path=''):
    """Preorder AST traversal. Qualifiers passed only to directly wrapped expression."""
    kind=node['kind']
    if kind=='qualified':
        current=node; all_qualifiers=[]
        while current['kind']=='qualified':
            all_qualifiers.extend((path+'/qualifiers/'+str(i), q) for i,q in enumerate(current['qualifiers']))
            path+='/expression';current=current['expression']
        yield path or '/',current,all_qualifiers
        yield from children(current,path)
    else:
        yield path or '/',node,[]
        yield from children(node,path)


def children(node: dict, path: str):
    if node['kind']=='relation':
        yield from nodes(node['subject'],path+'/subject')
        yield from nodes(node['object'],path+'/object')
    elif node['kind']=='application':
        for i,arg in enumerate(node['arguments']): yield from nodes(arg,path+'/arguments/'+str(i))


def ref_type(node: dict) -> str | None:
    while node['kind']=='qualified': node=node['expression']
    # Types of relation and application outputs are NOT specified by P1.1.
    return node['address'].get('concept_id') if node['kind']=='reference' else None


class SemanticValidator:
    def __init__(self):
        self.resolver=Resolver()
        # P1.4 adds one local diagnostic extension without changing frozen P1.1.
        self.diags=dict(self.resolver.diag_contract)
        self.diags['P1_QUALIFIER_SIGNATURE']={
            'code':'P1_QUALIFIER_SIGNATURE','stage':'qualifier_typing','default_status':'FAIL',
            'reference_rule':'P1.4 qualification-profiles/1 local scoped signature (not v9.4 ontology)'
        }

    def _diagnostic(self,code: str,path: str,message: str) -> dict:
        entry=self.diags[code]
        return {'code':code,'stage':entry['stage'],
                'severity':'error' if entry['default_status']=='FAIL' else 'unresolved',
                'message':f'{path or "/"}: {message}',
                'reference_rule':entry['reference_rule']}

    def _check_relation(self,node: dict,path: str,attached: list,ctx:dict|None):
        ident=node['predicate_id']
        all_contracts=[] if ctx is None else [p for p in ctx['predicate_contracts'] if p['predicate_id']==ident]
        scope=ctx.get('scope_ref') if ctx else None
        scoped=[p for p in all_contracts if scope and p['scope']==scope]
        if not scoped:
            return 'UNRESOLVED',[self._diagnostic('P1_PREDICATE_PROFILE_MISSING',path,
                'No matching declared versioned, scoped predicate signature for '+repr(ident)+'.')]
        if len(scoped)!=1:
            return 'UNRESOLVED',[self._diagnostic('P1_PREDICATE_PROFILE_MISSING',path,
                'Ambiguous predicate revision/signatures; no arbitrary selection.')]
        p=scoped[0]
        # Only reference nodes have a declared referent type in P1.1.
        left,right=node['subject'],node['object']
        def concept_of(value):
            while value['kind']=='qualified':value=value['expression']
            if value['kind']!='reference': return None
            a=value['address']; e=self.resolver.exact.get((a['home'],a['concept_key']))
            if not e or e['instantiation']=='not_instantiable':return None
            return e['concept_id']
        l=concept_of(left);r=concept_of(right)
        if l is None or r is None:
            return 'UNRESOLVED',[self._diagnostic('P1_PREDICATE_PROFILE_MISSING',path,
                'Operand is not a resolved reference type; nested expression return types are undefined in P1.1.')]
        if l not in p['subject_concept_ids'] or r not in p['object_concept_ids']:
            return 'FAIL',[self._diagnostic('P1_PREDICATE_SIGNATURE',path,
                'Predicate '+repr(ident)+' does not admit the directed (subject,object) concept IDs in this fixture scope.')]
        attached_coords={qual['coordinate'] for _,qual in attached}
        missing=set(p.get('required_qualifiers',[]))-attached_coords
        if missing:
            return 'FAIL',[self._diagnostic('P1_PREDICATE_SIGNATURE',path,
                'Required predicate-level qualifier(s) absent: '+','.join(sorted(missing))+'.')]
        if node['parameters']:
            return 'UNRESOLVED',[self._diagnostic('P1_PREDICATE_PROFILE_MISSING',path,
                'This P1.1 signature has no typed predicate-parameter contract.')]
        # A wrong/missing referent binding must not disappear behind a matching type pair.
        return 'PASS',[]

    def _check_method(self,node:dict,path:str,ctx:dict|None):
        ident=node['method_id'];scope=ctx.get('scope_ref') if ctx else None
        scoped=[] if ctx is None else [m for m in ctx.get('method_contracts',[]) if m['method_id']==ident and scope and m['scope']==scope]
        if len(scoped)!=1:
            return 'UNRESOLVED',[self._diagnostic('P1_METHOD_PROFILE_MISSING',path,
                'Missing or ambiguous revisioned, scoped method signature for '+repr(ident)+'.')]
        m=scoped[0];args=node['arguments'];count=len(args)
        if count<m['argument_min'] or count>m['argument_max']:
            return 'FAIL',[self._diagnostic('P1_METHOD_SIGNATURE',path,'Method argument cardinality mismatch.')]
        if m.get('effect_class')=='effectful_declared':
            return 'FAIL',[self._diagnostic('P1_METHOD_SIGNATURE',path,
                'Effectful method application is not admitted by the read-only P1 validator.')]
        if m.get('effect_class')!='pure_declarative':
            return 'UNRESOLVED',[self._diagnostic('P1_METHOD_PROFILE_MISSING',path,
                'Method effect class unknown; descriptive purity cannot be established.')]
        ids=m.get('argument_concept_ids')
        if ids is None or len(ids)!=count:
            return 'UNRESOLVED',[self._diagnostic('P1_METHOD_PROFILE_MISSING',path,
                'No complete ordered argument-concept signature is declared.')]
        for i,(arg,required) in enumerate(zip(args,ids)):
            current=arg
            while current['kind']=='qualified': current=current['expression']
            if current['kind']!='reference':
                return 'UNRESOLVED',[self._diagnostic('P1_METHOD_PROFILE_MISSING',path+'/arguments/'+str(i),
                    'Return type of nested expression is not specified.')]
            a=current['address']; e=self.resolver.exact.get((a['home'],a['concept_key']))
            if e and e['concept_id']!=required:
                return 'FAIL',[self._diagnostic('P1_METHOD_SIGNATURE',path+'/arguments/'+str(i),
                    'Declared method argument concept type does not match.')]
            if not e:
                return 'UNRESOLVED',[self._diagnostic('P1_METHOD_PROFILE_MISSING',path+'/arguments/'+str(i),
                    'Argument concept is unresolved.')]
        if node['parameters']:
            return 'UNRESOLVED',[self._diagnostic('P1_METHOD_PROFILE_MISSING',path,
                'P1.1 has no typed parameter signature for method keyword arguments.')]
        return 'PASS',[]

    def _check_qualifier(self,q:dict,path:str,ctx:dict|None,profile:dict|None):
        kind=q['coordinate'];params=q['parameters']
        if kind=='T':
            role=params.get('role')
            if role is not None and (not isinstance(role,str) or role not in T_ROLES):
                return 'FAIL',[self._diagnostic('P1_TEMPORAL_ROLE',path,
                    'Role is not one of the eight v9.4 temporal facets.')]
        if kind=='F' and 'method' in params:
            mid=params['method']
            if not isinstance(mid,str) or METHOD_ID.fullmatch(mid) is None:
                return 'UNRESOLVED',[self._diagnostic('P1_QUALIFIER_PROFILE_MISSING',path,
                    'F method requires a valid versioned method identifier.')]
        if kind=='O' and not params.get('witness_ref'):
            return 'UNRESOLVED',[self._diagnostic('P1_OBSERVER_WITNESS',path,
                'Observer flag/actor_ref is not a delivered, permitted or perceived witness.')]
        if profile is None:
            return 'UNRESOLVED',[self._diagnostic('P1_QUALIFIER_PROFILE_MISSING',path,
                'No scoped, unverified descriptive qualification profile supplied.')]
        if ctx is None or not ctx.get('scope_ref'):
            return 'UNRESOLVED',[self._diagnostic('P1_QUALIFIER_PROFILE_MISSING',path,
                'Qualification profile requires a matching declared binding-context scope.')]
        # Cross-scope mismatch is recorded independently by scope_consistency.
        if profile['scope']!=ctx['scope_ref']:
            return 'UNRESOLVED',[self._diagnostic('P1_QUALIFIER_PROFILE_MISSING',path,
                'Qualifier profile scope does not match binding-context scope.')]
        options=[p for p in profile['qualifiers'] if p['coordinate']==kind and
                 ('profile_ref' not in q or p['profile_ref']==q['profile_ref'])]
        if len(options)!=1:
            return 'UNRESOLVED',[self._diagnostic('P1_QUALIFIER_PROFILE_MISSING',path,
                'Missing or ambiguous qualifier profile for this coordinate/profile_ref.')]
        p=options[0]
        if set(params)-set(p['allowed_parameters']) or set(p['required_parameters'])-set(params):
            return 'FAIL',[self._diagnostic('P1_QUALIFIER_SIGNATURE',path,
                'Qualification parameters violate the selected fixture profile.')]
        for key,allowed in p['allowed_values'].items():
            if key in params and params[key] not in allowed:
                return 'FAIL',[self._diagnostic('P1_QUALIFIER_SIGNATURE',path,
                    'Qualification parameter outside declared allowed_values: '+key)]
        if kind=='T' and ('role' not in params or params['role'] not in T_ROLES):
            return 'UNRESOLVED',[self._diagnostic('P1_QUALIFIER_PROFILE_MISSING',path,
                'T facet must be explicitly declared to bind a time role.')]
        if kind=='F':
            if not isinstance(params.get('method'),str) or METHOD_ID.fullmatch(params['method']) is None:
                return 'UNRESOLVED',[self._diagnostic('P1_QUALIFIER_PROFILE_MISSING',path,
                    'F qualifier has no accepted revisioned method signature.')]
            matched=[m for m in ctx.get('method_contracts',[]) if m['method_id']==params['method'] and m['scope']==ctx['scope_ref']]
            if len(matched)!=1 or matched[0].get('effect_class')!='pure_declarative':
                return 'UNRESOLVED',[self._diagnostic('P1_QUALIFIER_PROFILE_MISSING',path,
                    'F requires one scoped pure_declarative method declaration.')]
        if p['requires_witness']:
            witness=params.get('witness_ref')
            if not isinstance(witness,str) or witness not in profile['witness_refs']:
                return 'UNRESOLVED',[self._diagnostic('P1_OBSERVER_WITNESS' if kind=='O' else 'P1_QUALIFIER_PROFILE_MISSING',path,
                    'Witness pointer not declared in this unverified qualification fixture.')]
        return 'PASS',[]

    @staticmethod
    def _stage(statuses:list[str],label:str):
        s=join(statuses)
        reasons={'PASS':'Every applicable '+label+' check passed in the declared descriptive scope.',
                 'FAIL':'At least one applicable '+label+' check violated a declared contract.',
                 'UNRESOLVED':'At least one applicable '+label+' check lacks a decisive declaration.',
                 'NOT_EVALUATED':'Not applicable, or not attempted because input failed an earlier stage.'}
        return {'status':s,'reason':reasons[s]}

    def validate_bytes(self,raw:bytes,*,input_format='acg_text',context:dict|None=None,
                       qualification_profiles:dict|None=None)->dict:
        if context is not None:validate_context(context)
        if qualification_profiles is not None:validate_qualification_profiles(qualification_profiles)
        parsed=parse_result(raw,input_format=input_format)
        checks={s:self._stage([],s) for s in CHECKS}
        checks['syntax']={'status':parsed['syntax_status'],'reason':
            'ACG grammar parsed.' if parsed['syntax_status']=='PASS' else
            'JSON AST input: original text syntax not witnessed.' if input_format=='json_ast' else
            'Lexical/syntax error prevented semantic validation.'}
        checks['structure']={'status':parsed['structure_status'],'reason':
            'AST structurally valid against P1.2 checks.' if parsed['structure_status']=='PASS' else
            'No structurally valid AST available.'}
        diagnostics=list(parsed['diagnostics'])
        if parsed['structure_status']=='PASS':
            ast=parsed['ast']
            resolution=self.resolver.resolve_ast(ast,context)
            for d in resolution['diagnostics']:
                # P1.1 report schema disallows ast_path: carry it in message.
                clean={k:v for k,v in d.items() if k!='ast_path'}
                clean['message']=d['ast_path']+': '+d['message']
                diagnostics.append(clean)
            checks['concept_resolution']=self._stage([x['concept_resolution'] for x in resolution['bindings']],'concept')
            checks['referent_binding']=self._stage([x['referent_binding'] for x in resolution['bindings']],'referent')
            relations=[];methods=[];qualifiers=[]
            for path,node,attached in nodes(ast):
                if node['kind']=='relation':
                    status,ds=self._check_relation(node,path,attached,context)
                    relations.append(status);diagnostics.extend(ds)
                elif node['kind']=='application':
                    status,ds=self._check_method(node,path,context)
                    methods.append(status);diagnostics.extend(ds)
                for qpath,q in attached:
                    status,ds=self._check_qualifier(q,qpath,context,qualification_profiles)
                    qualifiers.append(status);diagnostics.extend(ds)
            checks['predicate_typing']=self._stage(relations,'predicate typing')
            checks['method_typing']=self._stage(methods,'method typing')
            checks['qualifier_typing']=self._stage(qualifiers,'qualifier typing')
            scope_checks=[]
            if context is not None:
                declared_scope=context.get('scope_ref')
                if not declared_scope:
                    scope_checks.append('UNRESOLVED')
                    diagnostics.append(self._diagnostic('P1_CONTEXT_UNTRUSTED','/',
                        'Context has no explicit scope_ref; local scoped signatures cannot be selected.'))
                else:
                    scope_checks.append('PASS')
                    for binding in resolution['bindings']:
                        ref=next((r for r in context['referents'] if r['ref']==binding['referent_ref']),None)
                        if ref is not None and ref.get('scope_ref')!=declared_scope:
                            code='P1_SCOPE_CONFLICT' if ref.get('scope_ref') else 'P1_CONTEXT_UNTRUSTED'
                            status='FAIL' if ref.get('scope_ref') else 'UNRESOLVED'
                            scope_checks.append(status)
                            diagnostics.append(self._diagnostic(code,binding['ast_path'],
                                'Referenced object scope conflicts with, or is missing from, the declared validation scope.'))
                    # If a predicate or method name has signatures ONLY in foreign scopes, it cannot be borrowed.
                    for path,node,_ in nodes(ast):
                        if node['kind'] in ('relation','application'):
                            key='predicate_id' if node['kind']=='relation' else 'method_id'
                            contracts=context['predicate_contracts'] if node['kind']=='relation' else context.get('method_contracts',[])
                            named=[c for c in contracts if c[key]==node[key]]
                            if named and not any(c['scope']==declared_scope for c in named):
                                scope_checks.append('FAIL')
                                diagnostics.append(self._diagnostic('P1_SCOPE_CONFLICT',path,
                                    'Matching signature exists only in a conflicting declared scope.'))
                    if qualification_profiles is not None and qualification_profiles['scope']!=declared_scope:
                        scope_checks.append('FAIL')
                        diagnostics.append(self._diagnostic('P1_SCOPE_CONFLICT','/',
                            'Qualification profile scope contradicts binding-context scope.'))
            checks['scope_consistency']=self._stage(scope_checks,'scope')
        # Diagnostic sort: first source byte offsets when available, then stable code/stage/path order.
        ordinal={s:i for i,s in enumerate(CHECKS)}
        diagnostics.sort(key=lambda d:(d.get('byte_start',10**12), d['code'],ordinal.get(d['stage'],99),d['message']))
        overall=join([d['status'] for d in checks.values()])
        if overall=='NOT_EVALUATED':overall='UNRESOLVED'
        return {'format':'aiaeao.cube.validation-report/1',
                'reference_version':'v9.4','profile':'P1-VC/1.0.0',
                'overall_status':overall,'context_id':context['context_id'] if context else None,
                'input_sha256':hashlib.sha256(raw).hexdigest(),
                'checks':checks,'diagnostics':diagnostics,
                'epistemic_warrant':'NOT_EVALUATED','current_authority':'NOT_EVALUATED',
                'canonical_admission':'NOT_EVALUATED',
                'summary':'Descriptive fixture-scoped validation only. Context declarations and witnesses are unverified; no external truth or execution admission is asserted.'}
