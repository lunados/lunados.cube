import argparse,json
from pathlib import Path
from .printer import Printer, PrintError

def main():
    ap=argparse.ArgumentParser(description='AIAEAO P2 experimental 2D SVG printer. Purely presentational.')
    ap.add_argument('--input',required=True,help='JSON plan')
    ap.add_argument('--output',required=True,help='SVG output path')
    a=ap.parse_args()
    try:
        plan=json.loads(Path(a.input).read_text('utf8'))
        svg=Printer().render(plan)
        Path(a.output).parent.mkdir(parents=True,exist_ok=True)
        Path(a.output).write_bytes(svg)
        print(f'PASS printed {a.output} ({len(svg)} bytes) sha256={Printer.sha256(svg)}')
    except (PrintError,ValueError,OSError) as e:
        ap.exit(2,f'FAIL {e}\n')

if __name__=='__main__':main()
