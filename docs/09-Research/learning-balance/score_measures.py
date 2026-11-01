"""MILE-004 TASK-027: trägt die Bewertung in MEASURES.json ein und berechnet die Rangfolge nach SCORING-FRAME.md.
Aufruf aus dem Repo-Wurzelverzeichnis: python3 -I docs/09-Research/learning-balance/score_measures.py
Schreibt MEASURES-SCORED.json und RANKING.json; MEASURES.json (Rahmen) bleibt unverändert.
"""
import json
from pathlib import Path

BASE = Path("docs/09-Research/learning-balance")
doc = json.loads((BASE / "MEASURES.json").read_text(encoding="utf-8"))

# id: (A, P, I, V, U, Begründung)
SCORES = {
    "G-01": (3, 3, 1, 3, 2, "Schließt belegte Lücken in ARC-02/ARC-03 (Zählung, Abwesenheit) und BPMN-01/02 (genau einer je Aktivierung); NE-Fälle nicht ausgeführt."),
    "G-02": (3, 0, 0, 1, 1, "C4-02 und C4-03: unmarkierte Ableitung besteht P1; Voraussetzung für VR-01; durch P1-Läufe belegt."),
    "G-03": (2, 0, 2, 1, 1, "Verdichtung mit Quellenspur für C4-02 (ein Architekturfall); DSM-01/02 zählen zu I; P1 und Code-Analyse."),
    "G-04": (3, 1, 1, 0, 2, "C4-01 und ARC-01 brauchen versionierte Abbildungen und Namensfallen; BPMN-01 nur Namensrandfall; vor allem Analyse."),
    "G-05": (1, 0, 3, 0, 1, "Für Architektur nur indirekt (Kopplung, Partition); Kern ist DAG/DSM; durch LIB-Aufrufe belegt."),
    "G-06": (0, 0, 3, 0, 1, "Reiner Impact-Fall (DAG-01/03); kein Architektur- oder Prozessbezug; LIB-Aufrufe belegt."),
    "G-07": (0, 3, 1, 1, 2, "BPMN-01 und BPMN-02: Exklusivität und Synchronisation; Kern der Prozessspuren; NE-Fälle, nicht ausgeführt."),
    "G-08": (0, 3, 0, 0, 1, "BPMN-03 und Voraussetzung für G-07 und VR-12; belegt durch P1 (scoped/shared) und Probe E-2/L-2."),
    "G-09": (1, 0, 2, 0, 1, "Domänen- und Prädikatdisziplin betrifft Architekturmatrizen nur indirekt; Kern DSM-01/02; P1 belegt."),
    "G-10": (2, 0, 0, 1, 1, "Alternative Quellenbindung für C4-02; P1 UNRESOLVED belegt."),
    "T-01": (0, 0, 0, 0, 2, "Werkzeug für alle Studien, kein Anwendungsfallnutzen."),
    "T-02": (0, 0, 1, 0, 2, "Werkzeug für LIB-Aufrufe (DAG); kein Architektur- oder Prozessnutzen."),
    "LR-1": (2, 2, 1, 0, 1, "E-1 (Projektion, C4-02/03) und E-2 (Spurprüfung, BPMN-03): fachlicher Ergebniskern sonst untypisiert; Probe belegt."),
    "VR-01": (3, 0, 0, 1, 2, "V-01 in C4-02 und C4-03: Herkunft sichtbar; M-01A erfüllt alle Kriterien, blind richtig; nur Agenten-Proxy."),
    "VR-05": (2, 0, 1, 3, 2, "ARC-03 (Abwesenheit) im Bild trennbar; DSM-03 zählt zu V; M-05C blind richtig; nur Agenten-Proxy."),
    "VR-09": (0, 0, 3, 0, 2, "Zyklenkomponente für DAG-03; kein Architektur- oder Prozessbezug; nur Agenten-Proxy."),
    "VR-12": (0, 2, 0, 0, 2, "BPMN-03: Instanz und Paarung sichtbar; M-12B blind richtig; nur Agenten-Proxy."),
    "PO-1": (1, 0, 0, 0, 2, "Begriffskonflikt in R-2a/b (C4); Randfall der Beschriftung; Vor- und Blindprüfung."),
    "PO-2": (2, 1, 1, 0, 2, "Kanten und Richtung in cube.flow nur über das Ledger eindeutig (R-2, L-1, L-2; blind B04/B09)."),
    "PO-3": (1, 0, 1, 0, 1, "Linsenakzent nur Farbe/Strichstärke (attrs.json); betrifft Architekturflüsse indirekt."),
    "PO-4": (0, 0, 1, 0, 1, "Nur DAG-Vorher-Bild (P-09a)."),
    "PO-5": (0, 0, 2, 0, 1, "DSM-Lesart der Achsenreihenfolge (R-1); I."),
    "PO-6": (0, 0, 0, 2, 1, "Namen ausgeblendeter Spalten (R-1b); Vollständigkeit allgemein."),
    "PO-8": (0, 1, 0, 0, 1, "L-2: Instanzen werden zusammengepackt; schließt die Gruppierung nur teilweise (keine Verstoßmarke)."),
    "HT": (1, 1, 1, 1, 2, "Würde VR-01/VR-12 an Menschen prüfen; Nutzen indirekt, Anwendung erst nach Umsetzung."),
}
K_OF = {m["id"]: m for m in doc["measures"]}
assert set(SCORES) == set(K_OF), set(SCORES) ^ set(K_OF)
for m in doc["measures"]:
    a, p, i, v, u, r = SCORES[m["id"]]
    m["score"] = {"A": a, "P": p, "I": i, "V": v, "U": u, "rationale": r}
