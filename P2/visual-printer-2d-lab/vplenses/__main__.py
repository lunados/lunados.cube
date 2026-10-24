"""python -m vplenses --input bundle.json --lens cube.lens.semantics --output out.svg --report out.json"""
import argparse
import json
from pathlib import Path
from vpviews.__main__ import strict_load
from .printer import LensPrinter, LensError, PROFILES

def main():
    cli=argparse.ArgumentParser(description='VP-03 deterministic AIAEAO lens renderer; never a runtime authority')
    cli.add_argument('--input',required=True)
    cli.add_argument('--lens',required=True,choices=PROFILES)
    cli.add_argument('--output',required=True)
    cli.add_argument('--report')
    args=cli.parse_args()
    try:
        bundle=strict_load(args.input)
        renderer=LensPrinter()
        svg=renderer.render(bundle,args.lens)
        report=renderer.report(bundle,args.lens,svg)
        output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(svg)
        if args.report:
            path=Path(args.report);path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n','utf8')
        print('PASS VP-03',args.lens,'for',bundle['view_plan']['view'],'· sha256',report['svg_sha256'])
    except (LensError,ValueError,KeyError,OSError) as e:
        cli.exit(2,'FAIL VP-03: '+str(e)+'\n')

if __name__=='__main__':main()
