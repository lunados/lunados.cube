# MILE-022 — Workflow Builder

Status: **geplant (Entwurf)** · Stand: 2026-11-06 · Abhängig von [MILE-020](MILE-020-module-capability-descriptors.md) und der Abnahme von lunados.connector MILE-004 · Betrifft: lunados.workflow (neu), lunados.connector, lunados.cube, agent-relay-poc-v3

## Ziel und Entscheidung

Aus einer gesprochenen oder geschriebenen Beschreibung soll eine eindeutige Pipeline entstehen, deren Schritte den passenden Modulen zugeordnet sind. Der bisherige „TOML Builder“ heißt künftig neutral **Workflow Builder** (Nutzer, 2026-11-06); TOML ist das Format, nicht die Aufgabe.

Zuständigkeiten bleiben getrennt:

| Schritt | Zuständig |
|---|---|
| Pipeline vorschlagen und Schritte Modulen zuordnen | Workflow Builder |
| Fähigkeiten der Module | Deskriptoren aus MILE-020; der Builder liest sie nur |
| Form der Pipeline prüfen | Cube, Kontrollfluss-Profil P1.13 (`binding-context/9`) |
| Zulassung und Ausführung | Relay-Preflight und Relay-Loader |

## Ausgangslage (2026-11-06)

lunados.connector MILE-004 (in Review) liefert `agent/AIAEAO-TOML.md`, die Schemas in `schema/aiaeao-toml/` und `scripts/check_toml.py`. Die Regeln sind aus den Relay-Loadern übertragen (agent-relay-poc-v3 @ `6d6f62d`, Loader per SHA-256 gepinnt). Ablage im Connector war Entscheidung D-1 von MILE-004. Nach MILE-071 gehört das Zerlegen von Arbeit und die Zuordnung zu Modulen jedoch zur App bzw. zum Application Service; der Connector transportiert und übersetzt.

## Arbeitsumfang

1. **Eigenes Repository anlegen** (D-1, Arbeitsname `lunados.workflow`) und MILE-004 D-1 im Connector entsprechend fortschreiben. App und Agenten nutzen den Builder; der Connector verweist nur noch darauf.
2. Referenz, Schemas und `check_toml.py` mit Hash übernehmen; der Connector verweist danach nur noch darauf.
3. **Zuordnung Schritt → Modul** ausschließlich aus den MILE-020-Deskriptoren. Fehlt eine passende Fähigkeit, stellt der Builder eine Frage oder markiert `unknown`; er setzt keinen Standard.
4. **Formprüfung im Cube:** eine erzeugte Pipeline zusätzlich als Aussagenmenge für `binding-context/9` ausgeben, damit P1.13 sie prüfen kann. Die Abbildung TOML → Cube festlegen (D-2), gegebenenfalls als Übersetzungstabelle im Connector.
5. Der Format-Check des Builders bleibt ein Format-Check; der Relay-Preflight bleibt die Autorität.

## Entscheidungen

| ID | Frage | Optionen |
|---|---|---|
| D-1 | Ablage des Workflow Builders | **Entschieden (Nutzer, 2026-11-06): eigenes Repository**, Arbeitsname `lunados.workflow`. Nach MILE-071 bleibt die App Verbraucher; das Zerlegen von Arbeit in Schritte liegt im Builder, die fachliche Bedeutung der Ergebnisse weiter in der App. |
| D-2 | Abbildung Pipeline → Cube | eigenes P1.13-Mapping · Connector-Übersetzungstabelle |

## Abnahme

- [ ] Repository angelegt; Name „Workflow Builder“ in allen Verweisen.
- [ ] Referenz, Schemas und Prüfskript liegen am neuen Ort, gepinnt; der Connector verweist darauf.
- [ ] Für mindestens zwei Beschreibungen (eine Legacy-Pipeline, ein Starter Kit) entsteht je eine TOML-Datei mit Zuordnung zu Modulen laut Deskriptor oder einer benannten offenen Frage.
- [ ] Beide Pipelines bestehen die Cube-Prüfung mit P1.13 und den Relay-Preflight; Abweichungen sind dokumentiert.

## Nicht in MILE-022

Ausführung von Pipelines; automatische Übersetzung von Legacy-YAML (MILE-004 D-2 gilt weiter); eigene Fähigkeitslisten im Builder.

## Aufwand

Schätzung 2–3,5 PT, unsicher vor allem bei D-2.
