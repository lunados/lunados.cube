# Lunados Cube — Lernen aus fünf Grammatikvergleichen

**Stand:** 1. November 2026 · **Aktuelles Ziel:** Structurizr/C4, ArchiMate, DSM/MDM, BPMN und DAG als Vergleichsmaßstäbe nutzen, um Cube, LIB, Profile und Visualisierung gezielt zu verbessern.

## Zielkorrektur

Die Breite des Vergleichs betrifft **alle fünf Ansätze**, nicht den Bau vollständiger Interoperabilität. Die frühere Roadmap hat diesen Umfang überschritten. Sie bleibt mit ihren Aufwand-, Nutzen- und Komplexitätsschätzungen als [XXL-Referenz](XXL-REFERENZ.md) erhalten und ist kein aktueller Umsetzungsauftrag. Auch diese frühere Schätzung bezog sich auf begrenzte Austauschprofile; sie ist keine belastbare Schätzung universeller Vollkompatibilität.

Die maßgebliche Leitfrage lautet: **Was kann Cube aus dem direkten Vergleich lernen — und welcher kleine Eingriff schafft den größten Nutzen?**

## Aktueller Erkenntnisstand

Die [Antworten auf die sieben Leitfragen](LERNVERGLEICH.md) unterscheiden Quellenbefunde, geprüfte Fähigkeiten und noch offene Abdeckung:

- **Envelopes:** Der vorhandene generische Rahmen ist ein plausibler Ausgangspunkt. Eine vollständige Methoden- oder Lebenszyklusabdeckung ist nicht bewiesen; zusätzliche Methodennamen erfordern nicht automatisch neue Envelopes.
- **LIB:** Analysefunktionen passen bereits in den vorhandenen Library-Vertrag. Hoher erwarteter Nutzen liegt bei typisierter Teilgraphauswahl, Erreichbarkeit, Zyklen/Reihenfolgen und quellengebundener Verdichtung.
- **Profile:** Referenz- und Kardinalitätsregeln lassen sich abgegrenzt formulieren. Slot-, Methoden-, Relations- und Ausführungskardinalitäten bleiben unterschiedliche Prüfgegenstände.
- **LENS/MODE/Achsen:** Gute Grundlage, aber keine vollständige Visualisierungsautomatik. LENS-Hervorhebung, Projektion, Granularität, Betriebsregime und Layout müssen getrennt geprüft werden; M/O-Achsen sind im gelesenen Printer noch reserviert.
- **Visuelle Grammatik:** Der statische Prüfer bestand mit 129 Ankern, 12 Formoptionen, 17 Farben und zehn Negativkontrollen. Das belegt nicht alle Kombinationen oder ihre Verständlichkeit.
- **Entitätenabdeckung:** 129 visuelle Anker sind nicht 129 fachliche Entitäten. Der gelesene v9.4-Konzeptindex enthält 80 Einträge; daraus folgt keine vollständige Abdeckung aller Fremdsprachen.
- **Nutzen:** Die Vergleichsaufgaben reichen von verständlicher Architekturkommunikation über Kopplungs-/Änderungsanalyse bis zu präzisen Prozesszuständen. Die Auswahl nützlicher Fähigkeiten erfolgt anhand dieser Aufgaben, nicht anhand maximaler Symbol- oder Adapteranzahl.

## Kleine Roadmap für einen weiteren Analysedurchlauf

Keine Adapterimplementierung, produktive Engine oder Import-/Export-Suite im Umfang. Kleine Modellbeispiele und vorhandene Prüfer reichen, um viele Lücken zu finden. Eine Stichprobe ist ausdrücklich kein Vollständigkeitsbeweis.

