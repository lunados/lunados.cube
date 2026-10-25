#!/usr/bin/env python3
"""Single-command P1.6 local oracle runner; exit 0 PASS,1 UNRESOLVED,2 FAIL,3 config."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'semantic-validator-v1'))
sys.path.insert(0,str(ROOT/'instantiation-profile-v1'))
from cube_p16.validator import P16Validator,load_context_bytes
from cube_p16.instantiation import InstantiationError
from cube_resolver.resolver import ContextError,ContractError
from cube_semantic.validator import load_qualification_profiles_bytes,ProfileError
from cube_parser.parser import json_dump

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--input','-i',required=True)
    a.add_argument('--context')
    a.add_argument('--input-format',choices=['acg_text','json_ast'],default='acg_text')
    a.add_argument('--qualification-profiles')
    args=a.parse_args()
    try:
        raw=sys.stdin.buffer.read(1_048_577) if args.input=='-' else Path(args.input).read_bytes()
        ctx=load_context_bytes(Path(args.context).read_bytes()) if args.context else None
        qp=load_qualification_profiles_bytes(Path(args.qualification_profiles).read_bytes()) if args.qualification_profiles else None
        r=P16Validator().validate_bytes(raw,input_format=args.input_format,context=ctx,qualification_profiles=qp)
    except (ContextError,ContractError,ProfileError,InstantiationError,ValueError,OSError) as e:
        print(json.dumps({'format':'aiaeao.cube.semantic-input-error/1','message':str(e),'semantic_status':'NOT_EVALUATED'}),file=sys.stderr)
        return 3
    print(json_dump(r))
    return {'PASS':0,'UNRESOLVED':1,'FAIL':2}[r['overall_status']]
if __name__=='__main__':raise SystemExit(main())
