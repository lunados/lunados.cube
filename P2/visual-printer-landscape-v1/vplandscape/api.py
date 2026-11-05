"""VP-12 in-memory API (JSON in, {panels, index, report} out), shaped like vpmigration.api for a later G6 registration."""
from __future__ import annotations

from .source import from_plan
from .panels import print_panels, check_files


def source(context, plan_id, layers=None, labels=None, steps=None, placement_predicates=None, locale='en', granularity='detail'):
    doc, info = from_plan(context, plan_id, layers, labels, steps, placement_predicates, locale, granularity)
    return {'format': 'aiaeao.cube.plan-source/1', 'printer': 'vplandscape', 'profile': doc['profile'], 'source': doc, 'mapping': info['mapping']}


def views(doc):
    from vpmigration.api import to_result
    report, files = print_panels(doc)
    return to_result('vplandscape', 'cube.landscape', report, files)


def check(result):
    from vpmigration.api import to_files
    return check_files(to_files(result, 'VP12_PANEL_COVERAGE'))
