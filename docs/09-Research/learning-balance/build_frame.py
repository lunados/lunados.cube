"""MILE-004 TASK-026: erzeugt MEASURES.json (Maßnahmenliste mit Eingabewerten, ohne Bewertung) deterministisch.
Aufruf aus dem Repo-Wurzelverzeichnis: python3 -I docs/09-Research/learning-balance/build_frame.py
"""
import json
from pathlib import Path

OUT = Path("docs/09-Research/learning-balance/MEASURES.json")
GL = "docs/09-Research/grammar-sampling/GAP-LEDGER.md"
HO = "docs/09-Research/visual-check/HANDOVER.md"
PR = "docs/09-Research/learning-balance/PROBE-RESULTS.md"
K = {"niedrig": 1, "niedrig–mittel": 1.5, "mittel": 2, "mittel–hoch": 2.5, "hoch": 3}


def e_score(lo, hi):
    mid = (lo + hi) / 2
    return 1 if mid <= 0.5 else 2 if mid <= 1 else 3 if mid <= 2 else 4 if mid <= 3 else 5


def m(mid, title, level, src, cases, pt, kx, deps=(), note="", assumed=False):
    lo, hi = pt
    return {"id": mid, "title": title, "level": level, "source": src, "cases": list(cases), "effort_pt": [lo, hi], "E": e_score(lo, hi),
            "complexity": kx, "K": K[kx], "depends_on": list(deps), "inputs_assumed": assumed, "note": note,
            "score": {"A": None, "P": None, "I": None, "V": None, "U": None, "rationale": None}}


