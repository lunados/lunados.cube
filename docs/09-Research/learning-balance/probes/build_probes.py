"""MILE-004 TASK-024: erzeugt den Probeplan (PROBE-PLAN.json) deterministisch.

Aufruf aus dem Repo-Wurzelverzeichnis (Geschwisterordner lunados.space und lunados.lib erwartet):
    python3 -I docs/09-Research/learning-balance/probes/build_probes.py
Nur Standardbibliothek. Die Proben laufen erst in TASK-025; dieser Plan legt Eingaben, Erwartungen
und Entscheidungsregeln vorher fest.
"""
import copy, hashlib, json, subprocess
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs/09-Research/learning-balance/probes/PROBE-PLAN.json"
SPACE, LIB = ROOT.parent / "lunados.space", ROOT.parent / "lunados.lib"
EXP = "web/docs/cube/AIAEAO_EXP024_Charge3_Five_Envelopes_v0.1"


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def dig(o):
    return "sha256:" + hashlib.sha256(canon(o)).hexdigest()


def fsha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def head(repo):
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def pin(repo, rel, label):
    return {"label": label, "repo": repo.name, "commit": head(repo), "path": rel, "sha256": fsha(repo / rel)}


SOURCES = [
    pin(SPACE, f"{EXP}/contracts/evaluator-result.v0.2.schema.json", "Envelope-Ergebnisvertrag (EXP-024 Charge 3)"),
    pin(SPACE, f"{EXP}/contracts/evaluator-call.v0.1.schema.json", "Envelope-Aufrufvertrag (EXP-024 Charge 3)"),
    pin(SPACE, f"{EXP}/evaluators/evaluators.v0.1.json", "Evaluator-Register EXP-024 (ohne Ergebnisschema je Methode)"),
    pin(LIB, "schema/entry.v1.schema.json", "LIB-Eintragsvertrag (Ausgabe nur concept_id + cardinality)"),
    pin(ROOT, "docs/09-Research/cube-grammar-2026-11-01/LERNVERGLEICH.md", "Prüfkriterium Envelope-Erweiterung (§1), Bestandteile LENS/MODE (§4)"),
    pin(ROOT, "P2/visual-printer-2d-lab/VP03_LENS_GRAMMAR.md", "VP-03 Linsengrammatik (fünf Linsen, deklarierte Facettenbindungen)"),
    pin(ROOT, "P2/visual-printer-migration-v1/VP07_ACCEPTANCE_SPEC.md", "VP-07 Partition subject/object/step/track, Track-Map (D-3)"),
    pin(ROOT, "P2/visual-printer-migration-v1/vpmigration/adapter.py", "VP-07 Adapter: Track nur für Zeilen (Subjekte)"),
    pin(ROOT, "P2/visual-printer-migration-v1/vpmigration/panels.py", "VP-07 Panels: Partition track nach Zeilen-Track"),
    pin(ROOT, "P3/adapters/mcp-local/aiaeao_mcp_local/plan_views.py", "Implementierung hinter cube_plan_source/views/check"),
    pin(ROOT, "AIAEAO_Pure_Cube_P0_v9.4/v9.4/morphology.md", "M — Mode (§3.10): Werte, Übergänge, Bindung nicht eingefroren"),
    pin(ROOT, "AIAEAO_Pure_Cube_P0_v9.4/v9.4/grammar/constraints.json", "C021: Loose/Transitional/Strict sind keine autorisierten MODE-Werte"),
]

LIMS = ["Probe-Instanz von Hand erstellt (authored_synthetic); kein Evaluator ausgeführt.",
        "assessed bedeutet nur: innerhalb der Probe-Regeln bewertet; keine Domänenwahrheit."]


