# MILE-020 — Fähigkeits-Deskriptor je Modul

Status: **abgeschlossen** für den benannten lokalen Owner- und live G5-Stand ([Abschlussnachweis](../10-Evidence/MILE-020/CLOSURE.md)) · Stand: 2026-11-06 · Vorbedingung für [MILE-022](MILE-022-workflow-builder.md) und [MILE-023](MILE-023-playbook-library.md) · Betrifft: lunados.cube, lunados.lib, lunados.toolbox, lunados.connector, agent-relay-poc-v3

## Ziel und Entscheidung

Der Cube soll der Einstiegspunkt in die AIAEAO-Workspaces sein. Wer über den Cube einsteigt, soll sehen, welche Module es gibt und was jedes davon leisten kann. Dieses Wissen liegt **beim jeweiligen Modul**: Jedes Modul beschreibt seine Fähigkeiten selbst, versioniert und per Hash gepinnt. Der Cube verweist darauf; ein späterer Workflow Builder liest es nur. So entsteht keine zweite, veraltende Wahrheit an zentraler Stelle.

Ein Deskriptor ist dokumentarisch. Er gewährt keine Authority, keine Admission und keinen Aufruf und belegt nicht, dass eine Fähigkeit in einem Host läuft.

## Ausgangslage (2026-11-06)

- `cube_discover_surface` beschreibt nur P0–P3; `cross_domain.overall_status` ist `NOT_DEFINED`. lunados.lib erscheint nur im Text einzelner Drucker-Optionen; Lib-Index, Connector-Tabellen, Explorer-Format und Toolbox fehlen.
- Der Cube referenziert 3 von 13 Lib-Funktionen über `library_ref` (`analyze.population`, `project.aggregate-relations`, `analyze.trace-conformance`).
- Zwischen Cube und Toolbox gibt es in keiner Richtung Verweise; zwischen Cube und Core/Server keine Bindung (lunados.connector `docs/09-Research/MILE-002-RESPONSIBILITY-RECOMMENDATION.md`).
- Vorbild für eine saubere Bindung: Die Übersetzungstabellen in lunados.connector pinnen `cube.lunados.net/v9.4/...` mit SHA-256.
- Die Tabelle der sieben logischen Module in `agent-relay-poc-v3/docs/10-contracts/MILE-071-MODULE-CONTRACT-BASELINE.md` (Input, Output, Ausschlüsse) ist die fachliche Ausgangsfassung. Der Module-Contract-v2-Capability-Deskriptor im Relay-Repo hat feste Fähigkeitstypen; eine generische MCP-Tool-Deklaration ist kein gültiger v2-Deskriptor.

## Arbeitsumfang

1. **Format:** `aiaeao.module-capabilities/1` ([Vertrag und Offline-Prüfung](../../contracts/module-capabilities/v1/README.md), TASK-087). Je Modul: Kennung, Version, Quellen mit Hash, Fähigkeiten mit Input/Output und Status (`implemented`, `candidate`, `unknown`), Ausschlüsse. Module Contract v2 bleibt unverändert und wird bei passenden Quellen exakt referenziert (D-1).
2. **Cube:** Abschnitt `neighbors` in `cube_discover_surface` mit Verweisen auf die Deskriptoren der Nachbarn (Version, Hash). Rein beschreibend: kein Laden, kein Aufruf, keine automatische Bindung. G4 und G5 liefern denselben Inhalt.
3. **Lib:** Deskriptor aus `INDEX.json`. Für jede der 13 Funktionen das Verhältnis zum Cube festhalten: drei `cube-profile` mit konkreter Profil-/Ansichtsnutzung, zehn `standalone` (D-2). Alle 13 haben zusätzlich einen P1.8-Referenzfall mit `library_ref`; dieser allein begründet keine Profilnutzung.
4. **Toolbox:** erster Deskriptor nur für den Bestand `aiaeao-toolbox-dns==0.1.0`; keine neue Fähigkeit.
5. **Connector und Relay-Repo:** Deskriptor für `lunados.connector` mit internem Bereich `translator/` sowie Deskriptoren für Core/Server, App und das bestehende Paket `aiaeao-connector` aus vorhandenen Quellen (`adapters/registry.py`, Module Contract v2), nur dokumentarisch. Der gemeinsame Ziel-Repo-Name verschiebt noch keinen Paketcode.
6. **ADR Host-Pfad:** Einzelne Cube-Build-/Test-Leser greifen heute direkt auf den Lib-Nachbar-Checkout zu; die P1.8-/G5-Laufzeit löst `library_ref` nur formal auf. MILE-071 sieht Lib-Snapshots über den Host vor. Entschieden ist „beides, Hash führend“ (D-3); [ADR-001](../07-ADR/ADR-001-lib-snapshot-host-path.md) hält das fest und nennt die Folgen für MILE-071.
7. **Namen:** `lunados.connector` ist das gemeinsame logische Modul und Ziel-Repo; `translator/` ist dessen interner Übersetzungsbereich. `aiaeao-connector` bleibt der technische Name des heute im Relay-Repo liegenden Pakets (D-4).

