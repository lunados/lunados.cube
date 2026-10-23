"""Offline P1.3 CLI: resolvable concept instances under declared, untrusted context."""
import argparse
import json
from pathlib import Path
import sys
from cube_parser.parser import json_dump
from .resolver import Resolver, load_context_bytes, ContextError, ContractError

def main(argv=None):
    p=argparse.ArgumentParser(description='P1.3 v9.4 reference resolver (no predicate semantics or authority)')
    p.add_argument('--input','-i',required=True,help='ACG/JSON file or - for stdin')
    p.add_argument('--input-format',choices=['acg_text','json_ast'],default='acg_text')
    p.add_argument('--context',help='P1.1 binding-context/1 JSON; optional')
    args=p.parse_args(argv)
    try:
        if args.input=='-': raw=sys.stdin.buffer.read(1048577)
        else:
            with Path(args.input).open('rb') as f: raw=f.read(1048577)
        context=load_context_bytes(Path(args.context).read_bytes()) if args.context else None
        result=Resolver().resolve_bytes(raw,input_format=args.input_format,context=context)
    except (ContextError, ContractError, OSError, ValueError) as e:
        print(json.dumps({'format':'aiaeao.cube.resolver-input-error/1','message':str(e),'semantic_status':'NOT_EVALUATED'}),file=sys.stderr)
        return 3
    print(json_dump(result))
    return 0 if result['resolution_status']=='PASS' else 2 if result['resolution_status']=='FAIL' else 1
if __name__=='__main__': raise SystemExit(main())
