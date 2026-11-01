# MILE-002 — 15 geplante Vergleichsfälle

Status aller Fälle: planned. IDs sind lokal zu MILE-002. Die Reihenfolge ist keine Nutzenrangfolge.

| ID | Ansatz | Art | Aufgabe | Entscheidende Unterscheidung / Prüffrage | Lernort |
|---|---|---|---|---|---|
| C4-01 | C4/Structurizr | Normalfall | Komponente innerhalb eines Containers | Ebenen, Identitäten und Zugehörigkeit getrennt binden; Komponenten-/Containerbegriffe nicht über Namen allein gleichsetzen. | Profile / Referenzen |
| C4-02 | C4/Structurizr | Normalfall | Zwei Komponentenbeziehungen in eine übergeordnete Sicht verdichten | Quellbeziehungen, Aggregationsregel und resultierende Beziehung unterscheidbar halten; gewählte Structurizr-Strategie fixieren. | LIB / Projektion |
| C4-03 | C4/Structurizr | Gegenfall | Abgeleitete Beziehung wird als direkt deklarierte Tatsache behandelt | Zeigen, welche Herkunfts-/Ableitungsbindung die falsche Gleichsetzung verhindern müsste; keine Kausalität aus Verdichtung ableiten. | Vertragsbindung / Herkunft |
| ARC-01 | ArchiMate | Normalfall | Eine normativ belegte typisierte Beziehung | Für die ausgewählte Version konkrete Endpunkttypen und Relation mit Regelstelle festhalten; Cube-Typbindung dagegen prüfen. | Referenz-/Relationsprofil |
| ARC-02 | ArchiMate | Normalfall | Abgegrenzte Profilbelegung mit zählbaren Zielreferenzen | Zähldomäne und Vollständigkeit festlegen. Eine zusätzlich gewählte Min-/Max-Regel ausdrücklich als lokales Versuchsprofil kennzeichnen, sofern sie nicht normativ belegt ist. | Kardinalitätsprofil |
| ARC-03 | ArchiMate | Gegenfall | Fehlender Partner in einem nur partiell bekannten Modell | Nicht gefunden von nachgewiesen nicht vorhanden unterscheiden; keine Verletzung aus einer unvollständigen Sicht erfinden. | Scope / Ungewissheit |
| DSM-01 | DSM/MDM | Normalfall | Gerichtete Abhängigkeiten in einer Domäne | Zeilen-/Spaltenrichtung, Zellbedeutung und Identitäten binden; eine transponierte Lesart darf nicht still dasselbe bedeuten. | Relation / Matrixbedarf |
| DSM-02 | DSM/MDM | Normalfall | Zwei Domänen mit domänenübergreifender Zuordnung | DSM- und DMM-Beziehungen mit expliziten Domänen verbinden; heterogene Relationstypen nicht zu einer universellen Kante verflachen. | Profile / LIB |
| DSM-03 | DSM/MDM | Gegenfall | Leere, unbekannte und ausgeblendete Zelle fallen zusammen | Die drei Zustände semantisch unterscheiden und den Darstellungsbedarf für MILE-003 festhalten. | Abdeckung / visuelle Regel |
| BPMN-01 | BPMN | Normalfall | XOR-Entscheidung in einer abgegrenzten Instanz | Alternative aktivierte Pfade mit explizitem Zustand/Instanzbezug beschreiben; Syntax-PASS nicht als Ausführung interpretieren. | Envelope / MODE |
| BPMN-02 | BPMN | Normalfall | AND-Join mit korrekt korrelierten Eingängen | Instanz, erwartete Eingänge und Synchronisationsbedingung an einer kleinen dokumentierten Spur unterscheiden. | Übergangsvertrag / Kardinalität |
| BPMN-03 | BPMN | Gegenfall | Join kombiniert Signale verschiedener Prozessinstanzen | Konkret zeigen, welche Bindung oder Prüfung diese Verwechslung ausschließt bzw. wo sie heute fehlt. Keine Engine bauen. | Envelope / Korrelation |
| DAG-01 | DAG | Normalfall | Azyklischer Graph mit beliebigen IDs und einer numerisch rückwärts gerichteten Kante | Nummerierung von Zyklizität unterscheiden; die bekannte i<j-Grenze des vorhandenen Evaluators nicht als Grammatikgrenze ausgeben. | LIB / Normalisierung |
| DAG-02 | DAG | Normalfall | Mehrere zulässige topologische Reihenfolgen | Partielle Ordnung, ausgewählte Abhängigkeitstypen und mehrere Lösungen festhalten; keine Ressourcenparallelität aus der Ordnung folgern. | LIB / Dependency-Profil |
| DAG-03 | DAG | Gegenfall | Echter gerichteter Zyklus | Zyklus gegenüber bloßer Umnummerierung unterscheiden; ausdrückbaren Graph und für DAG-Analyse unzulässige Eingabe getrennt bewerten. | Prüfvertrag / Diagnose |

## Quellen- und Ergebnisbindung

Die Matrix konkretisiert den Untersuchungsumfang; normative Detailregeln werden in TASK-009 fixiert. Die ArchiMate-Zählregel in ARC-02 ist ausdrücklich eine lokale Profilfrage, solange keine entsprechende Normregel belegt ist. Aus jedem Dreierpaket entstehen drei eigene Fallberichte; ein gemeinsamer pauschaler PASS ersetzt sie nicht.

Die Darstellungsspalte eines Berichts benennt erforderliche Unterscheidungen und passende Sichten. Ein Render-/Lesbarkeitsnachweis wird erst in MILE-003 erwartet. Fälle werden nicht nachträglich vereinfacht, nur um vorhandene Cube-Prüfer bestehen zu lassen; begründete Lücken sind ein gewünschtes Forschungsergebnis.
