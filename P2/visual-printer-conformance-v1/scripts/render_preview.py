"""Generate static review page and optional local raster sheet; no renderer runtime requirement."""
import html,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'matrix';preview=ROOT/'previews'
preview.mkdir(exist_ok=True)
rows=[('cube.flow','flow_migration','flow_research'),('cube.diagramm','chart_inventory','chart_line'),('cube.tree','tree_modules','tree_resources')]
lenses=['semantics','provenance','execution','governance','epistemology']
levels=['overview','standard','detail']
parts=['<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
 '<title>AIAEAO VP-05 · View × Lens × Granularity</title><style>',
 'body{font:15px system-ui,sans-serif;max-width:1420px;margin:auto;padding:32px;color:#142033;background:#f5f7fb}',
 'h1,h2{letter-spacing:-.025em}.note{padding:13px 17px;background:#fff;border-left:4px solid #64748b}',
 '.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}',
 '.card{background:#fff;border:1px solid #d8e1ed;border-radius:10px;overflow:hidden;min-width:0}',
 '.card img{width:100%;display:block;aspect-ratio:1.7;object-fit:contain;background:white}',
 '.label{font-size:12px;padding:10px 14px}.sub{color:#617084;font-size:12px}',
 '.rejected{display:flex;align-items:center;justify-content:center;aspect-ratio:1.7;background:#f1f4f7;color:#5c6678;padding:15px;text-align:center}',
 '@media(max-width:850px){.grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:550px){.grid{grid-template-columns:1fr}}',
 '</style></head><body><h1>VP-05 · Combinatorial Conformance</h1>',
 '<p class="note">Statische Prüfung der 90 Kombinationen: 54 gültige Projektionen und 36 erwartete Ablehnungen (fehlende Lens-Deklaration). Die SVGs und ihre JSON-Ledger stammen aus unveränderten VP-04-Quellen. Kein Editor, kein Server, keine 3D-Ausgabe.</p>']
for view,rich,sparse in rows:
    for source in (rich,sparse):
        parts.append(f'<h2>{html.escape(view)} · {html.escape(source)}</h2><div class="grid">')
        for lens in lenses:
            for level in levels:
                name=f'{source}__{lens}__{level}'
                rpt=json.loads((R/(name+'.vp05.report.json')).read_text('utf8'))
                if rpt['status']=='PASS':
                    action=rpt['decision']['action']
                    image=f'<img src="matrix/{html.escape(name)}.svg" alt="{html.escape(name)} SVG">'
                else:
                    action='LENS_DECLARATION_MISSING'
                    image='<div class="rejected">Ausdrücklich keine Lens-Deklaration.<br>Keine automatische Relevanz-Inferenz.</div>'
                parts.append(f'<div class="card">{image}<div class="label"><strong>{html.escape(lens)} · {html.escape(level)}</strong><div class="sub">{html.escape(action)}</div></div></div>')
        parts.append('</div>')
parts.append('<p class="note">Quelle und Resultate sind deklarierte Fixtures, nicht empirisch verifiziert. Der Split-Hinweis generiert keine zusätzlichen SVG-Panels. Alle 90 JSON-Aufträge und Conformance-Berichte sind im Ordner <code>matrix/</code> enthalten.</p></body></html>')
(ROOT/'matrix_preview.html').write_text('\n'.join(parts)+'\n','utf8')
try:
 import cairosvg
 from PIL import Image,ImageOps,ImageDraw,ImageFont
except ImportError:
 print('optional CairoSVG/Pillow missing; HTML+SVG preview ready');raise SystemExit(0)
from io import BytesIO
thumbs=[]
for view,rich,_ in rows:
    for level in levels:
        name=f'{rich}__provenance__{level}'
        data=cairosvg.svg2png(bytestring=(R/(name+'.svg')).read_bytes(),output_width=560)
        pic=Image.open(BytesIO(data)).convert('RGB')
        pic.thumbnail((540,320))
        tile=Image.new('RGB',(580,355),'white')
        tile.paste(pic,((580-pic.width)//2,22))
        ImageDraw.Draw(tile).text((14,335),name,fill='#334155')
        path=preview/(name+'.png');tile.save(path)
        thumbs.append(tile)
out=Image.new('RGB',(580*3,355*3),(240,244,248))
for i,p in enumerate(thumbs):out.paste(p,((i%3)*580,(i//3)*355))
out.save(preview/'contact_sheet.png')
print('generated static HTML and 9 PNG + contact sheet')
