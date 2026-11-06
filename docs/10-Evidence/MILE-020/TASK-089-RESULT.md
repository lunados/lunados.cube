# TASK-089 — Toolbox- und Translator-Deskriptoren: Ergebnis

Stand: 2026-11-06 · Ausführung: Codex · [Task](../../05-Tasks/TASK-089-toolbox-translator-descriptors.md) · [führender Status](../../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md).

## Gelieferte Owner-Artefakte

In `lunados.toolbox/module-capabilities/v1/` liegen `descriptor.json`, `pins.json` und `README.md`. Der Deskriptor nennt ausschließlich das vorhandene Paket **`aiaeao-toolbox-dns==0.1.0`** im Relay-Repo. Er unterscheidet die pure, in-memory Fixture-Normalisierung (`dns.fixture-normalize/v1`) vom signiert zugelassenen Standalone-CLI-Pfad (`dns.fixture-cli/v1`). Beide sind in der ausgewählten Paketquelle implementiert; die frühere, begrenzte TASK-550-Installationsprüfung ist als Herkunft benannt. Der Workspace selbst bleibt dokumentarisch. Kein Code wurde verlagert, installiert oder ausgeführt; News/Document-Funktionen sind nicht Teil dieses ersten Deskriptors.

Die CLI kann erst nach einer separat signierten, an Request und Effekt gebundenen Admission Card sowie hostseitigem Schlüssel/Fingerprint, Clock und Replay-Ledger einen Einmalanspruch und begrenzte `result.json`-/`manifest.json`-Dateien schreiben. Der pure Pfad hat diese Effekte nicht. Live-DNS, Netzwerk und allgemeine Host-Qualifikation sind ausgeschlossen. Input, Output und Effekte sind im Owner-[README](/Users/johannesklapproth/SitesHeroku/lunados.toolbox/module-capabilities/v1/README.md) sowie im Deskriptor getrennt beschrieben.

In `lunados.connector/module-capabilities/v1/` liegen dieselben drei Artefakttypen. `document.mapping-tables/v1` beschreibt die sechs vorhandenen maschinenlesbaren Tabellen mit **134 dokumentarischen Zeilen** und ihren Prüfer. `translate.directional/v1` bleibt `candidate`: MILE-002 enthält eine noch nicht angenommene Verantwortungs- und Platzierungsempfehlung, aber weder ausgewählte Quelle/Ziel/Verbraucher noch einen ausführbaren Translator. Der bestehende AIAEAO-Transport `aiaeao-connector` wird nicht als diese Fähigkeit ausgegeben. Die genaue Anzeige-/Connector-Benennung bleibt D-4 in TASK-092 vorbehalten.

| Owner-Artefakt | SHA-256 der Datei-Bytes |
|---|---|
| Toolbox `module-capabilities/v1/descriptor.json` | `5268cefba656e0ba7e62f57b6ac5885effda4c2d6c73985377ef8d391d4aa21e` |
| Toolbox `module-capabilities/v1/pins.json` | `699a6a94ffca77c2efee290a7d652257d3919fa82dde259bc2b7cddc26001e7c` |
| Translator `module-capabilities/v1/descriptor.json` | `a499dfb0d0c645cc3b309358c3542c7c81eff8da8673f7be2a680207088f64ed` |
| Translator `module-capabilities/v1/pins.json` | `4e313384d9c91972338d7fefec5dfa388f5cf66fbe76050fc0e8a7b67de0c561` |

## Quellenpins und Herkunft

Die Toolbox-Pinliste enthält sieben Quellen: MILE-001-Inventar, Paket-Metadaten, drei relevante Paketdateien, installiertes Module-v3-Manifest und TASK-550-Handoff. Das Paket liegt im Relay-Repo bei lokalem HEAD `6d6f62d234696e85f8618da83d31ac9a2915a918`. `pyproject.toml` hat SHA-256 `6fc11365fa79057cbd4e19f8c2edf3204e990fcdaae783babbc0de88d90ca06a` und deklariert `aiaeao-toolbox-dns` Version `0.1.0` samt Entry Point `aiaeao-toolbox-dns-fixture`. Die Paketquellen `dns_fixture_contract.py` und `dns_standalone_cli.py` sind separat mit `dfab275b7353cecc9d7af3ae3c89f67f62a699fe0251e9fe13ede7eb0184fd10` und `3206a0c264487e01a6b8379c7dea9196f4e764c13cd4b86b803f34aac874c1d2` gepinnt. Alle sieben exakten Pfade und Hashes stehen im Deskriptor und Pin-Manifest.

Die Translator-Pinliste enthält zwölf Quellen: MILE-002-Empfehlung, MILE-003-Mappings-Manifest, Tabellenschema und -prüfer, sechs JSON-Tabellen sowie zwei Cube-v9.4-Grammatikdateien. Das Mappings-Manifest hat SHA-256 `9cf085dea283794c6b1b589ca1281417b38db3b8f7373faa5e4b9185ad8e4dab` und nennt die Cube-Referenz v9.4 samt `concepts_sha256` `a15b0db3a3cfdb5874b8ab59de0ec9f4af08e8280e0634c48e3b37c3498000b8` und `constraints_sha256` `eebc060a0f8c633226dd4739a86819808ca501062193d4e60c4e703125537d8a`. Beide Hashes wurden gegen die lokalen Cube-Bytes geprüft; die Pins stammen aus dem Manifest, nicht aus einer angenommenen Live-Transformation. Alle Tabellen-IDs TT-01–TT-06 und Zeilenzahlen entsprechen dem Manifest.

## Ausgeführte Prüfung und Grenze

| Prüfung | Beobachtet |
|---|---|
| Gemeinsamer TASK-087-Prüfer für Toolbox `pins.json` | `PASS`, keine Diagnosen; Schema, Deskriptor und sieben Quellenbytes stimmen. |
| Gemeinsamer TASK-087-Prüfer für Translator `pins.json` | `PASS`, keine Diagnosen; Schema, Deskriptor und zwölf Quellenbytes stimmen. |
| `python3 scripts/check_mappings.py` im Connector-Workspace | `6 tables, 134 rows, 0 findings`; JSON-Zeilen, Markdown-Sichten und gepinnte Cube-IDs/Regeln stimmen. |
| Paketmetadaten- und Tabellenabgleich | Paketname/Version/CLI-Entry-Point und alle sechs Tabellen-IDs/Zeilenzahlen stimmen mit den jeweiligen Quellmanifesten. |

Die Prüfungen sind lokal und lesend. Sie sind kein neuer Paket-Build, keine installierte Host-Probe, keine DNS-Anfrage und keine Translator-Ausführung. Die oben genannten Connector-Hashes sind der **TASK-089-Lieferstand vor D-4**. Der Nutzer hat D-4 danach entschieden; [TASK-092](TASK-092-RESULT.md) dokumentiert den aktuellen Connector-Deskriptorhash und ordnet `translator/` intern zu. Damit ist die formale TASK-089-Abhängigkeit erfüllt und TASK-089 abgeschlossen. Die MILE-020-Gesamtabnahme bleibt offen.