def envelope_case(case_id, method_id, purpose, inputs, parameters, disposition, kind, value, detail, findings):
    descriptor = {"method_id": method_id, "purpose": purpose, "status": "probe-only"}
    for i in inputs:
        i["source_revision"] = dig(i["content"])
    call = {"schema": "aiaeao.evaluator-call/v0.1", "method_id": method_id, "descriptor_digest": dig(descriptor),
            "derivation_ref": dig(inputs), "inputs": inputs, "parameters": parameters}
    result = {"schema": "aiaeao.evaluator-result/v0.2", "method_id": method_id, "descriptor_digest": call["descriptor_digest"],
              "derivation_ref": call["derivation_ref"], "evaluator_id": "probe.hand-authored/v0", "disposition": disposition,
              "outcome": {"kind": kind, "value": value, "detail": detail}, "findings": findings, "limitations": LIMS,
              "runtime_authority": "not-evaluated", "effectful_execution_authorized": False, "selected_alternative": None}
    return {"case_id": case_id, "descriptor": descriptor, "call": call, "result": result}


# ---------- E-1: Projektion mit Quellenspur (C4-02, Architektur) ----------
P1M = "project.aggregate-relations/v0-probe"
P1P = "Komponentenbeziehungen auf Containerebene verdichten, mit Quellenspur und Verlustbericht (G-03)"
CONTAIN = {"role": "containment", "ref": "model:c4-shop#api", "content": {"container": "c4:api", "components": ["c4:order-controller", "c4:order-repository"]}}
SRC_W = {"role": "source_relation", "ref": "model:c4-shop#orderController-db", "content": {"subject": "c4:order-controller", "object": "c4:db", "description": "Writes orders to"}}
SRC_R = {"role": "source_relation", "ref": "model:c4-shop#orderRepository-db", "content": {"subject": "c4:order-repository", "object": "c4:db", "description": "Reads orders from"}}
UNM = {"role": "source_relation", "ref": "model:c4-shop#api-db-unmarked", "content": {"subject": "c4:api", "object": "c4:db", "predicate": "uses"}}
E1 = [
    envelope_case("E-1a", P1M, P1P, [copy.deepcopy(CONTAIN), copy.deepcopy(SRC_W), copy.deepcopy(SRC_R)], {"strategy": "UnlessAny", "target_level": "container"},
                  "assessed", "projected_relation", "aggregated_with_loss",
                  {"subject": "c4:api", "object": "c4:db", "origin": "derived", "source_count": 2, "discarded_descriptions": 2},
                  ["2 source relations -> 1 projected relation c4:api -> c4:db", "descriptions not carried over: 2"]),
    envelope_case("E-1b", P1M, P1P, [copy.deepcopy(CONTAIN), copy.deepcopy(SRC_W)], {"strategy": "UnlessAny", "target_level": "container"},
                  "assessed", "projected_relation", "aggregated_without_loss",
                  {"subject": "c4:api", "object": "c4:db", "origin": "derived", "source_count": 1, "discarded_descriptions": 0},
                  ["1 source relation -> 1 projected relation c4:api -> c4:db"]),
    envelope_case("E-1c", P1M, P1P, [copy.deepcopy(UNM)], {"strategy": "UnlessAny", "target_level": "container"},
                  "unresolved", "projected_relation", "origin_unbound",
                  {"subject": "c4:api", "object": "c4:db", "origin": None},
                  ["relation c4:api -> c4:db carries no origin binding (C4-03 pattern)"]),
]
# ---------- E-2: Spurprüfung mit Instanzbindung (BPMN-02/03, Prozess) ----------
P2M = "analyze.trace-conformance/v0-probe"
P2P = "AND-Join-Aktivierung gegen die Spur prüfen: gleiche Instanz, je Eingang ein Token (G-07, G-08)"
JOIN = {"role": "join_spec", "ref": "bpmn:join", "content": {"incoming": ["f-stock-done", "f-credit-done"]}}
def tok(i, t, flow):
    return {"role": "token", "ref": f"bpmn:{i}/{t}", "content": {"instance": f"bpmn:{i}", "flow": flow}}
