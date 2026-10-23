"""P1.4 offline semantic CLI. Exit 0=PASS; 1=UNRESOLVED; 2=FAIL; 3=input/config error."""
import argparse,json,sys
from pathlib import Path
from cube_parser.parser import json_dump
from cube_resolver.resolver import load_context_bytes, ContextError, ContractError
from .validator import SemanticValidator,load_qualification_profiles_bytes,ProfileError

def main(argv=None):
    p=argparse.ArgumentParser(description='Pure Cube P1.4 descriptive semantic validator (offline; no effects)')
    p.add_argument('--input','-i',required=True,help='ACG or JSON AST filepath, or -')
    p.add_argument('--input-format',choices=['acg_text','json_ast'],default='acg_text')
    p.add_argument('--context',help='Optional P1.1 binding-context/1')
    p.add_argument('--qualification-profiles',help='Optional fixture-scoped P1.4 qualification-profiles/1')
    a=p.parse_args(argv)
    try:
        if a.input=='-':raw=sys.stdin.buffer.read(1_048_577)
        else:
            with Path(a.input).open('rb') as f:raw=f.read(1_048_577)
        ctx=load_context_bytes(Path(a.context).read_bytes()) if a.context else None
        qp=load_qualification_profiles_bytes(Path(a.qualification_profiles).read_bytes()) if a.qualification_profiles else None
        result=SemanticValidator().validate_bytes(raw,input_format=a.input_format,context=ctx,qualification_profiles=qp)
    except (ContextError,ContractError,ProfileError,OSError,ValueError) as e:
        print(json.dumps({'format':'aiaeao.cube.semantic-input-error/1','message':str(e),'semantic_status':'NOT_EVALUATED'}),file=sys.stderr)
        return 3
    print(json_dump(result))
    return {'PASS':0,'UNRESOLVED':1,'FAIL':2}[result['overall_status']]

if __name__=='__main__':raise SystemExit(main())
