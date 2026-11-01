# MILE-005-A — Prüffälle (TASK-030)

Stand: 2026-11-01 · Maschinenlesbar: [CHECK-CASES.json](CHECK-CASES.json), erzeugt mit [build_check_cases.py](build_check_cases.py) (deterministisch) · **festgelegt vor Spezifikation und Code** · Entscheidungen: [MILE-005 D-1–D-6](../../02-Milestones/MILE-005-completeness-instances.md)

21 formatneutrale Prüffälle aus den MILE-002-Fällen ARC-02, ARC-03, DSM-03, BPMN-01, BPMN-02 und BPMN-03. Jeder Fall nennt Aussagen, Vollständigkeitserklärungen (D-2: Referent × Relationstyp × Richtung oder Paar), bei Instanzfällen die Instanzbindungen und Prädikateigenschaften (D-4), die Erwartung **heute** und die Erwartung **mit Profil**. Sie sind die Orakel-Grundlage für TASK-031, TASK-033 und TASK-034.

**Schichten (D-6):** *P1* prüft Einzelaussagen im neuen Profil (Instanzbindung, Wohlgeformtheit der Erklärungen). *LIB* wertet Abwesenheit, Zählung und Join-Aktivierung über eine Aussagenmenge aus. **Statusregel:** im erklärten Umfang erfüllt → PASS, verletzt → FAIL; außerhalb → UNRESOLVED mit `P1_COVERAGE_UNDECLARED` (D-3), nie FAIL und nie „geprüft leer“. Diagnosecodes und Ergebnisbezeichner sind Arbeitstitel; TASK-031 darf sie umbenennen, Status und Schicht nicht.

| Fall | Matrix | Frage | Erklärung | Heute | Mit Profil |
|---|---|---|---|---|---|
| CC-01 | ARC-03 | Realisiert in der Service-Sicht nichts Transaction Processing? | — | NE | **LIB UNRESOLVED · coverage_undeclared · P1_COVERAGE_UNDECLARED** |
| CC-02 | ARC-03 | Realisiert Billing Transaction Processing (Vollsicht)? | am:transaction-processing · realizes · incoming | NE | **LIB PASS · absent_checked** |
| CC-03 | ARC-03 | Realisiert Accounting Transaction Processing nicht (Vollsicht)? | am:transaction-processing · realizes · incoming | NE | **LIB FAIL · absence_contradicted** |
| CC-04 | DSM-03 | Hat printer keine Abhängigkeit zu parser? | Paar m:printer → m:parser | NE | **LIB PASS · absent_checked** |
| CC-05 | DSM-03 | Hat validator keine Abhängigkeit zu printer? | Paar m:printer → m:parser | NE | **LIB UNRESOLVED · coverage_undeclared · P1_COVERAGE_UNDECLARED** |
| CC-06 | DSM-03 | Hat printer keine Abhängigkeit zu resolver, wenn die Zeile printer erklärt ist? | m:printer · dependsOn · outgoing | NE | **LIB PASS · absent_checked** |
| CC-07 | DSM-03 | Hat printer keine Abhängigkeit zu validator, wenn die Zeile printer erklärt ist? | m:printer · dependsOn · outgoing | NE | **LIB FAIL · absence_contradicted** |
| CC-08 | ARC-02 | Besteht Financial Processing aus zwei bis drei Teilfunktionen (Vollsicht)? | am:financial-processing · composedOf · outgoing | NE | **LIB PASS · within_bounds** |
| CC-09 | ARC-02 | Besteht Financial Processing aus zwei bis drei Teilfunktionen (Service-Sicht)? | — | NE | **LIB UNRESOLVED · coverage_undeclared · P1_COVERAGE_UNDECLARED** |
| CC-10 | ARC-02 | Besteht Financial Processing aus zwei bis drei Teilfunktionen, wenn nur eine erklärt vorliegt? | am:financial-processing · composedOf · outgoing | NE | **LIB FAIL · out_of_bounds** |
| CC-11 | BPMN-01 | Wurde Token i1/tok-route genau einem Pfad zugeleitet? | bpmn:i1/tok-route · routedTo · outgoing | NE | **LIB PASS · within_bounds** |
| CC-12 | BPMN-01 | Wurde Token i1/tok-route genau einem Pfad zugeleitet (zwei Aufzeichnungen)? | bpmn:i1/tok-route · routedTo · outgoing | NE | **LIB FAIL · out_of_bounds** |
| CC-13 | BPMN-01 | Wurde Token i1/tok-route genau einem Pfad zugeleitet (Spur nicht erklärt)? | — | NE | **LIB UNRESOLVED · coverage_undeclared · P1_COVERAGE_UNDECLARED** |
| CC-14 | BPMN-02 | Durfte der Join für i1 aktivieren? | bpmn:i1 · onFlow · incoming-to-join | NE | **LIB PASS · join_enabled** |
| CC-15 | BPMN-02 | Durfte der Join für i2 aktivieren? | bpmn:i2 · onFlow · incoming-to-join | NE | **LIB FAIL · join_not_enabled** |
| CC-16 | BPMN-02 | Durfte der Join für i2 aktivieren (Spur nicht erklärt)? | — | NE | **LIB UNRESOLVED · coverage_undeclared · P1_COVERAGE_UNDECLARED** |
| CI-01 | BPMN-03 | Paart J1 Token aus verschiedenen Instanzen (gemeinsamer Scope)? | — | PASS | **P1 FAIL · P1_INSTANCE_MISMATCH** |
| CI-02 | BPMN-03 | Instanz als Scope (Regressionsschutz) | — | FAIL P1_REFERENT_MISMATCH, P1_SCOPE_CONFLICT | **P1 FAIL · P1_REFERENT_MISMATCH, P1_SCOPE_CONFLICT** |
| CI-03 | BPMN-02 | Paart der Join Token derselben Instanz? | — | PASS | **P1 PASS** |
| CI-04 | BPMN-03 | Paart J1 Token verschiedener Instanzen, wenn eine Instanz nicht gebunden ist? | — | PASS | **P1 UNRESOLVED · P1_INSTANCE_UNDECLARED** |
| CI-05 | BPMN-01 | Gilt die Instanzregel auch für Prädikate ohne Eigenschaft? (Negativkontrolle) | — | PASS | **P1 PASS** |

Varianten (vom Modell abweichende Erklärungen oder Aussagen): CC-06, CC-07 (Zeilenerklärung printer), CC-10 (nur eine Teilfunktion). Sie sind im JSON als `variant_of_model` gekennzeichnet.

**Abdeckung:** Abwesenheit 7 Fälle, Zählung 6, Join-Aktivierung 3, Instanzbindung 5. Je Regelart mindestens ein PASS, ein FAIL und ein UNRESOLVED; bei der Instanzbindung ein Regressionsschutz (CI-02) und eine Negativkontrolle (CI-05).

**Heute:** 16 Fälle sind nicht ausführbar (NE) — dieselbe Lücke wie in MILE-002. Die fünf Instanzfälle stützen sich auf vier MILE-002-Läufe, die der [Baseline-Lauf](../../10-Evidence/MILE-005/task030-baseline-report.json) wiederholt; [Abgleich](../../10-Evidence/MILE-005/task030-baseline-check.json): alle 21 Erwartungen für heute bestätigt.