## Entscheidungen

| ID | Frage | Optionen |
|---|---|---|
| D-1 | Verhältnis zum Module-Contract-v2-Deskriptor | **Entschieden (Nutzer, 2026-11-06): eigenes dokumentarisches Format, v2 bei passender Quelle mit exakter Version und Hash referenzieren.** Kein normativer v2-Eingriff ([Quellenvergleich](../10-Evidence/MILE-020/TASK-086-RESULT.md#d-1--verhältnis-zum-module-contract-v2)). |
| D-2 | Status jeder ungenutzten Lib-Funktion | **Entschieden (Nutzer, 2026-11-06): drei `cube-profile`, zehn `standalone`.** `cube-profile` erfordert konkrete Nutzung in einem Cube-Profil oder einer Cube-Ansicht; der P1.8-Referenzfall allein genügt nicht. `standalone` ist ein Lib-Kandidat mit eigenem Evaluator und behauptet keine Host-Ausführung ([TASK-088](../10-Evidence/MILE-020/TASK-088-RESULT.md)). |
| D-3 | Host-Pfad für Lib-Snapshots | **Entschieden (Nutzer, 2026-11-06): beides, Hash führend.** Direkt aus dem gepinnten Lib-Stand für Build und Tests, über den Host zur Laufzeit; maßgeblich ist in beiden Fällen der gepinnte `INDEX.json`-Hash. [ADR-001](../07-ADR/ADR-001-lib-snapshot-host-path.md) und [TASK-091-Nachweis](../10-Evidence/MILE-020/TASK-091-RESULT.md). |
| D-4 | Connector und Translator zuordnen | **Entschieden (Nutzer, 2026-11-06):** ein gemeinsames Ziel-Repo `lunados.connector`, darin der Ordner `translator/`; keine eigene Modul-ID oder eigenes Repo `lunados.translator`. Das vorhandene Paket `aiaeao-connector` bleibt vorerst im Relay-Repo und behält seinen technischen Namen. [TASK-092-Nachweis](../10-Evidence/MILE-020/TASK-092-RESULT.md). |

## Abnahme

- [x] Format `aiaeao.module-capabilities/1` mit Schema und Prüfskript; D-1 entschieden ([TASK-086](../10-Evidence/MILE-020/TASK-086-RESULT.md), [TASK-087](../10-Evidence/MILE-020/TASK-087-RESULT.md)).
- [x] Je ein Deskriptor für Cube, Lib, Toolbox, Connector und die logischen Relay-Rollen, jeweils mit Version und Hash; Relay-Artefakte liegen im isolierten lokalen Worktree ([TASK-090](../10-Evidence/MILE-020/TASK-090-RESULT.md)).
- [x] `cube_discover_surface` enthält `neighbors`, im frisch gestarteten lokalen MCP-Server, nach Neustart im lokalen Codex-Host und live G5 bytegleich; bestehende Felder je Oberfläche unverändert ([TASK-093](../10-Evidence/MILE-020/TASK-093-RESULT.md), [TASK-094](../10-Evidence/MILE-020/TASK-094-RESULT.md)).
- [x] Alle 13 Lib-Funktionen haben einen Status zum Cube ([TASK-088](../10-Evidence/MILE-020/TASK-088-RESULT.md)).
- [x] ADR zum Host-Pfad liegt vor und gibt D-3 wieder ([ADR-001](../07-ADR/ADR-001-lib-snapshot-host-path.md), [TASK-091](../10-Evidence/MILE-020/TASK-091-RESULT.md)).
- [x] Connector-Modul, interner Translator-Bereich und bestehendes Paket sind eindeutig benannt ([TASK-092](../10-Evidence/MILE-020/TASK-092-RESULT.md)).

## Nicht in MILE-020

Ausführung, Admission oder Authority; Verlagerung von Code zwischen Repos; neue Toolbox-Fähigkeiten; der Workflow Builder selbst.

Die Integration der im isolierten TASK-090-Worktree abgenommenen Relay-Deskriptoren in Relay-`main` ist **kein Abschlusskriterium dieser Mile**. Sie ist ein separater Schritt, der **vor einer dauerhaften Verbraucher-Bindung** an diese Deskriptoren erforderlich ist; danach sind die Pins am integrierten Stand erneut zu prüfen. [Scope-Entscheidung und Abschluss](../10-Evidence/MILE-020/CLOSURE.md).

## Aufwand

Schätzung 2–3 PT, unsicher vor allem bei D-1 und der Abstimmung mit dem Relay-Repo.

## Ausführungsplanung (2026-11-06)

[EPIC-014](../03-Epics/EPIC-014-module-capability-descriptors.md) zerlegt die Mile in US-038–041 und TASK-086–094. Führender Status: [OpenSpec-Checkliste](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md); [Abnahmespur](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/TRACEABILITY.md).

D-1 ist mit [TASK-086](../10-Evidence/MILE-020/TASK-086-RESULT.md) entschieden; [TASK-087](../10-Evidence/MILE-020/TASK-087-RESULT.md) hat das Format und seine Offline-Prüfung geliefert. D-2 ist mit [TASK-088](../10-Evidence/MILE-020/TASK-088-RESULT.md) entschieden und im Lib-Repo umgesetzt. [TASK-089](../10-Evidence/MILE-020/TASK-089-RESULT.md) hat Toolbox- und Connector-Owner-Artefakte samt Pin-Prüfung geliefert; [TASK-090](../10-Evidence/MILE-020/TASK-090-RESULT.md) ergänzt Cube und drei logische Relay-Rollen sowie den gesondert geprüften Connector-Paketbestand. [TASK-092](../10-Evidence/MILE-020/TASK-092-RESULT.md) hat D-4 geklärt. D-3 ist in [ADR-001](../07-ADR/ADR-001-lib-snapshot-host-path.md) unverändert dokumentiert. Die Owner-Matrix erfasst die sieben logischen MILE-071-Rollen einschließlich Server GUI und den internen Connector-Bereich `translator/`, ohne daraus eigenständige Produkte abzuleiten. Bytegleichheit gilt für den neuen neighbors-Inhalt; bestehende oberflächenspezifische Felder bleiben unverändert.

Detailplanung: 2,5–4,5 PT ohne Entscheidungswartezeit und gesonderte Bereitstellung. Die ursprüngliche Schätzung oben bleibt als Ausgangswert sichtbar. Die sechs Kriterien sind in [TASK-094](../10-Evidence/MILE-020/TASK-094-RESULT.md) für den benannten Stand abgenommen; die Mile ist mit [CLOSURE](../10-Evidence/MILE-020/CLOSURE.md) formal geschlossen. Eine dauerhafte Relay-Integration ist ein separater Folgeschritt außerhalb dieser Mile.