| Schritt | Ergebnis | Zusätzlicher Analyseaufwand | Erwarteter Nutzen | Komplexität |
|---|---|---:|---|---|
| **L1 — Zähl- und Vertragsbasis fixieren** | Envelopes, Konzepte, visuelle Anker und Profile auseinanderhalten; je Ansatz konkrete Referenzversion und Aufgaben festlegen | **0,5–1 PT** | Sehr hoch: verhindert Kategorienfehler | Niedrig–mittel |
| **L2 — 15 gezielte Grammatikfälle** | Je Ansatz zwei Normalfälle und ein Gegenfall; Cube-Ausdruck, benötigter Vertrag, Diagnose und offene Kompatibilitätslücke | **2–3 PT** | Sehr hoch: zeigt konkrete Wiederverwendung und tatsächliche Lücken | Mittel–hoch; BPMN/ArchiMate am anspruchsvollsten |
| **L3 — Visuelle Ausdrucksprüfung** | Gegenfälle in Graph, Matrix und Sequenz: Unterschiede erkennbar, Verdichtung nachvollziehbar, Unknown nicht versteckt; kleiner Lesbarkeitstest | **1–2 PT** | Hoch: beantwortet die Frage nach sinnvoller Visualisierung | Mittel |
| **L4 — Lernbilanz und Maßnahmenwahl** | Priorisierte Vorschläge für LIB, Profile, VG und Dokumentation; nur belegte Kandidaten für Envelope-/Morphologieänderung | **0,5–1 PT** | Sehr hoch: übersetzt den Vergleich in kleine, nützliche Aufgaben | Niedrig–mittel |
| **Summe** | Begrenzter Erkenntnisdurchlauf über alle fünf Ansätze | **4–7 PT** | — | — |

PT sind grobe Engineering-/Review-Personentage, keine Agentenlaufzeit und kein Liefertermin. Die Schätzung gilt für 15 begrenzte Beispiele, vorhandene Werkzeuge und keine neue Produktimplementierung. Fehlender Normzugang oder erforderliche fachliche Entscheidungen werden als offen ausgewiesen, nicht durch zusätzliche Großprojekte ersetzt. Die bereits ausgeführte Bestandsaufnahme ist nicht als neuer Vollaufwand eingerechnet.

## Was jeder Fall liefern muss

1. **Fremdaufgabe und Unterscheidung:** Welches Problem löst der andere Ansatz, welche zwei Fälle müssen unterscheidbar bleiben?
2. **Cube-Darstellung:** Konkrete Referenten, Relationen, Qualifikationen, Scope und gegebenenfalls Envelope/Methodenvertrag.
3. **Prüfbarkeit:** Was lässt sich heute validieren? Was ist nur dokumentiert, braucht ein Profil oder bleibt unresolved?
4. **Visualisierung:** Welche Sicht hilft; welche Information muss sichtbar oder aufrufbar bleiben?
5. **Lücke und kleinster Eingriff:** Dokumentation → Komposition → Profil → LIB → visuelle Regel → erst bei nachgewiesenem Bedarf Morphologie.
6. **Nutzen:** Konkrete Nutzerfrage, erwartete Verbesserung und eine einfache Möglichkeit, sie zu messen.

Eine bloße Ablage fremder Semantik als Artifact/Freitext zählt nicht als vollständige Abdeckung. Umgekehrt rechtfertigt eine fehlende gleichnamige Cube-Entität noch keine neue Kategorie. Die Prüfung betrachtet Ausdruck, bindbaren Vertrag, implementierte Prüfung und verständliche Darstellung getrennt.

## Dokumente und Arbeitsstand

**Nachweisgrenze:** Die öffentliche Cube-Referenz ist ausschließlich lesbare Dokumentation. Interne P3-MCP-Proben stammen vom lokal verbundenen Adapter und gelten nur für die jeweils geprüfte Operation und Eingabe; sie belegen weder Ausführung noch allgemeine semantische Vollständigkeit. Ein neuer lokaler Chat muss die tatsächlich verfügbare Oberfläche zuerst ermitteln. Frühere Ergebnisse und Dateiprüfungen ersetzen diesen aktuellen Verbindungsnachweis nicht.

- [Lernvergleich: Antworten, Prioritäten und 15 Prüffälle](LERNVERGLEICH.md)
- [Erste interne Analyse mit Library-/MCP-Nachweisen](ANALYSE.md)
- [Bisheriger Research und spätere Korrekturen](HANDOVER.md)
- [XXL-Referenz: frühere Interoperabilitäts-Roadmap und Aufwand](XXL-REFERENZ.md)
- [Neue Inventur und Visual-Grammar-Prüfung](evidence/learning-review-inventory.json)

Die Dateien liegen lokal im SPACE-Repository. Produktcode, Library-Verträge und Morphologie wurden nicht verändert. Veröffentlichung, Commit und Push sind nicht erfolgt.
