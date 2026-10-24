"""Local CLI: python3 -m vpgranularity --input fixture.json --output result.svg --report result.report.json"""
import argparse
import json
from pathlib import Path
from .printer import GranularityPrinter, GranularityError
from vpviews.__main__ import strict_load

def main():
    cli=argparse.ArgumentParser(description='VP-04 deterministic granularity and budget SVG printer')
    cli.add_argument('--input',required=True);cli.add_argument('--output',required=True);cli.add_argument('--report')
    a=cli.parse_args()
    try:
        req=strict_load(a.input);printer=GranularityPrinter()
        svg=printer.render(req);report=printer.report(req,svg)
        dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(svg)
        if a.report:
            rp=Path(a.report);rp.parent.mkdir(parents=True,exist_ok=True)
            rp.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n','utf8')
        print('PASS VP-04',report['view'],report['granularity'],report['completeness'],'· sha256',report['svg_sha256'])
    except (GranularityError,ValueError,TypeError,OSError,KeyError) as err:
        cli.exit(2,'FAIL VP-04: '+str(err)+'\n')
if __name__=='__main__':main()