doc["scored"] = True


def e_score(mid):
    return 1 if mid <= 0.5 else 2 if mid <= 1 else 3 if mid <= 2 else 4 if mid <= 3 else 5


def mid(m):
    return sum(m["effort_pt"]) / 2


def chain(mid_):
    out = []
    for d in K_OF[mid_]["depends_on"]:
        for x in chain(d) + [d]:
            if x not in out:
                out.append(x)
    return out


def unit(members, key):
    ms = [K_OF[x] for x in members]
    pt = sum(mid(m) for m in ms)
    E = e_score(pt) if len(ms) > 1 else ms[0]["E"]
    s = {k: sum(m["score"][k] for m in ms) for k in "APIV"}
    K = max(m["K"] for m in ms)
    U = max(m["score"]["U"] for m in ms)
    return {"members": members, "pt_mid": round(pt, 3), "E": E, "K": K, "U": U, **s,
            "S": round((s["A"] + s["P"]) / E, 4), "S1": round(sum(s.values()) / E, 4), "S2": round((s["A"] + s["P"]) / (E * U), 4), "key": key}


order = [m["id"] for m in doc["measures"]]
own = lambda x: K_OF[x]["score"]["A"] + K_OF[x]["score"]["P"]


def build_units(score_key, include_zero):
    units = []
    for x in order:
        if not include_zero and own(x) == 0:
            continue
        if K_OF[x]["depends_on"]:
            units.append(unit(chain(x) + [x], score_key))
        else:
            units.append(unit([x], score_key))
    return units


def rank(units, key):
    return sorted(units, key=lambda u: (-u[key], u["K"], u["U"], order.index(u["members"][-1])))


def flatten(ranked):
    seen, out = set(), []
    for i, u in enumerate(ranked, 1):
        for x in u["members"]:
            if x not in seen:
                seen.add(x); out.append({"id": x, "unit_rank": i, "via": "+".join(u["members"]), "unit_S": u["S"]})
    return out


main_units = rank(build_units("S", False), "S")
# Alternativen G-02 / G-10: nur die besser gereihte bleibt
best = lambda x: min(i for i, u in enumerate(main_units) if x in u["members"])
alt_loser = "G-10" if best("G-02") <= best("G-10") else "G-02"
main_units = [u for u in main_units if alt_loser not in u["members"]]
main = flatten(main_units)
side = [x for x in order if x not in {r["id"] for r in main} and x != alt_loser]

sel = [main_units[0]]
if len(main_units) > 1 and main_units[0]["pt_mid"] + main_units[1]["pt_mid"] <= 5:
    sel.append(main_units[1])

sens = {k: [{"rank": i, "unit": "+".join(u["members"]), "value": u[k]} for i, u in enumerate(rank(build_units(k, k == "S1"), k)[:5], 1)] for k in ("S1", "S2")}
ranking = {"format": "mile004.ranking/1", "frame": "SCORING-FRAME.md", "units_ranked": [{"rank": i, **u} for i, u in enumerate(main_units, 1)],
           "measures_in_order": main, "alternative_not_ranked": {"id": alt_loser, "instead_of": "G-02" if alt_loser == "G-10" else "G-10"},
           "side_list": side, "mile005_selection": [{"unit": "+".join(u["members"]), "pt_mid": u["pt_mid"]} for u in sel],
           "mile005_pt_mid_total": round(sum(u["pt_mid"] for u in sel), 3), "sensitivity_top5": sens,
           "mile002_order": ["G-01", "G-06/G-05", "G-02 (oder G-10)", "G-03", "G-09/G-08", "G-04", "G-07"]}
(BASE / "MEASURES-SCORED.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(BASE / "RANKING.json").write_text(json.dumps(ranking, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for u in ranking["units_ranked"]:
    print(u["rank"], "+".join(u["members"]), "S", u["S"], "E", u["E"], "K", u["K"], "U", u["U"], "PT", u["pt_mid"])
print("alt", ranking["alternative_not_ranked"], "side", side)
print("MILE-005", ranking["mile005_selection"], ranking["mile005_pt_mid_total"])
print(json.dumps(sens, ensure_ascii=False))
