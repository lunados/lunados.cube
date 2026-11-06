# Design und Entscheidungsgrenzen

## Context

Ausgangsplanung vom 2026-11-06. Die Quellenbaseline und Entscheidungen wurden in TASK-086–094 umgesetzt und für den benannten Stand [abgenommen](../../../../docs/10-Evidence/MILE-020/TASK-094-RESULT.md); der führende Status steht in [tasks.md](tasks.md). Die folgende Tabelle hält die ursprünglich gelesenen Quellen fest.

| Gelesene Quelle, relativ zum lokalen Benutzerverzeichnis | SHA-256 der gelesenen Bytes |
|---|---|
| `SitesHeroku/lunados.cube/P3/adapters/mcp-local/aiaeao_mcp_local/surface.py` | `cc6849108e6b75741e6fff21727f332df8663d9fc4f3576e810f1889e8576999` |
| `SitesHeroku/lunados.lib/INDEX.json` | `aa2cfc92bd1aeb98ae72840fe5d225b7af6932824c57adc9635d6e82b9bbcdb6` |
| `SitesHeroku/lunados.toolbox/README.md` | `6708eeb6eae3230c5f589f835b059d41269366f2773a2881c0aa9fd3af2a9229` |
| `SitesHeroku/lunados.connector/docs/09-Research/MILE-002-RESPONSIBILITY-RECOMMENDATION.md` | `89965834ca1ee859a23e00e22d791d61e281fd3e8775d30d0cc0252c5939a4da` |
| `SitesHeroku/lunados.connector/schema/translation-table.schema.json` | `c38f2f51e36e6837702b6dc1189730a1b210726de62be116d6e2dcd31bcd3aa1` |
| `Documents/lunados-test/agent-relay-poc-v3/docs/10-contracts/MILE-071-MODULE-CONTRACT-BASELINE.md` | `0cec7ddb479e389d2ba55e3a0571f14e83ca74c4103d14e6a0e5dc31b2dd1470` |
| `Documents/lunados-test/agent-relay-poc-v3/contracts/module-contract/v2/schemas/descriptor.schema.json` | `57fe94f6f6def257c120abd79f37b87f615841e5e3cf4c3bb626a4bff92e7c0f` |
| `Documents/lunados-test/agent-relay-poc-v3/src/agent_relay/adapters/registry.py` | `2e6ce8ed64dc768d616207e8003c7e092a1feaa68b08ce955bc41fe5624e9765` |

Module v2 erlaubt nur `structured-inspection` und `artifact-observation`, Version v1, exakt zugeordnete Payload-Referenzen und keine Zusatzfelder. Es kann deshalb nicht kommentarlos um generische Modul-/MCP-Metadaten ergänzt werden. registry.py nennt openai/xai/codex, erstellt aber bei Aufruf reale Adapter; der Plan liest ausschließlich die Datei.

Toolbox ist derzeit ein dokumentarischer Workspace; sein Paketbestand liegt im Relay. Der Bereich `translator/` gehört nach D-4 zum gemeinsamen Ziel-Repo `lunados.connector`; die Translator-Empfehlung ist weiterhin keine angenommene Laufzeit- oder Codeverlagerungsentscheidung. Das bestehende Paket `aiaeao-connector` liegt noch im Relay-Repo. MILE-071 beschreibt sieben logische Verantwortungen, keine sieben fertigen Produkte. Server GUI bleibt in der Abdeckungsmatrix enthalten, auch wenn es Quellen mit Core/App teilt.

## Goals / Non-Goals

Owner-lokale, überprüfbare Beschreibungen und additive Referenzen. Keine zentrale Kopie der fachlichen Fähigkeitslisten im Cube; nur Pins und Quellenverweise. Keine Ausführung, Admission, Authority, neue Toolbox-Fähigkeit oder Codeverlagerung. MILE-021 verantwortet Explorer-Bindung; MILE-022 Builder und Modulzuordnung; MILE-023 Playbooks und deren eigene Beispiele. Keine Abhängigkeit von deren Implementierung.

## Decisions

| Entscheidung | Stand und Gate |
|---|---|
| D-1 | **Entschieden (Nutzer, 2026-11-06): eigenes dokumentarisches Format mit gezieltem v2-Verweis.** [TASK-086](../../../../docs/10-Evidence/MILE-020/TASK-086-RESULT.md) vergleicht alle Optionen. Module v2 bleibt unverändert; [TASK-087](../../../../docs/10-Evidence/MILE-020/TASK-087-RESULT.md) fixiert `aiaeao.module-capabilities/1`. |
| D-2 | **Entschieden (Nutzer, 2026-11-06):** Drei Methoden mit konkreter Cube-Profil-/Ansichtsnutzung sind `cube-profile`, die anderen zehn `standalone`. Alle 13 besitzen P1.8-Referenzfälle mit `library_ref`; das allein begründet kein `cube-profile`. `standalone` behauptet keine Host-Ausführung. [TASK-088-Nachweis](../../../../docs/10-Evidence/MILE-020/TASK-088-RESULT.md). |
| D-3 | Nutzerentscheidung: direkt für Build/Tests, über Host zur Laufzeit; INDEX.json-Hash in beiden Fällen führend. [ADR-001](../../../../docs/07-ADR/ADR-001-lib-snapshot-host-path.md) dokumentiert dies mit [TASK-091-Nachweis](../../../../docs/10-Evidence/MILE-020/TASK-091-RESULT.md), ohne Host-Implementierung. |
| D-4 | **Entschieden (Nutzer, 2026-11-06):** `lunados.connector` ist ein gemeinsames logisches Modul und Ziel-Repo; `translator/` ist sein interner Übersetzungsbereich. Keine eigene Modul-ID `lunados.translator`. Das technische Paket `aiaeao-connector` bleibt am heutigen Ort und behält seinen Namen; ein Cutover ist separat zu entscheiden. [TASK-092](../../../../docs/10-Evidence/MILE-020/TASK-092-RESULT.md). |