MEASURES = [
    m("G-01", "Vollständigkeitserklärung + Populationsprüfung (unbekannt ≠ geprüft leer ≠ verletzt)", "Profil + LIB", f"{GL}#3", ["ARC-02", "ARC-03", "DSM-03", "BPMN-01", "BPMN-02"], (2, 4), "mittel–hoch"),
    m("G-02", "Typisierte Relationsherkunft (declared/derived/unknown)", "Profil", f"{GL}#3", ["C4-02", "C4-03"], (1, 2), "mittel", note="Alternative: G-10"),
    m("G-03", "Projektion mit Quellenspur und Verlustbericht (inkl. PO-7: allgemeine Projektion statt nur P1.10-Pläne)", "LIB", f"{GL}#3; {HO}#3", ["C4-02", "DSM-01", "DSM-02"], (2, 3), "mittel"),
    m("G-04", "Abbildungsprofile je Fremdsprache + Namensfallen-Dokumentation", "Profil + Dokumentation", f"{GL}#3", ["C4-01", "ARC-01", "DSM-02", "BPMN-01"], (1, 2), "mittel", note="Aufwand je Sprache"),
    m("G-05", "Graphanalyse in LIB: cycle-gate, Generationen, Ordnungen, SCC", "LIB", f"{GL}#3", ["DAG-02", "DAG-03", "DSM-01"], (2, 3), "niedrig–mittel"),
    m("G-06", "impact.propagate v2 (Vorbedingung, Orientierung, präzise Ablehnung)", "LIB", f"{GL}#3", ["DAG-01", "DAG-03"], (0.5, 1), "niedrig", deps=["G-05"]),
    m("G-07", "Kontrollfluss-Profil + Spurkonformität", "Profil + LIB", f"{GL}#3", ["BPMN-01", "BPMN-02"], (3, 5), "hoch", deps=["G-08"]),
    m("G-08", "Typisierte Instanzbindung (instance_ref, Regel gleiche Instanz)", "Profil/Dokumentation", f"{GL}#3; {PR}", ["BPMN-03"], (0.5, 1), "niedrig–mittel"),
    m("G-09", "Prädikateigenschaften und Domänendeklaration", "Profil", f"{GL}#3", ["DSM-01", "DSM-02"], (0.5, 1), "niedrig"),
    m("G-10", "Typisierte Relationsoperanden (Alternative zu G-02)", "P1-Profil", f"{GL}#3", ["C4-02"], (1, 2), "mittel", note="schließt G-02 als Weg zur Quellenbindung aus oder ergänzt ihn"),
    m("T-01", "Registerpin pro Regel-ID statt ganzes Register", "Werkzeug", f"{GL}#4", ["alle"], (0.25, 0.5), "niedrig", assumed=True, note="Aufwand gemeinsam mit T-02 0,5–1 PT"),
    m("T-02", "LIB-Aufrufe im Runner", "Werkzeug", f"{GL}#4", ["DAG-01", "DAG-02", "DAG-03"], (0.25, 0.5), "niedrig", assumed=True, note="Aufwand gemeinsam mit T-01 0,5–1 PT"),
    m("LR-1", "LIB-Vertragsrevision: Ergebnisschema je Methode für outcome.detail/value", "LIB-Vertrag", PR, ["C4-02", "C4-03", "BPMN-03"], (1, 2), "mittel", assumed=True, note="neu aus E-1/E-2"),
    m("VR-01", "Herkunftslinie (Linienart nach gebundener Herkunft)", "P2", f"{HO}#2", ["C4-02", "C4-03"], (0.5, 1), "niedrig", deps=["G-02"]),
    m("VR-05", "Vier Zellzustände je erklärtem Umfang", "P2", f"{HO}#2", ["DSM-03", "ARC-03"], (1, 1.5), "mittel", deps=["G-01"]),
    m("VR-09", "Zyklenkomponente mit Status und Zeuge", "P2", f"{HO}#2", ["DAG-03", "DAG-01"], (1, 2), "mittel", deps=["G-05"]),
    m("VR-12", "Instanz und Paarung (Rahmen, Join-Aussage, Verstoßmarke)", "P2", f"{HO}#2", ["BPMN-03"], (1, 2), "mittel–hoch", deps=["G-08"]),
    m("PO-1", "Begriff 'declared' in cube.flow eindeutig machen", "P2", f"{HO}#3", ["C4-02"], (0.1, 0.25), "niedrig"),
    m("PO-2", "cube.flow ohne gemeinsame Senkrechten", "P2", f"{HO}#3", ["C4-02", "DAG-03"], (1, 2), "mittel"),
    m("PO-3", "Farbfreie Linsenakzent-Option", "P2", f"{HO}#3", ["DAG-03"], (0.5, 0.5), "niedrig"),
    m("PO-4", "Linse ohne Facettenbindung dokumentieren oder neutrale Linse", "P2/Dokumentation", f"{HO}#3", ["DAG-03"], (0.1, 0.25), "niedrig"),
    m("PO-5", "Deklarierte Achsenreihenfolge in cube.axes", "P2", f"{HO}#3", ["DSM-01"], (0.5, 0.5), "niedrig"),
    m("PO-6", "hide_empty nennt ausgeblendete Elemente", "P2", f"{HO}#3", ["DSM-03"], (0.1, 0.25), "niedrig"),
    m("PO-8", "Partition track legt Stränge nie zusammen (wie layer)", "P2", PR, ["BPMN-03"], (0.25, 0.5), "niedrig–mittel", assumed=True, note="neu aus L-2"),
    m("HT", "Menschlicher Lesbarkeitstest (Pilot nach Skript)", "Studie", "docs/09-Research/visual-check/HUMAN-TEST-SCRIPT.md", ["C4-02", "C4-03", "DSM-03", "DAG-03", "BPMN-03"], (1, 1.5), "niedrig", assumed=True, note="nach D-4 nicht in MILE-004; als Maßnahme für später bewertet"),
]
EXCLUDED = [
    {"id": "T-03", "reason": "kein Eingriff: Agent-Umgebung beibehalten"},
    {"id": "T-04", "reason": "erledigt: P3-Änderungen committet und gemergt (PR #31)"},
    {"id": "PO-7", "reason": "in G-03 aufgegangen"},
]
doc = {"format": "mile004.measures/1", "task": "TASK-026", "fixed_at": "2026-11-01", "scored": False,
       "frame": "docs/09-Research/learning-balance/SCORING-FRAME.md", "measures": MEASURES, "excluded": EXCLUDED}
OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(OUT, len(MEASURES))
