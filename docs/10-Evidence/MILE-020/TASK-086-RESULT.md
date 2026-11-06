# TASK-086 — Quellenbaseline und D-1-Vorlage

Stand: 2026-11-06 · Ausführung: Codex in `lunados.cube` · Ergebnis: Quellen und Modulabdeckung dokumentiert; **D-1 vom Nutzer entschieden**. Diese Bestandsaufnahme ist kein Deskriptor, keine Vertragsänderung und kein Nachweis einer neuen Host-Fähigkeit. [Task](../../05-Tasks/TASK-086-descriptor-baseline.md) · [MILE-020](../../02-Milestones/MILE-020-module-capability-descriptors.md).

## Gepinnte Quellstände

| Kürzel | Repository oder lokaler Workspace | Stand | Grenze |
|---|---|---|---|
| C | `lunados.cube` | Git `85d6701c85a87d31afc251411503e4c8bd6fd08d` | Dokumente der laufenden Planung sind uncommittet; die unten genannten Codequellen sind unverändert. |
| L | `lunados.lib` | Git `284f69d67c216cc1a500e7c86d648c74805c9df3` | Arbeitsbaum bei Prüfung sauber. |
| T | `lunados.toolbox` | kein Git-Repository | Lokale, dokumentarische Bestandsaufnahme; Hash ersetzt keinen Commit. |
| X | `lunados.connector` | kein Git-Repository | Translator-Platzierung ist ein Vorschlag, keine akzeptierte Laufzeitentscheidung. |
| R | `agent-relay-poc-v3` | Git `6d6f62d234696e85f8618da83d31ac9a2915a918` | Andere ungetrackte Research-Pfade vorhanden; unten genannte Dateien sind dadurch nicht verändert. |

Alle SHA-256-Werte beziehen sich auf die **gelesenen Datei-Bytes**, nicht auf normalisierten Text oder einen laufenden Dienst. Pfade sind relativ zum jeweiligen Repository/Workspace. „Owner“ benennt die bestehende Quellzuständigkeit, keine neue Freigabe.

