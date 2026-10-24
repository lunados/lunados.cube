# VP-05 Acceptance Matrix

| Gate | Akzeptanzkriterium | Nachweis |
|---|---|---|
| G01 | VP-04 inklusive VP-01–VP-03 Regression unverändert und grün | eigenständiger `verify_vp04.py` aus byteidentischem Snapshot |
| G02 | Matrix umfasst exakt 3 Views × 5 Lenses × 3 Levels × 2 Quellen je View | 90 feste Fälle in `matrix/` |
| G03 | Positiv/Negativ strikt ohne implizite Lens-Inferenz | 54 Golden-SVGs, 36 erwartete Deklarationsfehler |
| G04 | unabhängiges Vorab-Orakel, kein Self-Oracle | `fixtures/INDEPENDENT_ORACLE.json` und 42 Tests |
| G05 | keine neue Relation, Wurzel, Messung oder Lens-Authority | unabhängige Source/Output-Partitionen, XML-Metadaten und adversariale Tests |
| G06 | Same Input / Same SVG / Same Report | byteweiser Golden-Vergleich aller positiven Fälle |
| G07 | Auslassungs- und Split-Vorschläge bleiben ausdrücklich deklarativ | `split_feasibility`, Panel-Überlappung, Fehler für unerreichbare Tree-Fokusse |
| G08 | Schema-Validierung und CLI-Ausgabe | JSON-Schema Draft 2020-12 und Python-CLI-Positiv-/Negativtest |
| G09 | unveränderte Baselines und Paketintegrität | Snapshot-Hashes, Release-Manifest, SHA256-Ledger, frisch entpacktes ZIP |
| G10 | statische lokale Vergleichsansicht vorhanden | `matrix_preview.html` und 9 gerasterte Beispiele |

### Nicht durch diese Gates abgedeckt

- Lesbarkeit und Fontfallback auf jedem Betriebssystem; Live-Agent-Grafiken mit Claude/Grok
- Valide P1-Claims oder empirische Gültigkeit der synthetischen Messwerte
- Großer Graph / allgemeiner Auto-Layout-Algorithmus
- Automatisch erzeugter Multi-SVG-Export (nur Feasibility-Empfehlungen)
- 3D, Server, Web-App, GitHub-/Cloudflare-Deployment
