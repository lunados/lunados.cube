"""Additive P1.8 validator. Frozen P1.1-P1.5 and P1.6 executable files are NOT edited.

/1 and /2 delegate unconditionally to P1.6 (which delegates /1 to frozen P1.4).
/3 runs P1.6 on a lossless /2 projection and then adds only:
  * predicate typing for relations whose operand is a typed method application,
  * closed-scenario checks inside an explicit evaluation_frame,
  * evaluator / evaluation-record checks (EV-3a via the P1.6 instantiation check).
No method is executed, no digest/witness verified, no result scored.
"""
from __future__ import annotations
from cube_parser.parser import parse_result
from cube_resolver.resolver import validate_context as validate_context_v1
from cube_semantic.validator import SemanticValidator as FrozenValidator, join, nodes
from cube_p16.validator import P16Validator, validate_context as validate_context_v12
from cube_p16.instantiation import validate_context_v2, InstantiationCheck
from cube_p18.simulation import (FORMAT3, JUDGMENTS, DIGEST, project_v2, concept_table,
                                 validate_context_v3 as _validate_v3)

PROFILE = 'P1.8/simulation-profile-v1'
CODES = {
    'P1_METHOD_RETURN_UNDECLARED': ('predicate_typing','UNRESOLVED','P1.8 MR: application operand without declared return type'),
    'P1_METHOD_RETURN_TYPE': ('predicate_typing','FAIL','P1.8 MR-2: declared return type/cardinality not admitted by predicate side'),
    'P1_PREDICATE_SIGNATURE': ('predicate_typing','FAIL','Morphology §7.6.1 R01-AC02'),
    'P1_SCENARIO_REQUIRED': ('scope_consistency','UNRESOLVED','P1.8 SC: evaluation_frame names no declared scenario'),
    'P1_SCENARIO_WORLD_VIOLATION': ('scope_consistency','FAIL','P1.8 SC-1/EV-3: referent outside the closed scenario world'),
    'P1_SCENARIO_MODE': ('scope_consistency','FAIL','Morphology v9.4 §3.1 M / P1.8 SC-2, SC-3'),
    'P1_SCOPE_CONFLICT': ('scope_consistency','FAIL','P1.4 declared scope consistency'),
    'P1_EVALUATOR_UNDECLARED': ('referent_binding','UNRESOLVED','P1.8 EV-2: evaluator not declared for method'),
    'P1_EVALUATION_OUTPUT_TYPE': ('referent_binding','FAIL','Morphology v9.4 §6.2 / P1.8 EV-3, MR-4'),
    'P1_EVALUATION_WITNESS_MISSING': ('referent_binding','UNRESOLVED','P1.8 EV-4: declared witness pointer required'),
    'P1_EVALUATION_RECORD_INCONSISTENT': ('referent_binding','FAIL','P1.8 EV-5: digest format, scenario/method consistency'),
    'P1_BINDING_CONTEXT_REQUIRED': ('referent_binding','UNRESOLVED','P1.3 declared referent and exact binding'),
}
_REL_CODES = ('P1_PREDICATE_PROFILE_MISSING','P1_PREDICATE_SIGNATURE')


def _d(code, path, message):
    stage,status,rule=CODES[code]
    return {'code':code,'stage':stage,'severity':'error' if status=='FAIL' else 'unresolved',
            'message':f'{path or "/"}: {message}','reference_rule':rule}


def _status(code): return CODES[code][1]


def _unwrap(v):
    while v['kind']=='qualified': v=v['expression']
    return v


