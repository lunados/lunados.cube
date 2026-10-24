#!/usr/bin/env python3
"""Optional development-only PNG rasterization; SVG source remains authoritative."""
from pathlib import Path
import io
from PIL import Image, ImageDraw, ImageFont
import cairosvg
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'lens_previews';OUT.mkdir(exist_ok=True)
FILE_LIST=sorted((ROOT/'lens_outputs').glob('*.svg'))
thumbs={}
for path in FILE_LIST:
    data=cairosvg.svg2png(bytestring=path.read_bytes(),output_width=720)
    im=Image.open(io.BytesIO(data)).convert('RGB')
    (OUT/(path.stem+'.png')).write_bytes(data)
    im.thumbnail((550,360))
    thumbs[path.stem]=im
w=5*568+20;h=3*416+30
sheet=Image.new('RGB',(w,h),'#f3f5f8')
pen=ImageDraw.Draw(sheet)
rows=['flow_migration','chart_inventory','tree_modules']
cols=['semantics','provenance','execution','governance','epistemology']
for i,stem in enumerate(rows):
    for j,lens in enumerate(cols):
        x=14+j*568;y=10+i*416
        pen.text((x,y),f'{stem} · {lens}',fill='#1f2937')
        im=thumbs[f'{stem}__{lens}']
        sheet.paste(im,(x,y+26))
        pen.rectangle((x,y+26,x+550,y+26+im.height),outline='#bdc5d0',width=1)
sheet.save(OUT/'contact_sheet.png')
print('Raster previews',len(FILE_LIST),'and contact sheet')
