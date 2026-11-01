# MILE-002 — Lückenbilanz und Lerngewinn

Status: TASK-016 · Stand: 2026-11-01 · Grundlage: 15 [Fallberichte](README.md), [Quellenregister](SOURCE-REGISTER.md), Nachweise unter [10-Evidence/MILE-002](../../10-Evidence/MILE-002/)

Diese Bilanz verdichtet eine Stichprobe von 15 Fällen. Sie zeigt konkrete Fähigkeiten und Lücken. Sie beweist **keine** Vollständigkeit, keine Interoperabilität und keinen gemessenen Nutzen. Nutzen- und Aufwandsangaben sind Erwartungen bzw. grobe menschliche Personentage (PT), keine Messungen.

## 1. Datenbasis

| Nachweisart | Umfang | Ergebnis |
|---|---|---|
| Lokale P1-Prüfung über MCP stdio (`cube_validate`, P1-VC/1.0.0, binding-context/1) | 29 Fälle im Fallvertrag v2 (28 Matrixläufe + Pilot), je 2 frische Verbindungen, Agent-Umgebung | alle erwartungsgemäß; letzter Gesamtlauf: 20 PASS, 6 FAIL, 3 UNRESOLVED |
| Begründet nicht ausführbar (`not_executable`) | 6 (ARC-02, ARC-03, DSM-03 ×2, BPMN-01, BPMN-02) | kein Aufruf, kein Fachstatus |
| Direkte LIB-Evaluatoraufrufe (`impact.propagate/v1`) | 4 (DAG-01–03) | alle erwartungsgemäß |
| Quellen- und Codeanalyse | alle 15 Fälle | in den Berichten als solche gekennzeichnet |

Alle Erwartungen wurden vor dem jeweiligen Lauf committet (`2b37c31`, `3229dd3`, `fa50ee9`, `b45ac11`, `66efa7b`). Beobachtete Diagnosen: `P1_PREDICATE_SIGNATURE`, `P1_REFERENT_MISMATCH`, `P1_SCOPE_CONFLICT`, `P1_PREDICATE_PROFILE_MISSING`, `P1_BINDING_CONTEXT_REQUIRED`. Ausgangsstand ist durchgehend unverändert; alle Konzeptabbildungen und Prädikatverträge sind fallweise Versuchsabbildungen (A).

**Nachweisgrade im Register:** **P1** = an P1-Ergebnis beobachtet · **LIB** = an Evaluatorergebnis beobachtet · **NE** = begründet nicht ausführbar · **Q** = Quellen-/Codeanalyse.

## 2. Belegte Stärken

| ID | Stärke | Fälle | Grad |
|---|---|---|---|
| S-01 | Gerichtete, typisierte Prädikatsignaturen; Umkehr und falsche Endpunkttypen → FAIL | C4-01, ARC-01, DSM-02 | P1 |
| S-02 | Eine Identität = ein Konzept; dieselbe Identität auf zwei Ebenen → FAIL | C4-01 | P1 |
| S-03 | Unbekannter Partner → UNRESOLVED, nicht FAIL (keine erfundene Verletzung) | ARC-03 | P1 |
| S-04 | Relationen tragen die Richtung explizit; nach dem Import keine Matrixkonventions-Mehrdeutigkeit | DSM-01 | P1, Q |
| S-05 | Abgeleitete Beziehungen lassen sich per F-Qualifikator und Pflichtqualifikator im Prädikatvertrag markieren | C4-02, C4-03 | P1 |
| S-06 | Instanz-als-Scope weist instanzübergreifende Joins ab | BPMN-03 | P1 |
| S-07 | Cube-Graphen dürfen Zyklen enthalten; DAG-Gültigkeit ist eine Projektionseigenschaft | DAG-03 | P1, Q |
| S-08 | Die vorhandenen Y-Konzepte trennen Ausführung, Ergebnis und Evidenz; Token-Aufzeichnungen sind als Evidenz abbildbar, ohne X Events zu behaupten | BPMN-01–03 | Q |

## 3. Lückenregister

