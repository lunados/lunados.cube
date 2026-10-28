"""G6 test helper: run the unchanged P2 CLIs (subprocess, temp folders) as the parity reference (D-10).

Only tests use this module; the MCP tools never touch files.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PKG = {'vpmigration': ROOT/'P2/visual-printer-migration-v1', 'vpsequence': ROOT/'P2/visual-printer-sequence-v1',
       'vpaxes': ROOT/'P2/visual-printer-axes-v1'}


class CliError(Exception):
    def __init__(self, code, raw):
        super().__init__(code)
        self.code, self.raw = code, raw


def run(printer, *args):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    p = subprocess.run([sys.executable, '-B', '-m', printer, *map(str, args)], cwd=PKG[printer], env=env, capture_output=True)
    if p.returncode:
        try:
            code = json.loads(p.stderr)['code']
        except (ValueError, KeyError):
            code = 'CLI_EXIT_'+str(p.returncode)
        raise CliError(code, p.stderr)
    return p.stdout


def _write(tmp, name, obj):
    f = Path(tmp)/name
    f.write_text(json.dumps(obj, ensure_ascii=False), 'utf-8')
    return f


def from_plan(printer, context, plan_id, **opt):
    """CLI from-plan → (source bytes, mapping bytes or None)."""
    with tempfile.TemporaryDirectory() as tmp:
        args = ['from-plan', '--context', _write(tmp, 'ctx.json', context), '--plan', plan_id, '--out', Path(tmp)/'out.json']
        for k, flag in (('tracks', '--tracks'), ('labels', '--labels'), ('layers', '--layers'), ('edge_styles', '--edge-styles'),
                        ('witness_prefixes', '--witness-prefixes')):
            if opt.get(k) is not None:
                args += [flag, _write(tmp, k+'.json', opt[k])]
        for k, flag in (('track', '--track'), ('steps', '--steps'), ('profile', '--profile')):
            if opt.get(k) is not None:
                args += [flag, opt[k]]
        if opt.get('subjects') is not None:
            args += ['--subjects', ','.join(opt['subjects'])]
        run(printer, *args)
        m = Path(tmp)/'out.mapping.json'
        return (Path(tmp)/'out.json').read_bytes(), (m.read_bytes() if m.exists() else None)


def print_panels(printer, source, view=None, partition=None, granularity='standard', lens=None, rows=None, cols=None, overflow=None,
                 locale=None, hide_ledger=False, hide_empty=None):
    """CLI print-panels → {file name: bytes}."""
    with tempfile.TemporaryDirectory() as tmp:
        src, out = _write(tmp, 'src.json', source), Path(tmp)/'p'
        if printer == 'vpmigration':
            args = ['print-panels', '--source', src, '--view', view, '--partition', partition, '--granularity', granularity, '--out', out]
            if lens:
                args = args[:-2]+['--lens', lens]+args[-2:]
            if hide_ledger:
                args = args[:-2]+['--hide-ledger']+args[-2:]
        elif printer == 'vpsequence':
            args = ['print-panels', '--source', src, '--partition', partition or 'trigger', '--granularity', granularity,
                    '--overflow', overflow or 'summarize', '--out', out]
        else:
            args = ['print-panels', '--input', src, '--rows', rows, '--cols', cols, '--granularity', granularity, '--out', out]
            if hide_empty:
                args = args[:-2]+['--hide-empty', hide_empty]+args[-2:]
        if locale and printer != 'vpsequence':
            args = args[:-2]+['--locale', locale]+args[-2:]
        run(printer, *args)
        return {f.name: f.read_bytes() for f in out.iterdir()}


def check_panels(printer, files):
    """CLI check-panels on a folder holding `files` → stdout bytes."""
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)/'p'
        d.mkdir()
        for n, b in files.items():
            (d/n).write_bytes(b)
        return run(printer, 'check-panels', '--dir', d)