E2 = [
    envelope_case("E-2a", P2M, P2P, [copy.deepcopy(JOIN), tok("i1", "tok-stock", "f-stock-done"), tok("i1", "tok-credit", "f-credit-done")], {"activation_scope": "bpmn:i1"},
                  "assessed", "join_activation", "conforms",
                  {"instance": "bpmn:i1", "consumed": ["bpmn:i1/tok-stock", "bpmn:i1/tok-credit"]}, ["join in bpmn:i1 consumes one token per incoming flow of the same instance"]),
    envelope_case("E-2b", P2M, P2P, [copy.deepcopy(JOIN), tok("i1", "tok-stock", "f-stock-done"), tok("i2", "tok-credit", "f-credit-done")], {"activation_scope": "bpmn:i1"},
                  "assessed", "join_activation", "cross_instance_violation",
                  {"instance": "bpmn:i1", "consumed": ["bpmn:i1/tok-stock", "bpmn:i2/tok-credit"], "foreign_inputs": ["bpmn:i2/tok-credit"]},
                  ["J1 pairs bpmn:i1/tok-stock with bpmn:i2/tok-credit: input from another instance"]),
    envelope_case("E-2c", P2M, P2P, [copy.deepcopy(JOIN), tok("i2", "tok-credit", "f-credit-done")], {"activation_scope": "bpmn:i2"},
                  "unresolved", "join_activation", "waiting_for_input",
                  {"instance": "bpmn:i2", "consumed": [], "missing_flows": ["f-stock-done"]}, ["bpmn:i2 has no token on f-stock-done yet"]),
]

# T = eigenes, durch das Schema typisiertes Feld (enum/const/pattern oder feste Struktur);
# U = nur in untypisiertem Feld (outcome.detail, outcome.value, outcome.kind, findings, parameters, inputs[].content, inputs[].ref);
# N = nicht darstellbar. Das Ausführungsskript prüft die Pfade gegen das Schema.
DISTINCTIONS = {
    "E-1": [
        {"id": "d1", "what": "Endpunkte der verdichteten Kante", "expected_carrier": "U", "path": "result.outcome.detail.subject/object"},
        {"id": "d2", "what": "welche Quellbeziehungen eingeflossen sind", "expected_carrier": "T", "path": "result.derivation_ref -> call.inputs[].ref/source_revision", "note": "Bindung an die Eingaben per Digest typisiert; Rolle 'source_relation' nur Namenskonvention"},
        {"id": "d3", "what": "Verdichtungsstrategie", "expected_carrier": "U", "path": "call.parameters.strategy"},
        {"id": "d4", "what": "Verlust (verworfene Beschreibungen)", "expected_carrier": "U", "path": "result.outcome.detail.discarded_descriptions"},
        {"id": "d5", "what": "bewertet vs. unaufgelöst", "expected_carrier": "T", "path": "result.disposition"},
        {"id": "d6", "what": "Grund der Unauflösbarkeit (Herkunft nicht gebunden)", "expected_carrier": "U", "path": "result.outcome.value"},
    ],
    "E-2": [
        {"id": "d1", "what": "Instanz der geprüften Aktivierung", "expected_carrier": "U", "path": "call.parameters.activation_scope"},
        {"id": "d2", "what": "Instanz je verbrauchtem Token", "expected_carrier": "U", "path": "call.inputs[].content.instance"},
        {"id": "d3", "what": "konform vs. instanzübergreifender Verstoß", "expected_carrier": "U", "path": "result.outcome.value"},
        {"id": "d4", "what": "Verstoß vs. unvollständige Spur", "expected_carrier": "T", "path": "result.disposition"},
        {"id": "d5", "what": "ein Ergebnis je Instanz", "expected_carrier": "T", "path": "result.derivation_ref (je Aufruf)", "note": "nur über getrennte Aufrufe; kein Sammelergebnis"},
        {"id": "d6", "what": "keine Ausführungsbehauptung", "expected_carrier": "T", "path": "result.effectful_execution_authorized, result.runtime_authority"},
    ],
}

# ---------- L-1: Herkunft je Kante als LENS-Bindung (C4-03, Architektur) ----------
C4_REFS = [
    ("c4:api", "Z:module-body:runtime"), ("c4:order-controller", "Z:module-body:integration"),
    ("c4:order-repository", "Z:module-body:integration"), ("c4:db", "Z:module-body:provider")]
