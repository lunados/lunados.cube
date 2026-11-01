"""MILE-005 TASK-030: erzeugt CHECK-CASES.json (formatneutrale Prüffälle, Erwartung heute und mit Profil) deterministisch.
Aufruf aus dem Repo-Wurzelverzeichnis: python3 -I docs/09-Research/completeness-instances/build_check_cases.py
Die Fälle sind die Orakel-Grundlage für TASK-031/033/034. Diagnosecodes sind Arbeitstitel; ihre Namen darf TASK-031
festlegen, Status und Schicht nicht.
"""
import hashlib, json
from pathlib import Path

OUT = Path("docs/09-Research/completeness-instances/CHECK-CASES.json")
GS = Path("docs/09-Research/grammar-sampling")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
MODELS = {k: {"path": str(GS / "models" / f), "sha256": sha(GS / "models" / f)} for k, f in
          (("archimate", "archimate-billing.json"), ("dsm", "dsm-modules.json"), ("bpmn", "bpmn-order.json"))}


def stmt(pred, s, o, sid=None):
    return {"id": sid, "predicate": pred, "subject": s, "object": o}


def decl_rt(subject, predicate, direction, source):
    """D-2 Grundeinheit: Referent × Relationstyp × Richtung."""
    return {"scope": "referent_relation_direction", "referent": subject, "predicate": predicate, "direction": direction, "source": source}


def decl_pair(subject, predicate, obj, source):
    """D-2 Ergänzung: einzelnes Paar."""
    return {"scope": "pair", "subject": subject, "predicate": predicate, "object": obj, "source": source}


def case(cid, story, matrix, model, question, statements, declarations, claim, today, profile, why, variant=None, instances=None, predicate_props=None):
    c = {"case_id": cid, "story": story, "matrix_case": matrix, "model": MODELS[model], "question": question,
         "statements": statements, "declarations": declarations, "claim": claim,
         "expected_today": today, "expected_with_profile": profile, "rationale": why}
    if variant:
        c["variant_of_model"] = variant
    if instances is not None:
        c["instance_bindings"] = instances
    if predicate_props is not None:
        c["predicate_properties"] = predicate_props
    return c


T_NE = lambda ref: {"kind": "NE", "reason": "Regel über mehrere Aussagen bzw. Abwesenheit; cube_validate prüft Einzelausdrücke", "mile002_case": ref}
T_RUN = lambda ref, st, codes=(): {"kind": "P1", "status": st, "diagnostic_codes": list(codes), "mile002_case": ref, "verified_by": "Baseline-Lauf TASK-030"}
LIB = lambda st, val, code=None, count=None: {"layer": "LIB", "status": st, "value": val, **({"diagnostic_code": code} if code else {}), **({"count": count} if count is not None else {})}
P1 = lambda st, codes=(): {"layer": "P1", "status": st, "diagnostic_codes": list(codes)}

TP, ACC, BIL, FP = "am:transaction-processing", "am:accounting", "am:billing", "am:financial-processing"
R1 = stmt("realizes", ACC, TP, "am:r1")
COMP = [stmt("composedOf", FP, x, r) for x, r in (("am:accounting", "am:r2"), (BIL, "am:r3"), ("am:payment", "am:r4"))]
DSM = [stmt("dependsOn", s, o, i) for s, o, i in (("m:resolver", "m:parser", "d-rp"), ("m:validator", "m:resolver", "d-vr"), ("m:printer", "m:validator", "d-pv"), ("m:parser", "m:validator", "d-fb"))]
ROUTE_M = stmt("routedTo", "bpmn:i1/tok-route", "bpmn:approve-manual")
ROUTE_A = stmt("routedTo", "bpmn:i1/tok-route", "bpmn:approve-auto")
EXACTLY_ONE = {"rule": "count", "subject": "bpmn:i1/tok-route", "predicate": "routedTo", "direction": "outgoing", "min": 1, "max": 1, "source": "BPMN §10.6.2/§13.4.2 (R-BPMN-1)"}
COUNT_FP = {"rule": "count", "subject": FP, "predicate": "composedOf", "direction": "outgoing", "min": 2, "max": 3, "counted": "distinct targets", "source": "local_count_rule (A), archimate-billing.json"}
ABS = lambda s, p, o: {"rule": "absence", "subject": s, "predicate": p, "object": o}


def join_rule(inst):
    return {"rule": "join_activation", "instance": inst, "gateway": "bpmn:join", "per_incoming_flow": {"f-stock-done": [1, None], "f-credit-done": [1, None]}, "source": "BPMN §13.4.1 (R-BPMN-2)"}