class P18Validator:
    def __init__(self):
        self.p16=P16Validator()
        self.baseline=self.p16.baseline
        self.resolver=self.baseline.resolver
        self.concepts=concept_table(self.resolver)

    # -- context -------------------------------------------------------
    def validate_context(self, ctx):
        if isinstance(ctx,dict) and ctx.get('format')==FORMAT3:
            return _validate_v3(ctx, validate_context_v2, validate_context_v1, self.concepts)
        return validate_context_v12(ctx)

    # -- helpers -------------------------------------------------------
    def _method(self, mid, ctx):
        scope=ctx.get('scope_ref')
        found=[m for m in ctx.get('method_contracts',[]) if m['method_id']==mid and scope and m['scope']==scope]
        return found[0] if len(found)==1 else None

    def _ref_concept(self, node):
        a=node['address']; e=self.resolver.exact.get((a['home'],a['concept_key']))
        if not e or e['instantiation']=='not_instantiable': return None
        return e['concept_id']

    def _relation(self, node, path, attached, ctx3, ctx2):
        """None -> keep frozen judgement; else (status, diagnostics)."""
        ops=[_unwrap(node['subject']),_unwrap(node['object'])]
        if not any(o['kind']=='application' for o in ops): return None
        if any(o['kind']=='relation' for o in ops): return None          # MR-5: nested rel stays untyped
        scope=ctx2.get('scope_ref')
        scoped=[p for p in ctx2['predicate_contracts'] if p['predicate_id']==node['predicate_id'] and scope and p['scope']==scope]
        if len(scoped)!=1: return None                                   # frozen PROFILE_MISSING stands
        p=scoped[0]
        sides=(p['subject_concept_ids'],p['object_concept_ids'])
        for o,allowed in zip(ops,sides):
            if o['kind']=='reference':
                cid=self._ref_concept(o)
                if cid is None: return None
                if cid not in allowed:
                    return 'FAIL',[_d('P1_PREDICATE_SIGNATURE',path,'Predicate '+repr(node['predicate_id'])+
                                      ' does not admit the directed (subject,object) concept IDs in this fixture scope.')]
                continue
            m=self._method(o['method_id'],ctx3)
            if m is None: return None                                    # frozen method typing reports it
            if 'return_concept_ids' not in m:
                return 'UNRESOLVED',[_d('P1_METHOD_RETURN_UNDECLARED',path,
                    'Application operand '+repr(o['method_id'])+' has no declared return type.')]
            if m['return_cardinality']!='one':
                return 'FAIL',[_d('P1_METHOD_RETURN_TYPE',path,'A relation operand requires return_cardinality one.')]
            if not set(m['return_concept_ids']).issubset(allowed):
                return 'FAIL',[_d('P1_METHOD_RETURN_TYPE',path,
                    'Declared return type of '+repr(o['method_id'])+' is not admitted by predicate '+repr(node['predicate_id'])+'.')]
        missing=set(p.get('required_qualifiers',[]))-{q['coordinate'] for _,q in attached}
        if missing:
            return 'FAIL',[_d('P1_PREDICATE_SIGNATURE',path,'Required predicate-level qualifier(s) absent: '+','.join(sorted(missing))+'.')]
        if node['parameters']:
            return None                                                  # frozen: no typed predicate parameters
        return 'PASS',[]

    # -- main ----------------------------------------------------------
    def validate_bytes(self, raw, *, input_format='acg_text', context=None, qualification_profiles=None):
        if context is None or context.get('format')!=FORMAT3:
            return self.p16.validate_bytes(raw,input_format=input_format,context=context,
                                           qualification_profiles=qualification_profiles)
        self.validate_context(context)
        ctx2=project_v2(context)
        report=self.p16.validate_bytes(raw,input_format=input_format,context=ctx2,
                                       qualification_profiles=qualification_profiles)
        parsed=parse_result(raw,input_format=input_format)
        if parsed['structure_status']!='PASS': return report
        ast=parsed['ast']
        diags=report['diagnostics']; checks=report['checks']
        add={'predicate_typing':[],'scope_consistency':[],'referent_binding':[]}

        # 1. Return typing (relation operands only).
        rel_status=[]; replaced=set(); new_rel=[]
        for path,node,attached in nodes(ast):
            if node['kind']!='relation': continue
            res=self._relation(node,path,attached,context,ctx2)
            if res is None:
                st,_=self.baseline._check_relation(node,path,attached,ctx2)
            else:
                st,ds=res; replaced.add(path or '/'); new_rel.extend(ds)
            rel_status.append(st)
        if replaced:
            diags[:]=[d for d in diags if not (d['code'] in _REL_CODES and
                       any(d['message'].startswith(p+': ') for p in replaced))]
            diags.extend(new_rel)
            checks['predicate_typing']=FrozenValidator._stage(rel_status,'predicate typing')

        refs={r['ref']:r for r in context['referents']}
        scen={s['scenario_id']:s for s in context.get('scenarios',[])}

        # 2. Closed scenario inside an explicit evaluation frame.
        frame=context.get('evaluation_frame')
        if frame:
            sc=scen.get(frame['scenario_ref'])
            if sc is None:
                add['scope_consistency'].append(('UNRESOLVED',_d('P1_SCENARIO_REQUIRED','/evaluation_frame/scenario_ref',
                    'No declared scenario '+repr(frame['scenario_ref'])+'.')))
            else:
                if sc['mode'] not in ('simulation','replay'):
                    add['scope_consistency'].append(('FAIL',_d('P1_SCENARIO_MODE','/evaluation_frame',
                        'Scenario mode '+repr(sc['mode'])+' is outside P1.8 (simulation/replay only).')))
                if context.get('scope_ref') and sc['scope']!=context['scope_ref']:
                    add['scope_consistency'].append(('FAIL',_d('P1_SCOPE_CONFLICT','/evaluation_frame',
                        'Scenario scope conflicts with the declared validation scope.')))
                world=set(sc['world_refs'])
                for path,node,_ in nodes(ast):
                    if node['kind']=='reference' and node['referent_ref'] not in world:
                        add['scope_consistency'].append(('FAIL',_d('P1_SCENARIO_WORLD_VIOLATION',path,
                            'Referent '+repr(node['referent_ref'])+' is not a member of scenario '+repr(sc['scenario_id'])+'.')))
                    elif node['kind']=='application':
                        if node['method_id'] not in sc['method_ids']:
                            add['scope_consistency'].append(('FAIL',_d('P1_SCENARIO_MODE',path,
                                'Method is not declared for this scenario.')))
                        m=self._method(node['method_id'],context)
                        if m is not None and m.get('effect_class')!='pure_declarative':
                            add['scope_consistency'].append(('FAIL',_d('P1_SCENARIO_MODE',path,
                                'Only pure_declarative methods may appear in a simulated scenario.')))

        # 3. Evaluators and evaluation records.
        evals={e['evaluator_id']:e for e in context.get('evaluators',[])}
        check=InstantiationCheck(ctx2)
        for i,r in enumerate(context.get('evaluation_records',[])):
            base=f'/evaluation_records/{i}'
            sc=scen.get(r['scenario_ref'])
            if sc is None:
                add['referent_binding'].append(('FAIL',_d('P1_EVALUATION_RECORD_INCONSISTENT',base+'/scenario_ref','Record names an undeclared scenario.')))
            elif r['method_id'] not in sc['method_ids']:
                add['referent_binding'].append(('FAIL',_d('P1_EVALUATION_RECORD_INCONSISTENT',base+'/method_id','Method is not declared for the record scenario.')))
            if DIGEST.fullmatch(r['input_digest']) is None:
                add['referent_binding'].append(('FAIL',_d('P1_EVALUATION_RECORD_INCONSISTENT',base+'/input_digest',
                    'input_digest must be sha256:<64 lowercase hex>; it is never recomputed.')))
            ev=evals.get(r['evaluator_ref'])
            if ev is None or r['method_id'] not in ev['method_ids']:
                add['referent_binding'].append(('UNRESOLVED',_d('P1_EVALUATOR_UNDECLARED',base+'/evaluator_ref',
                    'No evaluator declared for this method.')))
            if not r.get('witness_ref'):
                add['referent_binding'].append(('UNRESOLVED',_d('P1_EVALUATION_WITNESS_MISSING',base+'/witness_ref',
                    'Evaluation record requires a declared witness pointer (witness truth NOT_EVALUATED).')))
            for j,out in enumerate(r['output_refs']):
                op=f'{base}/output_refs/{j}'
                t=refs.get(out)
                if t is None:
                    add['referent_binding'].append(('UNRESOLVED',_d('P1_BINDING_CONTEXT_REQUIRED',op,'Output is not a declared referent.')))
                    continue
                if sc is not None and out not in sc['world_refs']:
                    add['scope_consistency'].append(('FAIL',_d('P1_SCENARIO_WORLD_VIOLATION',op,'Output is not a scenario world member.')))
                cid=t['concept_id']
                if cid in JUDGMENTS:
                    add['referent_binding'].append(('FAIL',_d('P1_EVALUATION_OUTPUT_TYPE',op,'An evaluation never outputs an X judgment endpoint.')))
                    continue
                if ev is not None and cid not in ev['output_concept_ids']:
                    add['referent_binding'].append(('FAIL',_d('P1_EVALUATION_OUTPUT_TYPE',op,'Output concept is not declared for this evaluator.')))
                    continue
                if cid.startswith('X:endpoint:'):                      # EV-3a: P1.6-instantiated output
                    st,ds=check.run(out,t['layers'][0])
                    add['referent_binding'].append((st,None))
                    for d in ds:
                        add['referent_binding'].append((st,{k:v for k,v in d.items() if k!='ast_path'}|
                                                        {'message':d['ast_path']+': '+d['message']}))
                    act=(t.get('slots') or {}).get('action_ref')
                    if sc is not None and isinstance(act,str) and act not in sc['world_refs']:
                        add['scope_consistency'].append(('FAIL',_d('P1_SCENARIO_WORLD_VIOLATION',op,'Evaluation-run Action is not a world member.')))

        for stage,items in add.items():
            if not items: continue
            sts=[checks[stage]['status']] if checks[stage]['status']!='NOT_EVALUATED' else []
            sts+=[s for s,_ in items]
            diags.extend(d for _,d in items if d is not None)
            label={'predicate_typing':'predicate typing','scope_consistency':'scope','referent_binding':'referent'}[stage]
            checks[stage]=FrozenValidator._stage(sts,label)
        order=list(checks)
        diags.sort(key=lambda d:(d.get('byte_start',10**12),d['code'],
                   order.index(d['stage']) if d['stage'] in order else 99,d['message']))
        report['overall_status']=join([x['status'] for x in checks.values()])
        if report['overall_status']=='NOT_EVALUATED': report['overall_status']='UNRESOLVED'
        return report


def validate_context(ctx):
    return P18Validator().validate_context(ctx)