def ctx(cid, scope, refs, plan_id, deps):
    return {"format": "aiaeao.cube.binding-context/5", "reference_version": "v9.4", "context_id": cid, "source_kind": "illustrative_fixture",
            "scope_ref": scope, "referents": [{"ref": r, "concept_id": c, "home": c.split(":")[0], "layers": ["α"], "provenance_status": "declared_unverified", "scope_ref": scope} for r, c in refs],
            "predicate_contracts": [], "predicate_profile_refs": ["P1.10/migration-predicates-v1"],
            "migration_plans": [{"plan_id": plan_id, "revision": "mile004:v1", "scope": scope, "origin": "illustrative_fixture",
                                 "phases": [{"phase_id": "p0", "role": "current"}, {"phase_id": "p1", "role": "target"}], "transitions": [], "dependencies": deps}]}
def dep(i, s, o, p, w):
    return {"dependency_id": i, "subject": s, "object": o, "predicate_id": p, "kind": "other", "holds_in": ["p0", "p1"], "witness_ref": w}
L1_CTX = ctx("mile004-c4", "mile004:c4", C4_REFS, "mp-c4o", [
    dep("e-writes", "c4:order-controller", "c4:db", "writes-orders-to", "model:c4-shop#orderController-db"),
    dep("e-implied", "c4:api", "c4:db", "uses-implied", "derived:c4-shop#implied-api-db"),
    dep("e-unbound", "c4:order-repository", "c4:db", "reads-orders-from", "unbound:c4-shop#repository-db")])
VIEW = {"view": "cube.flow", "granularity": "standard", "partition": "object"}
L1 = {
    "mapping_note": "Darstellungsabbildung (A) wie R-2; e-unbound steht für eine Kante ohne gebundene Herkunft (C4-03-Muster) und ist deshalb auf das Paar Repository → Database gelegt, um Überlagerung mit e-implied zu vermeiden. Die Herkunftsklasse steckt im witness_ref-Präfix (model:/derived:/unbound:).",
    "context": L1_CTX, "plan_id": "mp-c4o",
    "calls": [
        {"call_id": "L-1a", "plan_source": {"printer": "vpmigration"}, "plan_views": {**VIEW, "lens": "cube.lens.provenance"}},
        {"call_id": "L-1b", "plan_source": {"printer": "vpmigration", "witness_prefixes": {"format": "aiaeao.cube.vp07-witness-prefixes/1", "prefixes": [{"prefix": "derived:", "note": "Herkunft abgeleitet"}]}},
         "plan_views": {**VIEW, "lens": "cube.lens.epistemology"}}],
    "expected": {
        "L-1a": ["plan_check PASS; drei Kanten, vier Knoten", "alle drei Kanten mit demselben Provenienz-Akzent; Linsenfeld 'PROVENANCE · 3 DECLARED FOCUS'",
                 "die drei Herkunftsklassen sind im Bild nicht unterscheidbar; das witness_ref-Präfix steht nur in den Metadaten"],
        "L-1b": ["plan_check PASS", "nur e-implied mit Epistemologie-Akzent; Linsenfeld '… 1 DECLARED FOCUS'",
                 "e-writes (deklariert) und e-unbound (Herkunft nicht gebunden) gleich gezeichnet: genau eine binäre Unterscheidung je Linse"]},
    "decision_rule": "Zeigt eine Linsenvariante drei Herkunftsklassen unterscheidbar, trägt LENS die Herkunft. Sonst: LENS hebt deklarierten Fokus binär hervor; Herkunft braucht typisierte Bindung (G-02) und Kantenstil (VR-01), keine LENS-Erweiterung."}

# ---------- L-2: Instanzgruppierung (BPMN-03, Prozess) ----------
L2_REFS = [("bpmn:i1/tok-stock", "Y:resource-object:resource"), ("bpmn:i1/tok-credit", "Y:resource-object:resource"),
           ("bpmn:i2/tok-credit", "Y:resource-object:resource"), ("bpmn:j1", "Y:resource-object:resource")]
