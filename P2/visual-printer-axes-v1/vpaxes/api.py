"""G6 MA-1…MA-3: in-memory API of VP-09 (axes input via from-plan; panels; check)."""
from __future__ import annotations

from vpmigration.api import to_result, to_files, SOURCE_FORMAT
from .common import VP09Error, via07
from .source import from_plan
from .panels import print_panels, check_files


def source(context, plan_id, tracks=None, track=None, labels=None, steps=None, subjects=None, layers=None, profile=None):
    doc, mapping = from_plan(context, plan_id, tracks, track, labels, steps, subjects, layers, profile=profile)
    return {'format': SOURCE_FORMAT, 'printer': 'vpaxes', 'profile': doc.get('profile'), 'source': doc, 'mapping': mapping}


def views(source, view='cube.axes', granularity='standard', rows=None, cols=None):
    report, files = print_panels(source, rows, cols, granularity)
    return via07(to_result, 'vpaxes', view, report, files, 'VP07_PANEL_COVERAGE', code='VP09_PANEL_COVERAGE')


def check(result):
    return check_files(to_files(result, 'VP09_PANEL_COVERAGE', VP09Error))
