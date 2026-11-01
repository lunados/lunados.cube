# Was Cube aus den fünf Vergleichen lernen kann

**Stand:** 1. November 2026 · **Ziel:** Grammatik und Vertragsbindung abtasten, konkrete Lücken ausweisen und nützliche Erweiterungen priorisieren. **Status:** erste Antworten mit Quellenbefunden und einem begrenzten Prüfprogramm; kein Vollständigkeitsnachweis über alle fünf Fremdsprachen.

Die frühere Interoperabilitäts-Roadmap ist als [XXL-Referenz](XXL-REFERENZ.md) archiviert. Sie beschreibt keinen aktuellen Umsetzungsauftrag. Breite bedeutet hier: **von allen fünf Ansätzen lernen**. Import-/Exportadapter und vollständige Roundtrips sind dafür keine Voraussetzung.

## 1. Sind die bisherigen Envelopes ausreichend?

**Vorläufig: als erweiterbarer Vertragsrahmen plausibel; als nachgewiesen vollständige Liste nein.** Die Zahl der Envelopes ist nicht das entscheidende Kriterium. Entscheidend ist, ob ein neuer Fall mit präzisen Ein-/Ausgaben, Zuständen, Bindungen und Fehlerfällen ausdrückbar ist, ohne Begriffe umzudeuten.

Dabei sind drei Dinge zu trennen:

- **Semantisches Muster:** etwa Decision, Dialectics, Experimentation, Validation, Feedback oder die Beschreibung einer Execution.
- **Methodenvertrag:** welche konkreten Eingaben, Ausgaben, Voraussetzungen und Wirkungen die Methode hat.
- **Envelope:** der versionierte Rahmen, in dem Beschreibung, Aufruf oder Ergebnis getragen werden. Ein weiterer Methodenname erfordert nicht automatisch ein weiteres Envelope-Schema.

Der konkret gelesene EXP-024-Nachweis „Five Method Envelopes“ umfasst **Decision, Dialectics, Experimentation, Validation und Feedback**. `Execution` ist dort kein sechster getesteter Fall, sondern betrifft an anderer Stelle den Ausführungs-/Lebenszykluskontext. Das verbietet keine Execution-Envelope; es verhindert nur einen falschen Abdeckungsnachweis. Die historische Erweiterung von einem Decision-förmigen Ergebnis zu einem generischen `evaluator-result/v0.2` zeigt bereits, dass feste Fachformen einen zu engen Rahmen ergeben können.

**Was die fünf Vergleiche zusätzlich herausfordern:** Projektion/Verdichtung (C4), typisierte Modellprüfung (ArchiMate), mehrteilige Analyseergebnisse und Alternativen (DSM), partielle Ordnung (DAG), zustandsbehaftete Aktivierung und Synchronisation (BPMN). Diese Aufgaben sind zunächst Methoden bzw. Kompositionen. Sie rechtfertigen nicht ohne Weiteres fünf neue Envelopes.

**Prüfkriterium für eine echte Envelope-Erweiterung:** Zwei fachlich verschiedene Zustände werden unter dem vorhandenen Vertrag ununterscheidbar, oder erforderliche Bindungen lassen sich nur in untypisiertem Freitext verstecken. Prüfen: Methoden-/Modellrevision, Eingaberollen, Prozess-/Aufrufidentität, Scope, Reihenfolge, partielle Ergebnisse, Fehler/Unresolved, Abbruch, mehrfacher Ergebnisempfang und Effektklasse. Nur fehlende Pflichtunterscheidungen begründen einen neuen Vertrag oder eine neue Revision. Ein schöner neuer Name reicht nicht.

Quelle: `lunados.space/web/docs/cube/AIAEAO_EXP024_Charge3_Five_Envelopes_v0.1/README.md`; Cube-Morphologie v9.4 §§5.7, 5.14, 5.18. Das Envelope-Urteil bleibt offen, bis diese Gegenfälle tatsächlich modelliert und geprüft sind.

## 2. Können hilfreiche Analysemethoden als LIB angelegt werden?

**Ja.** Der bestehende Library-Vertrag bietet dafür bereits Methoden-ID, Revision, typisierte Rollen, Ausgabe, Preconditions, Nicht-Implikationen, Evaluator, Orakel und Referenzfälle. Die vorherige Analyse hat zehn Einträge mit 109/109 Prüfungen bestätigt. Wiederverwendbare Algorithmen müssen nicht neu erfunden werden; die Cube-spezifische Leistung liegt vor allem in ihrer korrekten Bindung, Auswahl und Ergebnisinterpretation.

