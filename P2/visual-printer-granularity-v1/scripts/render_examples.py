#!/usr/bin/env python3
"""Compile fixed golden SVG/report fixtures, optionally rasterize 3x3 preview."""
import hashlib,html,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from vpgranularity import GranularityPrinter
from xml.etree import ElementTree as ET


def run():
    pr=GranularityPrinter()
    outputs=ROOT/'outputs';outputs.mkdir(exist_ok=True)
    rows=[]
    for f in sorted((ROOT/'fixtures').glob('*.json')):
        req=json.loads(f.read_text('utf8'));svg=pr.render(req);rep=pr.report(req,svg)
        (outputs/(f.stem+'.svg')).write_bytes(svg)
        (outputs/(f.stem+'.report.json')).write_text(json.dumps(rep,indent=2,ensure_ascii=False,sort_keys=True)+'\n','utf8')
        rows.append({'stem':f.stem,'view':rep['view'],'level':rep['granularity'],'items':rep['counts']['items_shown'],
                     'omitted':rep['counts']['items_omitted'],'edges_omitted':rep['counts']['edges_omitted'],'complete':rep['completeness']})
    styles='''*{box-sizing:border-box}body{font:14px system-ui, sans-serif;max-width:1500px;margin:32px auto;padding:0 20px;background:#f8fafc;color:#0f172a}h1{font-size:29px}p{line-height:1.5;color:#475569}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.tile{background:white;border:1px solid #cbd5e1;border-radius:12px;overflow:hidden}.tile h2{font-size:16px;padding:8px 14px 0;margin:8px 0}.tile p{font-size:12px;padding:0 14px;margin-bottom:10px}.tile object{width:100%;height:285px;object-fit:contain}.warn{border-left:4px solid #b45309;padding:12px;background:#fffbeb}a{color:#1d4ed8}footer{margin:32px 0;font-size:12px}@media(max-width:950px){.grid{grid-template-columns:1fr}}'''
    panel=[]
    for view in ('flow_research','chart_line','tree_resources'):
        panel.append('<h2>'+html.escape(view.replace('_',' ').title())+'</h2><div class="grid">')
        for level in ('overview','standard','detail'):
            row=next(x for x in rows if x['stem']==view+'__'+level)
            title=html.escape(row['stem']);panel.append(f'<div class="tile"><h2>{title}</h2><p>Shown {row["items"]} · Omitted {row["omitted"]} items / {row["edges_omitted"]} edges</p><object data="outputs/{title}.svg" type="image/svg+xml" aria-label="{title}">Your browser cannot preview this SVG.</object><p><a href="outputs/{title}.svg">SVG</a> · <a href="outputs/{title}.report.json">JSON ledger</a></p></div>')
        panel.append('</div>')
    extra=''.join(panel)
    (ROOT/'granularity_preview.html').write_text('<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AIAEAO VP-04 · Granularity Comparison</title><style>'+styles+'</style></head><body><h1>AIAEAO VP-04 · Complexity Budget</h1><p>Same declared source and lens across overview → standard → detail; rendering-only truncation, not an epistemic judgement.</p><p class="warn">The printed summaries disclose hidden items and edges. Reduction does not imply completeness, authorization, causality or successful execution. Values and hierarchies are illustrative fixtures.</p>'+extra+'<footer>Local file-only preview. No JavaScript, remote assets, application or 3D.</footer></body></html>','utf8')
    # Raster compare sheet is optional; no raster conversion occurs during SVG printing.
    try:
        import cairosvg
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        sheet=Image.new('RGB',(1410,1250),'#f1f5f9');draw=ImageDraw.Draw(sheet)
        for row,stem in enumerate(('flow_research','chart_line','tree_resources')):
            for col,level in enumerate(('overview','standard','detail')):
                name=stem+'__'+level
                content=(outputs/(name+'.svg')).read_bytes()
                png=cairosvg.svg2png(bytestring=content,output_width=460)
                (ROOT/'previews'/(name+'.png')).write_bytes(png)
                img=Image.open(BytesIO(png)).convert('RGB')
                img.thumbnail((460,360))
                x=10+470*col;y=30+400*row
                sheet.paste(img,(x,y+35))
                draw.text((x+10,y+5),f'{stem} / {level}',fill='#0f172a')
        sheet.save(ROOT/'previews'/'contact_sheet.png')
        raster='9/9 rasterized; contact sheet PASS'
    except ImportError:raster='NOT_EVALUATED (CairoSVG/Pillow absent)'
    print('Rendered',len(rows),'golden SVGs+reports;',raster)

if __name__=='__main__':run()
