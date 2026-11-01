# MILE-004-A — Probeergebnisse und Antworten auf Leitfrage 1 und 4 (TASK-025)

Stand: 2026-11-01 · Plan: [probes/PROBE-PLAN.md](probes/PROBE-PLAN.md) (`a0f6e95`, Nachtrag L-2 in `caec0e2`) · Lauf: [task025-probe-run.json](../../10-Evidence/MILE-004/task025-probe-run.json), Fehlversuch: [attempt1](../../10-Evidence/MILE-004/task025-probe-run-attempt1.json) · Skript: [run_probes.py](probes/run_probes.py)

Alle zwölf gepinnten Quellen stimmten beim Lauf mit ihren Hashes überein. Agent-Umgebung: Python 3.13.16, `jsonschema` 4.26.0.

## Ablauf

Der erste Lauf brachte E-1 und E-2 wie erwartet. Die drei Render-Aufrufe wurden abgelehnt: L-1 wegen eines Fehlers im Laufskript (Hülle von `plan_source` statt `source` übergeben), L-2 mit `VP07_ADAPTER_MAPPING`, weil Referenten mit `/` keine Anzeige-IDs sind. Eine Label-Map wurde als reines Anzeigeargument im Plan nachgetragen und vor dem zweiten Lauf committet; Eingaben, Erwartungen und Regeln blieben unverändert (maschinell gegen `a0f6e95` geprüft).

## Leitfrage 1 — Envelope (E-1, E-2)

Alle sechs Aufrufe und sechs Ergebnisse sind gültig gegen `evaluator-call/v0.1` bzw. `evaluator-result/v0.2`; die Identität Aufruf ↔ Ergebnis stimmt.

| Pflichtunterscheidung | E-1 Projektion (C4-02/03) | E-2 Spurprüfung (BPMN-03) |
|---|---|---|
| bewertet / unaufgelöst | **T** `disposition` | **T** `disposition` (Verstoß vs. unvollständig) |
| Bindung an die Eingaben, ein Ergebnis je Aufruf | **T** `derivation_ref` | **T** `derivation_ref` |
| keine Ausführungsbehauptung | — | **T** `effectful_execution_authorized`, `runtime_authority` |
| fachlicher Kern | **U** Endpunkte, Verlust in `outcome.detail`; Grund in `outcome.value`; Strategie in `parameters` | **U** Instanz der Aktivierung in `parameters`; Instanz je Token in `inputs[].content`; konform vs. Verstoß in `outcome.value` |

Alle zwölf Träger wie erwartet; kein N. Kein Fallpaar ist in allen Feldern gleich. E-1a/E-1b und E-2a/E-2b unterscheiden sich in typisierten Feldern aber **nur im Digest** `derivation_ref`; der fachliche Unterschied (mit/ohne Verlust, konform/Verstoß) steht ausschließlich in untypisierten Feldern. Ergebnis beider Proben: **R-E2**, wie erwartet.

**Antwort auf Leitfrage 1:** Für Projektion (Architektur) und instanzgebundene Spurprüfung (Prozess) **reicht der Envelope-Rahmen**; eine neue Envelope ist nicht begründet. Begründet ist eine **Typisierungslücke** auf zwei Ebenen, für die heute kein Bindungspunkt existiert:

- **Methodenergebnis:** Weder `evaluator-result/v0.2` noch das EXP-024-Evaluatorregister noch `lunados.lib/entry/v1` (Ausgabe nur `concept_id` + `cardinality`) können ein Schema für `outcome.detail`/`value` binden. Kleinster Eingriff: **LIB-Vertragsrevision** mit Verweis auf ein Ergebnisschema je Methode, gegen das der Evaluator prüft; Envelope unverändert.
- **Instanz je Eingang:** `evaluator-call/v0.1` kennt Rolle, Referenz und Revision je Eingang, aber keinen Scope; das Szenario hat nur einen `scope_ref`. Das deckt sich mit G-08 (typisierte Instanzbindung als Profil).

Präzise offen: Teilergebnisse, Abbruch, mehrfacher Ergebnisempfang über längere Spuren und Effektklassen jenseits `pure_declarative` wurden nicht geprobt.