| Kandidat — Arbeitstitel, noch kein neuer Registry-Eintrag | Was man daraus lernt bzw. gewinnt | Nutzen / Komplexität | Wichtige Grenze |
|---|---|---|---|
| Typisierte Teilgraphauswahl + Erreichbarkeit | Welche Abhängigkeiten gehören zu dieser Frage; was ist möglicherweise betroffen? | Sehr hoch / mittel | Erreichbarkeit ist keine reale Kausalität; Richtung und Scope binden |
| SCC + topologische Schichten | Wo sind Zyklen; welche Reihenfolgen sind möglich? | Sehr hoch / niedrig–mittel | SCC ist nicht Clustering; mögliche Parallelität berücksichtigt noch keine Ressourcen |
| Quellengebundene Aggregation/Projektion | Dieselben Inhalte auf verständliche Detailstufen verdichten | Sehr hoch / mittel | Herkunft, verwendete Regel und Informationsverlust erhalten |
| Relationssignatur + Populationskardinalität | Ungültige Kombinationen und fehlende/überzählige Bindungen erklären | Hoch / mittel | Vollständigen und partiellen Modellbestand unterscheiden |
| Graph-/Matrixvergleich | Welche Beziehungen ändern sich zwischen zwei Revisionen oder Szenarien? | Hoch / mittel | Gleiche Identitäten und Vergleichsgrundlage erforderlich |
| Clustering / Partitionierung | Architekturgrenzen und starke Kopplung untersuchen | Hoch / mittel–hoch | Zielfunktion, Gewichte, Seed und Alternativen offenlegen; kein automatisch „bestes“ Design |
| Begrenzte Transition-/Trace-Prüfung | Vorzeitige Joins, falsche Instanzzuordnung oder unzulässige Übergänge erkennen | Hoch bei Prozessfällen / hoch | Setzt explizite Prozesssemantik voraus; kein Ersatz für eine Engine |

**Priorität aus dieser Analyse:** Teilgraphauswahl/Erreichbarkeit, Zyklus-/Reihenfolgeanalyse und quellengebundene Verdichtung. Sie beantworten häufige Fragen mehrerer Ansätze und benötigen keine neue Ontologie. Diese Rangfolge ist eine begründete Nutzenhypothese für Cube, noch keine gemessene Kundennutzenstudie.

`impact.propagate/v1` und `claim.compose/v1` sind vorhandene Ausgangspunkte mit begrenztem Geltungsbereich. Die dokumentierte DAG-Nummerierungsgrenze und die modulare Impact-Formel dürfen bei einer Generalisierung nicht verschwinden. Neue Bedeutung → neuer Vertrag/Revision.

## 3. Lassen sich Referenzen und Kardinalitäten als Profile abgrenzen?

**Ja, für domänenspezifische Regeln ist das der passende erste Ansatz.** Bereits vorhanden sind scoped Prädikatssignaturen, Methodenkardinalitäten und feste Instanziierungsslots. Die Live-Proben haben deren Durchsetzung gezeigt. Daraus folgt noch keine allgemeine Relationsmultiplizitätsprüfung über einen Modellbestand.

Ein hilfreiches Profil müsste mindestens festlegen:

1. **Referenz:** Identität, Namespace, Revision, erlaubte Zieltypen, Scope, Auflösungsquelle und Umgang mit fehlenden/mehrdeutigen Zielen.
2. **Relation:** Prädikat, Richtung, Endpunkttypen, notwendige Qualifikationen und erlaubte Ableitungen.
3. **Kardinalität:** Was wird gezählt — Referenzen, unterschiedliche Zielidentitäten, Rollenbelegungen oder Aktivierungen? Mindest-/Höchstzahl, Zeitpunkt und Zähldomäne.
4. **Abdeckung:** Ist der relevante Modellbestand vollständig? Bei unvollständiger Sicht bedeutet „nicht gefunden“ nicht automatisch „existiert nicht“.
5. **Geltung:** Profilversion und tatsächlicher Validator; ein beschreibender Text ist noch keine durchgesetzte Regel.

