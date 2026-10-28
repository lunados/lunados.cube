"""G6 MA-1…MA-3: in-memory API of VP-08. VP-08 sources are declared directly (no from-plan, G6 D-7)."""
from __future__ import annotations

from vpmigration.api import to_result, to_files
from .common import VP08Error
from .panels import print_panels, check_files


def views(source, view='cube.sequence', granularity='standard', partition='trigger', overflow='summarize'):
    report, files = print_panels(source, partition, granularity, overflow)
    return to_result('vpsequence', view, report, files, 'VP08_PANEL_COVERAGE')


def check(result):
    return check_files(to_files(result, 'VP08_PANEL_COVERAGE', VP08Error))
