"""VP-06: small, stateless facade for the unchanged VP-05 / VP-04 engines.

Print jobs describe presentation of declared, unverified data; no P1 verdict,
no authorization, no network, no editor and no multi-panel materialization.
"""
from __future__ import annotations
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
VP05=HERE.parent/'visual-printer-conformance-v1'
VP04=HERE.parent/'visual-printer-granularity-v1'
if not (VP05.is_dir() and VP04.is_dir()):
    raise RuntimeError('VP-05 and VP-04 frozen release components are required')
if str(VP05) not in sys.path:sys.path.insert(0,str(VP05))
if str(VP04) not in sys.path:sys.path.insert(0,str(VP04))
from vpconformance import ConformanceAuditor,ConformanceError
from vpconformance.conformance import LENSES,VIEWS,LEVELS
from vpgranularity import GranularityPrinter,GranularityError,CAPS
from vpgranularity.printer import sha

PROFILE='P2-VP/1.0.0-rc1'
FORMAT='aiaeao.cube.vp06-print-result/1'
ERROR_FORMAT='aiaeao.cube.vp06-diagnostic/1'
MAX_INPUT_BYTES=2*1024*1024

class PrintError(ValueError):
    def __init__(self,code,message,stage='input'):
        super().__init__(message);self.code=code;self.stage=stage
    def diagnostic(self):
        return {'format':ERROR_FORMAT,'profile':PROFILE,'status':'FAIL','code':self.code,
                'stage':self.stage,'message':str(self),'files_written':False,
                'epistemic_warrant':'NOT_EVALUATED','current_authority':'NOT_EVALUATED',
                'canonical_admission':'NOT_EVALUATED'}

def encode(obj):
    return (json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')

def load_json(path):
    path=Path(path)
    try:
        if path.stat().st_size>MAX_INPUT_BYTES:
            raise PrintError('VP06_INPUT_TOO_LARGE','input exceeds 2 MiB','input')
        raw=path.read_bytes().decode('utf-8')
    except PrintError:raise
    except (OSError,UnicodeError) as e:raise PrintError('VP06_INPUT_UNREADABLE',str(e),'input') from e
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise PrintError('VP06_DUPLICATE_KEY','duplicate JSON key: '+k,'input')
            d[k]=v
        return d
    try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda v:(_ for _ in ()).throw(PrintError('VP06_INVALID_JSON','nonfinite number: '+v,'input')))
    except PrintError:raise
    except (ValueError,TypeError) as e:raise PrintError('VP06_INVALID_JSON',str(e),'input') from e

def classify(error):
    msg=str(error)
    low=msg.lower()
    if 'source checksum mismatch' in low or 'sha256' in low and 'lock' in low:
        return PrintError('VP06_SOURCE_DIGEST_MISMATCH',msg,'provenance')
    if 'selected lens has no explicit facet bindings' in low:
        return PrintError('VP06_LENS_NOT_DECLARED',msg,'lens')
    if 'unknown or unauthorized lens' in low:
        return PrintError('VP06_LENS_UNKNOWN',msg,'lens')
    if 'focus ancestry exceeds' in low or 'ancestor-closed subset' in low:
        return PrintError('VP06_FOCUS_BUDGET',msg,'granularity')
    if 'budget' in low or 'overflow=reject' in low:
        return PrintError('VP06_BUDGET_INCOMPATIBLE',msg,'granularity')
    if 'requested view differs' in low or 'wrong vp-04 format' in low or 'unknown view' in low:
        return PrintError('VP06_VIEW_INCOMPATIBLE',msg,'view')
    if 'no declared connected subset' in low or 'cannot fabricate' in low:
        return PrintError('VP06_PROJECTION_UNREPRESENTABLE',msg,'projection')
    return PrintError('VP06_REQUEST_REJECTED',msg,'projection')

def capabilities():
    return {'format':'aiaeao.cube.vp06-capabilities/1','profile':PROFILE,
            'reference_version':'v9.4',
            'views':list(VIEWS),'lenses':list(LENSES),'granularities':list(LEVELS),
            'budgets':{level:{view:{'max_items':a,'max_edges':b} for view,(a,b) in vv.items()} for level,vv in CAPS.items()},
            'operations':['prepare','check','print','capabilities'],
            'source_input':'aiaeao.cube.vp03-lens-bundle/1',
            'print_job_input':'aiaeao.cube.vp04-projection-request/1',
            'output':'SVG + JSON report (local filesystem only)',
            'transport':'local_cli_only','network_api':False,'auto_multisvg':False,'3d':False,
            'p1_validation_included':False,
            'projection_semantics':'declared_unverified_display_only'}