L2_CTX = ctx("mile004-bpmn", "mile004:bpmn", L2_REFS, "mp-bpmn", [
    dep("e-stock", "bpmn:i1/tok-stock", "bpmn:j1", "consumed-by", "trace:bpmn-order#i1-stock"),
    dep("e-cross", "bpmn:i2/tok-credit", "bpmn:j1", "consumed-by", "trace:bpmn-order#j1-i2-credit")])
L2 = {
    "mapping_note": "Darstellungsabbildung (A): Token und Join-Aktivierung J1 als Y:resource-object:resource (Adapterkonzept); J1 paart laut Aussage i1/tok-stock mit i2/tok-credit (BPMN-03). i1/tok-credit ist Referent, aber nicht Teil von J1. Instanz als deklarierte Track-Map (VP-07 D-3b); J1 ist i1 zugeordnet.",
    "context": L2_CTX, "plan_id": "mp-bpmn",
    "tracks": {"format": "aiaeao.cube.vp07-track-map/1", "tracks": {"i1": ["bpmn:i1/tok-stock", "bpmn:i1/tok-credit", "bpmn:j1"], "i2": ["bpmn:i2/tok-credit"]}},
    "labels": {"format": "aiaeao.cube.vp07-label-map/1", "labels": {
        "bpmn:i1/tok-stock": {"id": "i1-tok-stock", "label": "i1 · tok-stock"}, "bpmn:i1/tok-credit": {"id": "i1-tok-credit", "label": "i1 · tok-credit"},
        "bpmn:i2/tok-credit": {"id": "i2-tok-credit", "label": "i2 · tok-credit"}, "bpmn:j1": {"id": "j1", "label": "J1 · Join (AND)"}}},
    "calls": [{"call_id": "L-2", "plan_source": {"printer": "vpmigration", "tracks": "<tracks>", "labels": "<labels>"}, "plan_views": {"view": "cube.flow", "granularity": "standard", "partition": "track", "lens": "cube.lens.provenance"}}],
    "expected": {"L-2": ["plan_check PASS; zwei Panels mit Partitionswert i1 und i2", "Panel i1: e-stock; Panel i2: e-cross; J1 erscheint in beiden Panels und wird im Bericht als Wiederholung geführt",
                         "e-cross ist gezeichnet wie e-stock: keine Markierung als instanzübergreifend", "dass J1 zu i1 gehört, steht nirgends im Bild (Track nur für Subjekte)"]},
    "decision_rule": "Trennt die Partition die Instanzen und macht sie die Kante J1 ← i2/tok-credit als instanzübergreifend sichtbar, trägt die vorhandene Bindung die Instanzgruppierung. Trennt sie nur nach Subjekt-Track ohne Markierung: Gruppierung ist als Adapter-Map möglich, Instanzbindung und Verstoßmarkierung fehlen (G-08, VR-12)."}

MODE_NE = {"probe": "L-2/MODE", "status": "NE", "reason": "P0 v9.4 friert für M (Mode) weder Werte noch Übergänge noch Bindung ein (morphology.md §3.10, constraints C021); kein Validator und kein Printer liest MODE. Eine Probe 'Instanzsemantik als MODE' ist daher nicht ausführbar.",
           "consequence": "Leitfrage 4 bleibt für MODE präzise offen: Prüfbar erst nach einem eingefrorenen MODE-Schema; morphologisch ist Mode ein Betriebsregime, keine Instanzidentität."}

