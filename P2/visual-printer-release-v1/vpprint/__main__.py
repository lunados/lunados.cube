"""Stable VP-06 local entrypoint for agents. Always machine-readable failures."""
from __future__ import annotations
import argparse,json,sys
from .core import PrintError,capabilities,encode,load_json,make_job,persist_job,persist_print,render_job

def focus_from_cli(arg):
    if not arg:return None
    if ':' not in arg:raise PrintError('VP06_FOCUS_INVALID','focus must be kind:id, e.g. node:core','input')
    kind,identity=arg.split(':',1)
    if kind not in ('node','edge','sample','metric') or not identity:
        raise PrintError('VP06_FOCUS_INVALID','focus must use node|edge|sample|metric and an id','input')
    return {'kind':kind,'id':identity}

def main(argv=None):
    p=argparse.ArgumentParser(description='AIAEAO VP-06 offline, deterministic SVG Printer (not an API server)')
    s=p.add_subparsers(dest='command',required=True)
    s.add_parser('capabilities',help='print machine-readable capability card')
    prepare=s.add_parser('prepare',help='create a VP04 print job from an existing VP03 bundle')
    prepare.add_argument('--bundle',required=True)
    prepare.add_argument('--lens',required=True)
    prepare.add_argument('--granularity',required=True)
    prepare.add_argument('--overflow',default='summarize',choices=['summarize','reject'])
    prepare.add_argument('--focus',help='e.g. node:core or edge:e2')
    prepare.add_argument('--max-items',type=int)
    prepare.add_argument('--max-edges',type=int)
    prepare.add_argument('--out',required=True)
    chk=s.add_parser('check',help='validate and render in memory only; JSON result to stdout')
    chk.add_argument('--input',required=True)
    pr=s.add_parser('print',help='publish render.svg + report.json as one output directory')
    pr.add_argument('--input',required=True)
    pr.add_argument('--out',required=True)
    args=p.parse_args(argv)
    try:
        if args.command=='capabilities':
            sys.stdout.buffer.write(encode(capabilities()));return 0
        if args.command=='prepare':
            job=make_job(load_json(args.bundle),args.lens,args.granularity,args.overflow,
                         focus_from_cli(args.focus),args.max_items,args.max_edges)
            persist_job(job,args.out)
            sys.stdout.buffer.write(encode({'status':'PASS','operation':'prepare','job_file':args.out,
                                            'source_bundle_sha256':job['source_bundle_sha256']}));return 0
        job=load_json(args.input)
        result,svg=render_job(job)
        if args.command=='print':
            out=persist_print(result,svg,args.out,args.input)
            sys.stdout.buffer.write(encode({'status':'PASS','operation':'print','output_dir':str(out),
                                            'svg_sha256':result['svg_sha256'],'decision':result['decision']['action']}))
        else:sys.stdout.buffer.write(encode(result))
        return 0
    except PrintError as error:
        sys.stderr.buffer.write(encode(error.diagnostic()))
        return 2

if __name__=='__main__':raise SystemExit(main())
