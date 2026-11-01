"""MILE-003 TASK-023: Abschlussprüfung. Aufruf aus dem Repo-Wurzelverzeichnis:
    python3 -I docs/10-Evidence/MILE-003/verify_mile003.py
Schreibt docs/10-Evidence/MILE-003/verification.json. Nur Standardbibliothek und git.
"""
import hashlib, json, os, re, subprocess, sys, tempfile, unicodedata
from pathlib import Path

ROOT = Path.cwd()
VC = ROOT / "docs/09-Research/visual-check"
EV = ROOT / "docs/10-Evidence/MILE-003"
MILE003_BASE = "7959825"  # MILE-002 abgeschlossen; Beginn MILE-003


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)


out = {"head": git("rev-parse", "--short", "HEAD").stdout.strip(), "note": "HEAD vor dem Abschluss-Commit; Statusänderungen dieses Commits liegen im Arbeitsbaum."}

# 1. Inventur
inv = (VC / "INVENTORY.md").read_text(encoding="utf-8")
rows = {}
for line in inv.splitlines():
    m = re.match(r"\|\s*\**(V-\d\d)\**\s*\|.*?\|\s*\**(trägt|teilweise|Lücke)\**\s*\|", line)
    if m:
        rows[m.group(1)] = m.group(2)
out["inventory"] = {"rows": len(rows), "all_twelve": sorted(rows) == [f"V-{i:02d}" for i in range(1, 13)], "verdicts": rows}

# 2. Render-Logs
renders = {"runs": 0, "all_check_pass": True, "svg_hash_mismatch": []}
for log in ("task019-render-log.json", "task020-render-log.json"):
    for run in json.loads((EV / log).read_text())["runs"]:
        renders["runs"] += 1
        renders["all_check_pass"] &= run.get("check") == "PASS"
        for name, meta in run["svgs"].items():
            p = EV / name.rsplit("-", 1)[0] / name
            if not p.exists() or sha(p) != meta["sha256"]:
                renders["svg_hash_mismatch"].append(name)
out["renders"] = renders

# 3. Mockups
md = (VC / "MOCKUPS.md").read_text(encoding="utf-8")
documented = dict(re.findall(r"(M-\d\d[A-Z])\s*`([0-9a-f]{16})`", md))
symbols = (ROOT / "AIAEAO_Pure_Cube_P0_v9.4/v9.4/visual/symbols.json").read_text(encoding="utf-8")
mock = {"files": {}, "all_documented_hash_match": True, "all_marked": True, "no_active_content": True, "symbol_glyphs": [], "symbol_glyphs_in_symbols_json": True}
glyphs = set()
for p in sorted((VC / "mockups").glob("M-*.svg")):
    s = p.read_text(encoding="utf-8")
    h = sha(p)[:16]
    ok = documented.get(p.stem) == h
    marked = "MOCKUP — kein Printer-Output" in s and 'data-mockup="true"' in s
    active = any(t in s for t in ("<pattern", "<use", "<image", "href", "<script"))
    mock["files"][p.stem] = {"sha256_16": h, "documented": documented.get(p.stem), "match": ok, "marked": marked}
    mock["all_documented_hash_match"] &= ok
    mock["all_marked"] &= marked
    mock["no_active_content"] &= not active
    for ch in s:
        cat = unicodedata.category(ch)
        if cat == "So" or (0x1D400 <= ord(ch) <= 0x1D7FF):
            glyphs.add(ch)
mock["symbol_glyphs"] = sorted(glyphs)
mock["symbol_glyphs_in_symbols_json"] = all(g in symbols for g in glyphs)
with tempfile.TemporaryDirectory() as td:
    r = subprocess.run([sys.executable, "-I", str(VC / "mockups/mockups.py"), td], capture_output=True, text=True)
    regen = {f.stem: sha(f)[:16] for f in Path(td).glob("*.svg")}
mock["generator_reproduces_all"] = regen == {k: v["sha256_16"] for k, v in mock["files"].items()}
mock["count"] = len(mock["files"])
out["mockups"] = mock

