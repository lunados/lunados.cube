# Konsolidierte Spezifikationen

Die folgenden begrenzten Fähigkeiten sind umgesetzt und anhand MILE-001 bis MILE-010 geprüft:

- [comparison-evidence](comparison-evidence/spec.md): fixierte lokale Prüffälle (v1 historisch, v2 neu erstellt mit gepinnter Herkunft), getrennte Ergebnisse, Wiederholung, Variantenvergleich, dokumentierte Nichtausführbarkeit.
- [grammar-sampling](grammar-sampling/spec.md): Research-Protokoll für quellengebundene Fremdansatz-Vergleiche (MILE-002).
- [visual-distinction-check](visual-distinction-check/spec.md): Research-Protokoll für Darstellungsprüfungen mit Inventur, Minimalpaaren/Mockups und Agenten-Vorprüfung als Proxy (MILE-003).
- [learning-balance](learning-balance/spec.md): Research-Protokoll für vorab gerahmte Maßnahmenpriorisierung mit Proben (MILE-004).
- [completeness-declaration](completeness-declaration/spec.md): erklärte Abdeckung und Populationsregeln; „geprüft leer“ nur im erklärten Umfang (P1.12, lunados.lib `analyze.population/v1`; MILE-005).
- [instance-binding](instance-binding/spec.md): typisierte Instanzzugehörigkeit; instanzübergreifende Paarung im gemeinsamen Scope wird erkannt (P1.12; MILE-005).
- [cell-state-display](cell-state-display/spec.md): vier Zellzustände ohne Farbe (VP-10; MILE-005).
- [remote-coverage-validation](remote-coverage-validation/spec.md): `binding-context/8` und `/9` über den G5-Remote-Connector mit P1.12 und P1.13, live abgenommen (MILE-006, MILE-010).
- [declared-axis-order](declared-axis-order/spec.md): Matrix in deklarierter Reihenfolge mit farbfreier Rückkopplungsmarke (VP-10 0.10.1; MILE-006).
- [readability-check](readability-check/spec.md): kurze, angeleitete Sichtprüfung von Darstellungsänderungen (MILE-006).
- [statement-set-display](statement-set-display/spec.md): Aussagenmengen ohne Migrationsplan als Zellmatrix (VP-10 0.11.0; MILE-007).
- [relation-aggregation](relation-aggregation/spec.md): Verdichtung mit Quellenspur und Verlustbericht in lunados.lib, im Cube nur gelesen (MILE-007).
- [control-flow-declaration](control-flow-declaration/spec.md): Gateways, Flüsse, Bedingungsreihenfolge und Default deklarieren; Spur-Aussagen an deklarierte Flüsse binden (P1.13 `binding-context/9`; MILE-008).
- [trace-conformance](trace-conformance/spec.md): Spur je Instanz gegen den deklarierten Kontrollfluss, in lunados.lib berechnet, ohne Bedingungsauswertung (MILE-008).
- [instance-view](instance-view/spec.md): deklarierte Spur je Instanz mit genommenem Pfad und Join je Eingang, Urteile aus lunados.lib gelesen (VP-11; MILE-009).
- [remote-plan-views](remote-plan-views/spec.md): Plansichten VP-07 bis VP-11 über den G5-Remote-Connector, byte-gleich zu lokal; CPU-Grenze des Workers dokumentiert (MILE-010).
- [local-discovery-accuracy](local-discovery-accuracy/spec.md): additive lokale Kontext-/Profilmetadaten mit ausdrücklichen Präsenz-/Runtime-Grenzen.

Die übrigen bestehenden P0/P1/P2/P3-Verträge wurden nicht nach OpenSpec migriert und behalten ihre bisherigen Orte und Geltung. Der neue Specs-Bereich ersetzt nicht die Cube-Morphologie.
