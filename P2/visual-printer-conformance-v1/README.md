# AIAEAO Visual Printer – VP-05 Combinatorial Conformance

**P2-VP-CONFORMANCE/0.5.0** · lokaler 2D-Fortschrittsstand · Morphology v9.4 · keine App / kein Server / kein 3D.

Dieses ZIP enthält die unveränderten VP-01–VP-04-Snapshots und die **VP-05-Audit-Komponente**. 3 Views × 5 deklarierte Lenses × 3 Granularities wurden für **zwei Quellen je View** gegeneinander geprüft: 90 Fälle, davon 54 zulässige SVGs und 36 korrekt zurückgewiesene Fälle ohne notwendige Lens-Deklaration. Der lokale VP-05-Unit-Test enthält 42 Prüfmethoden zusätzlich zur unveränderten VP-04-Regression (149 Tests).

## Start auf macOS

ZIP über Finder entpacken. Anschließend `P2/visual-printer-conformance-v1/matrix_preview.html` doppelklicken – 90 Fälle, fünf Perspektiven und drei Detailstufen lassen sich ohne lokalen Webserver vergleichen.

```bash
cd P2/visual-printer-conformance-v1
python3 scripts/verify_vp05.py
```

Einen einzelnen VP-04-Auftrag mit vollständiger VP-05-Conformance prüfen und als SVG drucken:

```bash
python3 -m vpconformance \
  --input matrix/tree_modules__governance__overview.json \
  --output /tmp/cube-vp05-audit.json \
  --svg /tmp/cube-vp05.svg
```

Nur Python 3.10+ und Standardbibliothek für den eigentlichen Printer/CLI. Für das vollständige optionale JSON-Schema-Gate: `python3 -m pip install 'jsonschema>=4,<5'`. Für das erneute Erstellen von PNG-Vorschauen optional `CairoSVG` und `Pillow`.

## Material

- `VP05_CONTRACT.md` – Projektion, Split-Heuristik und **bewusste Scope-Grenze**
- `VP05_ACCEPTANCE.md` – Abnahmegates
- `fixtures/INDEPENDENT_ORACLE.json` – vorab definierte Erwartungen
- `matrix/` – 90 JSON-Aufträge, 54 Golden-SVGs, 54 originale VP04-Reports, 54 VP05-Audits, 36 negative VP05-Audits
- `matrix_preview.html`, `previews/contact_sheet.png` – visuelle lokale Inspektion
- `VP05_AUDIT_REPORT.schema.json`, `VP05_REJECTION.schema.json` – Draft 2020-12
- `vpconformance/` – separates Audit-Paket, keine Änderung an VP04
- `scripts/verify_vp05.py` – Gesamtabnahme, Quellenlocks und Prüfsummen
- `../visual-printer-granularity-v1/` – byteidentischer VP-04-Snapshot
- `../visual-printer-2d-lab/` – byteidentischer VP-03/02/01-Snapshot

**P0/P1, GitHub und Cloudflare bleiben unverändert.** Dieses ZIP wird nicht automatisch veröffentlicht. Die SVGs sind deskriptive Projektionen nicht verifizierter Fixtures – keine Wahrheits-, Autorisierungs-, Ausführungs- oder Admission-Aussagen.