| Stand | Pfad | SHA-256 | Versions-/Formatangabe | Owner und Aussagegrenze |
|---|---|---|---|---|
| C | `P3/adapters/mcp-local/aiaeao_mcp_local/surface.py` | `cc6849108e6b75741e6fff21727f332df8663d9fc4f3576e810f1889e8576999` | `aiaeao.cube.mcp-capability-surface/1`; G4 `P3-MCP-LOCAL/0.2.0-rc1`, G6 `0.3.0-rc1` | Cube: deklarierte lokale Discovery; kein Beleg für G5-Deployment oder Nachbaraufrufe. |
| C | `P3/adapters/mcp-local/aiaeao_mcp_local/server.py` | `08ce1312836a0c91d4247fbe513a0d4b31ad630d3a8ef75df686bca37f09d87c` | `cube_validate`, G4/G6-Adapter | Cube: lokale Tool-Signatur; P1-Prüfung ist deskriptiv, keine Authority oder Admission. |
| L | `INDEX.json` | `aa2cfc92bd1aeb98ae72840fe5d225b7af6932824c57adc9635d6e82b9bbcdb6` | `lunados.lib/index/v1`, 13 Einträge | Lib: Eintragskatalog; `candidate*` ist Quellstatus, keine Host-Verfügbarkeit oder Implementierungszusage. |
| L | `entries/analyze.population/v1/entry.json` | `f69963e0b0f5ae3fa46c1f867e78608d489cf4b6bb3da480f8dfce6c8e6f6720` | `lunados.lib/entry/v1`, `analyze.population/v1` | Lib: Methodensignatur und separater Evaluator; Cube konsumiert einen `library_ref`, führt die Methode nicht aus. |
| T | `README.md` | `6708eeb6eae3230c5f589f835b059d41269366f2773a2881c0aa9fd3af2a9229` | MILE-001 dokumentarisch abgeschlossen | Toolbox-Workspace: Inventar, keine neue Distribution oder universelle Tool-Laufzeit. |
| T | `docs/09-Research/MILE-001-CAPABILITY-INVENTORY.md` | `cf0b44cfffded399e818a519a1ae07defa18fa79b8cf7863bd0bb9cc354a3852` | TB-01 bis TB-03; `aiaeao-toolbox-dns==0.1.0` | Toolbox-Inventar: konkret begrenzter DNS-Fixture-Bestand im Relay-Repo. |
| X | `docs/09-Research/MILE-002-RESPONSIBILITY-RECOMMENDATION.md` | `89965834ca1ee859a23e00e22d791d61e281fd3e8775d30d0cc0252c5939a4da` | TASK-015-Vorschlag, nicht akzeptiert | Translator-Workspace: nur vorgeschlagene gerichtete Übersetzung; keine Platzierungs- oder Runtime-Autorität. |
| X | `schema/translation-table.schema.json` | `c38f2f51e36e6837702b6dc1189730a1b210726de62be116d6e2dcd31bcd3aa1` | `lunados.connector.translation-table/1` | Translator-Workspace: dokumentarisches Tabellenformat, kein ausführbarer universeller Mapper. |
| R | `docs/10-contracts/MILE-071-MODULE-CONTRACT-BASELINE.md` | `0cec7ddb479e389d2ba55e3a0571f14e83ca74c4103d14e6a0e5dc31b2dd1470` | MILE-071-Baseline 2026-10-23, v9.4-Referenz | Relay-Vertragsowner: sieben **logische** Rollen, keine sieben fertigen Produkte oder Services. |
| R | `contracts/module-contract/v2/manifest.json` | `2ef5fc7164668265aeeb9a34e3d2a55ff29b6257006a393f93095e34567bc31f` | `aiaeao-module-contract/v2` | Repository-Maintainer gemäß Manifest: genau zwei deklarierte Capability-Deskriptoren, kein generischer Modulvertrag. |
| R | `contracts/module-contract/v2/schemas/descriptor.schema.json` | `57fe94f6f6def257c120abd79f37b87f615841e5e3cf4c3bb626a4bff92e7c0f` | JSON Schema 2020-12, `$id` `https://aiaeao.local/contracts/module-contract/v2/schemas/descriptor.schema.json`; Capability-Version `v1` | Repository-Maintainer: `additionalProperties: false`, nur `structured-inspection` und `artifact-observation` mit je festem Input-/Result-Ref. |
| R | `src/agent_relay/adapters/registry.py` | `2e6ce8ed64dc768d616207e8003c7e092a1feaa68b08ce955bc41fe5624e9765` | kein eigener öffentlicher Vertrag | Relay-Adapter-Owner: bekannte openai/xai/codex-Namen; Quelllektüre belegt weder einen laufenden Adapter noch eine neue Connector-Fähigkeit. |

