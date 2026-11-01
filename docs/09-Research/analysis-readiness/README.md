# Analysebereitschaft — fixierte Fälle

Format `aiaeao.cube.research-case/1`. Drei exakte Eingabeextraktionen aus dem historischen MCP-Protokoll; Herkunftsdatei und Argumente sind gehasht. Erwartungen wurden vor dem neuen Lauf festgelegt:

| Fall | Erwarteter Fachstatus | Diagnose |
|---|---|---|
| P1-mode-display | PASS | keine |
| P1-method-arity-negative | FAIL | P1_METHOD_SIGNATURE |
| P1-mode-unbound | UNRESOLVED | P1_QUALIFIER_PROFILE_MISSING |

Ein erwartetes FAIL ist kein fehlgeschlagener Test. Fachstatus und `expectation_match` sind getrennt. Die beiden MODE-Fälle eignen sich später als Ausgangsfall/Profilvariante.

## Fallvertrag v1

Pflichtfelder: `format`, `case_id`, `operation`, `invocation_kind`, `origin` mit Pfad/Dateihash/Probe-ID/Referenzversion, `arguments`, `arguments_sha256`, `bindings` mit Kontextformat und kanonischen Hashes von Kontext/Qualifierprofilen sowie `expected` mit Fachstatus und Diagnosecodes. Hashkodierung: UTF-8, sortierte Schlüssel, kompakte JSON-Ausgabe, ensure_ascii=false; auch null hat einen eindeutigen Hash.

Der Loader prüft Hashes und exakte Übereinstimmung mit der angegebenen historischen Eingabe. Der Vertrag v1 ist absichtlich auf diese extrahierten `cube_validate`-Proben begrenzt. Spätere neue Vergleichsfälle benötigen eine explizite Erweiterung des Herkunftsvertrags; untypisierte Fremdsemantik wird nicht eingeführt.

## Berichtsvertrag v1

`aiaeao.cube.research-run/1` enthält Quell-/Codehashes und HEAD, Python/SDK-Version, vollständige Fälle, Rohantworten im SDK-JSON-Modell, tatsächliche Toolliste und Discovery je frischer Verbindung. Die Rohantwort ist die dekodierte SDK-Antwort, keine Behauptung originaler Transportbytes. Jeder Fall trennt Aufrufstatus, Fachstatus, Diagnosecodes, Erwartungsübereinstimmung und fünf Ergebnisdimensionen. Nur die tatsächlich beobachtete deklarative Prüfung erhält OBSERVED; Ausdruck/Bindung als Gesamturteil, Darstellung und Nutzen bleiben NOT_ASSESSED.

Wiederholungsprüfung vergleicht Fachstatus und Diagnosecodes, nicht Zeitstempel/Run-IDs. Konfigurationsfehler haben TOOL_ERROR und keinen Fachstatus. Ein kontrollierter Start eines nicht existierenden Programms belegt UNAVAILABLE ohne erfundene Fachdiagnose. Ein späterer Aufruffehler speichert bereits empfangene Antworten und verhindert die Erfolgsmeldung. Berichte werden ausschließlich in einem neuen Ausgabeordner angelegt.

## Wiederholen

Vom Repository-Root:

```sh
P3/adapters/mcp-local/.venv/bin/python -B scripts/research/comparison_runner.py --output /private/tmp/cube-readiness-neuer-lauf
```

Der Ausgabeordner darf noch nicht existieren. Keine zusätzliche Installation benötigt, wenn die vorhandene Adapter-venv mit MCP 2.0.0 verfügbar ist. Pro Wiederholung wird eine neue lokale stdio-Verbindung geöffnet. Das prüft keine bereits laufende Chat-Verbindung und keine Remote-/Public-Oberfläche.


## Ausgangsstand und Variante vergleichen

```sh
P3/adapters/mcp-local/.venv/bin/python -B scripts/research/comparison_runner.py --output /private/tmp/cube-readiness-vergleich-neu --compare P1-mode-unbound P1-mode-display
```

Der optionale `comparison`-Abschnitt erhält beide Fall-IDs und Eingabehashes, listet Änderungen mit JSON Pointer (einschließlich Unterscheidung fehlend/null) und zeigt beide beobachteten Ergebnisse je Lauf. Das Paar unterscheidet sich nur durch das Hinzufügen von `qualification_profiles`; Kontext und Ausdruck bleiben gleich. Es entsteht kein neues Profil oder neuer Envelope-Typ.