# 4. Priorisierte Paare
need = {"V-01": ["docs/10-Evidence/MILE-003/R-2a/R-2a-01.svg", "docs/10-Evidence/MILE-003/R-2b/R-2b-01.svg", "docs/09-Research/visual-check/mockups/M-01A.svg"],
        "V-05": ["docs/10-Evidence/MILE-003/R-1a/R-1a-01.svg", "docs/09-Research/visual-check/mockups/M-05C.svg"],
        "V-09": ["docs/10-Evidence/MILE-003/P-09a2/P-09a2-01.svg", "docs/10-Evidence/MILE-003/P-09b/P-09b-01.svg", "docs/09-Research/visual-check/mockups/M-09C.svg"],
        "V-12": ["docs/09-Research/visual-check/mockups/M-12A.svg", "docs/09-Research/visual-check/mockups/M-12B.svg"]}
out["priority_pairs"] = {k: all((ROOT / f).exists() for f in v) for k, v in need.items()}

# 5. Erwartung vor Lauf: Spezifikation zuletzt in ihrem Commit geändert, dieser ist echter Vorfahre des Nachweis-Commits
pairs = [("docs/09-Research/visual-check/renders/R-1.json", "657efe8", "97c2d09"),
         ("docs/09-Research/visual-check/renders/R-2.json", "1b4f4b7", "97c2d09"),
         ("docs/09-Research/visual-check/pairs/P-01.json", "02318c5", "63e9995"),
         ("docs/09-Research/visual-check/pairs/P-09.json", "03b8e62", "63e9995"),
         ("docs/09-Research/visual-check/precheck/PLAN.json", "1f329ef", "a75b183"),
         ("docs/09-Research/visual-check/precheck/BLIND-PLAN.json", "57f6549", "9ae1a44")]
exp = []
for f, spec_c, ev_c in pairs:
    last = git("log", "-1", "--format=%h", "--abbrev=7", "--", f).stdout.strip()
    anc = git("merge-base", "--is-ancestor", spec_c, ev_c).returncode == 0 and spec_c != ev_c
    dirty = bool(git("status", "--porcelain", "--", f).stdout.strip())
    exp.append({"file": f, "spec_commit": spec_c, "evidence_commit": ev_c, "last_change": last, "unchanged_since": last.startswith(spec_c) and not dirty, "before_evidence": anc})
out["expectation_before_run"] = {"items": exp, "issues": sum(1 for e in exp if not (e["unchanged_since"] and e["before_evidence"]))}

# 6. Vorprüfung
res = json.loads((VC / "precheck/RESULTS.json").read_text(encoding="utf-8"))
blind = json.loads((VC / "precheck/BLIND-RESULTS.json").read_text(encoding="utf-8"))
units_ok = all(set(u["criteria"]) == {f"C{i}" for i in range(1, 7)} for u in res["units"])
out["precheck"] = {"units": len(res["units"]), "all_six_criteria": units_ok, "answers_are_proxy": res["checker"]["answers_are_proxy"], "blind": res["checker"]["blind"],
                   "tally": res["tally"], "blind_rows": len(blind["rows"]), "blind_tally": blind["tally"]}

# 7. Eingefrorene Schichten
frozen = ["AIAEAO_Pure_Cube_P0_v9.4", "P1", "P2"]
out["frozen_layers"] = {"committed_unchanged_since_mile003_start": git("diff", "--quiet", MILE003_BASE, "HEAD", "--", *frozen, "P3").returncode == 0,
                        "worktree_P0_P2_unchanged": git("diff", "--quiet", "--", *frozen).returncode == 0,
                        "uncommitted_outside_scope": sorted(l[3:] for l in git("status", "--porcelain", "--", "P2", "P3").stdout.splitlines())}

# 8. Links
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

ok = (out["inventory"]["all_twelve"] and renders["all_check_pass"] and not renders["svg_hash_mismatch"] and mock["all_documented_hash_match"] and mock["all_marked"]
      and mock["no_active_content"] and mock["symbol_glyphs_in_symbols_json"] and mock["generator_reproduces_all"] and all(out["priority_pairs"].values())
      and out["expectation_before_run"]["issues"] == 0 and units_ok and out["precheck"]["blind_rows"] == 15
      and out["frozen_layers"]["committed_unchanged_since_mile003_start"] and out["frozen_layers"]["worktree_P0_P2_unchanged"] and not bad)
out["all_ok"] = ok
(EV / "verification.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k not in ("broken_link_list",)}, ensure_ascii=False, indent=1)[:4000])
sys.exit(0 if ok else 1)
