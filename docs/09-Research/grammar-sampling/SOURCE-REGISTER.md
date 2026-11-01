# MILE-002 — Quellen- und Regelregister

Status: fixiert für MILE-002-A (TASK-009) · Abrufdatum aller Webquellen: 2026-11-01 (Europe/Berlin) · Maschinenlesbar: [SOURCE-LOCK.json](../../10-Evidence/MILE-002/SOURCE-LOCK.json)

Dieses Register bindet die 15 Fälle der [Fallmatrix](CASE-MATRIX.md) an konkrete Quellenstände und Regelstellen. Es ist ein Quellenbefund, keine Cube-Prüfung. Aussagen sind eigene Kurzfassungen; Normtexte und lizenzierte PDFs werden nicht ins Repository kopiert.

## Geltungsstufen

| Stufe | Bedeutung |
|---|---|
| **N** — normativ | Veröffentlichte Norm/Spezifikation des Normgebers; Fundstelle mit Abschnitt |
| **K** — Normgeber-Kurzreferenz | Vom Normgeber herausgegebene Zusammenfassung; Definitionen belegt, Zulässigkeitsregeln nicht |
| **D** — dokumentarisch | Methoden- oder Werkzeugdokumentation ohne Normanspruch; gilt nur für den genannten Stand |
| **H** — Herstellerdokumentation | Drittanbieter-Material zu einer Norm; Beispiele belegen eine Lesart, nicht die normative Zulässigkeit |
| **A** — eigene Arbeitsannahme | In MILE-002 gesetzt; wird in Fallberichten als lokale Annahme bzw. Versuchsprofil gekennzeichnet |

## Entscheidung zur ArchiMate-Basis

Die vollständige ArchiMate-3.2-Spezifikation (Open Group C226) ist nicht verfügbar. Entscheidung des Projektverantwortlichen vom 2026-11-01: **Die ausstehende Spezifikation wird in der Betrachtung ausgelassen.** Folge: Normative Endpunkt-Zulässigkeit von Beziehungen (Spezifikation Kapitel 5 und Beziehungstabelle im Anhang) wird in MILE-002 nicht geprüft. ARC-01 bindet die Beziehungsdefinition an die Normgeber-Kurzreferenz (K) und das konkrete Endpunktpaar an Herstellerbeispiele (H). Eine Cube-Bewertung darf daraus keine ArchiMate-Konformität ableiten.

## Quellen