def make_job(bundle,lens,granularity,overflow='summarize',focus=None,max_items=None,max_edges=None):
    if type(bundle) is not dict or type(bundle.get('view_plan')) is not dict:
        raise PrintError('VP06_SOURCE_INVALID','VP-03 bundle with view_plan required','input')
    view=bundle['view_plan'].get('view')
    if view not in VIEWS:raise PrintError('VP06_VIEW_INCOMPATIBLE','unknown cube view: '+str(view),'view')
    if lens not in LENSES:raise PrintError('VP06_LENS_UNKNOWN','unsupported lens: '+str(lens),'lens')
    if granularity not in LEVELS:raise PrintError('VP06_LEVEL_UNKNOWN','unsupported granularity: '+str(granularity),'granularity')
    if overflow not in ('summarize','reject'):raise PrintError('VP06_OVERFLOW_UNKNOWN','unsupported overflow mode','granularity')
    limits=CAPS[granularity][view]
    job={'format':'aiaeao.cube.vp04-projection-request/1','profile':'P2-VP-GRANULARITY/0.4.0',
         'reference_version':'v9.4','source_bundle':copy.deepcopy(bundle),'source_bundle_sha256':sha(bundle),
         'projection':{'view':view,'lens':lens,'granularity':granularity,'focus':focus,'overflow':overflow,
                       'budget':{'max_items':limits[0] if max_items is None else max_items,
                                 'max_edges':limits[1] if max_edges is None else max_edges}}}
    try:GranularityPrinter().validate(job)
    except (GranularityError,KeyError,TypeError,ValueError) as e:raise classify(e) from e
    return job

def render_job(job):
    if type(job) is not dict:raise PrintError('VP06_INPUT_INVALID','print job must be JSON object','input')
    try:audit,svg,raw_vp04=ConformanceAuditor().audit(job,include_svg=True)
    except (ConformanceError,GranularityError,KeyError,ValueError,TypeError) as e:raise classify(e) from e
    request_sha=hashlib.sha256(encode(job)).hexdigest()
    result={'format':FORMAT,'profile':PROFILE,'status':'PASS','reference_version':'v9.4',
            'request_sha256':request_sha,'source_bundle_sha256':audit['source_bundle_sha256'],
            'svg_sha256':hashlib.sha256(svg).hexdigest(),
            'dimensions':audit['dimensions'],'completeness':audit['completeness'],
            'decision':audit['decision'],
            'loss_ledger':{'displayed_item_ids':audit['displayed_item_ids'],
                           'omitted_item_ids':audit['omitted_item_ids'],
                           'displayed_source_edge_ids':audit['displayed_source_edge_ids'],
                           'omitted_source_edge_ids':audit['omitted_source_edge_ids'],
                           'displayed_lens_declarations':audit['displayed_lens_declarations'],
                           'omitted_lens_declarations':audit['omitted_lens_declarations']},
            'split_feasibility':audit['split_feasibility'],
            'conformance':audit,
            'epistemic_warrant':'NOT_EVALUATED','current_authority':'NOT_EVALUATED',
            'canonical_admission':'NOT_EVALUATED',
            'limitations':['The source and facet declarations are unverified',
                           'P1 semantic conformance is not evaluated',
                           'Font availability varies by rendering environment',
                           'Split feasibility is not an automatic multi-SVG export']}
    assert result['svg_sha256']==audit['svg_sha256']
    return result,svg

def persist_job(job,output):
    """Exclusive JSON file; never replace an existing job."""
    path=Path(output)
    try:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as f:f.write(encode(job))
    except FileExistsError as e:raise PrintError('VP06_OUTPUT_EXISTS','output already exists: '+str(path),'output') from e
    except OSError as e:raise PrintError('VP06_OUTPUT_IO',str(e),'output') from e

def persist_print(result,svg,output_dir,input_path=None):
    """Stage both outputs in the same parent, publish as ONE directory rename."""
    out=Path(output_dir).expanduser().absolute()
    if input_path and Path(input_path).resolve()==out:
        raise PrintError('VP06_OUTPUT_COLLISION','input and output are the same path','output')
    if out.exists():raise PrintError('VP06_OUTPUT_EXISTS','output directory already exists: '+str(out),'output')
    stage=None
    try:
        out.parent.mkdir(parents=True,exist_ok=True)
        stage=Path(tempfile.mkdtemp(prefix='.vp06-stage-',dir=out.parent))
        (stage/'render.svg').write_bytes(svg)
        (stage/'report.json').write_bytes(encode(result))
        if out.exists():raise PrintError('VP06_OUTPUT_EXISTS','output directory appeared while staging','output')
        os.rename(stage,out)
        stage=None
    except PrintError:raise
    except OSError as e:raise PrintError('VP06_OUTPUT_IO',str(e),'output') from e
    finally:
        if stage is not None and stage.exists():
            import shutil
            shutil.rmtree(stage)
    return out
