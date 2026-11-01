> **Archivierte XXL-Referenz, nicht aktueller Auftrag.** Die folgende frühere Roadmap bleibt als Aufwand-/Komplexitätsreferenz erhalten. Das aktuelle Ziel ist der [Lernvergleich](README.md). Die damalige Interpretation „breite Interoperabilität“ wurde vom Nutzer ausdrücklich auf die breite Analyse der fünf Ansätze korrigiert. Auch die damalige Schätzung deckte begrenzte Profile ab, nicht universelle Vollkompatibilität.

# Lunados Cube — Roadmap zur Interoperabilität

**Stand:** 1. November 2026 · **Status:** Vorschlag auf Basis einer ersten internen Analyse · **Priorität des Nutzers:** breite Interoperabilität von **Structurizr/C4, ArchiMate, DSM/MDM, BPMN und DAG**.

## Empfehlung

Zuerst eine gemeinsame Abbildungs- und Nachweisschicht schaffen und damit **alle fünf Ansätze in begrenzten, expliziten Teilumfängen** anbinden. Anschließend die Semantik und Analysefunktionen vertiefen. Die vorhandene Cube-Morphologie bleibt die Ausgangsbasis; Erweiterungen werden erst bei einem konkreten, belegten Ausdrucksproblem erwogen.

Das Ziel ist ein durchgängiger Weg **Fremdmodell → gebundene Cube-Darstellung → geprüfte Projektion → Fremdformat**, mit nachvollziehbaren Identitäten und Verlustangaben. Nicht jede Richtung muss verlustfrei sein. Ein reines Originaldatei-Passthrough oder eine hübsche SVG-Ausgabe genügt nicht als Interoperabilitätsnachweis.

**Erste breite Demonstration:** M0–M2, geschätzt **19–32 Personentage**. **Belastbarer Pilotumfang über alle fünf Ansätze:** M0–M6, **53–92 Personentage**, zuzüglich ca. 25 % Reserve: **67–115 Personentage**.

Diese Spannen sind eine erste fachliche Schätzung, keine gemessene Produktivität und kein Liefertermin. Sie gelten für eine mit den Repositories vertraute Entwicklungsperson, punktuelle Fachreviews, vorhandene Bibliotheken und begrenzte Profile. Ein Personentag bedeutet ungefähr acht Stunden Engineering, einschließlich gezielter Tests und Dokumentation; er beschreibt keine Agentenlaufzeit. Nach M0/M2 neu schätzen. Kundenwartezeit, eine vollständige grafische Modellierungsoberfläche, Cloud-Sync/Mehrbenutzerbetrieb, Zertifizierung und eine eigene BPMN-Engine sind nicht enthalten.

## Bereits erledigte Analyse

- Alle fünf Vergleiche und ihre Korrekturen sind in der [Research-Baseline](HANDOVER.md) gesichert.
- Die drei Repositories wurden für die relevanten Contracts, Funktionen und Projektionen gesichtet.
- Die vorhandene Library-Verifikation bestand mit **109/109 Prüfungen**, einschließlich 89 Referenzfällen und zehn Cube-Deklarationsprüfungen.
- Acht gezielte lokale MCP-Validierungen lieferten die erwarteten PASS-/FAIL-/UNRESOLVED-Befunde; eine P2-Matrix wurde erzeugt und erfolgreich erneut geprüft.
- Die Nummerierungsgrenze des vorhandenen DAG-Evaluators wurde an einem konkreten Gegenfall reproduziert.

Einzelbefunde, Unsicherheiten und Rohbelege: [ANALYSE.md](ANALYSE.md). Diese Bestandsaufnahme ist abgeschlossen; die folgenden Implementierungsmilestones sind **noch nicht umgesetzt**.

## Milestones mit Aufwand, Nutzen und Komplexität

Nutzen und Komplexität sind relative Einschätzungen für das Ziel „fünf interoperable Ansätze“, keine Umsatzprognosen. Aufwände sind zusätzliche, nicht kumulierte Personentage; gemeinsam genutzte Infrastruktur wird nur einmal gerechnet.

