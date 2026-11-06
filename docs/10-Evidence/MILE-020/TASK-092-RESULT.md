# TASK-092 — Connector und `translator/`: D-4-Ergebnis

Stand: 2026-11-06 · Ausführung: Codex · [Task](../../05-Tasks/TASK-092-connector-names.md) · [führender Status](../../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md).

## Nutzerentscheidung D-4

Der Nutzer hat `lunados.connector` als **gemeinsames logisches Connector-Modul und Ziel-Repo** festgelegt. Die Übersetzungsarbeit gehört darin in einen schlichten Ordner **`translator/`**. Eine eigene Modul-ID oder ein eigenes Repo `lunados.translator` ist nicht vorgesehen. Der Nutzer beschreibt den Translator als integrierten Übersetzungsbereich desselben Repos; die tatsächliche semantische Abbildung bleibt in den Tabellen explizit, quellengebunden und verlustbewusst, nicht automatisch oder stillschweigend ausführbar.

Das heute vorhandene technische Paket `aiaeao-connector==0.1.0` bleibt mit seinem Namen im Relay-Repo `agent-relay-poc-v3/packages/aiaeao-connector/`. Der lokale `lunados.connector`-Workspace enthält weiterhin die dokumentarischen Übersetzungstabellen und derzeit keinen ausführbaren Translator. Das gemeinsame **Ziel** sagt keinen bereits vollzogenen Paket-Cutover aus. Source-of-truth, History, Build und Freigabe einer späteren Verlagerung benötigen eine eigene Entscheidung.

| Gegenstand | Name/Ort nach D-4 | Aussage |
|---|---|---|
| Logisches Connector-Modul und Ziel-Repo | `lunados.connector` | Eine der sieben MILE-071-Rollen; aktueller lokaler Ordner ist noch kein Git-Repo. |
| Interner Übersetzungsbereich | `lunados.connector/translator/` | Gehört zum Connector, kein achtes Modul; verweist auf die bestehenden führenden Tabellen in `mappings/`. |
| Bestehendes ausführbares Paket | `aiaeao-connector` im Relay-Repo | Technischer Paketname und aktuelle Code-Ablage bleiben erhalten. |
| Translator-Ansicht im lokalen Workbench | Web-App-Komponente | Nicht mit dem internen Connector-Ordner oder einem produktiven Translator gleichzusetzen. |

## Geänderte aktuelle Stellen

Im Connector-Workspace wurde `translator/README.md` angelegt und aus dem Root-README verlinkt. Der Owner-Deskriptor `module-capabilities/v1/descriptor.json` bleibt beim Modul `lunados.connector`, bindet den Ordner über eine zusätzliche Quelle `translator-boundary` ein und hat nun Version `mappings-2026-11-04+d4-2026-11-06`. Die vorhandenen Capability-IDs und technischen Paket-IDs wurden nicht umbenannt. Das Pin-Manifest wurde auf die neuen Deskriptorbytes und 13 Quellen aktualisiert. Die bisherige MILE-003-Empfehlung, Tabellen, Schemas, Checker und historischen Quellen wurden nicht umgeschrieben.

| Aktuelles Connector-Artefakt | SHA-256 der Datei-Bytes |
|---|---|
| `translator/README.md` | `34ed5786a22bd8021bf6253763a1f4a5af9de091da5f3da27e0961fe01b3a77b` |
| `module-capabilities/v1/descriptor.json` | `49fd756691ce5385f651c48cd5e960bd7d7b6c31f02fcece471b84ea4d92edf8` |
| `module-capabilities/v1/pins.json` | `99d2f876ed0ed3820471b76a981a5ad00ac01d810501cb0d96cd60dadf169f94` |

Auf lunados.space wurden die **aktuellen** Erklärtexte in `web/product/index.html`, `web/product/README.md` und `web/docs/atlas/MODUL-LANDSCHAFT.md` ergänzt: der Translator-Bereich gehört zum Connector und ist nicht die gleichnamige Workbench-Ansicht. Die Produktseite beschreibt keine automatische Transformation. Die ursprünglichen historischen Landschafts-/Experimentdateien bleiben unverändert. Die Space-Änderungen sind lokal, nicht veröffentlicht.

## Prüfung und Grenze

| Prüfung | Beobachtet |
|---|---|
| TASK-087-Prüfer für `lunados.connector/module-capabilities/v1/pins.json` | `PASS`, keine Diagnosen: Deskriptorstruktur und alle 13 Quellenpins stimmen. |
| `python3 scripts/check_mappings.py` im Connector-Workspace | `6 tables, 134 rows, 0 findings`; bestehende JSON-/Markdown-Tabellen und Cube-v9.4-Referenz bleiben konsistent. |
| `git diff --check` in Cube und Space | Bestanden. |
| Such-/Review-Liste | Connector-Root-README, `translator/README.md`, Owner-Deskriptor/README/Pinliste, MILE-020/EPIC-014/US-040/TASK-089/090/092, OpenSpec-Design/Spec/Status und die drei aktuellen Space-Erklärtexte zeigen eindeutige Referenten. |

Diese D-4-Umsetzung benennt und ordnet zu. Sie verschiebt keinen Paketcode, ändert keine API oder Normdatei, führt keinen Translator aus und veröffentlicht keine Space-Seite.
