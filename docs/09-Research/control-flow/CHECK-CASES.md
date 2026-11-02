# MILE-008-A — Prüffälle (TASK-048)

Stand: 2026-11-02 · Maschinenlesbar: [CHECK-CASES.json](CHECK-CASES.json), erzeugt mit [build_check_cases.py](build_check_cases.py) (deterministisch) · **festgelegt vor Spezifikation und Code** · Entscheidungen: [MILE-008 D-1–D-8](../../02-Milestones/MILE-008-control-flow.md)

27 formatneutrale Prüffälle aus BPMN-01, BPMN-02 und BPMN-03 ([Modell](../grammar-sampling/models/bpmn-order.json)). Jeder Fall nennt den deklarierten Kontrollfluss, die Spur (Token mit Instanz, Position, Leitung, Fluss, aufgezeichnete Bedingungsergebnisse), die Abdeckung der Spur (P1.12), die Erwartung **heute** und die Erwartung **mit Profil**. Sie sind die Orakel-Grundlage für TASK-049, TASK-050 und TASK-051.

**Schichten (D-3, D-4):** *P1* (9 Fälle) prüft die Deklaration und die Flussbindung einzelner Spur-Aussagen. *LIB* (18 Fälle) prüft die Spur je Instanz gegen das Modell. **Statusregel (D-5, D-6):** belegter Verstoß → FAIL; fehlende Abdeckung oder fehlende Bedingungsergebnisse → UNRESOLVED, nie FAIL; Überschuss wird gezählt. Diagnosecodes und value-Bezeichner sind Arbeitstitel.

**Modellergänzung:** Flüsse bpmn:f-checked, bpmn:f-manual-done, bpmn:f-auto-done, bpmn:f-approved, bpmn:f-ship und das Merge-Gateway ergänzen die Modellnotiz („both lead to split“, „join leads to ship“) um Namen. Varianten weichen bewusst vom Modell ab und sind im JSON als `variant_of_model` gekennzeichnet.

| Fall | Matrix | Frage | Heute | Mit Profil |
|---|---|---|---|---|
| CF-01 | BPMN-01 | Ist das deklarierte Modell wohlgeformt, und leitet i1/tok-route an ein Ziel eines ausgehenden Flusses? | P1 PASS | **P1 PASS** |
| CF-02 | BPMN-01 | Ein exklusives Gateway mit zwei Default-Flüssen? | NE | **P1 FAIL · P1_CONTROL_FLOW_INVALID** |
| CF-03 | BPMN-01 | Zwei bedingte Flüsse mit derselben Reihenfolge? | NE | **P1 FAIL · P1_CONTROL_FLOW_INVALID** |
| CF-04 | BPMN-02 | Ein paralleles Gateway mit Default-Fluss? | NE | **P1 FAIL · P1_CONTROL_FLOW_INVALID** |
| CF-05 | BPMN-01 | Ein inklusives Gateway? | NE | **P1 UNRESOLVED · P1_CONTROL_FLOW_UNSUPPORTED** |
| CF-06 | BPMN-01 | Leitet i1/tok-route an Ship, das kein Ziel des XOR ist? | P1 PASS | **P1 FAIL · P1_FLOW_UNDECLARED** |
| CF-07 | BPMN-02 | Liegt i1/tok-stock auf einem nicht deklarierten Fluss? | P1 PASS | **P1 FAIL · P1_FLOW_UNDECLARED** |
| CF-08 | BPMN-02 | Bleibt binding-context/8 ohne Kontrollfluss unverändert? | P1 PASS | **P1 PASS** |
| CF-09 | BPMN-01 | routedTo von einem Token ohne deklarierte Position am Gateway? | P1 PASS | **P1 UNRESOLVED · P1_TOKEN_POSITION_UNDECLARED** |
| CF-11 | BPMN-01 | Nahm i1 am XOR genau einen Pfad? | NE | **LIB PASS · exclusive_one_path** |
| CF-12 | BPMN-01 | Nahm i1 am XOR zwei Pfade? | NE | **LIB FAIL · exclusive_two_paths** |
| CF-13 | BPMN-01 | Erreichte i1/tok-route das XOR, ohne geleitet zu werden? | NE | **LIB FAIL · exclusive_no_path** |
| CF-14 | BPMN-01 | Nahm i1 genau einen Pfad, wenn die Spur nicht als vollständig erklärt ist? | NE | **LIB UNRESOLVED · coverage_undeclared** |
| CF-15 | BPMN-01 | Nahm i1 die erste wahre Bedingung? | NE | **LIB PASS · condition_first_true** |
| CF-16 | BPMN-01 | Nahm i1 den Default, als keine Bedingung wahr war? | NE | **LIB PASS · default_without_true** |
| CF-17 | BPMN-01 | Nahm i1 den Default, obwohl f-manual wahr war? | NE | **LIB FAIL · default_with_true_condition** |
| CF-18 | BPMN-01 | Nahm i1 die richtige Bedingung, wenn keine Bedingungsergebnisse aufgezeichnet sind? | NE | **LIB UNRESOLVED · conditions_unrecorded** |
| CF-19 | BPMN-01 | Nahm i1 die zweite wahre Bedingung statt der ersten? | NE | **LIB FAIL · not_first_true** |
| CF-21 | BPMN-02 | Durfte Ship für i1 starten? | NE | **LIB PASS · join_complete** |
| CF-22 | BPMN-02 | Startete Ship für i2 ohne Lagerprüfung? | NE | **LIB FAIL · join_incomplete** |
| CF-23 | BPMN-02 | Warum wartet i2? | NE | **LIB PASS · join_waiting** |
| CF-24 | BPMN-02 | Wartet i2, wenn die Spur nicht als vollständig erklärt ist? | NE | **LIB UNRESOLVED · coverage_undeclared** |
| CF-25 | BPMN-03 | Startete Ship für i1 mit dem Kreditergebnis von i2? | NE | **LIB FAIL · join_incomplete** |
| CF-26 | BPMN-02 | Bleibt in i1 ein überzähliger Lager-Token liegen? | NE | **LIB PASS · join_complete** |
| CF-27 | BPMN-02 | Erzeugte der Split für i1 je Ausgang einen Token? | NE | **LIB PASS · split_complete** |
| CF-28 | BPMN-02 | Fehlt nach dem Split für i1 der Kredit-Zweig? | NE | **LIB FAIL · split_incomplete** |
| CF-29 | BPMN-01 | Reicht das Merge den Token von approve-manual einmal weiter? | NE | **LIB PASS · merge_pass_through** |

**Abdeckung:** Deklaration 9 (davon 1 Regressionsschutz), exklusiv 4, Bedingungsreihenfolge 5, Join 6, Split 2, Merge 1; je Prüfart mindestens ein PASS und ein FAIL, bei exklusiv, Bedingung und Join zusätzlich UNRESOLVED.

**Heute:** 22 Fälle sind nicht ausführbar (NE). Teilersatz gibt es über die P1.12-Zählregeln aus MILE-005 (CC-11–CC-16), aber ohne Gateway-Typ, Flussbindung und Bedingungen. Die 5 heute ausführbaren Fälle (CF-01, CF-06, CF-07, CF-08, CF-09) bestehen als Einzelaussagen mit PASS, auch die falsche Leitung an Ship und der unbekannte Fluss — das ist die Lücke. Bestätigt durch den Baseline-Lauf und eine Probe mit dem unveränderten P1.12-Adapter.