| Milestone | Überprüfbares Ergebnis | Aufwand | Nutzen | Komplexität | Voraussetzung |
|---|---|---:|---|---|---|
| **M0 — Vergleichsgrundlage festlegen** | Fremdversionen, Zielformate, fünf Referenzmodelle und Akzeptanzmatrix gepinnt; P1-/MCP-Profilinventar stimmt mit `/1…/7` überein | **2–4 PT** | Sehr hoch: verhindert falsche Gleichsetzungen und Nacharbeit | Niedrig–mittel | Erste Analyse vorhanden |
| **M1 — Gemeinsame Mapping-Regeln** | Versioniertes Austauschpaket mit Identitätsmapping, Source Trace, Scope, Typen, unbekannten Feldern und maschinenlesbarem Verlustbericht; getrennte P1-/P2-Berichte | **5–8 PT** | Sehr hoch: gemeinsame Grundlage aller fünf Adapter | Mittel–hoch | M0 |
| **M2 — Fünf begrenzte Austauschpfade** | Für jeden Ansatz ein kleiner tatsächlicher Import, Cube-Abgleich und Export mit Rücklesen; Positiv-, Negativ- und Unresolved-Fälle | **12–20 PT** | Sehr hoch: erster breiter Nutzennachweis | Hoch | M1 |
| **M3 — Gemeinsame Graph-/Matrixanalyse** | Typfilter, stabile IDs, SCC/Zyklennachweis, topologische Sortierung, Reachability; DSM/DMM/MDM-Projektion und explizite Aggregationsregeln | **8–14 PT** | Hoch: wiederverwendbar für Architektur, Abhängigkeiten und Prozessanalyse | Mittel–hoch | M2; dessen begrenzte Graphhülle wiederverwenden |
| **M4 — C4/ArchiMate semantisch vertiefen** | C4-Aggregation mit gewählter Strategie; ArchiMate-Relationssignaturen und profilgebundene Multiplizitätsprüfung; semantisch definierte Roundtrips | **10–18 PT** | Hoch: Architekturmodelle belastbar austauschen | Hoch | M2; M3 für abgeleitete Sichten |
| **M5 — BPMN und Ausführungsspuren** | Modell-/Instanztrennung, korrelierte externe Engine-Traces, XOR/AND/Loop-Kontrollen; explizite Unsupported-Matrix für weitere Gateways | **10–18 PT** | Hoch: Verbindung von Prozessmodell und beobachteter Ausführung | Sehr hoch | M2, ausgewählte Engine und gepinnte Semantik |
| **M6 — Gemeinsamer Interoperabilitätspilot** | Alle fünf Profile zusammen an zwei realistischen Beispielen; Versionierungs-/Verlustregression, reproduzierbare Auslieferung und Nutzenmessung | **6–10 PT** | Sehr hoch: aus Einzelfunktionen wird ein nutzbares Angebot | Mittel–hoch | M3–M5 |
| **Gesamt** | Begrenzter, aber durchgängiger Fünf-Profil-Pilot | **53–92 PT** | — | — | **Mit 25 % Reserve: 67–115 PT** |

Bei einer Vollzeitperson entspricht die reservierte Spanne ungefähr 14–23 Arbeitswochen. M3–M5 können nach M2 teilweise zeitlich überlappen, wenn zusätzliche Personen und klare Schnittstellen verfügbar sind; der Gesamtaufwand wird dadurch nicht automatisch kleiner. Dies ist eine Planungsoption, keine bereits beauftragte Delegation.

## M2: Was „breit“ konkret umfasst

| Profil | Erster verbindlich begrenzter Umfang | Aufwand innerhalb M2 | Abnahmepunkt |
|---|---|---:|---|
| **C4/Structurizr** | Person/System/Container/Component, explizite Beziehungen und Hierarchie; zuerst gepinntes Workspace-JSON, DSL über einen festgelegten Fremdparser | **2–3 PT** | Export wird vom gewählten Parser gelesen; Original- und Projektionsidentitäten bleiben zuordenbar |
| **ArchiMate** | Ein festgelegtes Modell-Austauschschema, kleine gemeinsam definierte Typ-/Relationsmenge; keine pauschale Äquivalenz von Goal/Expectation oder Outcome/Result | **3–5 PT** | Typen und Relation Richtung bleiben im Rücklesen erhalten; nicht abbildbare Elemente erscheinen im Verlustbericht |
| **DSM/MDM** | Gerichtete DSM, DMM und ihre Blockkombination; JSON/CSV-Austausch mit separatem Metadatenvertrag | **2–3 PT** | Domänen, Zeilen-/Spalten-IDs und Zellsemantik werden vollständig rückgelesen; Unknown ≠ Empty |
| **BPMN** | BPMN 2.0.2 XML: Start/Ende, Task, Sequence Flow, XOR/AND als deklarierte Modellstruktur | **3–5 PT** | XML lässt sich im festgelegten Werkzeug öffnen; unbekannte Konstrukte werden markiert; noch keine Behauptung operativer Gateway-Konformität |
| **DAG** | Typisierte Abhängigkeiten mit beliebigen stabilen IDs; Grundnormalisierung/Zyklusgate mit vorhandener Graphbibliothek; gemeinsames JSON-Schema | **2–4 PT** | IDs und Richtung bleiben erhalten; echte Zyklen werden erkannt; reine Referenzen werden nicht zu Ausführungsabhängigkeiten |

