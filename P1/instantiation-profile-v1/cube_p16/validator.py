"""Additive P1.6 validator. Immutable P1.1-P1.5 executable files are NOT edited.

/1 dispatch delegates unconditionally to frozen P1.4. /2 receives the
original P1.4 result from a losslessly projected /1 context and replaces only
X endpoint instantiation judgments with P1.6's independently evaluated slots.
"""
from __future__ import annotations
import copy
import hashlib
import json
from cube_parser.parser import parse_result
from cube_resolver.resolver import validate_context as validate_context_v1, load_context_bytes as load_context_bytes_v1, reject_duplicate_pairs
from cube_resolver.resolver import ContextError, Resolver
from cube_semantic.validator import SemanticValidator as FrozenValidator, join
from cube_p16.instantiation import validate_context_v2, InstantiationCheck, InstantiationError


def validate_context(ctx):
    if isinstance(ctx,dict) and ctx.get('format')=='aiaeao.cube.binding-context/2':
        return validate_context_v2(ctx,validate_context_v1)
    return validate_context_v1(ctx)


def load_context_bytes(raw):
    if len(raw)>16*1024*1024:raise ContextError('Context exceeds 16 MiB input limit')
    try:
        ctx=json.loads(raw.decode('utf-8-sig'),object_pairs_hook=reject_duplicate_pairs)
    except (ValueError,UnicodeError,RecursionError) as e:
        raise ContextError('Cannot decode context JSON: '+str(e)[:140]) from e
    return validate_context(ctx)


def project_v1(ctx):
    result=copy.deepcopy(ctx)
    result['format']='aiaeao.cube.binding-context/1'
    result.pop('instantiation_profiles',None)
    for r in result['referents']:
        r.pop('instantiation_profile_ref',None)
        r.pop('slots',None)
    return result


class P16Validator:
    def __init__(self):
        self.baseline=FrozenValidator()
        self.resolver=self.baseline.resolver

    def validate_bytes(self, raw, *, input_format='acg_text', context=None, qualification_profiles=None):
        if context is None or context.get('format')!='aiaeao.cube.binding-context/2':
            return self.baseline.validate_bytes(raw,input_format=input_format,
                                                context=context,qualification_profiles=qualification_profiles)
        validate_context_v2(context,validate_context_v1)
        projected=project_v1(context)
        report=self.baseline.validate_bytes(raw,input_format=input_format,context=projected,
                                           qualification_profiles=qualification_profiles)
        parsed=parse_result(raw,input_format=input_format)
        if parsed['structure_status']!='PASS':return report
        resolution=self.resolver.resolve_ast(parsed['ast'],projected)
        checker=InstantiationCheck(context)
        statuses=[];new=[];remove=set()
        byref={r['ref']:r for r in context['referents']}
        for b in resolution['bindings']:
            status=b['referent_binding']
            if (b.get('instantiation')=='requires_binding_profile' and
                b.get('concept_id','').startswith('X:endpoint:')):
                path=b['ast_path'];remove.add(path)
                r=byref.get(b['referent_ref'])
                if r is None:
                    status='UNRESOLVED'
                    new.append({'code':'P1_BINDING_CONTEXT_REQUIRED','stage':'referent_binding',
                                'severity':'unresolved','message':path+': X endpoint referent is not declared.',
                                'reference_rule':'P1.3 declared context referent required'})
                elif r['concept_id']!=b['concept_id'] or r['home']!=b['home'] or b['layer'] not in r['layers']:
                    status='FAIL'
                    new.append({'code':'P1_REFERENT_MISMATCH','stage':'referent_binding',
                                'severity':'error','message':path+': X endpoint concept/home/layer contradicts request.',
                                'reference_rule':'P1.3 exact identity consistency'})
                elif context.get('scope_ref') and r.get('scope_ref')!=context['scope_ref']:
                    status='FAIL' if r.get('scope_ref') else 'UNRESOLVED'
                    new.append({'code':'P1_SCOPE_CONFLICT' if r.get('scope_ref') else 'P1_BINDING_CONTEXT_REQUIRED',
                                'stage':'referent_binding','severity':'error' if r.get('scope_ref') else 'unresolved',
                                'message':path+': X endpoint declared scope does not match the validation scope.',
                                'reference_rule':'P1.4 scope consistency'})
                else:
                    status, ds=checker.run(b['referent_ref'],b['layer'])
                    for d in ds:
                        # P1.1 report schema is closed: carry JSON Pointer in message.
                        new.append({k:v for k,v in d.items() if k!='ast_path'} |
                                   {'message':d['ast_path']+': '+d['message']})
            statuses.append(status)
        if remove:
            # Remove only the frozen placeholder for X endpoints; retain the Z-zone
            # placeholder, other unresolved diagnostics and all parser/type checks.
            report['diagnostics']=[d for d in report['diagnostics'] if not (
                d['code']=='P1_INSTANTIATION_PROFILE_REQUIRED' and
                any(d['message'].startswith(path+': ') for path in remove))]
            report['diagnostics'].extend(new)
            report['checks']['referent_binding']=FrozenValidator._stage(statuses,'referent')
            report['diagnostics'].sort(key=lambda d:(d.get('byte_start',10**12),d['code'],
                  tuple(report['checks']).index(d['stage']) if d['stage'] in report['checks'] else 99,d['message']))
            report['overall_status']=join([x['status'] for x in report['checks'].values()])
            if report['overall_status']=='NOT_EVALUATED':report['overall_status']='UNRESOLVED'
        return report