| ID | Ansatz | Quelle | Stand / Version | Stufe | Zugriff |
|---|---|---|---|---|---|
| S-C4-1 | C4 | [C4 model — Container](https://c4model.com/abstractions/container) | ohne Seitenversion/-datum; abgerufen 2026-11-01; CC BY 4.0 | D | Web |
| S-C4-2 | C4 | [C4 model — Component](https://c4model.com/abstractions/component) | wie S-C4-1 | D | Web |
| S-SZ-1 | Structurizr | [Structurizr DSL — Implied relationships](https://docs.structurizr.com/dsl/implied-relationships) | ohne Seitenversion; Navigationsangabe „Binaries v2026.09.19“ nicht seitengebunden | D | Web |
| S-SZ-2 | Structurizr | [Structurizr for Java — Implied relationships](https://docs.structurizr.com/java/implied-relationships) | ohne Seitenversion; abgerufen 2026-11-01 | D | Web |
| S-AM-1 | ArchiMate | The Open Group, *ArchiMate® 3.2 Specification — Reference Cards* (N221), Personal PDF Edition | © 2022, PDF erstellt 2022-11-28; 14 S. | K | lokal, nicht im Repo |
| S-AM-2 | ArchiMate | Bizzdesign, *ArchiMate® 3.2 Concepts* v1.0 | PDF erstellt 2023-05-31; 9 S. | H | lokal, nicht im Repo |
| S-AM-3 | ArchiMate | Bizzdesign, *ArchiMate® 3.2 Elements and Relationships* (Poster) | PDF erstellt 2022-10-17; 2 S. | H | lokal, nicht im Repo |
| S-AM-4 | ArchiMate | Bizzdesign, *ArchiMate 3.1 Concepts* v1.0 | PDF erstellt 2019-05-28; 8 S. | H (Vorgängerversion) | lokal; nicht ausgewertet |
| S-AM-X | ArchiMate | The Open Group, *ArchiMate® 3.2 Specification* (C226) | — | N | **nicht verfügbar; ausgelassen** |
| S-DSM-1 | DSM | [DSM Web — Reading a DSM](https://dsmweb.org/reading-a-dsm/) | veröffentlicht 2019-04-25, geändert 2026-03-03; nach Eppinger & Browning 2012 | D | Web |
| S-DSM-2 | DMM | [DSM Web — Domain Mapping Matrix](https://dsmweb.org/domain-mapping-matrix-dmm/) | veröffentlicht 2019-04-25, geändert 2026-03-03 | D | Web |
| S-DSM-3 | MDM | [DSM Web — Multiple-Domain Matrix](https://dsmweb.org/multiple-domain-matrix-mdm/) | veröffentlicht 2019-04-25, geändert 2026-03-03 | D | Web |
| S-BPMN-1 | BPMN | OMG, [*Business Process Model and Notation 2.0.2*](https://www.omg.org/spec/BPMN/2.0.2/PDF), formal/13-12-09 | Januar 2014; jüngste formale Version laut [OMG-Seite](https://www.omg.org/spec/BPMN/) | N | Web (PDF) |
| S-DAG-1 | DAG | [NetworkX — topological_generations](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.dag.topological_generations.html) | Dokumentation NetworkX 3.7 | D | Web |
| S-DAG-2 | DAG | [NetworkX 2.3 — DAG-Algorithmen](https://networkx.org/documentation/networkx-2.3/reference/algorithms/dag.html) | 2.3, als unmaintained markiert; nur Funktionsbestand | D | Web |

Hashes der lokalen PDFs (SHA-256): S-AM-1 `0dab858eda810c6bb67926e044951f540ec683dd5c35fbfd849ccffa0ef836df` · S-AM-2 `68361eb1641fa7d80d3e35f1749e160cf439158dbfb7de823ec91475d7ce8dc5` · S-AM-3 `d383051a95421441efb0942d4ed0fa6d5ba9716b608d41aed574097f892f2071` · S-AM-4 `58d260c171a59612ecb5284ce1977d065af9684e43228ba5c7118eb244713266`.

Die Webseiten wurden nicht archiviert; ihre Aussagen gelten für den Abruftag. Eine erneute Fallausführung prüft bei Abweichung zuerst die Quelle.

## Regeln

| ID | Quelle · Fundstelle | Stufe | Aussage (eigene Formulierung) | Fälle |
|---|---|---|---|---|
| R-C4-1 | S-C4-1 | D | Ein Container ist eine Laufzeitgrenze um ausgeführten Code oder gespeicherte Daten. Deployment ist eine eigene Frage; derselbe Container bleibt einer, auch wenn er unterschiedlich verteilt wird. | C4-01 |
| R-C4-2 | S-C4-2 | D | Eine Komponente bündelt zusammengehörige Funktionalität hinter einer Schnittstelle, liegt innerhalb eines Containers und ist nicht eigenständig deploybar. Paket-, Modul- oder Ordnergrenzen sind nicht automatisch Komponenten. | C4-01 |
| R-SZ-1 | S-SZ-1 | D | Die DSL erzeugt implizite Beziehungen standardmäßig. `!impliedRelationships true` entspricht `CreateImpliedRelationshipsUnlessAnyRelationshipExistsStrategy`; `false` schaltet ab; ein Klassenname wählt eine andere Strategie. | C4-02, C4-03 |
| R-SZ-2 | S-SZ-2 | D | In der Java-Bibliothek ist `DefaultImpliedRelationshipsStrategy` Standard und erzeugt keine impliziten Beziehungen. `…UnlessSameRelationshipExists…` erzeugt laut Dokumentation meist zu viele Beziehungen. | C4-02 |
| R-AM-1 | S-AM-1, S. 2 | K | ArchiMate 3.2 kennt elf Beziehungstypen in vier Gruppen (strukturell, Abhängigkeit, dynamisch, sonstige) sowie Junctions als Verbinder. | ARC-01–03 |
| R-AM-2 | S-AM-1, S. 2 | K | Realization: Ein Element trägt wesentlich zur Entstehung, Erreichung, Erhaltung oder zum Betrieb eines abstrakteren Elements bei. | ARC-01 |
| R-AM-3 | S-AM-2, S. 5 („Application Service“) | H | Beispiel: Eine Application Function realisiert einen Application Service. Belegt eine gängige Lesart des Endpunktpaars, nicht dessen normative Zulässigkeit. | ARC-01 |
| R-AM-4 | S-AM-1, S. 2; S-AM-2, S. 8 („Composition“) | K / H | Composition: Ein Element besteht aus einem oder mehreren anderen Konzepten. Beispiel: eine Funktion aus drei Teilfunktionen. Eine Mindest-/Höchstzahl ist in den Quellen nicht angegeben. | ARC-02 |
| R-AM-5 | S-AM-1, S. 2; S-AM-2, S. 8 („Junction“) | K / H | Junctions verbinden Beziehungen desselben Typs; And- und Or-Junction werden unterschieden. | ARC-02 (optional) |
| R-AM-6 | S-AM-X | N | Zulässige Endpunktkombinationen je Beziehungstyp. **Ausgelassen** (siehe Entscheidung). | ARC-01 |
| R-DSM-1 | S-DSM-1 | D | Diagonalzellen stehen für Elemente; eine Markierung außerhalb der Diagonale steht für eine gerichtete Interaktion. Die Konventionen IR/FAD und IC/FBD sind zueinander transponiert und tragen dieselbe Information — sofern die Konvention bekannt ist. | DSM-01 |
| R-DSM-2 | S-DSM-1 | D | Die Basis-DSM ist binär (Interaktion vorhanden/markiert); numerische DSMs ergänzen Stärke oder Anzahl. Ein eigener Zustand für „unbekannt“ oder „ausgeblendet“ ist nicht beschrieben. | DSM-01, DSM-03 |
| R-DSM-3 | S-DSM-2 | D | Eine DMM ist rechteckig und bildet Elemente einer Domäne auf Elemente einer anderen ab (Beispiel: Personen auf Aufgaben). | DSM-02 |
| R-DSM-4 | S-DSM-3 | D | Eine MDM setzt DSMs je Domäne auf die Diagonale und DMMs in die Off-Diagonal-Blöcke; mehrere Relationstypen können verschiedene Ausprägungen derselben Teilmatrix ergeben. | DSM-02 |
| R-BPMN-1 | S-BPMN-1 §10.6.2, §13.4.2 | N | Exclusive Gateway: datenbasierte Entscheidung für genau einen ausgehenden Pfad bzw. exklusives Zusammenführen. | BPMN-01 |
| R-BPMN-2 | S-BPMN-1 §10.6.4, §13.4.1 | N | Parallel Gateway: Aufspalten in nebenläufige Pfade und Synchronisation beim Zusammenführen. | BPMN-02, BPMN-03 |
| R-BPMN-3 | S-BPMN-1 §10.9, §13.2, Anhang C | N | Prozessinstanzen, Instanziierung/Beendigung und der Token-Begriff. | BPMN-01–03 |
| R-DAG-1 | mathematische Standarddefinition | A | Ein DAG ist ein gerichteter Graph ohne gerichteten Zyklus. Knotennummerierung ist keine Eigenschaft des Graphen. | DAG-01, DAG-03 |
| R-DAG-2 | S-DAG-1 | D | `topological_generations` schichtet einen DAG in Generationen; bei Zyklus wird `NetworkXUnfeasible` ausgelöst, ggf. erst beim Iterieren. | DAG-02, DAG-03 |
| R-DAG-3 | S-DAG-2 | D | `all_topological_sorts` liefert alle topologischen Ordnungen; `is_directed_acyclic_graph` prüft Zyklenfreiheit. Bestand für 2.3 belegt; für 3.7 nur über S-DAG-1 indirekt. | DAG-02, DAG-03 |
| R-DAG-4 | lokal: LIB `impact.propagate/v1` (s. u.); [ANALYSE.md](../cube-grammar-2026-11-01/ANALYSE.md) | D (lokal) | Der vorhandene Evaluator setzt `i < j` voraus und lehnt die azyklische Kante `1 → 0` mit „cycle / reverse DAG edge rejected“ ab. Implementierungsgrenze, keine Grammatikgrenze. | DAG-01 |

**Lesehinweis BPMN:** Die Abschnittsnummern stammen aus dem Inhaltsverzeichnis der abgerufenen Spezifikation. Der genaue Regelwortlaut von §13.4.1/§13.4.2 und die Glossardefinition „Token“ werden in TASK-014 gelesen und im Fallbericht paraphrasiert, bevor eine Erwartung fixiert wird.

## Zuordnung der 15 Fälle

| Fall | Regeln | Stärkste Stufe | Offen / Arbeitsannahme |
|---|---|---|---|
| C4-01 | R-C4-1, R-C4-2 | D | C4 ist eine Methode ohne Norm; Begriffe gelten für die Seite vom Abruftag. |
| C4-02 | R-SZ-1, R-SZ-2 | D | **Strategie fixiert (A):** DSL mit `!impliedRelationships true` = `…UnlessAnyRelationshipExists…`. Abweichender Java-Standard wird im Fallbericht als Kontrast festgehalten. |
| C4-03 | R-SZ-1 | D | Dass eine implizite Beziehung keine deklarierte Tatsache ist, ist eine Cube-Prüffrage (A), keine Structurizr-Regel. |
| ARC-01 | R-AM-1, R-AM-2, R-AM-3 | K + H | Normative Endpunkt-Zulässigkeit (R-AM-6) ausgelassen. |
| ARC-02 | R-AM-4 (opt. R-AM-5) | K + H | Zähldomäne und Min/Max sind **lokales Versuchsprofil (A)**, nicht ArchiMate. |
| ARC-03 | R-AM-1 | K | Unterscheidung „nicht gefunden“ / „nachweislich nicht vorhanden“ ist Cube-Scope-Frage (A). |
| DSM-01 | R-DSM-1, R-DSM-2 | D | Konvention je Fall explizit wählen (A: IR/FAD). |
| DSM-02 | R-DSM-3, R-DSM-4 | D | Domänen und Relationstypen je Fall selbst festlegen (A). |
| DSM-03 | R-DSM-2 | D | Quelle kennt nur binär/numerisch; die Dreiteilung leer/unbekannt/ausgeblendet ist Arbeitsannahme (A). |
| BPMN-01 | R-BPMN-1, R-BPMN-3 | N | Regelwortlaut in TASK-014 lesen. |
| BPMN-02 | R-BPMN-2, R-BPMN-3 | N | wie BPMN-01 |
| BPMN-03 | R-BPMN-2, R-BPMN-3 | N | wie BPMN-01; keine Engine-Konformität. |
| DAG-01 | R-DAG-1, R-DAG-4 | A + D (lokal) | — |
| DAG-02 | R-DAG-2, R-DAG-3 | D | Nur bei tatsächlicher Ausführung wird die NetworkX-Version des Laufs festgehalten. |
| DAG-03 | R-DAG-1, R-DAG-2, R-DAG-3 | A + D | — |

Alle 15 Fall-IDs der Fallmatrix (Hash `be2d7c88…` am Abruftag) sind abgedeckt. Kein Fall hängt allein an einer Einstiegsseite, die als vollständig gelesene Norm ausgegeben wird.

## Cube- und LIB-Ausgangsstand

| Gegenstand | Stand |
|---|---|
| lunados.cube HEAD | `4e80df4275692864aa81a6dea953141d6ab879f6` (Branch-Basis für MILE-002; enthält C-12-Commits bis `47d915d`, die noch nicht in `main` `7792d0d` sind) |
| P0 v9.4 `morphology.md` | `749bb26b…bfd9` — identisch mit öffentlichem Manifest |
| P0 v9.4 `grammar/concepts.json` · `relations.json` · `constraints.json` | `a15b0db3…00b8` · `a1c0c98b…0488` · `eebc060a…537d8a` — identisch mit Manifest |
| P3-Snapshot `lock.json` | `cb259c59…a1` = gemeldeter P0-Snapshot-Lock |
| Runner `scripts/research/comparison_runner.py` | `e1e480c7…739919` (Fallvertrag v1) |
| lunados.lib HEAD | `4d0765016816b3274446ebe49474268f35c72ba4` |
| LIB `impact.propagate/v1/entry.json` · `evaluator/evaluate.py` | `459bdfaa…b204` · `c98411f9…c668` |

**Arbeitsbaum-Hinweis:** Zum Abrufzeitpunkt enthält der lokale Arbeitsbaum nicht committete P3-Adapteränderungen (`validation_discovery.py`, Änderungen an `server.py`/`surface.py`). Der lokale MCP-Server läuft aus dem Arbeitsbaum. Jeder MILE-002-B-Lauf hält deshalb zusätzlich den Diff-Zustand der Adapterdateien fest.

## Grenzen

- Webquellen ohne Seitenversion gelten nur für den Abruftag.
- ArchiMate: keine normative Zulässigkeitsprüfung (Entscheidung oben). Bizzdesign-Beispiele werden nicht als Norm zitiert.
- BPMN: Fundstellen gebunden, Wortlaut noch zu lesen (TASK-014).
- Dieses Register ändert keine Fälle, Erwartungen, Morphologie, Profile oder Werkzeuge.
