> Archivierte Research-Baseline. Diese Kopie wird im lokalen lunados.space-Repository unter `web/docs/research/cube-interop-2026-11-01/` abgelegt. Historische Aussagen zur fehlenden SPACE-Ablage und zu noch nicht ausgeführten Prüfungen beschreiben den früheren Stand. Maßgeblich für den aktualisierten Arbeitsstand sind [Analyse](ANALYSE.md) und [Roadmap](README.md). Keine Online-Veröffentlichung durch diese Ablage.

# Lunados Cube — Grammatikvergleich & MCP-Reevaluation

**Research-Handover / Stand:** 1. November 2026  
**Kontext:** AIAEAO / Lunados Cube als eigenständige Modellierungs- und Grammatikschicht  
**Status:** Research konsolidiert; lokaler P3-MCP-Zugang durch Discovery bestätigt; **keine** abgeschlossene interne Konformitätsprüfung  
**Ziel:** In einer neuen lokalen Codex-/ChatGPT-App-Unterhaltung mit aktiviertem internem Cube-MCP die fünf Vergleiche gegen die **tatsächliche interne Implementierung** erneut durchführen.

> **Wichtige methodische Grenze:** Die ursprüngliche Research-Unterhaltung wurde im Browser begonnen und anschließend in der App fortgeführt. Für die Analyse war **nur der öffentliche, read-only Cube** verfügbar. Der lokale P3-MCP-Server war dort nicht als Tool zugänglich. Die in der ersten Vergleichsrunde benannten „Lücken“ können daher lediglich Lücken der öffentlichen Referenz, eines dort sichtbaren Funktionsprofils oder des Nachweises sein — **nicht automatisch Lücken des internen Cube**.

---

## Übergabestatus und Leseschlüssel