| ID | Lücke · verlorene Unterscheidung | Fälle · Quelle | Grad | Kleinste Ebene | Wiederverwendung | Erwarteter Nutzen | Aufwand · Komplexität |
|---|---|---|---|---|---|---|---|
| **G-01** | **Vollständigkeit und Population.** „unbekannt“ vs. „geprüft leer“ vs. „verletzt“; Zählregeln über Aussagenmengen; „genau einer je Eingang/Aktivierung“ | ARC-02, ARC-03, DSM-03, BPMN-01, BPMN-02 · R-AM-4, R-DSM-2, R-BPMN-1/2 | NE, P1 (ARC-03) | **Profil** (Vollständigkeitserklärung je Sicht/Referent und Relationstyp, mit Witness) + **LIB** (reine Populations-/Zählprüfung) | Statuslogik P1.10.1 D-2 („incomplete, not contradictory“ → UNRESOLVED) | sehr hoch — vier von fünf Ansätzen | 2–4 PT · mittel–hoch |
| **G-02** | **Herkunft einer Relation.** deklariert vs. abgeleitet; unmarkierte Ableitung besteht P1 | C4-02, C4-03 · R-SZ-1, R-SZ-3; relations.json `qualified_relation_form` | P1 | **Profil** (typisierter Relationsparameter `origin` oder Pflicht-Herkunftsqualifikator; fehlend → UNRESOLVED) | relations.json sieht `origin` bereits vor | hoch | 1–2 PT · mittel |
| **G-03** | **Projektion mit Quellenspur und Verlustbericht.** Quellbeziehungen, Strategie und Verlust (2 → 1) einer Verdichtung; Matrixkonvention beim Import/Export | C4-02, DSM-01, DSM-02 · R-SZ-3, R-DSM-1/3/4 | P1, Q | **LIB** (`project.aggregate-relations`, `project.dsm`, `project.mdm`; Konvention und Strategie als Pflichtparameter) | Y:relation-arrow:projection/derivation; P2-Projektionen | hoch | 2–3 PT · mittel |
| **G-04** | **Fremdbegriffe ohne neutrale Zielkonzepte.** C4-Ebenen, ArchiMate-Typen, Domänen nur über Arbeitsabbildung; Namensfallen (Outcome, Capability, Constraint, Resource) | C4-01, ARC-01, DSM-02, BPMN-01 · R-C4-1/2, R-AM-1–3 | P1, Q | **Profil** (versionierte Abbildungsprofile je Fremdsprache) + **Dokumentation** (Namensfallen-Tabelle) | ARC-01-Tabelle | mittel–hoch | 1–2 PT je Sprache · mittel |
| **G-05** | **Graphanalyse.** Zyklusnachweis, Generationen, alle Ordnungen, SCC/Partition | DAG-02, DAG-03, DSM-01 · R-DAG-1–3 | LIB, Q | **LIB** (`analyze.cycle-gate`, `analyze.topological-generations`, `analyze.topological-orders`, `analyze.scc`, `analyze.partition`) | Referenz-Implementierung z. B. NetworkX; Library-Vertrag vorhanden | hoch | 2–3 PT · niedrig–mittel |
| **G-06** | **LIB-Vertragspräzision `impact.propagate/v1`.** topologische Nummerierung als undeklarierte Vorbedingung; Meldung „cycle“ für azyklische Eingabe; Kantenorientierung umgekehrt zur Cube-Lesart | DAG-01, DAG-03 · R-DAG-4 | LIB, Q | **LIB** (neue Revision: Vorbedingung + Orientierung in `entry.json`, präzise Ablehnung, optional Normalisierung) | G-05 cycle-gate | hoch (Impact ist Hauptanwendungsfall) | 0,5–1 PT · niedrig |
| **G-07** | **Kontrollfluss- und Übergangssemantik.** Exklusivität, Bedingungsreihenfolge, Default/Exception, Synchronisation, Überschuss-Token | BPMN-01, BPMN-02 · §10.6.2, §13.4.1/2 | NE, P1 | **Profil** (Kontrollfluss-Profil je Gateway-Typ) + **LIB** (`analyze.trace-conformance`: beobachtete Spur gegen Modell) | P1.10 Transitionen (nicht untersucht) | hoch, aber nur bei bestätigtem Prozess-Anwendungsfall | 3–5 PT · hoch |
| **G-08** | **Instanzkorrelation.** Instanzzugehörigkeit nur über Scope-Überladung; im gemeinsamen Scope unbemerkt | BPMN-03 · §13.2 | P1 | **Profil/Dokumentation** (Konvention „Instanz = Scope“ festschreiben oder typisierte `instance_ref` mit Regel „gleiche Instanz“) | Y:identified-object:bounded-execution | mittel–hoch | 0,5–1 PT · niedrig–mittel |
| **G-09** | **Prädikateigenschaften und Domänendisziplin.** Irreflexivität; „ein Relationstyp je MDM-Block“; breite Prädikate erlauben Abflachung | DSM-01, DSM-02 · R-DSM-1/4 | P1 | **Profil** (optionale Prädikatmerkmale; Domänendeklaration) | Prädikatvertrag `additional_constraints` heute nur Freitext | mittel | 0,5–1 PT · niedrig |
| **G-10** | **Relationsoperanden.** `rel` als Operand ist grammatisch erlaubt, Rückgabetyp in P1.1 undefiniert → UNRESOLVED | C4-02 · EBNF | P1 | **P1-Profil** (typisierte Relationsoperanden) — Alternative zu G-02 für Quellenbindung | — | mittel | 1–2 PT · mittel |

