# TASK-087 — Deskriptorformat und Offline-Prüfung: Ergebnis

Stand: 2026-11-06 · Ausführung: Codex im Repository `lunados.cube` · [Task](../../05-Tasks/TASK-087-capability-schema.md) · [D-1-Entscheidung](TASK-086-RESULT.md#d-1--verhältnis-zum-module-contract-v2).

## Gelieferter Vertrag

Das eigene dokumentarische Format heißt nun **`aiaeao.module-capabilities/1`**. [Vertrag und Betriebsgrenze](../../../contracts/module-capabilities/v1/README.md) enthalten Deskriptor-, Pin-Manifest- und neighbors-Schema, den lokalen [Prüfer](../../../contracts/module-capabilities/v1/check.py), eine synthetische [Beispiel-Pinliste](../../../contracts/module-capabilities/v1/examples/pins.json) und fokussierte Prüffälle. Der neue Vertrag verweist nur gezielt und exakt auf Module v2; dessen normative Dateien wurden nicht geändert.

| Artefakt | SHA-256 der Datei-Bytes |
|---|---|
| `contracts/module-capabilities/v1/descriptor.schema.json` | `79f0c13f797d1c68d9b29f2f7b8fc470662ed744b2fb45484b38a4ba4acdb98f` |
| `contracts/module-capabilities/v1/pin-manifest.schema.json` | `0a0371ea6896a087ae2f1d693822b3e4ff7e3847579ed200fafb121f3123aade` |
| `contracts/module-capabilities/v1/neighbors.schema.json` | `f0e30dca7adb7d10d309bb0ff50bcf4a77533ac9f9af0ae1ac576f306082cb29` |
| `contracts/module-capabilities/v1/check.py` | `5041610dc94974a2e0817d23b8c81fad3af066b9852dec983ecc3e0910cfdcc7` |
| `contracts/module-capabilities/v1/examples/descriptor.json` | `f36b98b8a352cb9bb347d16f89f4d96e010ad34688cee71089dc9251b647675f` |

Der Deskriptor enthält keinen eigenen Hash. Das explizit gelieferte Pin-Manifest nennt seine vollständigen Bytes und die lokalen Dateien aller deklarierten Quellen. `neighbors` enthält nur Modul-ID/-Version, Deskriptorformat, beschreibenden Locator und Deskriptorhash. Seine Bytes sind UTF-8-JSON mit nach `module_id` sortierten Einträgen, sortierten Objektschlüsseln und ohne Leerraum. Nur dieser Block ist für spätere lokale/G5-Byteparität vorgesehen.

## Ausgeführte Prüfung

| Befehl / Fall | Beobachtet |
|---|---|
| `python3 contracts/module-capabilities/v1/check.py --manifest contracts/module-capabilities/v1/examples/pins.json` | `PASS`, Exit 0; synthetischer Deskriptor und Quelle stimmen exakt mit ihren SHA-256-Pins überein. |
| Derselbe Aufruf mit `--neighbors-only` | Ein kanonischer neighbors-Block für `example.module`, Exit 0. |
| `python3 -m unittest discover -s contracts/module-capabilities/v1/tests -v` | 12/12 Fälle bestanden. Darunter gültiger Deskriptor, falsches Format, Typ und Status, doppelte IDs, unbelegte Referenz, fehlende Quellenzuordnung, geänderte Bytes, fehlender lokaler Snapshot, doppelte JSON-Schlüssel, v2-Verweis, stabile neighbors-Reihenfolge sowie die CLI-Exitcodes für Fehler und Unverfügbarkeit. |
| Separater JSON-Schema-Abgleich gegen den echten v2-Schemapin aus [TASK-086](TASK-086-RESULT.md) | Gültiger `structured-inspection/v1`-Deskriptor schema-gültig; `generic-mcp-tool` als unveränderter v2-Deskriptor abgewiesen. |
| `git diff --check` | Bestanden. |

Fehlende lokale Bytes führen zu **`UNAVAILABLE`** (Exit 2), falsche Hashes oder Strukturen zu **`FAIL`** (Exit 1); beide verhindern neighbors-Ausgabe und einen erfolgreichen Pin-Nachweis. Ein Fehler hat Vorrang, wenn zugleich eine Quelle fehlt. Der Prüfer nutzt `jsonschema` 4.x und benötigt keine Netzwerkverbindung.

## Aussagegrenze und Übergabe

Die Prüfung belegt Format, lokale Bytegleichheit und interne Referenzen. Sie authentifiziert keinen Owner, bewertet die inhaltliche Stärke eines Implementierungsbelegs nicht und weist weder eine laufende Host-Fähigkeit noch Admission, Authority oder Ausführung nach. Die `artifact`-/`version`-Angaben einer generischen Quelle sind Owner-Aussagen; nur für den gezielten v2-Verweis prüft der Prüfer zusätzlich die beiden festen v2-Deskriptor-/Payload-Paare im bereitgestellten Manifest.

Die synthetische Beispieldatei ist **kein** Owner-Deskriptor. TASK-088–090 müssen reale, owner-lokale Deskriptoren und ihre Quellenpins liefern; TASK-093 übernimmt erst danach die passive Cube-Discovery. Es gab keine Bereitstellung und keinen G5-Live-Test für das neue Format.
