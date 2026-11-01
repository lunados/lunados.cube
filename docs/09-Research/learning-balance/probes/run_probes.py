"""MILE-004 TASK-025: führt die Proben aus PROBE-PLAN.json aus und schreibt Nachweise nach docs/10-Evidence/MILE-004/.

Aufruf aus dem Repo-Wurzelverzeichnis mit der Agent-Umgebung (jsonschema, Printer):
    .agent-env/venv/bin/python -B docs/09-Research/learning-balance/probes/run_probes.py
E-1/E-2: Schemaprüfung, Identität Aufruf ↔ Ergebnis, Trägerklassifikation gegen das Schema.
L-1/L-2: cube_plan_source → cube_plan_views → cube_plan_check (Implementierung hinter den MCP-Tools).
"""
import hashlib, json, platform, subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
PLAN = ROOT / "docs/09-Research/learning-balance/probes/PROBE-PLAN.json"
EV = ROOT / "docs/10-Evidence/MILE-004"
sys.path.insert(0, str(ROOT / "P3/adapters/mcp-local"))

import jsonschema  # noqa: E402

plan = json.loads(PLAN.read_text(encoding="utf-8"))
sha = lambda b: hashlib.sha256(b).hexdigest()
log = {"format": "mile004.probe-run/1", "plan_sha256": sha(PLAN.read_bytes()),
       "git_head": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip(),
       "python": platform.python_version(), "jsonschema": __import__("importlib.metadata").metadata.version("jsonschema"),
       "sources_verified": [], "envelope": {}, "render": {}}

# Quellen gegen den Plan prüfen
for s in plan["sources"]:
    p = (ROOT if s["repo"] == ROOT.name else ROOT.parent / s["repo"]) / s["path"]
    log["sources_verified"].append({"path": s["path"], "match": p.exists() and sha(p.read_bytes()) == s["sha256"]})

# ---------------- Envelope-Proben ----------------
space = ROOT.parent / "lunados.space"
src = {s["label"].split(" ")[0]: s for s in plan["sources"]}
schema_path = lambda name: next(space / s["path"] for s in plan["sources"] if s["path"].endswith(name))
R_SCHEMA = json.loads(schema_path("evaluator-result.v0.2.schema.json").read_text())
C_SCHEMA = json.loads(schema_path("evaluator-call.v0.1.schema.json").read_text())
RV, CV = jsonschema.Draft202012Validator(R_SCHEMA), jsonschema.Draft202012Validator(C_SCHEMA)

# Schemaort je Pflichtunterscheidung (JSON-Pointer in Ergebnis- bzw. Aufrufschema)
POINTERS = {
    ("E-1", "d1"): ("result", "/properties/outcome/properties/detail"),
    ("E-1", "d2"): ("result", "/properties/derivation_ref"),
    ("E-1", "d3"): ("call", "/properties/parameters"),
    ("E-1", "d4"): ("result", "/properties/outcome/properties/detail"),
    ("E-1", "d5"): ("result", "/properties/disposition"),
    ("E-1", "d6"): ("result", "/properties/outcome/properties/value"),
    ("E-2", "d1"): ("call", "/properties/parameters"),
    ("E-2", "d2"): ("call", "/properties/inputs/items/properties/content"),
    ("E-2", "d3"): ("result", "/properties/outcome/properties/value"),
    ("E-2", "d4"): ("result", "/properties/disposition"),
    ("E-2", "d5"): ("result", "/properties/derivation_ref"),
    ("E-2", "d6"): ("result", "/properties/effectful_execution_authorized"),
}


def node(schema, pointer):
    n = schema
    for part in pointer.strip("/").split("/"):
        n = n[part]
    while "$ref" in n:
        n = node(schema, n["$ref"].lstrip("#"))
    return n


def carrier(n):
    if any(k in n for k in ("enum", "const", "pattern")):
        return "T"
    if n.get("type") == "object" and "properties" not in n:
        return "U"
    if n.get("type") == "string":
        return "U"
    return "T"


