"""CLI: python3 -m vpconformance --input vp04.json --output report.json [--svg out.svg]."""
import argparse
import json
import sys
from pathlib import Path
from .conformance import ConformanceAuditor,ConformanceError

# Input JSON duplicate keys are rejected (unlike Python's default last-key-wins).
def load(path):
    def hook(items):
        out={}
        for k,v in items:
            if k in out:raise ConformanceError('duplicate JSON key: '+k)
            out[k]=v
        return out
    return json.loads(Path(path).read_text('utf-8'),object_pairs_hook=hook)

def main():
    cli=argparse.ArgumentParser(description='AIAEAO VP05 deterministic combinatorial conformance audit')
    cli.add_argument('--input',required=True);cli.add_argument('--output',required=True);cli.add_argument('--svg')
    args=cli.parse_args()
    try:
        r,svg,_=ConformanceAuditor().audit(load(args.input),include_svg=True)
        # All evaluation completes before any output is written.
        p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+'\n','utf-8')
        if args.svg:
            s=Path(args.svg);s.parent.mkdir(parents=True,exist_ok=True);s.write_bytes(svg)
        print('PASS VP05',r['dimensions'],r['decision']['action'],r['split_feasibility']['status'])
    except (ConformanceError,ValueError,KeyError,TypeError,OSError) as e:
        print('FAIL VP05:',str(e),file=sys.stderr)
        raise SystemExit(2)
if __name__=='__main__':main()
