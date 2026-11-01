# Skript für einen späteren menschlichen Lesbarkeitstest

Status: vorbereitet, **nicht durchgeführt** (D-1). Stand: 2026-11-01. Grundlage: [Agenten-Vorprüfung](PRECHECK.md), Antwortschlüssel in [precheck/PLAN.json](precheck/PLAN.json) (`answer_keys`).

## Ziel

Prüfen, ob Menschen die vier vorrangigen Unterscheidungen aus dem Bild allein richtig, schnell und mit passender Sicherheit lesen, und zwar mit dem Kandidaten besser als mit der heutigen Darstellung. Der Test bewertet Darstellungen, nicht Personen.

## Bedingungen und Stimuli

Jede Unterscheidung hat eine Ausgangs- und eine Kandidatenbedingung, bei V-05 zusätzlich eine Kontrollbedingung. Stimuli als PNG in fester Größe aus den gehashten SVGs; je Stimulus auch eine Graustufenfassung (farbfreie Lesbarkeit, optional).

| Item | Unterscheidung | Ausgang | Kandidat | Kontrolle |
|---|---|---|---|---|
| T-01 | V-01, Fall C4-02 | R-2a-01 | M-01A (linkes Feld) | R-2b-01 |
| T-02 | V-01, Fall C4-03 | — (nicht darstellbar) | M-01A (rechtes Feld) | — |
| T-03 | V-05 | R-1a-01 | M-05C | M-05A |
| T-04 | V-09 | P-09b-01 | M-09C | M-09B |
| T-05 | V-12 | M-12A | M-12B | — |

SVG-Pfade und Hashes: [MOCKUPS](MOCKUPS.md), [Render-Logs](../../10-Evidence/MILE-003/). Die Kennzeichnung „MOCKUP — kein Printer-Output“ bleibt sichtbar; Fall- und Variantenkennungen im Kopf werden für den Test abgedeckt, damit sie keine Antwort verraten.

## Design

- Jede Person sieht jedes Item genau einmal, in einer Bedingung; Zuteilung über ein lateinisches Quadrat, Reihenfolge der Items zufällig.
- Pilot: 12 Personen (je Bedingung 4–6 Antworten pro Item). Das reicht für grobe Richtungen, nicht für statistische Aussagen.
- Zielgruppe: Personen, die Architektur- oder Prozessdiagramme lesen; Cube-Kenntnis wird nur als Band erfasst (keine / etwas / regelmäßig).

## Ablauf je Person (ca. 15 Minuten)

1. Einverständnis: freiwillig, anonym, jederzeit abbrechbar; keine Namen, keine Kontaktdaten im Datensatz.
2. Einführung, wörtlich vorlesen: „Sie sehen nacheinander fünf Diagramme. Beantworten Sie jede Frage nur mit dem, was im Bild steht. ‚Lässt sich aus dem Bild nicht sagen‘ ist eine gültige Antwort.“ Keine Erklärung von Legenden oder Begriffen.
3. Je Item: Bild zeigen, Frage und Antwortoptionen zeigen, Zeit ab Anzeige bis zur Antwort messen, danach Sicherheit 1–5 abfragen.
4. Abschluss: zwei offene Fragen — „Was war am schwersten zu erkennen?“ und „Gab es etwas, das Sie für widersprüchlich hielten?“

## Fragen und Schlüssel

Die Fragen verwenden die Wörter der Bilder (Restbefund der Vorprüfung). Option „X — lässt sich aus dem Bild nicht sagen“ ist immer vorhanden.

| Item | Frage | Optionen | Richtig je Stimulus |
|---|---|---|---|
| T-01 | Ist die Beziehung api → db deklariert oder abgeleitet? | A deklariert · B abgeleitet · C Herkunft unbekannt · X | R-2a: X (B nur durch Nachschlagen im Ledger, gesondert zählen) · R-2b: B · M-01A: B |
| T-02 | Ist die Beziehung api → db deklariert oder abgeleitet? | wie T-01 | M-01A: C |
| T-03 | Hat printer eine Abhängigkeit zu parser? | A ja · B nein, geprüft · C unbekannt (nicht erhoben) · X | R-1a: X · M-05A/M-05C: B |
| T-04 | Ist der Plan abarbeitbar? Wenn nein: Welche Kanten liegen auf einem Zyklus? | A abarbeitbar · B nicht abarbeitbar + Kantenauswahl · X | P-09b: X · M-09B, M-09C: B mit allen fünf Kanten |
| T-05 | Stammt ein Eingang des Joins aus einer anderen Instanz, und ist ein Start von ship belegt? | A fremder Eingang, Start belegt · B fremder Eingang, Start nicht belegt · C kein fremder Eingang · X | M-12A: X oder B · M-12B: B |

T-04 wird als ganz richtig nur gewertet, wenn alle fünf Kanten gewählt sind; Teilauswahlen werden getrennt erfasst (Fehler „ein Zyklus übersehen“).

## Messgrößen und Auswertung

- Richtig-Anteil je Item und Bedingung; Median der Antwortzeit; Sicherheit getrennt für richtige und falsche Antworten (Kalibrierung).
- Überlesen: Anteil sicherer Antworten (Sicherheit ≥ 4), wo das Bild „X“ verlangt.
- Erfolgskriterium für einen Kandidaten (Pilot): Richtig-Anteil ≥ 0,8 und nicht schlechter als die Ausgangsbedingung; kein Anstieg des Überlesens. Ergebnis ist eine Richtung für MILE-004, kein Nachweis.

## Datensatz (CSV)

`person_code, band, item, condition, stimulus_sha256, grayscale, answer, kanten_auswahl, correct, lookup_only, seconds, confidence, comment`

`person_code` ist eine zufällige Kennung ohne Bezug zur Person.

## Aufwand

Vorbereitung 0,5 PT (Stimuli abdecken, Formular, Zufallszuteilung), Durchführung ca. 15 min je Person, Auswertung 0,5 PT.
