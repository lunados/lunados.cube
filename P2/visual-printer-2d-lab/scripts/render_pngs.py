"""Optional local raster preview, never a normative/rendering dependency."""
from pathlib import Path
import cairosvg
root=Path(__file__).resolve().parents[1]
out=root/'previews';out.mkdir(exist_ok=True)
for p in sorted((root/'outputs').glob('*.svg')):
    target=out/(p.stem+'.png')
    cairosvg.svg2png(bytestring=p.read_bytes(),write_to=str(target),output_width=1200)
    print(target)