def tok(i, t, flow):
    return {"id": f"bpmn:{i}/{t}", "predicate": "onFlow", "subject": f"bpmn:{i}/{t}", "object": flow}


CASES = [
    # --- US-018 Vollständigkeit: Abwesenheit ---
    case("CC-01", "US-018", "ARC-03", "archimate", "Realisiert in der Service-Sicht nichts Transaction Processing?",
         [], [], ABS(None, "realizes", TP),
         T_NE("ARC-03-absence-claim"), LIB("UNRESOLVED", "coverage_undeclared", "P1_COVERAGE_UNDECLARED"),
         "Service-Sicht ist ausdrücklich partiell; ohne Erklärung für eingehende realizes von TP ist Abwesenheit unbekannt, nicht nachgewiesen."),
    case("CC-02", "US-018", "ARC-03", "archimate", "Realisiert Billing Transaction Processing (Vollsicht)?",
         [R1], [decl_rt(TP, "realizes", "incoming", "am:view/full declared complete")], ABS(BIL, "realizes", TP),
         T_NE("ARC-03-absence-claim"), LIB("PASS", "absent_checked", count=0),
         "Eingehende realizes von TP sind erklärt; nur am:r1 (Accounting) liegt vor; Abwesenheit für Billing ist nachgewiesen."),
    case("CC-03", "US-018", "ARC-03", "archimate", "Realisiert Accounting Transaction Processing nicht (Vollsicht)?",
         [R1], [decl_rt(TP, "realizes", "incoming", "am:view/full declared complete")], ABS(ACC, "realizes", TP),
         T_NE("ARC-03-absence-claim"), LIB("FAIL", "absence_contradicted", count=1),
         "Gegenfall: Die Abwesenheitsbehauptung widerspricht am:r1 im erklärten Umfang."),
    case("CC-04", "US-018", "DSM-03", "dsm", "Hat printer keine Abhängigkeit zu parser?",
         DSM, [decl_pair("m:printer", "dependsOn", "m:parser", "dsm_modules.cells: empty_known 'analysed; no dependency'")], ABS("m:printer", "dependsOn", "m:parser"),
         T_NE("DSM-03-empty-known"), LIB("PASS", "absent_checked", count=0),
         "Paar-Erklärung (D-2) deckt genau diese Zelle; keine Aussage printer → parser."),
    case("CC-05", "US-018", "DSM-03", "dsm", "Hat validator keine Abhängigkeit zu printer?",
         DSM, [decl_pair("m:printer", "dependsOn", "m:parser", "dsm_modules.cells: empty_known")], ABS("m:validator", "dependsOn", "m:printer"),
         T_NE("DSM-03-empty-known"), LIB("UNRESOLVED", "coverage_undeclared", "P1_COVERAGE_UNDECLARED"),
         "Zelle (validator, printer) ist im Modell 'unknown'; keine Erklärung deckt sie."),
    case("CC-06", "US-018", "DSM-03", "dsm", "Hat printer keine Abhängigkeit zu resolver, wenn die Zeile printer erklärt ist?",
         DSM, [decl_rt("m:printer", "dependsOn", "outgoing", "Variante: ausgehende dependsOn von printer vollständig erhoben")], ABS("m:printer", "dependsOn", "m:resolver"),
         T_NE("DSM-03-empty-known"), LIB("PASS", "absent_checked", count=0),
         "Grundeinheit Referent × Relationstyp × Richtung: Zeilenerklärung deckt jede Zelle der Zeile; widerspruchsfrei mit d-pv.",
         variant="Erklärung für die ganze Zeile printer ist eine Variante; im Modell ist (printer, resolver) unbekannt"),
    case("CC-07", "US-018", "DSM-03", "dsm", "Hat printer keine Abhängigkeit zu validator, wenn die Zeile printer erklärt ist?",
         DSM, [decl_rt("m:printer", "dependsOn", "outgoing", "Variante wie CC-06")], ABS("m:printer", "dependsOn", "m:validator"),
         T_NE("DSM-03-empty-known"), LIB("FAIL", "absence_contradicted", count=1),
         "Gegenfall: d-pv widerspricht der Abwesenheit im erklärten Umfang.", variant="wie CC-06"),
    # --- US-018 Vollständigkeit: Zählung ---
    case("CC-08", "US-018", "ARC-02", "archimate", "Besteht Financial Processing aus zwei bis drei Teilfunktionen (Vollsicht)?",
         COMP, [decl_rt(FP, "composedOf", "outgoing", "am:view/full declared complete")], COUNT_FP,
         T_NE("ARC-02-count-rule"), LIB("PASS", "within_bounds", count=3),
         "Drei Composition-Ziele im erklärten Umfang; 2 ≤ 3 ≤ 3."),
    case("CC-09", "US-018", "ARC-02", "archimate", "Besteht Financial Processing aus zwei bis drei Teilfunktionen (Service-Sicht)?",
         [], [], COUNT_FP,
         T_NE("ARC-02-count-rule"), LIB("UNRESOLVED", "coverage_undeclared", "P1_COVERAGE_UNDECLARED"),
         "Partielle Sicht ohne Erklärung: Anzahl unbekannt, nicht null."),
    case("CC-10", "US-018", "ARC-02", "archimate", "Besteht Financial Processing aus zwei bis drei Teilfunktionen, wenn nur eine erklärt vorliegt?",
         COMP[:1], [decl_rt(FP, "composedOf", "outgoing", "Variante: vollständig erhoben")], COUNT_FP,
         T_NE("ARC-02-count-rule"), LIB("FAIL", "out_of_bounds", count=1),
         "Gegenfall: eine Teilfunktion im vollständig erklärten Umfang unterschreitet min 2.", variant="nur am:r2"),
    case("CC-11", "US-018", "BPMN-01", "bpmn", "Wurde Token i1/tok-route genau einem Pfad zugeleitet?",
         [ROUTE_M], [decl_rt("bpmn:i1/tok-route", "routedTo", "outgoing", "Spur i1 am XOR vollständig aufgezeichnet")], EXACTLY_ONE,
         T_NE("BPMN-01-exclusivity"), LIB("PASS", "within_bounds", count=1),
         "Genau ein routedTo im erklärten Umfang (§13.4.2)."),
    case("CC-12", "US-018", "BPMN-01", "bpmn", "Wurde Token i1/tok-route genau einem Pfad zugeleitet (zwei Aufzeichnungen)?",
         [ROUTE_M, ROUTE_A], [decl_rt("bpmn:i1/tok-route", "routedTo", "outgoing", "wie CC-11")], EXACTLY_ONE,
         T_NE("BPMN-01-exclusivity"), LIB("FAIL", "out_of_bounds", count=2),
         "Gegenfall: zwei Pfade für einen Token widersprechen §10.6.2; Einzelaussagen bleiben je PASS (BPMN-01-ctrl-other-branch)."),
    case("CC-13", "US-018", "BPMN-01", "bpmn", "Wurde Token i1/tok-route genau einem Pfad zugeleitet (Spur nicht erklärt)?",
         [ROUTE_M], [], EXACTLY_ONE,
         T_NE("BPMN-01-exclusivity"), LIB("UNRESOLVED", "coverage_undeclared", "P1_COVERAGE_UNDECLARED"),
         "Ohne Erklärung ist 'nur einer' nicht feststellbar."),
    case("CC-14", "US-018", "BPMN-02", "bpmn", "Durfte der Join für i1 aktivieren?",
         [tok("i1", "tok-stock", "f-stock-done"), tok("i1", "tok-credit", "f-credit-done")],
         [decl_rt("bpmn:i1", "onFlow", "incoming-to-join", "Spur i1 an bpmn:join vollständig aufgezeichnet")], join_rule("bpmn:i1"),
         T_NE("BPMN-02-sync-condition"), LIB("PASS", "join_enabled"),
         "Je eingehendem Fluss ein Token der Instanz i1 (§13.4.1)."),
    case("CC-15", "US-018", "BPMN-02", "bpmn", "Durfte der Join für i2 aktivieren?",
         [tok("i2", "tok-credit", "f-credit-done")],
         [decl_rt("bpmn:i2", "onFlow", "incoming-to-join", "Spur i2 an bpmn:join vollständig aufgezeichnet")], join_rule("bpmn:i2"),
         T_NE("BPMN-02-sync-condition"), LIB("FAIL", "join_not_enabled"),
         "Gegenfall: Auf f-stock-done liegt im vollständig erklärten Umfang kein Token von i2."),
    case("CC-16", "US-018", "BPMN-02", "bpmn", "Durfte der Join für i2 aktivieren (Spur nicht erklärt)?",
         [tok("i2", "tok-credit", "f-credit-done")], [], join_rule("bpmn:i2"),
         T_NE("BPMN-02-sync-condition"), LIB("UNRESOLVED", "coverage_undeclared", "P1_COVERAGE_UNDECLARED"),
         "Fehlender Stock-Token kann ausstehen; ohne Erklärung keine Verletzung."),
    # --- US-019 Instanzbindung ---
    case("CI-01", "US-019", "BPMN-03", "bpmn", "Paart J1 Token aus verschiedenen Instanzen (gemeinsamer Scope)?",
         [stmt("joins", "bpmn:i1/tok-stock", "bpmn:i2/tok-credit")], [], {"rule": "single_statement"},
         T_RUN("BPMN-03-join-cross-instance-shared", "PASS"), P1("FAIL", ["P1_INSTANCE_MISMATCH"]),
         "D-4: instance_ref i1 bzw. i2 und joins verlangt gleiche Instanz; heute PASS, weil die Instanz nur im Namen steckt.",
         instances={"bpmn:i1/tok-stock": "bpmn:i1", "bpmn:i2/tok-credit": "bpmn:i2"}, predicate_props={"joins": {"requires_same_instance": True}}),
    case("CI-02", "US-019", "BPMN-03", "bpmn", "Instanz als Scope (Regressionsschutz)",
         [stmt("joins", "bpmn:i1/tok-stock", "bpmn:i2/tok-credit")], [], {"rule": "single_statement"},
         T_RUN("BPMN-03-join-cross-instance-scoped", "FAIL", ["P1_REFERENT_MISMATCH", "P1_SCOPE_CONFLICT"]), P1("FAIL", ["P1_REFERENT_MISMATCH", "P1_SCOPE_CONFLICT"]),
         "Der bestehende Scope-Fall bleibt unverändert; das Profil fügt nichts hinzu und nimmt nichts weg.",
         instances={}, predicate_props={}),
    case("CI-03", "US-019", "BPMN-02", "bpmn", "Paart der Join Token derselben Instanz?",
         [stmt("joins", "bpmn:i1/tok-stock", "bpmn:i1/tok-credit")], [], {"rule": "single_statement"},
         T_RUN("BPMN-02-join-same-instance", "PASS"), P1("PASS"),
         "Gleiche Instanz i1; Regel erfüllt.",
         instances={"bpmn:i1/tok-stock": "bpmn:i1", "bpmn:i1/tok-credit": "bpmn:i1"}, predicate_props={"joins": {"requires_same_instance": True}}),
    case("CI-04", "US-019", "BPMN-03", "bpmn", "Paart J1 Token verschiedener Instanzen, wenn eine Instanz nicht gebunden ist?",
         [stmt("joins", "bpmn:i1/tok-stock", "bpmn:i2/tok-credit")], [], {"rule": "single_statement"},
         T_RUN("BPMN-03-join-cross-instance-shared", "PASS"), P1("UNRESOLVED", ["P1_INSTANCE_UNDECLARED"]),
         "D-4 optional: Verlangt das Prädikat gleiche Instanz und fehlt eine Bindung, ist das unentscheidbar, nicht PASS.",
         instances={"bpmn:i1/tok-stock": "bpmn:i1"}, predicate_props={"joins": {"requires_same_instance": True}}),
    case("CI-05", "US-019", "BPMN-01", "bpmn", "Gilt die Instanzregel auch für Prädikate ohne Eigenschaft? (Negativkontrolle)",
         [ROUTE_M], [], {"rule": "single_statement"},
         T_RUN("BPMN-01-routed", "PASS"), P1("PASS"),
         "routedTo verlangt keine gleiche Instanz; unterschiedliche oder fehlende Bindungen ändern nichts.",
         instances={"bpmn:i1/tok-route": "bpmn:i1"}, predicate_props={"routedTo": {"requires_same_instance": False}}),
]

doc = {"format": "mile005.check-cases/1", "task": "TASK-030", "fixed_at": "2026-11-01", "fixed_before_spec": True,
       "decisions": "MILE-005 D-1–D-6 (0c810bb)",
       "layers": {"P1": "Einzelaussage im neuen Profil (binding-context/8): Instanzbindung D-4, Wohlgeformtheit der Erklärungen",
                  "LIB": "Auswertung über eine Aussagenmenge (D-6): Abwesenheit, Zählung, Join-Aktivierung; Statusabbildung PASS/FAIL/UNRESOLVED"},
       "status_rule": {"inside_declared_scope": "Regel erfüllt → PASS; verletzt → FAIL",
                       "outside_declared_scope": "UNRESOLVED mit P1_COVERAGE_UNDECLARED (D-3), nie FAIL, nie 'geprüft leer'"},
       "naming": "Diagnosecodes und value-Bezeichner sind Arbeitstitel; TASK-031 darf sie umbenennen, Status und Schicht nicht.",
       "baseline_cases": sorted({c["expected_today"]["mile002_case"] for c in CASES if c["expected_today"]["kind"] == "P1"}),
       "cases": CASES}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(OUT, len(CASES), sha(OUT)[:16])