Diese Austauschspezifikationen sind Vorschläge, keine bereits angenommenen Contracts. M0 fixiert Versionen und konkrete Werkzeuge. Es wird nicht vorausgesetzt, dass CSV selbst standardisierte DSM-Semantik trägt oder dass ein beliebiges DAG-JSON schon toolübergreifend normiert ist.

## Akzeptanzgates

**M0:** Für jeden Ansatz sind Version, unterstützter Teilumfang, Referenzwerkzeug und Messkriterium schriftlich festgelegt. Insbesondere ArchiMate-Version und Relationsmultiplizitäten dürfen nicht aus verschiedenen Normständen vermischt werden. Ein Modell ist ausdrücklich als vollständig oder partiell deklariert.

**M1:** Für jedes fremde Element gibt es genau eine dokumentierte Disposition: typisiert abgebildet, bewusst opaque erhalten, explizit verworfen oder abgelehnt. Nicht modellierte Semantik darf weder verschwinden noch als bewiesen erscheinen. Ableitungen speichern Regel, Eingangsrevision, Quellenbezüge und Verluststatus. Das Austauschpaket ergänzt die vorhandenen Contracts; es ersetzt nicht ungeprüft deren Identitäten.

**M2:** Alle fünf Pfade laufen, mindestens mit einem Positiv-, Negativ- und Unresolved-Fall je Profil. Das Zielwerkzeug liest den Export tatsächlich. Ein identischer Dateirücklauf allein genügt nicht: mindestens eine unterstützte Cube-Modifikation muss korrekt zurückprojiziert werden. Opaque Teile zählen nicht als semantisch gemappt.

**M3:** Umbenennung und Eingabereihenfolge ändern das fachliche Ergebnis nicht. Der Testkorpus enthält die azyklische Kante `1 → 0`, einen echten Zyklus, Self-Loops, doppelte Kanten, isolierte Knoten und unzulässige Dependency-Typen. SCC wird nicht mit Clustering gleichgesetzt; Impact-Reichweite nicht mit tatsächlicher Kausalität. Gewichte, Skalen und etwaige Aggregation sind im jeweiligen Profil definiert.

**M4:** C4-Implied-Relationships werden gegen die gewählte Structurizr-Strategie verglichen. Relationsmultiplizitäten werden an Modellpopulationen getestet; Methodensignatur und Slotkardinalität dienen nicht als Ersatz. Fehlende Instanzen in einem partiellen Modell werden nicht ungeprüft als Normverletzung ausgegeben.

**M5:** Prozessdefinition, Prozessinstanz und Beobachtung bleiben getrennt. Tests enthalten vorzeitigen Join, fremde Instanz-ID, doppelte/verspätete Beobachtung und Loop. Cube übernimmt keine implizite Ausführungsfreigabe. OR-Join, Event-Based, Cancellation und Compensation bleiben bis zu eigenen Nachweisen ausdrücklich außerhalb des freigegebenen Teilprofils; eine Vertiefung erhöht den Umfang und benötigt neue Schätzung.

**M6:** Zwei realistische Modelle durchlaufen alle jeweils sinnvollen Projektionen. Zielwerte: keine stillen Verluste; jeder exportierte Knoten und jede Kante auf Quellen bzw. erklärte Synthese rückführbar; vollständiges Bestehen der festgelegten Profiltests. Bearbeitungszeit, manuelle Reparaturen und verlorene Semantik werden gegen einen direkten Fremdtool-Workflow gemessen. Ein wirtschaftlicher Vorteil wird erst aus diesen Ergebnissen abgeleitet.