**Konsolidierte Fassung vom 1. November 2026 (Europe/Berlin).** Grundlage ist die vom Nutzer bereitgestellte Datei `Lunados_Cube_Grammar_Research_Handover.md` aus der Browser-Unterhaltung [„Laufzeiten erklären“](chatgpt-conversation://6ae12b0a-bd34-83eb-b58a-1773df6c913b). Die ursprüngliche Datei bleibt unverändert.

- **Historischer Research:** Abschnitte 1–10, 12–13 und 15 bewahren die gelieferten Vergleichsergebnisse, Korrekturen und Hypothesen. Sie sind keine neue Prüfung der Fremdstandards oder der internen Implementierung.
- **Offene Folgearbeit:** Abschnitte 11 und 14 enthalten den Prüfplan und einen vorgeschlagenen Folgeauftrag. Die enthaltenen Anweisungen wurden für diese Übergabe nicht als Auftrag zur Ausführung der Experimente übernommen.
- **Aktuell beobachtet:** Abschnitt 16 dokumentiert die tatsächlich erhaltenen Public-Manifest- und lokalen P3-Discovery-Antworten. Abschnitt 17 präzisiert die daraus folgenden offenen Prüfaufträge.
- **Ablage:** Diese Datei wurde lokal im AIAEAO-Arbeitsbereich erstellt. Sie wurde **nicht in Lunados SPACE hinterlegt**: Es war kein entsprechendes verbundenes Schreibwerkzeug verfügbar; die Pluginsuche nach „Lunados SPACE“ lieferte keine Treffer. Dies ist eine Feststellung zur verfügbaren Anbindung, keine Aussage darüber, ob der Dienst oder ein Workspace existiert.

**Entscheidender Stand:** Die fünf Vergleiche rechtfertigen bislang keine Änderung der kanonischen Morphologie. Die interne Verfügbarkeit der dafür benötigten Contracts, Analysefunktionen und Ausführungssemantik ist weiterhin zu prüfen. Der nun bestätigte MCP-Zugang beseitigt die frühere Zugriffshürde, ersetzt diese Prüfung aber nicht.

---

## 1. Ausgangspunkt und Fragestellung

Ein praktisches Refactoring-Experiment zeigte für den Cube bereits eigenständigen Nutzen: Ein komplexer, mehrere Tools umfassender Ablauf ließ sich in eine eindeutige, kompakte, programmierbare Grammatik überführen. Dadurch wurden Knotenpunkte und Abhängigkeiten sichtbar; die Achsenzuordnung half bei der Visualisierung.

Daraus entstand die Frage, ob **Lunados Cube als Standalone** vermarktet werden kann, getrennt von der AIAEAO-Server-/Browser-App.

Diskutiertes Produktmodell:

| Stufe | Möglicher Umfang | Vorläufige Rolle |
|---|---|---|
| Cube Reference | Öffentliches Handbuch, Morphologie, Notation, Beispiele, read-only Referenz / ChatGPT-Plugin | Einstieg und Standardisierung |
| Cube Studio | Lokales Modellieren, Visualisieren, Validieren, Import/Export | Adoption durch Entwickler und Architekten |
| Cube Sync | Versionierte, persistente Workspaces, Write-API, Datenbank, Synchronisierung | Kommerzielles Angebot |
| Enterprise | Teams, Berechtigungen, Auditing, privates Hosting und Integrationen | Erweiterung für Organisationen |

**Produktthese:** Der Cube ist weder bloß eine Diagrammsprache noch zwingend eine eigene Workflow-Engine. Er könnte als **semantisch qualifiziertes Referenzmodell** dienen, aus dem spezialisierte Architektur-, Prozess- und Graphprojektionen erzeugt und analysiert werden. Diese Positionierung ist eine **Hypothese**, noch kein Markt- oder Interoperabilitätsnachweis.

**Wichtige Produktentscheidung als Vorschlag:** Lokales Authoring nicht zwingend monetarisieren; wirtschaftlichen Wert eher in Sync, gemeinsamer Modellverwaltung, Versionierung, Berechtigungen und nachvollziehbaren Ableitungen suchen.

---

## 2. Welche Cube-Quelle wurde tatsächlich geprüft?

Verfügbar war die öffentliche, versionierte **Cube-v9.4-Referenz**, u. a.:

- Manifest: <https://cube.lunados.net/manifest.json>
- Dokumentarische Morphologie: <https://cube.lunados.net/v9.4/morphology.md>
- Core: <https://cube.lunados.net/v9.4/core.json>
- Time: <https://cube.lunados.net/v9.4/time.json>
- Observer: <https://cube.lunados.net/v9.4/observer.json>
- Konzepte: <https://cube.lunados.net/v9.4/grammar/concepts.json>
- Relationen: <https://cube.lunados.net/v9.4/grammar/relations.json>
- Constraints: <https://cube.lunados.net/v9.4/grammar/constraints.json>
- ACG-Notation: <https://cube.lunados.net/v9.4/notation/syntax.json>
- EBNF: <https://cube.lunados.net/v9.4/notation/grammar.ebnf>
- AST-Schema: <https://cube.lunados.net/v9.4/notation/ast.schema.json>
- Agent-Anleitung: <https://cube.lunados.net/v9.4/agent-guide.md>
- Public Validation Manifest: <https://cube.lunados.net/validation/v1/manifest.json>
- Public P1-Konformitätsindex: <https://cube.lunados.net/validation/v1/conformance.json>

Die öffentliche Referenz weist ausdrücklich darauf hin, dass:

- **X/Y/Z** die primären *Ontology Definition Homes* sind; **T/F/M/O** sind Qualifikationen, keine zusätzlichen Ontologie-Homes.
- Die Schichten **α/β/ζ** unterschiedliche Bindungs-/Materialisierungskontexte repräsentieren; Bindung heißt nicht Informationsauslöschung.
- **ACG** u. a. `Reference`, `Qualified`, `Relation`, `Application` ausdrücken kann.
- Eine strukturell gültige Notation / AST **keine** semantische Wahrheit, erfolgreiche Ausführung, aktuelle Authority oder Admission beweist.
- Ein universelles, produktionsverbindliches REL-Prädikatsregister in der öffentlichen v9.4-Referenz nicht als abgeschlossen vorausgesetzt werden darf.
- Das öffentliche P1-Validierungsprofil getrennte Prüfstufen vorsieht, aber `epistemic_warrant`, `current_authority` und `canonical_admission` als **NOT_EVALUATED** ausweist.

**Nicht geprüft:** Interne Morphologie-/Contract-Erweiterungen, konkrete Function-Library-Registry und ihr Implementierungsstand, interne MODE-Verträge, Transitionen, Runtime-Prozesse sowie der verfügbare Toolumfang des lokalen P3-MCP-Servers.

### 2.1 Vier getrennte Ebenen für die Reevaluation

1. **Morphologie:** Was ist grundsätzlich ausdrückbar?
2. **Grammatik / Contracts / Constraints:** Was ist wohlgeformt, gebunden und semantisch zulässig?
3. **Function Library:** Was ist algorithmisch berechenbar, ableitbar oder projizierbar?
4. **MODE / Runtime:** Unter welchen Interaktions-/Ausführungsbedingungen können Funktionen ausgeführt und Zustände verändert werden?

Jede behauptete „Lücke“ muss zunächst einer dieser Ebenen zugeordnet werden.

---

## 3. Einheitliches Prüfschema

Die fünf Vergleiche wurden entlang derselben sechs Gesichtspunkte diskutiert:

| Prüfkriterium | Frage |
|---|---|
| Ontologie | Welche Konzepte, Identitäten und Objekttypen gibt es? |
| Grammatik | Wie werden Referenzen, Beziehungen und Regeln ausgedrückt? |
| Topologie | Wie werden Hierarchie, Abhängigkeit, Grenze und Struktur organisiert? |
| Dimensionen | Wie werden Zeit, Funktion, Betriebsregime, Beobachtung und Status behandelt? |
| Constraints | Was wird definiert bzw. tatsächlich validiert? |
| Interoperabilität | Was ist verlustfrei abbildbar, was benötigt ein Profil, was ist lossy / unresolved? |

**Grundsatz:** Eine vorhandene Ausdrucksmöglichkeit ist nicht automatisch eine implementierte Funktion. Ein vorhandener Algorithmus ist nicht automatisch eine semantisch gerechtfertigte Ableitung. Die Konformität einer Fremdnotation ist nicht gleich Cube-Konformität.

---

## 4. Vergleich 1 — Structurizr / C4

### 4.1 Erste Einordnung

- **C4** arbeitet mit Architekturabstraktionen wie Person, Software System, Container, Component; Structurizr ergänzt Deployment-Elemente, Beziehungen und unterschiedliche Views.
- **Cube** klassifiziert Referenten über X/Y/Z und qualifiziert sie über T/F/M/O sowie α/β/ζ.
- Structurizr stellt ein gut nutzbares, etabliertes deklaratives Workspace-/DSL-Konzept und mehrere Architekturprojektionen bereit.
- Eine 1:1-Zuordnung „C4 Container = bestimmtes Z-Konzept“ ist **nicht** ohne Profil gerechtfertigt.

### 4.2 Streitpunkt: *Implied relationships*

In der ersten Analyse hieß es, Structurizr könne Beziehungen auf übergeordneten Ebenen automatisch ableiten; im Cube dürfe aus einem Pfad nicht einfach ein neues Prädikat gefolgert werden.

**Korrektur aus der Diskussion:** Die Cube-Morphologie enthält bereits Projection / Derivation sowie die Unterscheidung von Ebenenbindung und Informationsverlust. Das grundsätzliche **Ableiten verdichteter Sichten** ist deshalb nicht als morphologische Lücke anzusehen.

**Wichtige Präzisierung:**

- Eine aus Komponentenbeziehungen errechnete **übergeordnete View-Beziehung** darf als Projektion/Aggregation erscheinen.
- Das berechtigt **nicht** dazu, dieselbe Relation als eigenständige, nachgewiesene semantische Tatsache über die Elternreferenten auszugeben.
- Es braucht Herkunft, verwendete Aggregationsregel, Scope, mögliche Informationsverluste und einen klaren Status als *abgeleitet*.

**Offene P3-Prüfung:** Gibt es in F / Function Library bereits `project`/`derive` bzw. ein passendes Aggregationsprofil mit Source Trace und Loss Accounting? Können zwei konkrete C4-Modellstufen konsistent und rückverfolgbar projiziert werden?

**Vorläufige Entscheidung:** Keine Änderung der Morphologie; ein optionales **C4 Foreign Mapping / Projection Profile** prüfen.

---

## 5. Vergleich 2 — ArchiMate

### 5.1 Erste Einordnung

- ArchiMate besitzt eine spezialisierte Enterprise-Architecture-Ontologie mit Architekturelementen, Motivation, Verhalten und typisierten Beziehungen.
- Cube verfolgt eine andere Klassifikationslogik: Referenten und Grenzen, Semantik, Methoden, Zeit und Beobachtung werden getrennt betrachtet.
- ArchiMate ist bei Architektur-Relationssignaturen und zulässigen Typkombinationen ein anspruchsvoller Referenzmaßstab; daraus folgt keine allgemeine ontologische Überlegenheit gegenüber Cube.
- Ein ArchiMate-Goal ist nicht automatisch dieselbe Entität wie eine Cube-Expectation, ein Outcome nicht automatisch Cube-Result; ein modelliertes Event nicht automatisch ein kanonisch aufgenommenes Cube-Event.

### 5.2 Streitpunkt: Kardinalitäten

Die erste Analyse stellte ArchiMate-Kardinalitäten einer angeblich nicht etablierten allgemeinen Relationskardinalität im Cube gegenüber.

**Korrektur:** Die Cube-Morphologie enthält bereits **feste ontologische Kardinalitätsregeln**, etwa die Struktur der fünf X-Dimensionen mit je einem Scope und zwei komplementären Endpunkten. Laut Nutzer existieren im internen Cube weitere Kardinalitätsfestlegungen; Umfang noch nicht eingesehen.

Drei **nicht zu vermischende** Begriffe:

| Art | Beispiel / Prüfgegenstand |
|---|---|
| Ontologische Kardinalität | Wie viele definitorische Bestandteile sind an einem Cube-Konzept zulässig? |
| Relationskardinalität | Wie viele kompatible Instanzen dürfen an einem Relationstyp hängen (`0..1`, `1..*` usw.)? |
| Ausführungskardinalität | Wie viele Signale/Beteiligungen müssen vor einer Transition vorliegen? |

**Offene P3-Prüfung:** Sind Relations-Endpunktmultiplizitäten durch interne Contracts bereits ausdrückbar und validierbar? Sind sie kanonisch fest oder in versionierten Foreign Profiles einschränkbar?

**Vorläufige Entscheidung:** Kein Beleg für eine morphologische Lücke. Falls frei konfigurierbare Fremd-Kardinalitäten benötigt werden, diese eher als **versionierte Relationsprofil-Regeln** statt als Mutation der kanonischen Ontologie behandeln.

---

## 6. Vergleich 3 — DSM / MDM

### 6.1 Erste Einordnung

- **DSM (Design Structure Matrix)** stellt gerichtete Abhängigkeiten zwischen Elementen einer Domäne in einer Matrix dar.
- **DMM (Domain Mapping Matrix)** verbindet verschiedene Domänen; **MDM (Multiple Domain Matrix)** kombiniert mehrere DSM/DMM-Sichten.
- Typische Analysen: Clustering, Partitioning, Sequencing, Cycle Detection, Erreichbarkeit, Change Propagation / Impact Analysis und Tearing.
- Cube kann geeignete Referenten, Relationstypen und Gültigkeitskontexte für eine DSM-/MDM-Projektion liefern.

### 6.2 Streitpunkt: Algorithmische Ausgereiftheit

Die erste Formulierung „DSM algorithmisch deutlich ausgereifter“ war für einen Architekturvergleich zu pauschal.

**Korrektur:** Die Algorithmen gehören sachgerecht in die **Function Library**, nicht in den kanonischen Ontologie-Kern. Der Cube kann ein Modell darstellen, eine DSM/MDM als Projektion erzeugen und F-Funktionen zur Analyse nutzen, **sofern sie intern implementiert sind**.

Potenzielle Funktionsfamilien:

| Analyse | Funktionskandidat |
|---|---|
| Zyklen | Strongly Connected Components / Cycle Detection |
| Cluster | Graph Clustering |
| Partitionen | Dependency Partitioning |
| Reihenfolge | Topological Sorting / Sequencing |
| Erreichbarkeit | Reachability / Traversal |
| Änderungen | Impact / Change Propagation |
| Rückkopplungen | Feedback Edge Analysis / Tearing |

**Qualitätsanforderung:** Ein Algorithmus kann **strukturelle Erreichbarkeit** berechnen, ohne damit **wirkliche Kausalität oder bestätigte Änderungsauswirkung** zu beweisen. Herkunft und Rechtfertigung der ausgewählten Kanten müssen sichtbar bleiben.

**Offene P3-Prüfung:** Welche dieser Funktionen sind tatsächlich in der Library-Registry vorhanden? Welche Signaturen, Typen, Negative Tests und Konformitätsprofile gelten? Gibt es eine DSM- bzw. MDM-Projektion ohne Datenmodelländerung?

**Vorläufige Entscheidung:** Kein Anlass für eine morphologische Erweiterung. DSM/MDM ist ein starker Kandidat für einen **praktischen Analytik-Proof** anhand des vorhandenen Refactorings.

---

## 7. Vergleich 4 — BPMN

### 7.1 Erste Einordnung

- BPMN modelliert Prozesse mit Activities, Events, Gateways, Sequence Flows, Message Flows, Participants/Lanes, Datenobjekten etc.
- BPMN besitzt spezifische **Control-Flow- und Token-Semantik** für Abzweigungen, Synchronisation, Schleifen, Exceptions und weitere Ausführungsfälle.
- Cube kann Prozessreferenten und typisierte Beziehungen konzeptionell einordnen; aus einer Graphstruktur folgt aber nicht automatisch eine BPMN-konforme Aktivierung/Synchronisation.

### 7.2 Streitpunkt: Sequence Flow und MODE

**Nutzerhypothese:** Kann MODE die in der ersten Analyse behauptete Control-Flow-Lücke adressieren?

**Korrigierte Antwort:** Teilweise. Ein plausibles Zuständigkeitsmodell lautet:

| Cube-Ebene | Rolle |
|---|---|
| Y/Z + Relationsprofile | Prozessreferenten, Grenzen und gerichtete Beziehungen |
| F / Function Library | Übergangsregeln, Entscheidung, Aktivierung, Synchronisation |
| M / MODE | Betriebs- bzw. Interpretationsregime, in dem diese Regeln verwendet werden |
| T/O/X | Zeitbezug, Beobachtung, Ausführungsnachweise, Governance und epistemische Bewertung |

Die operative **Ausführungssemantik** muss explizit sein: `MODE` allein als Kennzeichnung eines Regimes garantiert noch nicht, dass z. B. ein Join auf alle erforderlichen Signale wartet. Es kann sein, dass die interne Implementierung dafür bereits geeignete Mode-/Transition-Contracts hat — dies ist über P3 zu prüfen.

### 7.3 Gateway- und Token-Semantik als Profil, nicht sofort neue Ontologie

Ein empfohlenes Prüf-/Designmodell ist ein **versioniertes Control Flow Semantics Profile**, das auf vorhandenen Achsen, Relationsprofilen, F und M aufsetzt.

| Gateway | Notwendige ausführungsbezogene Regel |
|---|---|
| XOR Split | Genau eine zulässige Alternative wählen |
| AND Split | Alle definierten Ausgangspfade aktivieren |
| AND Join | Erst bei Vorliegen aller erforderlichen Eingangssignale fortfahren |
| OR Split | Eine oder mehrere Alternativen aktivieren |
| OR Join | Korrekte Synchronisation tatsächlich aktivierter und noch relevanter Pfade |
| Event-Based | Warten/Auswahl aufgrund eintretender Ereignisse |

**Token-Unterscheidung:** Ein temporärer Token-/Aktivierungszustand einer Prozessinstanz ist **nicht automatisch** ein kanonischer Cube-Event oder Beleg für erfolgte Ausführung.

Mindestens zu klären:

- Identität der Prozessinstanz und Modellrevision
- Korrelation und aktuelle Position im Ablauf
- Aktivierungs- und Konsumbedingungen
- Join-/Split-Semantik, Zähl-/Wiederholungsregeln
- Exceptions, Timeouts, Retries und Compensation (spätere Stufe)
- Trennung von geplanter Aktivierung, tatsächlichem Effekt und nachgewiesenem Result

**Minimaler Konformitätsumfang:** XOR, AND Split, AND Join, Loop; anschließend OR Join, Event-Based Gateway, Cancellation und Compensation.

**Offene P3-Prüfung:** Sind diese Zustände und Transitionen bereits in MODE-/F-/Runtime-Verträgen vorhanden? Welche Semantik ist dokumentiert, welche ausführbar, welche durch Tests gedeckt?

**Vorläufige Entscheidung:** Mögliche **Spezialprofil-Lücke**, nicht automatisch eine neue morphologische Kategorie. Der Cube muss keine eigenständige BPMN-Engine nachbauen.

### 7.4 BPMN-Integrationsrichtungen

1. **BPMN → Cube:** Prozessdefinition importieren und semantisch qualifizieren.
2. **Cube → BPMN:** Nur ausreichend determinierte Kontrollflussmodelle projizieren.
3. **BPMN-Ausführung → Cube:** Tatsächliche Ausführungsnachweise einer externen Engine beobachten und korrekt einordnen.

Vorläufig besonders interessant: **Variante 3**, weil der Cube die Unterscheidung zwischen Execution, Result, Verification und Satisfaction liefern kann, ohne selbst Prozessausführung übernehmen zu müssen.

---

## 8. Vergleich 5 — DAG

### 8.1 Erste Einordnung

Ein **Directed Acyclic Graph** ist ein gerichteter Graph ohne gerichtete Zyklen. Er ist eine mathematische Struktur, **keine eigenständige universelle Prozessontologie**. Bei Airflow, Dagster und vergleichbaren Systemen kommen domänenspezifische Scheduling-/Runtime-Regeln hinzu.

**Cube-Bezug:** Eine geeignete Auswahl typisierter Cube-Relationen könnte als DAG projiziert werden; die Cube-Topologie als Ganzes muss **nicht** azyklisch sein.

### 8.2 Algorithmen und Grenzen

| Analyse | Ergebnis |
|---|---|
| Cycle Detection | Feststellen, ob der gewählte Teilgraph ein DAG ist |
| Topological Sort | Zulässige Reihenfolgen, nicht zwingend eindeutige Reihenfolge |
| Reachability | Vor- und Nachfolger / strukturelle Wirkungsketten |
| Topological Generations | Potenziell unabhängig bearbeitbare Ebenen |
| Critical Path | Pfadanalyse bei geeigneten Gewichten und Scheduling-Annahmen |

**Wichtige Unterscheidungen:**

- `A references B` ist **nicht** automatisch `B muss vor A ausgeführt werden`.
- Ein zyklenfreier Graph kann fachlich falsche Abhängigkeiten enthalten.
- Ein fachlich korrekter Cube-Beziehungsgraph kann Zyklen enthalten; nur die ausgewählte DAG-Projektion wäre dann ungültig.
- Ein geplanter Task / eine Kante ist kein Beweis der tatsächlichen Ausführung.

### 8.3 Vorgeschlagenes DAG Projection Profile

`Select → Filter → Qualify → Project → Validate → Analyze`

- *Select:* geeignete Referenten (z. B. Work Items) wählen.
- *Filter:* nur gebundene und zulässige Dependency-Prädikate.
- *Qualify:* Scope, Zeitkontext, Revision, Evidenzstatus und Quellen berücksichtigen.
- *Project:* Knoten/Kanten inkl. Richtung und Source Mapping erzeugen.
- *Validate:* Zyklenfreiheit und Identitäts-/Graphintegrität prüfen.
- *Analyze:* Reihenfolge, Erreichbarkeit, Parallelisierung etc. berechnen.

**Offene P3-Prüfung:** Liegen Auswahl-, Projektions-, Validierungs- und Analysefunktionen bereits intern vor? Welche Teilmengen sind supported, welche unresolved? Können graphische Ergebnisse wieder auf originale Referenten zurückgeführt werden?

**Vorläufige Entscheidung:** DAG eignet sich besonders gut als **abgeleitete Projektion**, ohne die Morphologie zu verändern.

---

## 9. Konsolidierte Vergleichsmatrix (Stand: vor interner MCP-Prüfung)

| Referenz | Primäre Stärke | Potenzielle Cube-Rolle | Wichtigste offene Prüfung |
|---|---|---|---|
| **Structurizr / C4** | Deklaratives Architekturmodell, Views, implied relations | Architecture Projection / Foreign Mapping | Aggregation inkl. Provenance und Loss Reporting |
| **ArchiMate** | Breite, typisierte Enterprise-Architektursemantik | Semantic Mapping / Relationsprofil | Relationsmultiplizitäten und semantische Gleichwertigkeit |
| **DSM / MDM** | Kopplung, Cluster und Abhängigkeitsanalyse | Graph-/Matrixprojektion + F-Analyse | Konkrete Algorithmen der Function Library |
| **BPMN** | Prozesslogik, Gateways, Token-Semantik | Control-Flow-Profil und Execution Trace Mapping | MODE/F-Transitions, Synchronisation, Token-State |
| **DAG** | Mathematische Reihenfolge-/Erreichbarkeitsanalyse | DAG Projection + F-Analyse | Dependency-Prädikate, Cycle Gate, Rückverfolgbarkeit |

**Nicht nachgewiesen:** Vollständige wechselseitige Interoperabilität, verlustfreie Roundtrips, alle Function-Library-Algorithmen, universelle Gateway-Semantik und vollständige Runtime-Konformität.

---

## 10. Die fünf expliziten Korrekturen aus der Diskussion

| Frühere problematische Aussage | Korrigierte Lesart | P3-Nachweis |
|---|---|---|
| C4 implied relationships fehlen / widersprechen Cube-Regeln | Projektion/Derivation und kontrollierter Informationsverlust sind konzeptionell vorhanden; Ableitung darf nicht still als neue Tatsache gelten | Projektions-/Ableitungs-Contract + C4-Beispiel |
| ArchiMate-Kardinalität sei beim Cube nicht vorhanden | Feste ontologische Kardinalitäten existieren; Relations-/Ausführungskardinalitäten gesondert prüfen | interne Cardinality-/REL-Constraints |
| DSM sei dem Cube als Architektur algorithmisch überlegen | DSM-Algorithmen gehören sinnvoll in die Cube Function Library; Verfügbarkeit prüfen | Function Registry + echte Aufrufe/Tests |
| BPMN Sequence Flow und Synchronisation seien grundsätzlich fehlend | Gerichtete Relationen und F/M können eine Basis sein; operative Transitionen benötigen explizite Semantik | MODE- und Transition-Contracts |
| Gateway-/Token-Semantik erfordere neue Morphologie | Zuerst spezialisiertes Control-Flow-Profil und temporären Instanzzustand prüfen; neue kanonische Konzepte nur bei nachgewiesener Notwendigkeit | XOR/AND/Loop-Tests, danach weitere Gateways |

**Zentrales Ergebnis:** Aus der Public-only-Analyse ergibt sich **kein belastbarer Anlass**, die kanonische Cube-Morphologie zu ändern. Das bedeutet **nicht**, dass sämtliche benötigten Contracts/Library-Funktionen intern bereits vorhanden sind.

---

## 11. Konkrete MCP-Reevaluation im neuen Chat

### 11.1 Verbindungs- und Toollage

Die funktionierende Claude-Konfiguration für den lokalen Cube-P3-MCP-Server war:

```json
{
  "aiaeao-cube": {
    "command": "/Users/johannesklapproth/SitesHeroku/lunados.cube/P3/adapters/mcp-local/.venv/bin/python",
    "args": [
      "-u",
      "/Users/johannesklapproth/SitesHeroku/lunados.cube/P3/adapters/mcp-local/run_server.py"
    ]
  }
}
```

Die entsprechende `~/.codex/config.toml` wurde im Verlauf der Unterhaltung vom Nutzer angepasst. Ein neues **lokales** App-Fenster ermöglicht laut Nutzer den `/mcp`-Aufruf; die aus dem Browser fortgeführte Unterhaltung hatte diesen lokalen MCP-Kontext nicht übernommen. **Historischer Stand:** Der interne Toolzugriff musste noch bestätigt werden. **Aktualisierung dieser Übergabe:** Der lokale Aufruf von `cube_discover_surface` war erfolgreich; die konkrete Oberfläche und ihre Grenzen sind in Abschnitt 16 festgehalten. In einer weiteren neuen Unterhaltung ist die dort tatsächlich verfügbare Verbindung erneut zu entdecken.

Es gibt außerdem Public-Reference-Plugins. Die geprüften Plugin-Dateien enthielten jeweils nur `cube-public-reference` über einen HTTP-MCP-Endpunkt. Die Public-Verbindung ist **keine** interne P3-Verbindung. Die Kompatibilität mit Claude erfordert **keine** Änderung des bestehenden Python-Servers und keine Aktualisierung von Claude, solange sich die gemeinsame MCP-Schnittstelle nicht inkompatibel ändert.

### 11.2 Minimaler Startablauf

1. **Interne Toolentdeckung:** Im neuen lokalen Chat bestätigen, welche P3-MCP-Tools tatsächlich sichtbar und erreichbar sind. Keine internen Toolnamen erfinden.
2. **Versionen:** `version`, Profile, Registry-/Contract-Revision und ggf. Engine-/Adapter-Version lesen, sofern Tools vorhanden.
3. **Capabilities / Contracts:** Morphologie, interne Notation, Relations-/Kardinalitätsverträge, Library Registry, MODE, Transition-/Runtime-Semantik inspizieren.
4. **Public-vs-Internal-Diff:** Für die fünf Untersuchungsgebiete getrennt festhalten, was Public dokumentiert und intern zusätzlich nachweisbar ist.
5. **Fünf gezielte Konformitätsexperimente** ausführen (siehe nächste Tabelle), möglichst mit Positiv-, Negativ- und Unresolved-Fällen.
6. **Bewerten:** Nicht allein `PASS`, sondern Interpretation, Datenbasis, Fehleradressen, Loss Report, Quellen und Grenzen dokumentieren.
7. **Ergebnis liefern:** Aktualisierte Vergleichsmatrix und nur tatsächlich notwendige Vorschläge für Profile, Functions oder Morphologie.

### 11.3 Vorgeschlagene Experimente

| ID | Bereich | Positiver Fall | Negativ-/Grenzfall | Erwartete Aussage |
|---|---|---|---|---|
| E1 | C4 Projection | Zwei Komponentenrelationen korrekt zu System-View aggregieren | Unzulässige semantische Vererbung als Tatsachenprädikat | Ableitung ist quellgebunden und als Projektion markiert |
| E2 | ArchiMate Cardinality | Feste oder profilgebundene Mindest-/Höchstbelegung prüfen | Zu viele/zu wenige Relationspartner | Exakte Cardinality-Constraint und Diagnose |
| E3 | DSM Library | Abhängigkeitsmatrix mit SCC/Clustern analysieren | Ungebundene oder semantisch ungeeignete Kanten | Graphanalyse getrennt von Evidenzanspruch |
| E4 | BPMN/F/M | XOR, AND Split/Join, Loop korrekt aktivieren/synchronisieren | Vorzeitiger Join; unkorrelierte Tokens | Kontrollflusssemantik ist spezifiziert/prüfbar oder offen |
| E5 | DAG Projection | Azyklische Work-Item-Relationen topologisch sortieren | Zyklus, falscher Dependency-Typ | DAG-Gate gilt nur für ausgewählten Teilgraphen |

### 11.4 Bewertungskategorien

Jeder Befund ist ausdrücklich einer Kategorie zuzuweisen:

- **A — Implementiert und geprüft:** Contract + callable Function/Runtime + unabhängige Tests vorhanden.
- **B — Formal spezifiziert, Implementierung unbestätigt:** klare Regel/Profil ohne gesicherten Laufzeitnachweis.
- **C — Durch versioniertes Mapping-/Function-Profil ergänzbar:** kein Eingriff in kanonische Morphologie nötig.
- **D — Echte morphologische Lücke:** weder vorhandene Ausdrucks-/Contract-Mittel noch Profilmechanik reichen aus; Beweis durch konkreten Gegenfall.
- **U — Unresolved:** notwendige Registry, Bindung, Evidenz oder Toolzugriff fehlt; nicht automatisch FAIL.

### 11.5 Reproduzierbarkeits- und Sicherheitsanforderungen

- Public und Internal Cube inklusive Profil-/Build-Version voneinander unterscheiden.
- Interne Funktionen zunächst **read-only / side-effect-free** testen, sofern möglich.
- Foreign IDs nicht mit kanonischen Identitäten oder authentifizierten Principals gleichsetzen.
- Parserfolg nicht mit Wahrheit, Verifikation, Authority, Admission, Completion oder Satisfaction gleichsetzen.
- Profilabhängige Semantik und notwendige Quellenbindung angeben; bei unbelegter Bindung `UNRESOLVED`.
- Keine tatsächlichen Änderungen an Cube-Morphologie, Library, Repositories oder produktiven Daten ohne gesonderte Beauftragung.

---

## 12. Vorläufige strategische Produktimplikationen

Aus dem bisherigen Research ergibt sich als **Arbeitsmodell**:

```text
                        Lunados Cube
            Morphology / Grammar / Constraints
                               |
                   Typed Mapping Profiles
                               |
              Functions / Derive / Project / Analyze
                               |
         +----------+-----------+----------+---------+
         |          |           |          |         |
        C4      ArchiMate     DSM/MDM     BPMN      DAG
```

Diese Darstellung ist **eine Architekturhypothese**, keine Aussage über den bereits implementierten internen Funktionsumfang.

Ein Standalone-Angebot hätte vermutlich den stärksten Nutzen bei komplexen Refactorings, Software-/Enterprise-Architecture-Mappings und Multi-Agent-/Workflow-Modellierung. Der kommerzielle Unterschied zu bestehenden Tools muss durch **nachweisbare semantische Qualität, wiederverwendbare Profile, Provenance/Loss Accounting und mehrere analytisch berechenbare Sichten** demonstriert werden — nicht durch eine bloße Behauptung universeller Überlegenheit.

**Pragmatischer erster Proof:** Das bereits vorhandene Multi-Tool-Refactoring-Modell für **DSM + DAG** nutzen und messen, ob definierte Abhängigkeitsknoten, Zyklen, Cluster, Impact-Ketten und zulässige Reihenfolgen reproduzierbar herauskommen. Die Cube-Semantik soll dabei im Original erhalten bleiben; beide Verfahren sind spezialisierte Projektionen, kein Ersatz der Morphologie.

---

## 13. Offene Fragen, nach Priorität

**P0 — Ohne diese Antworten keine gültige Neubewertung**

1. Welche konkrete **interne Cube-Version** und welche P3-MCP-Tools liegen vor?
2. Was ist im aktuellen **F-/Function-Library-Registry** implementiert und testbar?
3. Wie sind **MODE**, Transitionen, Gateway-Aktivierungszustände und zeitliche Constraints verbindlich definiert?
4. Welche **Relations- und Cardinality-Contracts** gelten intern und wo liegen die zugehörigen Konformitätstests?
5. Welche **Projection-/Derivation-Contracts** erhalten Herkunft und dokumentieren Informationsverlust?

**P1 — Für die fünf Vergleichsprofile**

- C4: Aggregationssemantik inklusive Verlustbericht.
- ArchiMate: Abbildungsregeln für Kardinalität, Goals, Outcomes, Events und Beziehungen.
- DSM/MDM: vorhandene Algorithmen sowie Typ-/Evidenzfilterschnittstelle.
- BPMN: XOR, AND, OR, Event-Based, Loop, Compensation; eindeutige Token-/Transition-Semantik.
- DAG: Auswahl gültiger Kanten, Cycle Gate, Herkunft, Topological Sort und Impact Analysis.

**P2 — Für die Standalone-Vermarktung**

- Minimal interoperable Profile und dokumentierte Imports/Exports.
- Lokal nutzbare Modellierungs-/Prüffunktionen versus kostenpflichtiger Sync/Collaboration-Betrieb.
- Lizenzierung von Text/Grammatik/Code/Hosting getrennt definieren.
- Fremdprofile unabhängig versionieren und Contract-Tests veröffentlichen.

---

## 14. Vorgeschlagener Folgeauftrag für die neue Unterhaltung (nicht ausgeführt)

> **Bitte verwende die Datei „Lunados_Cube_Grammar_Research_Handover_Konsolidiert_2026-11-01.md“ als Research-Baseline.** Es geht um eine Neubewertung von Structurizr/C4, ArchiMate, DSM/MDM, BPMN und DAG gegenüber dem **internen Lunados Cube P3**. Bitte zunächst die **tatsächlich verfügbaren lokalen Cube-MCP-Tools** ermitteln und deren Version/Capabilities lesen. Danach die fünf bislang nur Public-Reference-basierten Vergleiche anhand der realen internen Morphologie, Relations-/Cardinality-Contracts, Function Library, MODE und Execution-/Transition-Semantik überprüfen. Für jeden zuvor vermuteten Mangel A/B/C/D/U klassifizieren und konkrete Positiv-, Negativ- und Unresolved-Tests angeben. **Keine Änderung der Morphologie oder des Codes ohne Rücksprache.** Public-Dokumentation, interne Implementierung und eigene Hypothesen strikt trennen. Starte mit einer kompakten Inventur, dann Schritt für Schritt mit Vergleich 1.

---

## 15. Quellen- und Vertrauenshinweis

Dieses Handover ist eine **Konsolidierung des vorangegangenen Chats**, keine frisch durchgeführte, vollständige externe Normenrecherche. Die Diskussion behandelte Fachstandards/Tools wie Structurizr/C4, ArchiMate, DSM/MDM, BPMN und DAG. Detailaussagen über deren **aktuellste** Releases/Normen sollten bei Bedarf erneut mit den offiziellen Spezifikationen geprüft werden; dafür sind hier bewusst keine erfundenen Zitierreferenzen übernommen worden.

Primäre im Chat tatsächlich verwendete Cube-Baseline: das oben verlinkte Public-Manifest und dessen v9.4-Assets. Die im Chat später formulierten Korrekturen stützen sich auf diese Baseline und auf Hinweise des Nutzers zum **erweiterten internen Cube**. Sie sind nicht als ausgeführte interne Tests auszugeben.

**Kernbotschaft:** *Nicht die Cube-Morphologie an fremde Werkzeuge anpassen, bevor durch die interne MCP-Reevaluation nachgewiesen ist, dass vorhandene Contracts, Qualifikationen, Library-Funktionen und versionierte Mapping-Profile nicht ausreichen.*


---

## 16. Ergänzung: tatsächlich beobachtete MCP-Oberfläche am 1. November 2026

### 16.1 Nachweise und ihre Reichweite

| Nachweis | Tatsächlich beobachtetes Ergebnis | Nicht dadurch nachgewiesen |
|---|---|---|
| Public `cube_read_public_reference`, Manifestabruf | `reference_version: v9.4`; `scope: public_static_read_only`; `writes_available: false`; `function_invocation_available: false` | Interne Functions, Validierung oder Ausführung |
| Lokales `mcp__aiaeao_cube__cube_discover_surface` | Erfolgreiche Antwort mit Release, Version, P0/P1/P2-Domänen und Toolinventar | Erfolgreiche Einzelaufrufe aller genannten Tools; Konformität E1–E5 |
| Pluginsuche nach `Lunados SPACE` und verfügbares Toolinventar | Keine Treffer und kein nutzbares SPACE-Schreibwerkzeug | Nichtexistenz von Lunados SPACE oder fehlende Berechtigung außerhalb dieses Chats |

Public-Quelle: [Live-Manifest](https://cube.lunados.net/manifest.json), Abruf laut Tool `2026-11-01T08:41:34.504Z` (= 09:41:34 Europe/Berlin). `sha256_verified` war beim Manifest **null**; das ist kein bestätigter Hashvergleich. Die in Abschnitt 2 aufgeführten einzelnen Assets wurden für diese Konsolidierung nicht erneut vollständig gelesen oder hashgeprüft. Aussagen darüber stammen aus der gelieferten Research-Baseline.

Die lokale Quelle ist die tatsächliche Toolantwort, kein öffentlicher Dokumentlink. Ihre zentralen Werte sind im Folgenden wiedergegeben. Serverangaben zu Fähigkeiten sind als solche zu lesen; die erfolgreiche Discovery allein ist kein unabhängiger Funktionstest.

### 16.2 P3 bezeichnet hier den Adapterzugang, nicht ein neues Wahrheitsniveau

```text
Release:           aiaeao-cube-local
Adapterversion:    P3-MCP-LOCAL/0.3.0-rc1
Releasestatus:     release_candidate
Referenzversion:   v9.4
Transport:         stdio
P1-Profil:         P1-VC/1.0.0
P2-Kernprofil:     P2-VP/1.0.0-rc1
P0-Snapshot-Lock:  cb259c5962a61c507ace6260d37ae364cf6658794a115052e3bc4fefdca477a1
```

Der Ausdruck „interner Cube P3“ wird aus dem bisherigen Research übernommen. Die tatsächlich entdeckte Oberfläche exponiert P0, P1 und P2 über den lokalen P3-Adapter. Sie meldet weiterhin **v9.4** als Referenzversion. Daraus folgt kein Nachweis einer zusätzlichen internen Morphologie oder einer allgemeinen Workflow-Runtime.

| Domäne | Gemeldete Werkzeuge / Leistung | Geltungsgrenze |
|---|---|---|
| **P0 — Reference** | MCP Resources; `cube_read_reference` als paginierter Fallback; 14 Resource-URIs / 13 Source References | Dokumentarisch; keine Validierung und keine Wahrheitsprüfung. Resource-Sichtbarkeit ist hostabhängig. |
| **P1 — Validation** | `cube_validate`; Syntax, Struktur, Konzeptauflösung, Referentenbindung, Prädikat-, Methoden- und Qualifikatortypisierung, Scope-Konsistenz | Deskriptive Validierung mit `PASS`, `FAIL`, `UNRESOLVED`; Source Truth, Authority und Admission bleiben `NOT_EVALUATED`. |
| **P2 — Presentation** | `cube_prepare_print`, `cube_check_print`, `cube_render_svg`; außerdem `cube_plan_source`, `cube_plan_views`, `cube_plan_check` | Darstellungsprojektionen aus deklarierten Daten; `source_warrant: declared_unverified`; keine eingeschlossene P1-Validierung. |

`cube_get_capabilities` ist laut Discovery eine **Legacy-Karte nur für den P2-Printer**. Für eine vollständige Inventur ist `cube_discover_surface` zu verwenden. Eine reine Printer-Karte wäre keine ausreichende Grundlage, um den Gesamtumfang des Cube zu bewerten.

Gemeldete Planansichten sind `cube.phases`, `cube.flow`, `cube.sequence` und `cube.axes`. Genannt werden unter anderem `P2-VP-MIGRATION/0.7.5`, `P2-VP-SEQUENCE/0.8.0` sowie `P2-VP-AXES/0.9.2`; die jeweiligen Defaults können älter bzw. kontextabhängig sein. Für reproduzierbare Prüfungen muss deshalb das tatsächlich verwendete Profil festgehalten werden. Eine Sequenzansicht ist kein Nachweis einer BPMN-Engine; eine Achsenansicht kein Nachweis einer DSM-Analysefunktion.

### 16.3 Explizite Grenzen zwischen Referenz, Validierung und Darstellung

Die lokale Discovery meldet:

```text
P0 → P1:  NO_AUTOMATIC_REFERENCE_BINDING
P1 → P2:  NO_AUTOMATIC_ACG_TO_VP03_MAPPING
Gesamt:   overall_status = NOT_DEFINED
          epistemic_warrant = NOT_EVALUATED
          current_authority = NOT_EVALUATED
          canonical_admission = NOT_EVALUATED
```

Damit sind folgende Schlussfolgerungen unzulässig:

- Ein gelesenes Referenzdokument sei automatisch an den Validierungslauf gebunden.
- Ein `PASS` bestätige die fachliche Wahrheit, einen tatsächlichen Effekt oder eine Ausführungsbefugnis.
- Ein erzeugtes SVG beweise P1-Konformität oder eine verlustfreie semantische Ableitung.
- Der lokale P3-Zugang enthalte schon allein aufgrund seines Namens sämtliche benötigten Function-Library- oder MODE-Funktionen.

Die lokale Oberfläche meldet keine Dateisystemnebeneffekte ihrer MCP-Tools. Das ist eine Capability-Angabe für diesen Adapter; sie ist keine allgemeine Ausführungsfreigabe für beliebige später entdeckte Runtime-Funktionen. Eine getrennt sichtbare G5-Anbindung wurde für diese Übergabe nicht getestet und nicht mit dem lokalen Zugang gleichgesetzt.

### 16.4 Einordnung der früheren Einrichtungsschleife

Der Nutzer berichtete, dass der aus dem Browser fortgeführte Chat keinen passenden lokalen MCP-Kontext hatte, während `/mcp` in einer neuen lokalen Unterhaltung verfügbar war. Dies ist als Beobachtung dieser konkreten Sitzung zu bewahren; aus dem Fensternamen allein lässt sich die tatsächlich nutzbare Tooloberfläche nicht ableiten.

Die aktuelle offizielle Dokumentation beschreibt lokale STDIO-Server, die gemeinsame `config.toml` sowie die Einrichtung über Desktop-Einstellungen und `/mcp`. Eine zusätzliche CLI-Installation ist für diesen dokumentierten Desktop-Weg keine Voraussetzung. Ein Public-Reference-Plugin ist keine Bestätigung einer internen P3-Verbindung. Umgekehrt kann ein Plugin MCP-Server bündeln; die Bezeichnung „Plugin“ allein bestimmt deshalb nicht den Funktionsumfang. Entscheidend sind die tatsächlich erreichbaren Werkzeuge und ihre Antworten. Quelle: [OpenAI — Model Context Protocol](https://learn.chatgpt.com/docs/extend/mcp?surface=cli), im Zuge dieser Übergabe gelesen.

An der Konfiguration wurde für diese Konsolidierung nichts geändert. Der konkrete lokale Discovery-Aufruf war erfolgreich; eine erneute Installations- oder Tunnelanleitung ist daher für den nächsten Research-Schritt nicht erforderlich.

## 17. Präzisierter Prüfstand und Übergabe an die Reevaluation

### 17.1 Was erledigt ist und was offen bleibt

| Arbeitspunkt | Stand dieser Übergabe |
|---|---|
| Fünf Vergleiche einschließlich späterer Korrekturen sichern | Erledigt auf Grundlage der vom Nutzer gelieferten Chat-Zusammenfassung |
| Standalone-Produktthese und Grenzen festhalten | Erledigt als Hypothese, nicht als Marktvalidierung |
| Public-Referenz und lokalen P3-Zugang unterscheiden | Erledigt; Manifest und lokale Discovery tatsächlich abgerufen |
| Lokale Adapter-/Referenzversion feststellen | Erledigt für diesen Chat; weitergehende interne Contract-/Registry-Versionen offen |
| E1–E5 ausführen und fachlich bewerten | **Nicht ausgeführt** |
| Function Registry, Kardinalitätsverträge und MODE-Transitionen intern prüfen | **Offen** |
| Morphologie ändern oder Implementierung ergänzen | Nicht Gegenstand dieses Übergabeauftrags |
| Datei in Lunados SPACE speichern | **Nicht erfolgt; keine nutzbare Anbindung verfügbar** |

### 17.2 Konkreter nächster Arbeitsumfang

Die Experimente E1–E5 aus Abschnitt 11 bleiben der Arbeitsplan. Vor ihrer Ausführung sind passende Contracts und Eingabeformate zu lesen. Die bislang gemeldete P1-Validierung und die P2-Printer reichen allein nicht zum Beweis allgemeiner Graphanalyse oder operativer Gateway-Semantik.

| Experiment | Durch die Inventur bereits gestützt | Weiterhin benötigter Beleg |
|---|---|---|
| E1 — C4 | Darstellungs-/Planprojektionen werden angeboten | Tatsächliche C4-Aggregationsregel, Herkunftszuordnung, Verlustbericht und Abgrenzung zur Tatsachenbehauptung |
| E2 — ArchiMate | P1 meldet Struktur- und Typprüfungen | Exakte Relationsmultiplizitäten, Profilbindung und Diagnosen bei Unter-/Überbelegung |
| E3 — DSM/MDM | Achsen-/Planansichten werden angeboten | Registry und aufrufbare SCC-/Cluster-/Impact-Funktionen; eine Matrixdarstellung genügt nicht |
| E4 — BPMN | Methoden-/Qualifikatortypisierung und Sequenzdarstellung werden angeboten | Operative MODE-/F-Verträge, Prozessinstanzkorrelation und ausführbare Join-/Loop-Regeln |
| E5 — DAG | Referenz-, Validierungs- und Projektionswerkzeuge sind benannt | Gebundene Dependency-Auswahl, Zyklusprüfung, topologische Sortierung und Source Mapping |

Nicht sichtbare Registry- oder Runtime-Funktionen sind zunächst **nicht nachgewiesen**, nicht automatisch nicht vorhanden. Falls sie über die entdeckte Oberfläche nicht erreichbar sind, ist der fehlende Zugriff konkret zu benennen. `UNRESOLVED` eines P1-Laufs ist außerdem von „nicht ausgeführt“ und „Capability nicht verfügbar“ zu unterscheiden; diese Fälle benötigen separate Protokolleinträge.

### 17.3 Ergebnisprotokoll für jeden Vergleich

Jeder Folgeversuch sollte mindestens festhalten:

1. Vergleich/Experiment-ID, konkrete Behauptung und Herkunft aus dem bisherigen Research.
2. Referenz-, Adapter-, Contract- und Profilversion sowie Quelle der jeweiligen Regel.
3. Vollständige Eingabe, Kontext-/Referentenbindungen und tatsächlich verwendetes Tool.
4. Erwartetes Verhalten des Positiv-, Negativ- oder Unresolved-Falls vor dem Lauf.
5. Tatsächliches Ergebnis, Diagnoseadresse und gegebenenfalls erzeugte Artefakte.
6. Herkunftsabbildung und Informationsverlust; getrennte P1-/P2-Ergebnisse.
7. Bewertung A/B/C/D/U aus Abschnitt 11.4 mit Begründung und verbleibender Unsicherheit.

Die Klasse **A** ist durch die bisherige Discovery für keines der fünf Experimente erreicht. Auch **C** ist zunächst ein begründeter Profilvorschlag, solange seine Umsetzbarkeit nicht gezeigt wurde. Eine **D**-Feststellung erfordert einen konkreten Gegenfall; fehlender Toolzugriff oder fehlende Evidenz reichen dafür nicht.

**Übergabeergebnis:** Die Research-Baseline ist gesichert und um eine überprüfte Zugangsinventur ergänzt. Die fachliche Reevaluation kann daran anschließen, ohne die frühere Public-only-Analyse als interne Implementierungsprüfung auszugeben.
