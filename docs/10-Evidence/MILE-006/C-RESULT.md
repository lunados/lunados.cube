# MILE-006 — Abschlussnachweis

Stand: 2026-11-02 · Branch `feature/mile006-remote-and-order` · Prüfung: [verification.json](verification.json), Skript [verify_mile006.py](verify_mile006.py) · Hashes: [MANIFEST.json](MANIFEST.json)

## Prüfung

| Kriterium | Ergebnis |
|---|---|
| G5-Erwartungen vor Kern und Bereitstellung (`68ba97f` vor `49e3893`); VP-10.1-Orakel und Pins der 0.10.0-Ausgaben vor dem Printercode (`507f8a6` vor `b2f75f5`); Entscheidungen Q-1–Q-6 vor dem Code (`ec147e5`) | erfüllt |
| Erwartungen, Orakel und Pins seitdem unverändert | erfüllt |
| P1.12 K-01–K-21 21/21, Tests grün; G5-Kern frisch zusammengestellt, Parität G4/G5 offline 21/21 | erfüllt |
| Host-Abnahme über den G5-Connector (Version `42e7b8a9…`): 13 Vektoren, 2 Fehler, Golden, 2 Regressionen, 24/24 Prüfzeilen PASS | erfüllt |
| VP-10 J-01–J-14 14/14, 24 Tests; VP-10.1 O-01–O-10 10/10, 14 Tests; 16/16 Ausgaben aus 0.10.0 byte-gleich | erfüllt |
| Adapter: `cube.cells` mit `axis_order` über G6, MILE-005-Adapter und Discovery grün; G6-Parität 201/201 ([TASK-040-Lauf](task040-run.json)) | erfüllt |
| Sichtprüfung nach [Anleitung](SICHTPRUEFUNG.md): 7/7 ja | erfüllt |
| P0, P1.1–P1.11, VP-07, VP-09 und die übrigen P2-Pakete seit `main` unverändert; P1.12 nur README und Paritätsskript ergänzt; alle Prüfsummenlisten halten (P3 Charge-3-Schnappschuss historisch) | erfüllt |
| Relative Links in docs/, openspec/, VP-10 und den G5-Nachweisen | keine kaputten |

## Chargen

| Mile | Abschlusskriterium | Nachweis |
|---|---|---|
| MILE-006-A | Offline-Prüfung und Parität G4/G5; Live-Abnahme mit vorab festgelegten Erwartungen | [Erwartungen](../../../P3/remote-mcp-g5/evidence/G5_R4_P112_EXPECTATIONS.json), [Host-Bericht R4](../../../P3/remote-mcp-g5/evidence/G5_R4_P112_HOST_REPORT.md) |
| MILE-006-B | Orakel vor Code; Vektoren wie erwartet; 0.10.0 byte-gleich | [Spezifikation VP-10.1](../../../P2/visual-printer-cells-v1/VP10_1_ACCEPTANCE_SPEC.md), [Lauf TASK-040](task040-run.json), [Renderings](task040/README.md) |
| MILE-006-C | Anleitung committet; jeder Prüfpunkt beantwortet; jedes „nein“ bearbeitet | [Sichtprüfung](SICHTPRUEFUNG.md) (D-6 revidiert: kurze Sichtprüfung statt Lesbarkeitstest) |

## Ergebnis

- `cube_validate` im Remote-Connector nimmt `binding-context/8` an (`P3-MCP-REMOTE/0.7.0-proof`); Discovery nennt P1.12 und die drei Diagnosen. Der Release-Status bleibt `remote_proof_not_accepted` für Produktion.
- VP-10 `0.10.1` (opt-in `axis_order`): Reihenfolge je Art-Gruppe, „nicht geordnet“, farbfreie Marke „Rückkopplung“ über der Diagonale; CLI und G6. Ohne Option bleibt `0.10.0` byte-gleich.
- Die Darstellung ist gesichtet; es gab keine Mängel.

## Grenzen

- Plansichten (VP-10) laufen weiterhin nur lokal (G6); remote nur `cube_validate` (D-2).
- Host-Abnahme nur mit Claude als Host.
- Orakel und Printer stammen vom selben Autor; die Übereinstimmung kontrolliert Implementierungsunterschiede.
- Die Sichtprüfung durch eine Person findet nur offensichtliche Mängel; weitere Lücken zeigen sich in der Praxis.
- Alle Fälle synthetisch, ohne Kundendaten.

## Offen aus der MILE-005-Übergabe

PO-7/G-03 (Aussagenmengen ohne Plan), VR-12 (Instanzsicht) und G-07 (Kontrollfluss) bleiben für einen späteren Schritt ([Übergabe](../../09-Research/completeness-instances/HANDOVER.md)).
