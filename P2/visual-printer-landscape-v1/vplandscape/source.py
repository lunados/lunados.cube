"""VP-12 §1.1: landscape input from the unchanged VP-07.8 source path (origin lines on, optional VP-07.2 layer map)."""
from __future__ import annotations
import copy

from .common import (PROFILE, SOURCE_PROFILE, INPUT_FORMAT, LEVELS, LOCALES, PLACEMENT_DEFAULT, clean, need, sha_json)

KEYS = ('format', 'profile', 'source', 'concepts', 'steps', 'placement_predicates', 'locale', 'granularity')


def from_plan(context, plan_id, layers=None, labels=None, steps=None, placement_predicates=None, locale='en', granularity='detail'):
    from vpmigration.api import source as vp07_source
    doc = vp07_source(context, plan_id, labels=labels, profile=SOURCE_PROFILE, layers=layers, origin_lines=True)
    src, mapping = doc['source'], doc['mapping']
    pids = [s['id'] for s in src['steps']]
    out = {'format': INPUT_FORMAT, 'profile': PROFILE, 'source': src,
           'concepts': {r['id']: r['concept_id'] for r in mapping['referents']},
           'steps': list(steps) if steps is not None else [pids[0], pids[-1]] if len(pids) > 1 else pids[:1],
           'placement_predicates': list(PLACEMENT_DEFAULT if placement_predicates is None else placement_predicates),
           'locale': locale, 'granularity': granularity}
    validate_input(out)
    return out, {'source_context_sha256': src['source_context_sha256'], 'layer_map_sha256': sha_json(layers) if layers is not None else None,
                 'mapping': mapping}


def validate_input(doc):
    from vpmigration.source import validate_source
    need(isinstance(doc, dict) and doc.get('format') == INPUT_FORMAT, 'VP12_INPUT', 'input is not an '+INPUT_FORMAT+' document')
    need(set(doc) == set(KEYS), 'VP12_INPUT', 'landscape input fields must be exactly '+', '.join(KEYS))
    need(doc['profile'] == PROFILE, 'VP12_INPUT', 'profile must be '+PROFILE)
    src = doc['source']
    need(isinstance(src, dict) and src.get('profile') == SOURCE_PROFILE and src.get('origin_lines') is True
         and src.get('source_kind') == 'migration_plan', 'VP12_INPUT',
         'source must be a '+SOURCE_PROFILE+' migration-plan source with origin lines (§1.1)')
    validate_source(copy.deepcopy(src))
    need(isinstance(doc['concepts'], dict) and all(clean(k, 100) and clean(v, 100) for k, v in doc['concepts'].items()),
         'VP12_INPUT', 'concepts must map display IDs to concept IDs')
    st = doc['steps']
    need(isinstance(st, list) and st and all(isinstance(s, str) for s in st) and len(set(st)) == len(st), 'VP12_INPUT',
         'steps must be a non-empty list of distinct step IDs (§1.5)')
    pids = [s['id'] for s in src['steps']]
    unknown = [s for s in st if s not in pids]
    need(not unknown, 'VP12_STEP_UNKNOWN', 'step(s) not declared in the plan: '+', '.join(unknown))
    pp = doc['placement_predicates']
    need(isinstance(pp, list) and all(clean(p, 60) for p in pp) and len(set(pp)) == len(pp), 'VP12_INPUT',
         'placement_predicates must be distinct predicate IDs')
    need(doc['locale'] in LOCALES, 'VP12_INPUT', 'locale must be one of '+', '.join(LOCALES))
    need(doc['granularity'] in LEVELS, 'VP12_INPUT', 'granularity must be one of '+', '.join(LEVELS))
    led = {e['cell_id'] for e in src['origin_ledger']}
    need(led == {c['id'] for c in src['cells']}, 'VP12_INPUT', 'origin ledger does not cover the cells')
    return doc
