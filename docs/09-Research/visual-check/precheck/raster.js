// TASK-022: Farb- und Graustufenrasterung der Prüfeingaben (Chromium/Playwright)
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const [,, listFile, outDir] = process.argv; const items = JSON.parse(fs.readFileSync(listFile, 'utf8'));
(async () => { const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 1.4 }); const log = [];
  for (const it of items) { const svg = fs.readFileSync(it.file, 'utf8');
    for (const mode of ['color', 'gray']) {
      const filt = mode === 'gray' ? 'filter:grayscale(1);' : '';
      await p.setContent(`<html><body style="margin:0;background:#fff"><div style="${filt}display:inline-block">${svg}</div></body></html>`);
      const out = path.join(outDir, `${it.id}.${mode}.png`); await (await p.$('div')).screenshot({ path: out });
      log.push({ id: it.id, mode, png: path.basename(out), sha256: crypto.createHash('sha256').update(fs.readFileSync(out)).digest('hex') }); } }
  fs.writeFileSync(path.join(outDir, 'raster-log.json'), JSON.stringify(log, null, 1)); await b.close(); })();
