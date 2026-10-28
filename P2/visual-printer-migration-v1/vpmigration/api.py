"""G6 MA-1…MA-3: in-memory API of VP-07 (JSON in, {panels, index, report} out; no paths, no side effects).

`views` returns exactly the files `print-panels` writes; `check` rebuilds them and applies the unchanged
checks of `check-panels`. Shared helpers `to_result` / `to_files` are used by VP-08 and VP-09 as well.
"""
from __future__ import annotations
import json

from .common import VP07Error, need, encode, sha_bytes
from .adapter import from_plan
from .panels import print_panels, check_files

RESULT_FORMAT = 'aiaeao.cube.plan-views/1'
SOURCE_FORMAT = 'aiaeao.cube.plan-source/1'


def to_result(printer, view, report, files, code='VP07_PANEL_COVERAGE'):
    """(report, files) of print-panels → result object; every file is carried with its SHA-256 (MA-1)."""
    names = [e['panel'] for e in report['panel_ledger']]
    want = {n+x for n in names for x in ('.svg', '.input.json')} | {'index.svg', 'report.json'}
    need(set(files) == want, code, 'print-panels files differ from the panel ledger', 'coverage')
    panels = [{'name': n, 'svg': files[n+'.svg'].decode('utf-8'), 'sha256': sha_bytes(files[n+'.svg']),
               'input': json.loads(files[n+'.input.json']), 'input_sha256': sha_bytes(files[n+'.input.json'])} for n in names]
    rep = json.loads(files['report.json'])
    return {'format': RESULT_FORMAT, 'printer': printer, 'profile': rep.get('profile'), 'view': view, 'panels': panels,
            'index': {'svg': files['index.svg'].decode('utf-8'), 'sha256': sha_bytes(files['index.svg'])}, 'report': rep}


def to_files(result, code='VP07_PANEL_COVERAGE', error=VP07Error):
    """Result object → the files mapping print-panels wrote (MA-2); shape errors are coverage errors."""
    try:
        need(isinstance(result, dict) and result.get('format') == RESULT_FORMAT, code, 'not a plan-views result', 'coverage')
        files = {}
        for p in result['panels']:
            files[p['name']+'.svg'] = p['svg'].encode('utf-8')
            files[p['name']+'.input.json'] = encode(p['input'])
        files['index.svg'] = result['index']['svg'].encode('utf-8')
        files['report.json'] = encode(result['report'])
        need(len(files) == 2*len(result['panels'])+2, code, 'duplicate panel names', 'coverage')
        return files
    except (KeyError, TypeError, AttributeError) as e:
        raise error(code, 'plan-views result is malformed: '+type(e).__name__, 'coverage') from e
    except VP07Error as e:
        raise error(code, str(e), 'coverage') from e


def source(context, plan_id, tracks=None, track=None, labels=None, steps=None, subjects=None, edge_styles=None,
           witness_prefixes=None, profile=None, layers=None):
    src, mapping = from_plan(context, plan_id, tracks, track, labels, steps, subjects, edge_styles, witness_prefixes,
                             profile=profile, layers=layers)
    return {'format': SOURCE_FORMAT, 'printer': 'vpmigration', 'profile': src['profile'], 'source': src, 'mapping': mapping}


def views(source, view, granularity, partition, lens=None, locale=None, hide_ledger=False):
    """VP-07.5 options are passed only when set, so 0.7.0…0.7.4 calls stay the unchanged call."""
    opts = {k: v for k, v in (('locale', locale), ('hide_ledger', hide_ledger)) if v}
    report, files = print_panels(source, view, partition, granularity, lens, **opts)
    return to_result('vpmigration', view, report, files)


def check(result):
    return check_files(to_files(result))
