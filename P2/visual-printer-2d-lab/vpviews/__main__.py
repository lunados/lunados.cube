"""Run with python3 -m vpviews --input ... --output ... [--report ...]."""
import argparse
import json
from pathlib import Path
from .printer import ViewPrinter,ViewError


def strict_load(path):
    def pairs(seq):
        o={}
        for k,v in seq:
            if k in o:raise ViewError('duplicate JSON property: '+k)
            o[k]=v
        return o
    return json.loads(Path(path).read_text('utf-8'),object_pairs_hook=pairs,
                      parse_constant=lambda c: (_ for _ in ()).throw(ViewError('non-finite JSON number: '+c)))

def main():
    parser=argparse.ArgumentParser(description='AIAEAO VP-02 local cube views; no app / execution authority.')
    parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--report')
    args=parser.parse_args()
    try:
        plan=strict_load(args.input)
        printer=ViewPrinter()
        svg=printer.render(plan)
        report=printer.report(plan,svg)
        Path(args.output).parent.mkdir(parents=True,exist_ok=True)
        Path(args.output).write_bytes(svg)
        if args.report:
            path=Path(args.report);path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n','utf-8')
        print(f'PASS {plan["view"]}: {args.output} ({len(svg)} bytes; sha256={report["svg_sha256"]})')
    except (ViewError,ValueError,OSError) as e:
        parser.exit(2,'FAIL VP-02: '+str(e)+'\n')

if __name__=='__main__':main()
