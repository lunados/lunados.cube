# ADR-001 — Lib-Snapshot: direkter Build-Pfad und Host-Pfad zur Laufzeit

Status: **accepted** · Datum: 2026-11-06 · Zugehöriger Change: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md), [TASK-091](../05-Tasks/TASK-091-lib-host-path-adr.md) · Entscheidung: MILE-020 D-3 durch den Nutzer am 2026-11-06

## Kontext

Die Functions Library besitzt einen versionierten `INDEX.json` mit Hashes der einzelnen `entry.json`-Dateien. Build und Tests des Cube können heute einen Lib-Checkout direkt lesen: `P2/visual-printer-cells-v1/scripts/materialize_s01_s16.py` verwendet standardmäßig den Nachbar-Checkout oder `--lib`, liest den Index und führt einen ausgewählten Evaluator aus. `P2/visual-printer-instances-v1/tests/test_vp11.py` sucht ein Lib-Schema im Nachbar-Checkout und überspringt den Test, wenn es fehlt. Diese vorhandenen Lesewege belegen weder die Prüfung eines vorgegebenen **Index-Hashes** noch eine Host-Anbindung.

P1.8 prüft `library_ref` nur auf Format und holt keine Lib-Datei (`P1/simulation-profile-v1/P1_8_ACCEPTANCE_SPEC.md`, §2 und §8). Der G5-Quellstand nennt `library_resolution: format_check_only` (`P3/remote-mcp-g5/python-core/core_runtime.py`). Die dortige P1.8-Entscheidung namens „D-3 Library pin“ betrifft die Optionalität von `library_ref`; sie ist **nicht** die hiesige MILE-020-Entscheidung D-3.

Die Relay-Baseline `agent-relay-poc-v3/docs/10-contracts/MILE-071-MODULE-CONTRACT-BASELINE.md` beschreibt für die Functions Library einen **Host-selected Descriptor snapshot**, den der Cube über den Host erhält. Sie bezeichnet damit eine Zielarchitektur, keine nachgewiesene aktuelle Laufzeitbindung. MILE-020 muss den heutigen direkten Entwicklungsweg und dieses Ziel auf einen identischen, überprüfbaren Stand beziehen.

## Optionen

| Option | Folge |
|---|---|
| Nur direkter Checkout | Einfach für Build und Tests, aber keine festgelegte Laufzeitübergabe durch den Host. |
| Nur Host-Snapshot | Einheitlicher Transport, aber Build und Tests wären von einem Host abhängig. |
| Direkter gepinnter Stand für Build/Tests; gepinnter Host-Snapshot zur Laufzeit | Zwei Bezugswege mit einem gemeinsamen Inhaltsanker und expliziter Fehlerbehandlung. **Gewählt.** |

## Entscheidung

1. **Build und Tests** dürfen den ausgewählten Lib-Snapshot direkt lesen. **Zur Laufzeit** erhält der Cube den ausgewählten Lib-Snapshot über den Host. Ein lokaler Pfad oder Host-Name identifiziert den Inhalt nicht.
2. Führender Identitätsanker ist in beiden Fällen der **SHA-256-Hash der exakten Bytes von `INDEX.json`**, verglichen mit einem vorab ausgewählten Pin. Der Pin muss unabhängig vom gerade gelesenen Snapshot feststehen; der gelesene Index darf seinen eigenen Sollwert nicht liefern. Für jede tatsächlich verwendete `entry.json` wird zusätzlich der im geprüften Index deklarierte SHA-256-Hash gegen ihre Bytes geprüft. Weitere genutzte Quellen oder ausführbarer Code brauchen ihre eigenen deklarierten Bindungen; der Index-Hash allein beglaubigt sie nicht.
3. Gleiche verifizierte Index-Bytes und passende Entry-Bytes erlauben die Aussage, dass die **ausgewählten Lib-Definitionen** auf beiden Wegen gleich gebunden sind. Sie belegen weder einen gleichen vollständigen Checkout noch eine gleiche Ausführungsumgebung, Host-Verfügbarkeit, Authority, Admission oder fachliche Wahrheit.
4. Fehlt ein benötigter Pin, Snapshot oder Eintrag, oder passt ein Hash nicht, wird die betroffene Bindung ausdrücklich als nicht verfügbar beziehungsweise fehlerhaft behandelt. Es gibt keinen stillen Wechsel auf einen Nachbar-Checkout, einen früheren Cache, eine andere Host-Antwort oder `latest`.

| Fall | Festgelegte Behandlung |
|---|---|
| Direkter Build-/Test-Snapshot, vorgegebener Index-Pin und benötigte Entry-Hashes stimmen | Ausgewählte Lib-Definitionen dürfen für diesen Build/Test verwendet werden; keine Aussage über den Host. |
| Host-Snapshot zur Laufzeit, derselbe vorgegebene Index-Pin und benötigte Entry-Hashes stimmen | Inhaltsbindung ist zulässig; die konkrete Host-Übergabe und ihr Consumer müssen gesondert implementiert und geprüft werden. |
| Host-Snapshot oder vorgegebener Pin fehlt | Explizit nicht verfügbar; keine direkte Laufzeit-Ausweichquelle. |
| Index-Hash oder benötigter Entry-Hash weicht ab | Bindung ablehnen und Abweichung melden; keinen Ersatzstand wählen. |
| Direkter und Host-Snapshot haben verschiedene verifizierte Index-Hashes | Keine Pfadgleichheit behaupten; ausgewählte Pins und Bereitstellung klären, bevor beide als derselbe Stand bezeichnet werden. |

Der aktuelle Lib-Index mit SHA-256 `aa2cfc92bd1aeb98ae72840fe5d225b7af6932824c57adc9635d6e82b9bbcdb6` ist ein **Beispiel des am Entscheidungstag geprüften Standes**, kein zeitloser fest eingebauter Sollwert. [TASK-091-Nachweis](../10-Evidence/MILE-020/TASK-091-RESULT.md) bindet die gelesenen Quellen.

## Konsequenzen

- Die Formulierung der MILE-071-Baseline („Cube receives snapshots through the host“) bleibt als Laufzeit-Ziel gültig. Diese ADR ergänzt den direkten, gepinnten Build-/Test-Pfad und die gemeinsame Index-Identität; sie ändert die Relay-Baseline nicht rückwirkend.
- Für Relay ist eine **dokumentarische Folge-/Verweisnotiz** zur MILE-071-Baseline vorzusehen: Verweis auf ADR-001 und MILE-020 D-3, Build-/Test-Ausnahme, Auswahl und Übergabe des Soll-Index-Pins, notwendige Entry-Prüfung und die Fehlerfälle. Die zuständige Relay-Arbeit muss diese Notiz in ihrem eigenen Verfahren integrieren; TASK-091 schreibt nicht in die Relay-Baseline.
- Ein künftiger Host-Loader muss Pin-Auswahl, Übergabe und Fehlerfälle konkret definieren und verifizieren. Weder diese ADR noch die MILE-020-Deskriptoren implementieren ihn. Bestehende P1.8- und G5-Formatprüfung bleibt als aktueller Stand gesondert ausgewiesen.
