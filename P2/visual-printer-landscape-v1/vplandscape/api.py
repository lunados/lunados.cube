"""VP-12 in-memory API (JSON in, {panels, index, report} out), shaped like vpmigration.api; used by G6 `cube_plan_*`.

`views` takes the display options of the plan-view tools: granularity and locale replace the values the input carries
(both are display options of the input, §1.1); the steps and placement predicates stay as `source` wrote them.
"""
from __future__ import annotations
import copy

from .source import from_plan, validate_input
from .panels import print_panels, check_files


def source(context, plan_id, layers=None, labels=None, steps=None, placement_predicates=None, locale='en', granularity='detail',
           profile=None):
    doc, info = from_plan(context, plan_id, layers, labels, steps, placement_predicates, locale, granularity, profile)
    return {'format': 'aiaeao.cube.plan-source/1', 'printer': 'vplandscape', 'profile': doc['profile'], 'source': doc, 'mapping': info['mapping']}


def views(doc, granularity=None, locale=None):
    from vpmigration.api import to_result
    validate_input(doc)
    doc = copy.deepcopy(doc)
    if granularity is not None:
        doc['granularity'] = granularity
    if locale is not None:
        doc['locale'] = locale
    report, files = print_panels(doc)
    return to_result('vplandscape', 'cube.landscape', report, files)


def check(result):
    from vpmigration.api import to_files
    return check_files(to_files(result, 'VP12_PANEL_COVERAGE'))