**Morphologie:** Kein Fall begründet eine Änderung. Offen bleibt nur die Frage aus C4-01, ob ein neutrales Z-Konzept für Softwareelemente sinnvoll wäre; die Stichprobe zeigt lediglich, dass die vorhandenen Modulkörper AIAEAO-Rollen sind.

**Bloße Implementierungsgrenzen (keine semantische Lücke):** G-06 (Evaluator), die Einzelausdrucksprüfung von `cube_validate` (Ursache der NE-Fälle, durch G-01/G-07 adressiert).

## 4. Werkzeug- und Prozessbefunde

| ID | Befund | Fall/Quelle | Vorschlag |
|---|---|---|---|
| T-01 | Fälle pinnen den Hash des ganzen Quellenregisters; jede Ergänzung erzwingt Neu-Pinnen aller Fälle (beim Piloten erfolgt; DSM- und BPMN-Präzisierungen deshalb in Fallberichten statt im Register) | TASK-011, DSM-01, BPMN-01 | Pin pro Regel-ID (Regeltext-Hash) oder versionierte Registerrevisionen |
| T-02 | LIB-Aufrufe laufen außerhalb des Runners; Aufruf- und Erwartungsdateien sind committet, das Ausführungsskript nicht | DAG-01–03 | kleine `lib_call`-Unterstützung im Runner oder dokumentiertes Skript |
| T-03 | Agent-Testumgebung offline über Wheelhouse eingerichtet; Mac-venv und Agent unterscheiden sich in der Python-Patchversion | TASK-010 | beibehalten; Lock bei venv-Änderung erneuern |
| T-04 | Lokaler MCP-Server läuft aus dem Arbeitsbaum mit nicht committeten P3-Änderungen; in den Berichten über Dateihashes erfasst | alle Läufe | P3-Änderungen committen oder vor Läufen stashen |

## 5. Die sieben Leitfragen

1. **Reicht der Envelope-Rahmen?** *Nicht direkt geprüft.* Keiner der 15 Fälle benötigte eine Methoden-Envelope; die beobachteten Lücken liegen darunter (Übergangsverträge G-07, Population G-01). **Offene Frage:** Braucht eine Kontrollfluss-Spurprüfung (G-07) eine eigene Envelope oder genügt ein Profil plus LIB-Ergebnis im vorhandenen generischen Evaluator-Ergebnis?
2. **Welche Analysemethoden eignen sich für LIB?** Projektion mit Quellenspur (G-03), Zyklus-Gate, Generationen, Ordnungen, SCC (G-05), Populationsprüfung (G-01), Spurkonformität (G-07); dazu eine präzisierte Revision von `impact.propagate` (G-06). Alle sind rein und deklarativ beschreibbar; keine wurde implementiert.
3. **Welche Referenz- und Kardinalitätsregeln gehören in Profile?** Vollständigkeitserklärungen und Zählregeln (G-01), Relationsherkunft (G-02), Prädikateigenschaften und Domänenblöcke (G-09), Instanzkorrelation (G-08), Fremdbegriffsabbildungen (G-04). Die P1.6-Slot-Arity (one/many, nur X-Endpunkte) löst keine dieser Populationsfragen.
4. **Welche Bindungen brauchen LENS, MODE und Achsen?** *Weitgehend offen.* Genutzt wurde nur F (Ableitungsmethode, C4-02). Aus den Fällen folgen Bindungsanforderungen: Matrixkonvention (DSM-01), Domänenblöcke (DSM-02), Instanzgruppierung (BPMN-03), Herkunftsart je Kante (C4-03). Ob MODE Kontrollflusssemantik tragen soll, wurde nicht untersucht.
5. **Welche visuellen Unterscheidungen sind ungesichert?** Siehe Übergabe MILE-003 (Abschnitt 6). Schwerpunkte: abgeleitete vs. deklarierte Kante, vier Zellzustände, Zeugenzyklus, Instanzgruppierung. Kein Rendering und kein Lesbarkeitstest in MILE-002.
6. **Wo fehlen Ausdrucksmöglichkeiten — und wo nur Vertrag oder Prüfer?** *Ausdruck fehlt:* Abwesenheit/„geprüft leer“ (ohne Vollständigkeitserklärung, G-01), n-stellige Synchronisation (BPMN-02). *Nur Vertrag fehlt:* Relationsherkunft (G-02), Instanzbindung (G-08), Prädikateigenschaften (G-09), Fremdbegriffe (G-04). *Nur Prüfer fehlt:* Population (G-01), Graphanalyse (G-05), Spurkonformität (G-07). Konzepte und visuelle Anker selbst fehlten in keinem Fall nachweislich.
7. **Welche Aufgaben stiften den höchsten erwarteten Nutzen?** Erwartet, nicht gemessen: (a) Impact- und Reihenfolgefragen über Abhängigkeiten (DAG, DSM) mit Zyklusnachweis, (b) „unbekannt“ nie als „leer“ oder „verletzt“ ausgeben (ARC-03, DSM-03), (c) verdichtete Sichten mit nachvollziehbarer Herkunft (C4-02/03), (d) instanzgenaue Prozessspuren (BPMN-01–03). Messideen stehen in den Fallberichten.