Die 13 Lib-IDs und ihre Quellstatus sind im [Planungsdesign](../../../openspec/changes/archive/2026-11-06-declare-module-capabilities/design.md#lib-ausgangsliste) vollständig aufgelistet. Für TASK-086 wurden sie gegen den aktuellen `INDEX.json` gezählt; D-2 bleibt eine spätere Zuordnungsentscheidung. Die drei bereits dokumentierten Cube-`library_ref`-Beziehungen zu `analyze.population/v1`, `project.aggregate-relations/v1` und `analyze.trace-conformance/v1` sind Ausgangsbefunde, keine automatische Aussage über die übrigen zehn Methoden.

## Abdeckungsmatrix der logischen Rollen

Die spätere Deskriptorquelle ist hier eine **geplante Owner-Ablage**, keine heute vorhandene Deskriptordatei. Die Quelle links liefert den jetzigen Mindestbeleg; `candidate` und `unknown` dürfen bei fehlendem Implementierungsbeleg nicht zu `implemented` aufgewertet werden.

| Rolle aus MILE-071 | Zuständiger Quellort für späteren Deskriptor | Jetzt belegte Quelle und Grenze | Fähigkeitsstatus für den späteren Deskriptor |
|---|---|---|---|
| Core/Server | Relay-Repo, Core-/Server-Owner | MILE-071 und `packages/aiaeao-core/` (`0.1.2`); keine allgemeine Admission-API aus dem Zielbild folgern. | Einzelne vorhandene Quellen; konkrete Fähigkeiten in TASK-090 quellengebunden prüfen, sonst `unknown`. |
| Server GUI | Relay-Repo, Server-GUI-Owner | MILE-071; eigenständige logische Ansicht bei gemeinsamer Datenquelle mit App, kein eigener Service behauptet. | `unknown` bis konkrete Ansicht und Quelle geprüft sind. |
| Web App einschließlich Application Service | Relay-Repo, App-Owner | MILE-071; App-Verantwortung bleibt auch bei Code im Serverprozess App-owned. | `candidate` für Zielbild; konkrete bestehende Fähigkeiten einzeln prüfen. |
| Connector (Transport) | Relay-Repo, Connector-Owner | MILE-071; `packages/aiaeao-connector/` (`0.1.0`) und `registry.py` sind unterschiedliche konkrete Quellen; kein generischer Live-Provider. | Begrenzter Paketbestand belegt; generische Transportfähigkeit `unknown`. |
| Toolbox | `lunados.toolbox` für Modul-Inventar; DNS-Paketquelle im Relay-Repo | MILE-001-Inventar und `aiaeao-toolbox-dns==0.1.0`; nur begrenzte DNS-Fixture-Fähigkeit belegt. | DNS-Fixture konkret belegt; weitere Toolbox-Fähigkeiten `unknown`. |
| Pure Cube | `lunados.cube`, Cube-Owner | `surface.py` und `server.py`; P0/P1/P2/P3 sind getrennte Oberflächen, strukturelle Prüfung ist keine Wahrheit oder Zulassung. | Aktuelle Tool-Signaturen belegt; jede Fähigkeitsbehauptung in TASK-090 begrenzen. |
| Functions Library | `lunados.lib`, Lib-Owner | `INDEX.json` mit 13 Einträgen; ein Eintrag ist kein automatisch laufender Host-Dienst. | `candidate`-Quellenstatus der Einträge; Implementierungsstatus separat in TASK-088 prüfen. |
| Translator (zusätzlich, nicht eine der sieben Rollen) | `lunados.connector`, dortiger Quellenowner | TASK-015-Empfehlung und Tabellen-Schema; Platzierung/Runtime noch nicht entschieden. | `candidate` als Verantwortungsvorschlag, Runtime `unknown`. |

## Beobachtete Cube-Oberflächen

Am 2026-11-06 in dieser Codex-Sitzung je einmal `cube_discover_surface` über den verbundenen lokalen Cube und G5 aufgerufen. Diese Beobachtung ist **Host-Discovery**, keine Prüfung aller Tools oder des zugrunde liegenden Git-Deployments. Ein vollständiger Response-Byte-Pin wurde nicht erzeugt; die folgenden Felder sind die gesicherte Vergleichsbasis.

| Feld | Lokal | G5 |
|---|---|---|
| `format` | `aiaeao.cube.mcp-capability-surface/1` | gleich |
| `release.version` | `P3-MCP-LOCAL/0.3.0-rc1` | `P3-MCP-REMOTE/0.9.3-proof` |
| `deployment.remote_mcp_available` | `false` | `true` |
| `deployment.remote_transport` | nicht vorhanden | `streamable_http` |
| `mcp.tools` | zehn deklarierte Namen | dieselben zehn Namen |
| `domains.P0.reference_version` | `v9.4` | `v9.4` |
| `cross_domain.overall_status` | `NOT_DEFINED` | `NOT_DEFINED` |
| `neighbors` | nicht vorhanden | nicht vorhanden |

Die vollständigen Antworten enthalten absichtlich verschiedene lokale/G5-Felder. TASK-093 muss deshalb den neuen `neighbors`-Block separat bytegleich prüfen und die bisherigen Felder **je Oberfläche** gegen deren eigene Baseline vergleichen. Live-G5-Discovery beweist weder einen aktuellen Git-Commit des Workers noch dessen Bereitstellung für alle Hosts.

## D-1 — Verhältnis zum Module Contract v2

**Konkreter Vergleich.** Cube `cube_validate` nimmt `input_text`, `input_format`, optionalen Kontext und Qualifikationsprofile an und liefert deskriptive P1-Status. Lib `analyze.population/v1` beschreibt eine deklarative Methode mit vier Eingaberollen, Result-Schema und getrenntem Evaluator. Module v2 kennt dagegen ausschließlich `structured-inspection/v1` mit `structured-parameters`/`structured-result` und `artifact-observation/v1` mit `artifact-observation-parameters`/`artifact-observation-result`. Beide v2-Typen sind gültige Quellen für ihre jeweiligen konkreten Relay-Fähigkeiten, aber keine allgemeine Repräsentation der Cube- oder Lib-Signaturen.

| Option | `cube_validate` / `analyze.population/v1` | Beide v2-Typen | Kompatibilität und Auswirkung |
|---|---|---|---|
| **v2 unverändert übernehmen** | Lassen sich nicht als diese beiden Capability-IDs mit ihren festen Payload-Refs darstellen, ohne ihre Bedeutung zu verfälschen. | Bleiben exakt gültig. | Für alle MILE-020-Module ungeeignet; eine falsche v2-Konformitätsbehauptung wäre erforderlich. |
| **v2 erweitern** | Neue IDs/Felder/Refs könnten sie prinzipiell ausdrücken, aber erst nach neuem normativem Vertrag und tatsächlicher Owner-Entscheidung. | Bestehende v2-Bytes und Konsumenten dürfen nicht stillschweigend umgedeutet werden. | Vertragsrevision, unabhängige Consumer-Prüfung und Migration nötig; Umfang über eine bloße Metadatenliste hinaus. |
| **Eigenes dokumentarisches Format, v2 gezielt referenzieren** | Eigene quellengebundene Fähigkeiten mit expliziten Input-/Output-Refs und Status möglich. | Bestehende v2-Deskriptoren nur mit exakter Version/Hash als Quelle referenzieren; keine eingebettete Ersatzdefinition. | Erhält den geschlossenen v2-Vertrag und die Owner-Grenze. Neuer Format-/Schema-Owner und Offline-Prüfung in TASK-087 erforderlich. |

**Entscheidung D-1 (Nutzer, 2026-11-06):** eigenes dokumentarisches Format mit gezieltem v2-Verweis. Der neue Vertrag darf v2-Deskriptoren nur mit exakter Version und Hash referenzieren und keine ihrer Bedeutungen umschreiben. Module v2 wird nicht geändert; deshalb ist für D-1 keine normative v2-Owner-Freigabe ausgelöst. Die späteren Deskriptoren und ihre Quellenbehauptungen bleiben bei ihren jeweiligen Ownern zur Prüfung. TASK-087 kann auf dieser Entscheidung aufbauen; der konkrete Formatname, Schema-Bytes und Offline-Prüfung entstehen erst dort.

## Prüfung und offene Punkte

- Gelesene Dateien erneut per SHA-256 berechnet; die acht bereits im Planungsdesign genannten Hashes stimmen überein. Zusätzliche Hashes für `server.py`, Lib-Beispiel, Toolbox-Inventar und v2-Manifest stehen oben.
- Cube-Tool, Lib-Methode und beide v2-Fähigkeitstypen wurden **quellenlesend** verglichen. Weder Lib-Evaluator noch Relay-Adapter wurden importiert oder ausgeführt; keine Vertrags- oder Host-Prüfung erfolgte dadurch.
- TASK-086 ist mit Quellenmatrix, Oberflächenbaseline, Optionsvergleich und dokumentierter D-1-Entscheidung abgeschlossen. D-2 und D-4 gehören zu späteren Tasks. Keine aktuelle Deskriptor-Ablage ist durch diese Baseline autorisiert.