Planungspräzisierung: Bytegleichheit bezieht sich auf den neuen `neighbors`-Inhalt bei explizit festgelegter Serialisierung. Vollständige lokale und G5-Antworten enthalten bereits absichtlich unterschiedliche Transport-/Deployment-Aussagen und bleiben je Oberfläche unverändert. Sollte eine vollständige Antwortgleichheit gewünscht sein, wäre das eine zusätzliche Entscheidung außerhalb dieser additiven Planung.

Quellhash und Deskriptorhash sind verschiedene Pins. Der Deskriptor pinnt seine Quellen; der Cube-Verweis pinnt dessen vollständige Bytes. Kein eigener Hash im gehashten Dokument. Schema-/Modul-/Fähigkeitsversion und Quellrevision dürfen nicht miteinander verwechselt werden. Die spätere Prüfung führt keinen entfernten Fetch aus; fehlende Bytes bleiben unprüfbar.

## Lib-Ausgangsliste

Die D-2-Zuordnung ist im Lib-Owner-Artefakt `module-capabilities/v1/cube-relations.json` je Eintrag begründet und mit Quellen gepinnt. Quellstatus ist nicht Implementierungsstatus. `candidate-authored` und `candidate-extracted` bleiben Kandidaten.

| method_id | INDEX-Quellstatus | Cube-Zuordnung in dieser Planung |
|---|---|---|
| `decision.compare/v1` | `candidate` | `standalone` |
| `dialectics.compare/v1` | `candidate` | `standalone` |
| `experimentation.plan/v1` | `candidate` | `standalone` |
| `validation.assess/v1` | `candidate` | `standalone` |
| `feedback.propose/v1` | `candidate` | `standalone` |
| `measure.scale-check/v1` | `candidate-extracted` | `standalone` |
| `claim.compose/v1` | `candidate-extracted` | `standalone` |
| `impact.propagate/v1` | `candidate-extracted` | `standalone` |
| `verify.reuse/v1` | `candidate-extracted` | `standalone` |
| `counterworld.diff/v1` | `candidate-extracted` | `standalone` |
| `analyze.population/v1` | `candidate-authored` | `cube-profile` |
| `project.aggregate-relations/v1` | `candidate-authored` | `cube-profile` |
| `analyze.trace-conformance/v1` | `candidate-authored` | `cube-profile` |

## Risks / Trade-offs

- Offene Owner-/Formatentscheidungen begrenzen die Parallelisierung. Die ADR und Quelleninventur sind unabhängig vorziehbar.
- Ein Deskriptor kann `implemented` nur in einem quellenbelegten Umfang ausweisen, niemals daraus aktuelle Host-Verfügbarkeit folgern.
- Fehlende Quellen oder geänderte Pins werden sichtbar, nicht durch automatischen Fallback verborgen.
- G5-Quell-/Offline-Parität allein ist kein Deployment-/Host-Nachweis. [TASK-094](../../../../docs/10-Evidence/MILE-020/TASK-094-RESULT.md) dokumentiert zusätzlich die private Core-Bereitstellung und den live über den bestehenden G5-Zugang gelesenen `neighbors`-Block.
- Detailaufwand 2,5–4,5 PT ohne Wartezeit/Bereitstellung; D-1-Erweiterung oder unerwartete Quelllücken können Neubewertung erfordern.

## Migration Plan

Zunächst Entscheidungen und Vertrag, dann Owner-Artefakte, schließlich nur additive Cube-Verweise. Bestehende Verträge, IDs und Quellenbytes bleiben erhalten. Keine Runtime-Migration Teil der Mile. Bei Fehlern keine automatische Aktivierung oder Auswahl neuer Versionen.

## Open Questions

D-1, D-2 und D-4 sind durch den Nutzer entschieden, ohne den normativen v2-Vertrag zu ändern. Cube, Lib, Toolbox und `lunados.connector` haben Owner-Artefakte unter `module-capabilities/v1/`; `lunados.connector` enthält außerdem den internen Ordner `translator/`. Drei logische Relay-Rollen und der gesonderte Connector-Paketbestand liegen im isolierten TASK-090-Worktree unter demselben Deskriptorpfad; sie sind noch nicht in Relay-`main` integriert. D-3 ist als ADR-001 dokumentiert. [TASK-093](../../../../docs/10-Evidence/MILE-020/TASK-093-RESULT.md) hat den siebenfach gepinnten `neighbors`-Block lokal und im G5-Quellartefakt belegt; [TASK-094](../../../../docs/10-Evidence/MILE-020/TASK-094-RESULT.md) ergänzt die tatsächlichen Aufrufe über den lokalen Codex-Host und live G5 sowie die Gesamt-Abnahme für diesen Stand.