## Arbeitsteilung zwischen den drei Repositories

| Ort | Vorgeschlagene Verantwortung | Abgrenzung |
|---|---|---|
| **lunados.cube** | P1-Contracts und Validierung; P2-Projektionen; zutreffende MCP-Capability-Deklaration | Keine automatische Ausführung von Library-Methoden; keine aus P1 abgeleitete Wahrheit/Authority |
| **lunados.lib** | Wiederverwendbare reine Mapping-/Analysefunktionen mit Revision, Referenzfällen und Vergleichsorakel | Bestehende v1-Einträge nicht still verändern; zukünftige Kandidaten nicht vorab als produktiv bezeichnen |
| **lunados.space** | Research, profilübergreifende Beispiele, Testnachweise, Nutzerführung und Dokumentation | Die lokale Dokumentablage ist kein Nachweis einer veröffentlichten Website oder angenommenen Norm |

Wo formatabhängige Import-/Export-Adapter dauerhaft liegen, wird in M0 festgelegt. Sie müssen nicht alle zu kanonischen Cube-Methoden oder Library-Einträgen werden. Ihre Transport-/Parserabhängigkeiten sollten von der reinen Validierung getrennt bleiben.

## Risiken und bewusste Umfangsgrenzen

| Risiko | Auswirkung | Geplante Begrenzung |
|---|---|---|
| Fremdversion oder Austauschschema nicht fixiert | Falsche Mappings und Aufwandssprünge | Versionen und Parser in M0 pinnen; Versionen getrennt behandeln |
| „Alles verlustfrei“ wird still vorausgesetzt | Unbegrenzter Umfang | Pro Richtung unterstützte Semantik und Verluststatus festlegen |
| Synthetische Fixtures erscheinen als allgemeine Lösung | Nutzen wird überschätzt | M6 mit realistischen Modellen und direktem Vergleichsworkflow |
| Vorhandene Impact-Formel wird als universelle Analyse eingesetzt | Fachlich falsche Aussagen | Neuer Adapter/Revision; keine stillen Änderungen an v1 |
| BPMN-Modellierung wächst zur eigenen Engine | Hohe zusätzliche Komplexität | Bestehende Engine als Referenz/Trace-Lieferant; keine Engine im Basisumfang |
| Alle fünf Formate erhalten gleichzeitig volle Oberflächen | Aufwand übersteigt Semantikarbeit | Zuerst reproduzierbarer dateibasierter Austausch, danach UI nach Nutzen |

## Was der Nutzer noch klären kann

**Für die erste Analyse und diese Roadmap war keine weitere Antwort nötig.** Die Priorität „alle fünf Ansätze“ ist übernommen. Für M0 helfen anschließend drei konkrete Angaben:

1. **Reale Modelle und Zielwerkzeuge:** Je ein repräsentatives Beispiel, falls vorhanden; insbesondere ArchiMate-Version/-Tool und bevorzugte BPMN-Engine. Ohne Kundenbeispiele beginnt die Profilentwicklung mit kleinen synthetischen Modellen und kennzeichnet das.
2. **Erwarteter Rückweg:** Genügt pro Profil nachvollziehbarer Import/Export eines definierten Teilumfangs, oder sollen bearbeitete Fremdmodelle einschließlich Layout/Erweiterungen vollständig zurücklaufen? Die Schätzung oben nimmt semantischen Teilumfang mit offen ausgewiesenen Verlusten an, keine pixel- oder byteidentische Vollreproduktion.
3. **Kapazität und Zieltermin:** Die Roadmap ist derzeit in Personentagen formuliert. Erst mit verfügbarem Team und Reviewkapazität lässt sich ein belastbarer Kalenderplan ableiten.

## Ablage und Status

Dieses Paket ist zur lokalen Ablage unter `lunados.space/web/docs/research/cube-interop-2026-11-01/` bestimmt. Es enthält Research, erste Analyse, Roadmap und Nachweise. Es wurde kein Produktcode geändert und keine Veröffentlichung, kein Commit oder Push durchgeführt.

- [Historischer Research mit Korrekturen](HANDOVER.md)
- [Aktuelle interne Analyse und Quellen](ANALYSE.md)
- [Quellstand und Prüfevidenz](evidence/source-lock.json)