Ontologische Festlegungen bleiben unverändert. Ein Fremdprofil darf beispielsweise ein `one`-Slot nicht still zu `many` machen. BPMN-Join-Zählungen sind wiederum Regeln einer Prozessinstanz, nicht einfach Relationskardinalitäten. **Der Erkenntnisgewinn ist die saubere Trennung dieser Regeln**, nicht ein universelles Min-/Max-Feld überall.

## 4. Reichen Achsen, LENS und MODE für effiziente Visualisierung?

**Als konzeptionelle Grundlage weitgehend ja; als vollständige Implementierung oder Effizienznachweis noch nicht.** Die Komponenten beantworten unterschiedliche Fragen:

| Bestandteil | Aufgabe |
|---|---|
| X/Y/Z und T/F/M/O | Welche Referenten und Qualifikationen werden beschrieben? |
| LENS | Welche fachliche Frage bzw. welche deklarierten Aspekte sollen hervortreten? |
| VIEW / Projektionsregel | Welche Struktur wird gezeigt: Baum, Graph, Matrix, Sequenz, Zeit-/Phasensicht? |
| Granularität / Scope | Welche Detailstufe und welcher Ausschnitt sind für die Frage relevant? |
| MODE | Welches explizit gebundene Interpretations-/Betriebsregime gilt? Keine allgemeine Erlaubnis zur Umdeutung |
| Layout / Interaktion | Wie werden Inhalte lesbar platziert, erkundet und verglichen? |

**Konkrete Grenze:** VP-03-LENS verändert laut Vertrag die Hervorhebung ausdrücklich markierter Elemente bei unveränderter Geometrie und unverändertem Inhalt. Daraus folgt keine automatische semantische Filterung, Aggregation oder neue Graphstruktur. VP-09 bietet bereits mehrere Achsenpaare; **M und O sind dort reserviert**, M×T und O×X ausdrücklich nicht umgesetzt. Spätere Profile ergänzen Granularität und Sichtaufteilung, aber keine universelle Ableitung aller Sichten.

**Effizient** muss gemessen werden: Wie schnell findet jemand eine Abhängigkeit, einen Widerspruch oder eine Freigabegrenze? Wie oft verwechselt er Plan, Beobachtung und bestätigtes Ergebnis? Ein kleines Vergleichsexperiment mit denselben Aufgaben in Graph, Matrix und Sequenz liefert hierfür mehr Erkenntnis als weitere Symbole. Renderzeit, Abdeckung und menschliche Verständlichkeit sind getrennte Kriterien.

## 5. Ist die visuelle Grammatik vollständig?

**Für den abgegrenzten Ankerbestand ist Konsistenz nachgewiesen; für alle Ausdrucks- und Benutzungsfälle nicht.** Der erneut ausgeführte statische Prüfer meldete:

```text
PASS P1-VG-basic: 129 v9.4 Unicode anchors; 12 form choices
(11 historical + neutral fallback); 17 colors; 10 negative controls;
immutable v9.4; public manifest integrity; zero SVG
```

Das belegt Registry-, Form-/Farb- und bestimmte Negativregeln. Es belegt weder alle möglichen Kompositionen noch Lesbarkeit, Fremdnotationsabdeckung oder Fehlerfreiheit aller Renderer. Der P0-Visual-Guide nennt außerdem eine gesondert reservierte Palette von **26 mathematischen Operatoren**, deren vollständiges Register in Annex J nicht enthalten ist. Das ist eine konkrete Dokumentations-/Registergrenze, kein Beweis, dass sämtliche Operatoren für die betrachteten Aufgaben benötigt werden.

Die nächste Abdeckungsprüfung braucht drei Ebenen:

- **Inventar:** Sind die für eine Aufgabe benötigten Marker vorhanden und eindeutig?
- **Komposition:** Lassen sich Richtung, Typ, Multiplikation, Gruppierung, Parallelität, Schleife, Ausnahme, Unsicherheit und Herkunft unterscheidbar ausdrücken?
- **Nutzung:** Bleiben diese Unterscheidungen bei Verdichtung, Graustufen, begrenzter Fläche und unterschiedlichen Fonts erkennbar?

Zuerst Gegenbeispiele bauen, etwa „Sequence Flow vs. Message Flow“, „AND vs. XOR“, „unbekannte vs. leere Matrixzelle“ und „abgeleitete vs. deklarierte Beziehung“. Fehlt nur eine zulässige Kombination oder Legende, braucht es nicht zwingend einen neuen kanonischen Anker. Es werden hier noch keine vollständigen visuellen Gegenbeispieltests behauptet.