## Leitfrage 4 — LENS, MODE, Achsen (L-1, L-2)

| Probe | Erwartung | Beobachtung | Abgleich |
|---|---|---|---|
| L-1a Provenienz-Linse | drei Kanten gleicher Akzent; Klassen nur in Metadaten | e1, e2, e3 gleich hervorgehoben; „PROVENANCE · 3 DECLARED FOCUS“; Ledger nennt Prädikate, nicht die Herkunft | erfüllt |
| L-1b Epistemologie-Linse, Präfix `derived:` | nur e-implied hervorgehoben; deklariert und ungebunden gleich | nur e2 grün und breiter; e1 und e3 gleich grau; „EPISTEMOLOGY · 1 DECLARED FOCUS“ | erfüllt |
| L-2 Partition `track` | zwei Panels i1 und i2 | zwei Panels **je Schritt** (p0, p1), jedes mit **beiden** Strängen („track: i1, i2“); die Partition packt Stränge zusammen, solange das Budget reicht (VP-07 PE-2, `_pack`) | **abweichend** |
| L-2 | Panel i1: e-stock; Panel i2: e-cross; J1 wiederholt | beide Kanten in jedem Panel; Wiederholung über die Schritt-Panels gelistet | **abweichend** |
| L-2 | e-cross wie e-stock gezeichnet | ja, keine Markierung | erfüllt |
| L-2 | Zugehörigkeit von J1 zu i1 nicht im Bild | nicht im Bild; Track gilt nur für Subjekte | erfüllt |
| MODE | NE (vorab) | — | nicht ausführbar |

SVGs: [L-1a](../../10-Evidence/MILE-004/L-1a/L-1a-01.svg), [L-1b](../../10-Evidence/MILE-004/L-1b/L-1b-01.svg), [L-2](../../10-Evidence/MILE-004/L-2/L-2-01.svg); Berichte und Quellen je Ordner.

**Antwort auf Leitfrage 4:**

- **LENS** trägt je Linse genau **eine binäre, deklarierte Hervorhebung**, keine Klassifikation. Drei Herkunftsklassen sind mit keiner Linse unterscheidbar, und die Hervorhebung ist farbabhängig (vgl. PO-3). Herkunft gehört in eine typisierte Bindung (G-02) mit Kantenstil (VR-01); ein LENS-Ausbau ist nicht begründet.
- **Achsen und Partition** gruppieren nach deklarierter Track-Map, aber nur **Subjekte**, und die Partition **packt** mehrere Stränge in ein Panel. Eine Instanzgruppierung ist damit nicht garantiert; die Instanz eines Objekts (J1) und die instanzübergreifende Kante bleiben unsichtbar. Es fehlen eine typisierte Instanzbindung (G-08) und eine Gruppierungsregel, die Instanzen nie zusammenlegt (VR-12; Vorbild: `layer` wird nie zusammengelegt). Neuer Printer-Befund **PO-8**: „Partition `track` ist eine Packung, keine Gruppierungsgarantie“.
- **MODE** bleibt **präzise offen**: prüfbar erst mit einem eingefrorenen MODE-Schema (P0 §3.10, C021). Morphologisch ist Mode ein Betriebsregime und kein Träger für Instanzidentität; die Proben geben keinen Anlass, das zu ändern.
- VP-09-Achsenpaare wurden nicht geprobt; M und O sind dort reserviert.

## Folgen für die Lernbilanz (TASK-026/027)

- Keine Envelope- und keine Morphologie-Kandidaten aus diesen Proben.
- Neue bzw. geschärfte Maßnahmen: **LIB-Vertragsrevision mit Ergebnisschema je Methode** (aus E-1/E-2), **G-08** bestätigt für Envelope und Darstellung, **PO-8** Partition ohne Gruppierungsgarantie.
- G-02 + VR-01 und G-08 + VR-12 werden durch die Proben gestützt, nicht ersetzt.

Grenzen: Envelope-Instanzen von Hand erstellt, kein Evaluator ausgeführt; vier Proben belegen Ausdrückbarkeit an diesen Fällen, nicht Vollständigkeit.
