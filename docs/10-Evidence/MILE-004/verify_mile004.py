"""MILE-004 TASK-029: Abschlussprüfung. Aufruf aus dem Repo-Wurzelverzeichnis:
    python3 -I docs/10-Evidence/MILE-004/verify_mile004.py
Schreibt docs/10-Evidence/MILE-004/verification.json. Nur Standardbibliothek und git.
Die Skripte build_probes.py, build_frame.py und score_measures.py werden zur Reproduktionsprüfung
ausgeführt; ihre Ausgaben werden danach mit git auf den committeten Stand zurückgesetzt.
"""
import hashlib, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
LB = ROOT / "docs/09-Research/learning-balance"
EV = ROOT / "docs/10-Evidence/MILE-004"
MILE004_BASE = "dbddb17"   # Planungs-Commit MILE-004
MAIN_BASE = "b916cc6"      # main vor MILE-004


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


out = {"head": git("rev-parse", "--short", "HEAD").stdout.strip(), "note": "HEAD vor dem Abschluss-Commit; Statusänderungen dieses Commits liegen im Arbeitsbaum."}

# 1. Erwartung vor Lauf, Rahmen vor Bewertung
order = [("docs/09-Research/learning-balance/probes/PROBE-PLAN.json", "caec0e2", "8300de7", "Probeplan (Nachtrag L-2) vor dem Lauf"),
         ("docs/09-Research/learning-balance/MEASURES.json", "60d24d5", "08157d4", "Bewertungsrahmen vor der Bewertung"),
         ("docs/09-Research/learning-balance/SCORING-FRAME.md", "60d24d5", "08157d4", "Bewertungsrahmen vor der Bewertung")]
items = []
for f, spec, ev, what in order:
    last = git("log", "-1", "--format=%h", "--abbrev=7", "--", f).stdout.strip()
    anc = git("merge-base", "--is-ancestor", spec, ev).returncode == 0 and spec != ev
    dirty = bool(git("status", "--porcelain", "--", f).stdout.strip())
    items.append({"file": f, "what": what, "spec_commit": spec, "evidence_commit": ev, "last_change": last, "unchanged_since": last.startswith(spec) and not dirty, "before_evidence": anc})
first_plan = git("log", "--format=%h", "--abbrev=7", "--", "docs/09-Research/learning-balance/probes/PROBE-PLAN.json").stdout.split()[-1]
plan_now = json.loads((LB / "probes/PROBE-PLAN.json").read_text(encoding="utf-8"))
plan_first = json.loads(git("show", f"{first_plan}:docs/09-Research/learning-balance/probes/PROBE-PLAN.json").stdout)
same = all(plan_first["probes"][k].get(f) == plan_now["probes"][k].get(f) for k in plan_now["probes"] for f in ("expected", "decision_rule", "distinctions", "instances", "context")) \
    and plan_first["envelope_rule"] == plan_now["envelope_rule"]
frame_committed = json.loads(git("show", "60d24d5:docs/09-Research/learning-balance/MEASURES.json").stdout)
out["order"] = {"items": items, "issues": sum(1 for i in items if not (i["unchanged_since"] and i["before_evidence"])),
                "first_plan_commit": first_plan, "expectations_unchanged_by_amendment": same,
                "frame_unscored_when_committed": all(all(v is None for v in m["score"].values()) for m in frame_committed["measures"])}

# 2. Quellen und Lauf
run = json.loads((EV / "task025-probe-run.json").read_text(encoding="utf-8"))
src_now = []
for s in plan_now["sources"]:
    p = (ROOT if s["repo"] == ROOT.name else ROOT.parent / s["repo"]) / s["path"]
    src_now.append(p.exists() and sha(p) == s["sha256"])
svg_bad = []
for k, calls in run["render"].items():
    for c in calls:
        for n, h in c.get("svgs", {}).items():
            p = EV / c["call_id"] / n
            if not p.exists() or sha(p) != h:
                svg_bad.append(n)
out["probe_run"] = {"plan_sha256_matches": run["plan_sha256"] == sha(LB / "probes/PROBE-PLAN.json"),
                    "sources_ok_at_run": all(s["match"] for s in run["sources_verified"]), "sources_ok_now": all(src_now),
                    "envelope": {k: {"all_valid": v["all_valid"], "rule": v["rule"], "carriers_as_expected": all(d["match"] for d in v["distinctions"])} for k, v in run["envelope"].items()},
                    "render": {c["call_id"]: {"status": c["status"], "check": c.get("check")} for calls in run["render"].values() for c in calls},
                    "svg_hash_mismatch": svg_bad}