## 6. Decken 120–130 Entitäten alle Optionen der fünf Ansätze ab?

**Das ist derzeit nicht nachgewiesen; die Zählbasis muss zuerst korrigiert werden.** Im tatsächlich gelesenen v9.4-Stand:

| Bestand | Anzahl | Bedeutung |
|---|---:|---|
| `grammar/concepts.json` | **80** | Konzeptindex: X 26, Y 29, Z 25; einschließlich analytischer Dimensionen und anderer nicht pauschal instanziierbarer Kategorien |
| `visual/symbols.json` | **129** | Visuelle Anker: Gruppen X 22, Y 63, Z 31, UI 13 |
| Historische visuelle Alias-IDs | **4** | Separat; keine vier zusätzlichen kanonischen Entitäten |

Insbesondere ist ein UI-Zeichen keine zusätzliche fachliche Entität. Die Gruppe `UI` und die feinere Rollenklassifikation `ui_marker` haben unterschiedliche Zählweisen; die 13 sind die Gruppenzahl. Auch der 80er-Index ist kein Beweis, dass die gesamte Morphologie exakt 80 instanziierbare Entitätstypen besitzt.

Ein BPMN-Gateway, ein ArchiMate-Goal und ein C4-Container verlangen keine drei gleichnamigen Cube-Wurzeln. Sie können durch vorhandene Referenten, typisierte Rollen, Relationen und Profile beschrieben werden — **wenn ihre fachlichen Unterscheidungen erhalten und prüfbar bleiben**. Umgekehrt ist die Ablage als beliebiges Artifact oder Annotation allein kein ausreichender Abdeckungsbeleg.

Die richtige Frage je Fremdkonstrukt lautet: **Kann Cube zwei dort unterschiedliche Fälle ebenfalls unterscheiden, die zugehörige Regel binden und die Verletzung diagnostizieren?** Erst ein scheiternder konkreter Fall rechtfertigt die Diskussion einer morphologischen Lücke. Eine kleine Stichprobe kann Lücken finden, aber keine universelle Vollständigkeit beweisen.

## 7. Welche Aufgaben stehen bei den fünf Ansätzen im Vordergrund?

Die mittlere Spalte beschreibt den jeweiligen Aufgabenfokus; die rechte ist unsere eigene Nutzenableitung für Cube. Rangfolgen sind kontextabhängig.