TYPED = ["schema", "method_id", "descriptor_digest", "derivation_ref", "evaluator_id", "disposition", "runtime_authority", "effectful_execution_authorized", "selected_alternative"]
for pid in ("E-1", "E-2"):
    pr = plan["probes"][pid]
    rows = []
    for inst in pr["instances"]:
        ce = [e.message for e in CV.iter_errors(inst["call"])]
        re_ = [e.message for e in RV.iter_errors(inst["result"])]
        ident = all(inst["result"][k] == inst["call"][k] for k in ("method_id", "descriptor_digest", "derivation_ref"))
        rows.append({"case_id": inst["case_id"], "call_valid": not ce, "call_errors": ce, "result_valid": not re_, "result_errors": re_, "identity_ok": ident,
                     "disposition": inst["result"]["disposition"], "outcome_value": inst["result"]["outcome"]["value"]})
    dist = []
    for d in pr["distinctions"]:
        which, ptr = POINTERS[(pid, d["id"])]
        obs = carrier(node(R_SCHEMA if which == "result" else C_SCHEMA, ptr))
        dist.append({"id": d["id"], "what": d["what"], "expected": d["expected_carrier"], "observed": obs, "schema": which, "pointer": ptr, "match": obs == d["expected_carrier"]})
    # Kollisionen: Paare, die sich nur in untypisierten Feldern unterscheiden bzw. ganz gleich sind
    insts = pr["instances"]
    pairs = []
    for i in range(len(insts)):
        for j in range(i + 1, len(insts)):
            a, b = insts[i]["result"], insts[j]["result"]
            typed_diff = [k for k in TYPED if a[k] != b[k]]
            untyped_diff = [k for k in ("outcome", "findings") if a[k] != b[k]]
            pairs.append({"pair": [insts[i]["case_id"], insts[j]["case_id"]], "typed_fields_differing": typed_diff, "untyped_fields_differing": untyped_diff,
                          "identical": not typed_diff and not untyped_diff})
    n_count = sum(1 for d in dist if d["observed"] == "N")
    u_count = sum(1 for d in dist if d["observed"] == "U")
    rule = "R-E1" if n_count or any(p["identical"] for p in pairs) else ("R-E2" if u_count else "R-E3")
    log["envelope"][pid] = {"instances": rows, "distinctions": dist, "pairs": pairs, "rule": rule,
                            "all_valid": all(r["call_valid"] and r["result_valid"] and r["identity_ok"] for r in rows)}

# ---------------- Render-Proben ----------------
from aiaeao_mcp_local import plan_views as pv  # noqa: E402


def run_call(probe, call):
    ps = dict(call["plan_source"])
    if ps.get("tracks") == "<tracks>":
        ps["tracks"] = probe["tracks"]
    if ps.get("labels") == "<labels>":
        ps["labels"] = probe["labels"]
    printer = ps.pop("printer")
    out = {"call_id": call["call_id"], "plan_source": call["plan_source"], "plan_views": call["plan_views"]}
    try:
        wrapped = pv.plan_source(probe["context"], probe["plan_id"], printer, **ps)
        source = wrapped["source"]
        v = dict(call["plan_views"])
        res = pv.plan_views(source, v.pop("view"), v.pop("granularity"), **v)
        chk = pv.plan_check(res)
    except BaseException as e:  # Ablehnungen sind Ergebnisse
        out.update(status="REFUSED", error=repr(e)[:2000])
        return out
    d = EV / call["call_id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "source.json").write_text(json.dumps(wrapped, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    svgs = {}
    if isinstance(res.get("index"), dict) and res["index"].get("svg"):
        svgs[f'{call["call_id"]}-00.svg'] = res["index"]["svg"]
    for i, p in enumerate(res.get("panels", []), 1):
        svgs[f'{call["call_id"]}-{i:02d}.svg'] = p["svg"]
    for name, s in svgs.items():
        (d / name).write_text(s, encoding="utf-8")
    rep = {k: v for k, v in res.items() if k not in ("panels", "index")}
    rep["panels_meta"] = [{k: v for k, v in p.items() if k != "svg"} for p in res.get("panels", [])]
    (d / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    out.update(status="RENDERED", check=chk.get("status", chk.get("result")), check_detail={k: v for k, v in chk.items() if k not in ("printer",)},
               svgs={n: sha(s.encode("utf-8")) for n, s in svgs.items()})
    return out


for pid in ("L-1", "L-2"):
    pr = plan["probes"][pid]
    log["render"][pid] = [run_call(pr, c) for c in pr["calls"]]

EV.mkdir(parents=True, exist_ok=True)
(EV / "task025-probe-run.json").write_text(json.dumps(log, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps({"sources_ok": all(s["match"] for s in log["sources_verified"]),
                  "envelope": {k: {"all_valid": v["all_valid"], "rule": v["rule"], "carriers": {d["id"]: (d["observed"], d["match"]) for d in v["distinctions"]}} for k, v in log["envelope"].items()},
                  "render": {k: [(c["call_id"], c["status"], c.get("check"), list(c.get("svgs", {}))) for c in v] for k, v in log["render"].items()}}, ensure_ascii=False, indent=1))