## 6. Übergabe an MILE-003 — Darstellungsanforderungen

| ID | Anforderung | Fall |
|---|---|---|
| V-01 | Abgeleitete und deklarierte Kante unterscheidbar; unbekannte Herkunft als „unbekannt“, nie stillschweigend „deklariert“ | C4-02, C4-03 |
| V-02 | Verdichtungshinweis „n Quellen → 1 Kante, k Beschreibungen verworfen“, Quellen aufrufbar | C4-02 |
| V-03 | Zugehörigkeit als verschachtelte Grenze; Fremdebene neben Cube-Konzept | C4-01 |
| V-04 | Fremdtyp und Cube-Konzept nebeneinander; Hinweis bei Namensgleichheit | ARC-01 |
| V-05 | Vier Zellzustände: markiert, geprüft leer, unbekannt, ausgeblendet (mit Zähler); unbekannt ≠ leer, auch für VP-09.2 `--hide-empty` | DSM-03, ARC-03 |
| V-06 | Matrixkonvention in der Legende; Rückkopplungsmarken hervorgehoben; Zelle → Quellaussage | DSM-01 |
| V-07 | MDM-Blöcke mit Domänen- und Relationstyp-Beschriftung; unmodellierte Blöcke als unbekannt | DSM-02 |
| V-08 | Generationen als Spalten mit Hinweis „strukturell unabhängig, nicht zwingend parallel“ | DAG-02 |
| V-09 | Zeugenzyklus als hervorgehobene Kantenfolge; „nicht abarbeitbar“ vs. „falsch nummeriert“ | DAG-03 |
| V-10 | Genommener vs. nicht genommener XOR-Pfad je Instanz; zwei Pfade für einen Token als Fehler | BPMN-01 |
| V-11 | Join mit Eingangsliste und Status je Eingang | BPMN-02 |
| V-12 | Instanz als Gruppierung/Band; instanzübergreifende Kanten als Fehler | BPMN-03 |

Vergleichsaufgaben für den Lesbarkeitstest in MILE-003: V-01, V-05, V-09, V-12 (je eine Nutzerfrage aus dem Fallbericht).

## 7. Übergabe an MILE-004 — vorläufige Maßnahmenliste

Reihenfolge nach erwartetem Nutzen je Aufwand; vorläufig, Entscheidung in MILE-004.

| Rang | Maßnahme | Lücken | Ebene | Aufwand |
|---|---|---|---|---|
| 1 | Vollständigkeitserklärung + Populationsprüfung (UNRESOLVED bei Unvollständigkeit) | G-01 (+ BPMN-02) | Profil + LIB | 2–4 PT |
| 2 | `impact.propagate` v2-Revision mit deklarierter Vorbedingung und Orientierung, davor `analyze.cycle-gate` | G-06, G-05 | LIB | 1–2 PT |
| 3 | Typisierte Relationsherkunft | G-02 (oder G-10) | Profil | 1–2 PT |
| 4 | Projektionsfunktionen mit Quellenspur und Verlustbericht | G-03 | LIB | 2–3 PT |
| 5 | Prädikateigenschaften, Domänendeklaration, Instanzkonvention | G-09, G-08 | Profil/Dokumentation | 1–2 PT |
| 6 | Abbildungsprofile + Namensfallen-Dokumentation (zuerst C4 oder ArchiMate) | G-04 | Profil + Dokumentation | 1–2 PT je Sprache |
| 7 | Kontrollfluss-Profil + Spurkonformität — nur bei bestätigtem Prozess-Anwendungsfall | G-07 | Profil + LIB | 3–5 PT |
| — | Werkzeug: Registerpin pro Regel, LIB-Aufrufe im Runner | T-01, T-02 | Werkzeug | 0,5–1 PT |

Keine Maßnahme erfordert eine Morphologieänderung.