plan = {
    "format": "mile004.probe-plan/1", "task": "TASK-024", "fixed_at": "2026-11-01", "fixed_before_run": True,
    "decisions": "MILE-004 D-1 (Architektursichten, Prozessspuren), D-2 (kleine Proben, Erwartung vorab)",
    "sources": SOURCES,
    "envelope_rule": {
        "criterion": "LERNVERGLEICH §1: Erweiterung nur, wenn zwei fachlich verschiedene Zustände ununterscheidbar werden oder Pflichtbindungen nur untypisiert unterzubringen sind.",
        "R-E1": "Mindestens eine Pflichtunterscheidung N, oder zwei Fälle, die sich in einer Pflichtunterscheidung unterscheiden, sind in allen Feldern gleich → Kandidat Envelope-Erweiterung.",
        "R-E2": "Pflichtunterscheidungen nur U → Typisierungslücke. Maßnahme auf der Ebene, die einen typisierten Bindungspunkt hat; fehlt er in Envelope und LIB-Eintrag, Kandidat: LIB-Vertragsrevision mit Ergebnisschema-Verweis; Envelope unverändert.",
        "R-E3": "Alle Pflichtunterscheidungen T → keine Maßnahme."},
    "envelope_tool": "jsonschema (Draft 2020-12) in der Agent-Umgebung; Identitätsprüfung Aufruf ↔ Ergebnis wie EXP-024 harness (method_id, descriptor_digest, derivation_ref); Trägerklassifikation gegen das Schema",
    "probes": {
        "E-1": {"question": 1, "use_case": "Architektursichten", "case": "C4-02 (Gegenfall C4-03)", "gap": "G-03, G-02", "instances": E1, "distinctions": DISTINCTIONS["E-1"],
                "expected": ["alle drei Aufrufe und Ergebnisse schema-gültig, Identität Aufruf ↔ Ergebnis stimmt", "Träger wie in distinctions angegeben: keine N, d5 T, d2 T über derivation_ref, d1/d3/d4/d6 nur U",
                             "E-1a und E-1b unterscheiden sich nur in untypisierten Feldern (detail, findings) und im Digest", "Ergebnis nach R-E2: Typisierungslücke, keine Envelope-Erweiterung"]},
        "E-2": {"question": 1, "use_case": "Prozessspuren", "case": "BPMN-03 (BPMN-02)", "gap": "G-07, G-08", "instances": E2, "distinctions": DISTINCTIONS["E-2"],
                "expected": ["alle drei Aufrufe und Ergebnisse schema-gültig, Identität stimmt", "Träger wie angegeben: keine N, d4/d5/d6 T, d1/d2/d3 nur U",
                             "Instanzbindung je Eingang hat keinen typisierten Ort (nur content/ref); Sammelergebnis über Instanzen nicht vorgesehen",
                             "Ergebnis nach R-E2: Typisierungslücke (deckt sich mit G-08), keine Envelope-Erweiterung"]},
        "L-1": {"question": 4, "use_case": "Architektursichten", "case": "C4-02/C4-03", "gap": "G-02, VR-01, PO-3", **L1},
        "L-2": {"question": 4, "use_case": "Prozessspuren", "case": "BPMN-03", "gap": "G-08, VR-12", **L2, "mode": MODE_NE},
    },
    "amendments": [{"date": "2026-11-01", "probe": "L-2", "change": "Label-Map (aiaeao.cube.vp07-label-map/1) als Anzeigeargument ergänzt",
                    "reason": "Erster Lauf: VP07_ADAPTER_MAPPING — Referenten mit '/' sind keine gültigen Anzeige-IDs (D-11). Reines Anzeigeargument; Eingaben, Erwartungen und Entscheidungsregeln unverändert.",
                    "failed_run_log": "docs/10-Evidence/MILE-004/task025-probe-run-attempt1.json"},
                   {"date": "2026-11-01", "probe": "L-1", "change": "keine Planänderung",
                    "reason": "Erster Lauf: VP07_SOURCE_INVALID, weil das Laufskript die Hülle von plan_source statt des enthaltenen source an plan_views übergab; im Skript behoben."}],
    "not_claimed": ["Vollständigkeit des Envelope-Rahmens über diese Fälle hinaus", "Nutzen oder Lesbarkeit", "Laufzeitverhalten eines echten Evaluators"],
}
OUT.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(OUT.relative_to(ROOT), fsha(OUT)[:16])
