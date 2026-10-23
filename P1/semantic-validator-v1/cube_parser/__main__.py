"""CLI interface for P1.2 parser, executed with python -m cube_parser."""
import argparse
import sys
from pathlib import Path
from .parser import parse_result, json_dump, canonical_acg


def main(argv=None) -> int:
    cli = argparse.ArgumentParser(prog='python -m cube_parser', description='P1.2 ACG parser / structural AST checker (not semantic validator)')
    cli.add_argument('--input', '-i', required=True, help='Input file path; use - for stdin')
    cli.add_argument('--input-format', choices=['acg_text', 'json_ast'], default='acg_text')
    cli.add_argument('--emit', choices=['result','ast','acg'], default='result')
    args = cli.parse_args(argv)
    try:
        if args.input == '-':
            raw = sys.stdin.buffer.read(1_048_577)
        else:
            with Path(args.input).open('rb') as file:
                raw = file.read(1_048_577)
    except OSError as e:
        print('I/O error: '+str(e), file=sys.stderr)
        return 3
    result = parse_result(raw, input_format=args.input_format)
    if result['diagnostics']:
        print(json_dump({k:v for k,v in result.items() if k!='ast'})+'\n')
        return 2
    try:
        if args.emit == 'ast':
            print(json_dump(result['ast']))
        elif args.emit == 'acg':
            print(canonical_acg(result['ast']))
        else:
            print(json_dump(result))
    except ValueError as e:
        print('Canonical ACG serialization unavailable: '+str(e), file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
