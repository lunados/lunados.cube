# TASK-093 — Gepinnte `neighbors` in G4/G5: Ergebnis

Stand: 2026-11-06 · Ausführung: Codex · [Task](../../05-Tasks/TASK-093-neighbors-discovery.md) · [führender Status](../../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md).

## Referenzbestand und Einbau

Der einzige Cube-eigene Referenzbestand liegt als kanonischer JSON-Block in `P3/adapters/mcp-local/aiaeao_mcp_local/neighbors.json` (SHA-256 `fdfa98c731b2cd5efb1cda79f89e4de6b676d146089e39ddfb242ad77c190c26`, 2196 Bytes). `module-capabilities/v1/build_neighbors.py` prüfte offline die fünf Owner-Pin-Manifeste von Cube, Lib, Toolbox, Connector und den drei Relay-Rollen mit dem TASK-087-Checker, verlangte genau sieben bekannte Modul-IDs und serialisierte gemäß `aiaeao.module-capabilities.neighbors/1`. Der isolierte Relay-Worktree aus [TASK-090](TASK-090-RESULT.md) war die Quelle der drei Relay-Rollen; sein zusätzliches `aiaeao-connector`-Paket gehört nicht zur Nachbarliste.

| Modul-ID | Owner-Deskriptor SHA-256 |
|---|---|
| `aiaeao.core-server` | `a622465268c692f6b4ab23767de448d6d0542c2ee76dd118b8de5f1a79d9728b` |
| `aiaeao.server-gui` | `88fd83549b5750d3eb6777f78dcd850cd1113c9c0025ef22af4985604a17927a` |
| `aiaeao.web-app` | `f7a5f1792d99c889eefe5524c9da00956b53890f00b6d513118181d82c1779f4` |
| `lunados.connector` | `49fd756691ce5385f651c48cd5e960bd7d7b6c31f02fcece471b84ea4d92edf8` |
| `lunados.cube` | `0c3f17186e06a0112c60c7fc71b84585d393e8cf690cf12d7208a82759c02936` |
| `lunados.lib` | `cf6bc1da44ecc9d5a9d2c8c3cef1eac5c663f42d501a1e2d5751ba9a9e022f4b` |
| `lunados.toolbox` | `5268cefba656e0ba7e62f57b6ac5885effda4c2d6c73985377ef8d391d4aa21e` |

Jeder Eintrag führt zusätzlich Modulversion, Deskriptorformat und beschreibenden Owner-Locator in der JSON-Datei. Discovery liest ausschließlich dieses mit dem Cube-Paket ausgelieferte Asset und greift zur Aufrufzeit weder auf Nachbar-Checkouts noch auf deren Module zu. G5 verwendet dieselbe `surface.discover_surface()`-Basis wie G4. Das G5-Assembly kopierte das Asset in `.g5-runtime` und listete es mit demselben SHA-256 in `G5_SOURCE_MANIFEST.json`. Die G4-Surface-Schemaerweiterung ist additiv; alte Felder behalten ihre oberflächenspezifischen Aussagen.

Die Cube-Owner-Deskriptorquelle `p3-surface` wurde wegen des geänderten `surface.py` auf SHA-256 `a844765e4699496494375727789e60d4960b8b0241df2f40d747f91ce9067fe1` neu gepinnt. Dadurch änderte sich der Cube-Deskriptorhash gegenüber dem historischen TASK-090-Stand auf den oben genannten Wert; `module-capabilities/v1/pins.json` ist entsprechend aktualisiert. Die übrigen Owner-Deskriptorbytes blieben unverändert.

## Vorher/Nachher und Prüfungen

| Prüfung | Beobachtet |
|---|---|
| `python3 module-capabilities/v1/build_neighbors.py --relay <TASK-090-Worktree>` | `PASS seven pinned neighbors (2196 canonical bytes)`; alle fünf Manifeste und deren Quellen wurden offline geprüft. |
| `python3 contracts/module-capabilities/v1/check.py --manifest module-capabilities/v1/pins.json` | `PASS`, keine Diagnosen für den aktualisierten Cube-Deskriptor. |
| G4-Discovery ohne `neighbors` gegen `G4_CAPABILITIES_GOLDEN.json` | Vollständig gleich; 57 G4-Surface-Tests und JSON Schema Draft 2020-12 bestanden. |
| G6-lokale Discovery ohne `neighbors` gegen den unveränderten `surface.py`-Stand aus `HEAD` | Vollständig gleich. |
| G5-Discovery ohne `neighbors` gegen die **vor dem neuen Assembly** gesicherte `.g5-runtime`-Karte | Vollständig gleich. Die Remote-spezifischen Felder und bisherigen Top-Level-Profile blieben erhalten. |
| Kanonische `neighbors`-Bytes aus G6-lokaler und G5-Discovery gegen das Paket-Asset | Drei Bytefolgen gleich; SHA-256 `fdfa98c731b2cd5efb1cda79f89e4de6b676d146089e39ddfb242ad77c190c26`. |
| G6 historische Baseline ohne den neuen Block | 22/22 alte Digest-Ausgaben bytegleich. Die Baseline-Pins selbst wurden nicht überschrieben. |
| `python3 P3/remote-mcp-g5/scripts/assemble_core.py` | `PASS`, 169 gestagte Quelldateien einschließlich `neighbors.json`; G5-Quellartefakt lokal neu erzeugt. |
| G5-Contract-Tests gegen `.g5-runtime` | 27 Tests bestanden, einschließlich der neuen Prüfung gegen das gepackte `neighbors.json`. |
| G5-Assembly in isoliertes temporäres Verzeichnis kopiert; `python -I`, Socket-Erzeugung gesperrt | `cube_discover_surface` lieferte sieben Nachbarn ohne benachbarten Owner-Checkout und ohne Netzwerk. |

Die alten G4-/G6-Golden-Dateien wurden als Vorher-Baselines beibehalten; ihre Vergleiche ignorieren ausschließlich den neuen `neighbors`-Block. Der lokale G6-Antwortkörper und das neue G5-Quellartefakt enthalten den Block. **Ein tatsächlich ausgelieferter G5-Endpunkt wurde in TASK-093 nicht geändert oder abgefragt.** Diese Offline-/Artefaktparität belegt weder Deployment noch Host-Verfügbarkeit, Admission, Authority oder Ausführung eines Nachbarmoduls. Die echte Remote-Abnahme bleibt TASK-094 vorbehalten.