# 3. Reproduktion
def regen(script, outputs, ignore_commit=False):
    before = {o: (LB / o).read_bytes() for o in outputs}
    r = subprocess.run([sys.executable, "-I", str(LB / script)], cwd=ROOT, capture_output=True, text=True)
    res = {}
    for o in outputs:
        after = (LB / o).read_bytes()
        if ignore_commit:
            a, b = json.loads(before[o]), json.loads(after)
            for d in (a, b):
                for s in d.get("sources", []):
                    s.pop("commit", None)
            res[o] = a == b
        else:
            res[o] = before[o] == after
        (LB / o).write_bytes(before[o])
    return {"exit": r.returncode, "identical": res}
out["reproduction"] = {"build_probes": regen("probes/build_probes.py", ["probes/PROBE-PLAN.json"], ignore_commit=True),
                       "build_frame": regen("build_frame.py", ["MEASURES.json"]),
                       "score_measures": regen("score_measures.py", ["MEASURES-SCORED.json", "RANKING.json"])}

# 4. Rangfolge und Auswahl
rk = json.loads((LB / "RANKING.json").read_text(encoding="utf-8"))
u = rk["units_ranked"]
out["ranking"] = {"rank1": "+".join(u[0]["members"]), "rank2": "+".join(u[1]["members"]),
                  "selection": [s["unit"] for s in rk["mile005_selection"]], "selection_pt": rk["mile005_pt_mid_total"],
                  "selection_rule_ok": rk["mile005_pt_mid_total"] <= 5 and len(rk["mile005_selection"]) == 2,
                  "all_scored": all(m["score"]["A"] is not None for m in json.loads((LB / "MEASURES-SCORED.json").read_text())["measures"])}

# 5. MILE-005 nur geplant; Schichten unverändert
frozen = ["AIAEAO_Pure_Cube_P0_v9.4", "P1", "P2", "P3"]
out["no_implementation"] = {"P0_P3_committed_unchanged_since_main": git("diff", "--quiet", MAIN_BASE, "HEAD", "--", *frozen).returncode == 0,
                            "worktree_P0_P3_unchanged": git("diff", "--quiet", "--", *frozen).returncode == 0,
                            "untracked_outside_scope": sorted(l[3:] for l in git("status", "--porcelain", "--", *frozen).stdout.splitlines()),
                            "mile005_status_planned": "Status: planned" in (ROOT / "docs/02-Milestones/MILE-005-completeness-instances.md").read_text(encoding="utf-8")}

# 6. Links
bad = []
for base in ("docs", "openspec"):
    for d, _, fs in os.walk(ROOT / base):
        for f in fs:
            if f.endswith(".md"):
                p = Path(d) / f
                for t in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", p.read_text(encoding="utf-8")):
                    if t.startswith(("http", "mailto")) or "chatgpt" in t:
                        continue
                    if not (p.parent / t).resolve().exists():
                        bad.append(f"{p.relative_to(ROOT)} -> {t}")
out["broken_links"] = len(bad)
out["broken_link_list"] = bad

pr = out["probe_run"]
ok = (out["order"]["issues"] == 0 and out["order"]["expectations_unchanged_by_amendment"] and out["order"]["frame_unscored_when_committed"]
      and pr["plan_sha256_matches"] and pr["sources_ok_at_run"] and all(v["all_valid"] and v["carriers_as_expected"] for v in pr["envelope"].values())
      and all(v["status"] == "RENDERED" and v["check"] == "PASS" for v in pr["render"].values()) and not pr["svg_hash_mismatch"]
      and all(all(r["identical"].values()) and r["exit"] == 0 for r in out["reproduction"].values())
      and out["ranking"]["selection_rule_ok"] and out["ranking"]["all_scored"]
      and out["no_implementation"]["P0_P3_committed_unchanged_since_main"] and out["no_implementation"]["worktree_P0_P3_unchanged"] and out["no_implementation"]["mile005_status_planned"]
      and not bad)
out["all_ok"] = ok
(EV / "verification.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k != "broken_link_list"}, ensure_ascii=False, indent=1)[:3500])
sys.exit(0 if ok else 1)