| Ansatz | Typische zentrale Aufgabe | Lerngewinn mit hohem erwarteten Nutzen für Cube |
|---|---|---|
| **C4 / Structurizr** | Softwarearchitektur auf verständlichen Abstraktionsebenen kommunizieren; mehrere konsistente Sichten pflegen | Frage und Zielgruppe bestimmen die Sicht. Wenige klare Ebenen und nachvollziehbare Verdichtung können mehr helfen als maximale Ausdrucksdichte. [C4-Kontextsicht](https://c4model.com/diagrams/system-context), [Structurizr-Ableitungsregeln](https://docs.structurizr.com/dsl/implied-relationships) |
| **ArchiMate** | Fachliche und technische Architekturzusammenhänge für Veränderungsentscheidungen beschreiben | Beziehungen und Rollen präzise typisieren; gezielte Viewpoints und Wirkungsketten über Bereiche hinweg. Keine bloße Gleichsetzung ähnlich benannter Begriffe. [Einführung der ArchiMate-Community](https://archimate-community.pages.opengroup.org/workgroups/archimate-101/) |
| **DSM / MDM** | Kopplung, Rückkopplung, Modularisierung und Reihenfolge in komplexen Abhängigkeiten untersuchen | Kompakte Matrixsichten plus SCC, Clustering und Impact-Fragen; besonders nützlich für Refactoring. [DSM-Einführung](https://dsmweb.org/introduction-to-dsm/), [DSM/DMM/MDM](https://dsmweb.org/tutorial-overview/) |
| **BPMN** | Abläufe, Verzweigungen, Synchronisation und Zusammenarbeit ausdrücklich modellieren | An Gegenfällen lernen, welche Zustands-, Korrelations- und Übergangsverträge fehlen. Sequence, Message und Datenbeziehung nicht verwechseln. [OMG-Baseline 2.0.2](https://www.omg.org/spec/BPMN/2.0.2) |
| **DAG** | Partielle Ordnung, Erreichbarkeit und mögliche Bearbeitungsreihenfolgen untersuchen | Allgemeine Graphnormalisierung, Zyklusprüfung, topologische Schichten und Bedingtheit von Parallelität. DAG selbst ist eine mathematische Struktur, kein einzelner konkurrierender Produkthersteller. [DAG-Algorithmen](https://networkx.org/documentation/stable/reference/algorithms/dag.html) |

Die größte kurzfristige Nutzenchance liegt aus heutiger Sicht in **besser beantwortbaren Fragen**: „Was hängt wovon ab?“, „Was ändert sich?“, „Welche Bindung fehlt?“, „Welche Sicht braucht dieser Betrachter?“ und „Was wird hier nur geplant und was ist beobachtet?“ Der Vergleich sollte an diesen Aufgaben gemessen werden.

## 8. Begrenzte Abtastung: konkrete nächste Fälle

Dies ist eine priorisierte Untersuchungsmatrix, kein bereits abgeschlossener Fremdsprachentest. Pro Ansatz werden zwei Normalfälle und ein Gegenfall mit Quelle, Cube-Ausdruck, erforderlichem Profil, erwarteter Diagnose und Darstellungsbedarf dokumentiert.

| Ansatz | Normalfall 1 | Normalfall 2 | Gegenfall | Primärer Lernort |
|---|---|---|---|---|
| C4 | Komponente innerhalb eines Containers | Beziehung in eine übergeordnete Sicht verdichten | Abgeleitete Beziehung wird fälschlich als direkte Tatsache behandelt | Projektion / LIB / View |
| ArchiMate | Getypte fachliche/technische Beziehung | Profilgebundene Belegung einer Relation | Fehlender Partner in nur partiell bekanntem Modell | Referenz- und Kardinalitätsprofil |
| DSM/MDM | Gerichtete Abhängigkeitsmatrix | Domänenübergreifende Zuordnung | Leere, unbekannte und ausgeblendete Zelle werden gleich dargestellt | LIB / Profil / visuelle Komposition |
| BPMN | XOR-Entscheidung mit explizitem Zustand | AND-Join mit korrelierter Prozessinstanz | Join feuert nach zwei Signalen aus verschiedenen Instanzen | Envelope / Transition-Vertrag / MODE |
| DAG | Beliebige IDs und azyklische Rückwärtskante | Mehrere mögliche Reihenfolgen | Zyklus oder reine Referenz wird als ausführbare Abhängigkeit behandelt | LIB / Dependency-Profil |

Das Ergebnis je Fall wird getrennt bewertet: **Ausdruck vorhanden**, **Vertrag bindbar**, **Prüfung implementiert**, **Darstellung eindeutig**, **Nutzen plausibel/gemessen**. Ein einziges Gesamt-PASS würde diese unterschiedlichen Nachweise verdecken.

Für jede Lücke wird der kleinste passende Eingriff benannt: bessere Dokumentation; bestehende Komposition; versioniertes Profil; LIB-Funktion; visuelle Regel; erst zuletzt neue Morphologie. „Ungeprüft“ bleibt ausdrücklich ungeprüft. Quellen müssen jeweils versionsgebunden sein; insbesondere ArchiMate-Normversion und konkrete Multiplizitätsregel sind vor dem betreffenden Fall noch zu pinnen.

## 9. Nachweise dieses Durchlaufs

- [Neue Inventur und Visual-Prüfung](evidence/learning-review-inventory.json)
- [Vorherige interne Analyse und MCP-Proben](ANALYSE.md)
- Lokale Quellen: Cube-P0 v9.4 `morphology.md` §§5.7/5.14/5.18, `grammar/concepts.json`, `visual/symbols.json`, `visual/README.md`; `P2/visual-printer-2d-lab/VP03_LENS_GRAMMAR.md`; `P2/visual-printer-axes-v1/README.md`; `lunados.lib/LIBRARY_CONTRACT.md`; EXP-024 Charge-3 README in SPACE.

Die neue Prüfung bestätigt den statischen VG-Bestand. Sie erweitert die früheren Library-/MCP-Tests nicht um eine behauptete Gesamtvalidierung aller fünf Ansätze. Die weitere Abtastung aus Abschnitt 8 ist der gezielte nächste Durchlauf.
