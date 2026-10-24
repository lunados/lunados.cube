from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from vp2d import Printer
p=Printer(); out=ROOT/'outputs';out.mkdir(exist_ok=True)
report=[]
for src in sorted((ROOT/'fixtures').glob('*.json')):
    raw=json.loads(src.read_text('utf8'))
    svg=p.render(raw)
    (out/(src.stem+'.svg')).write_bytes(svg)
    report.append({'input':src.name,'output':src.stem+'.svg','sha256':hashlib.sha256(svg).hexdigest(),'bytes':len(svg)})
print(json.dumps({'status':'PASS','svg_count':len(report),'outputs':report},indent=2))
