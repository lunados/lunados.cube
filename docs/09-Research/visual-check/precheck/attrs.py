"""TASK-022, Kriterium 1: tragende SVG-Merkmale maschinell auslesen (Strichmuster, Strichstärke, Farbe, Text)."""
import json, re, sys, hashlib
import xml.etree.ElementTree as ET
NS = "{http://www.w3.org/2000/svg}"
def edges(root):
    out = {}
    for g in root.iter(NS + "g"):
        eid = g.get("data-edge-id")
        if not eid: continue
        st = {"stroke": set(), "width": set(), "dash": set()}
        for el in g:
            if el.tag in (NS + "line", NS + "path", NS + "polyline"):
                st["stroke"].add(el.get("stroke")); st["width"].add(el.get("stroke-width")); st["dash"].add(el.get("stroke-dasharray"))
        out[eid] = {k: sorted(x for x in v if x) for k, v in st.items()}
    return out
def summary(root):
    dashes, widths, texts = set(), set(), []
    for el in root.iter():
        if el.get("stroke-dasharray"): dashes.add(el.get("stroke-dasharray"))
        if el.get("stroke-width"): widths.add(el.get("stroke-width"))
        if el.tag == NS + "text" and (el.text or "").strip(): texts.append(el.text.strip())
    return {"dasharrays": sorted(dashes), "stroke_widths": sorted(widths, key=float), "text_count": len(texts), "texts": texts}
res = {}
for item in json.load(open(sys.argv[1])):
    raw = open(item["file"], "rb").read(); root = ET.fromstring(raw)
    s = summary(root); e = edges(root)
    res[item["id"]] = {"sha256_16": hashlib.sha256(raw).hexdigest()[:16], "edges": e, **{k: v for k, v in s.items() if k != "texts"},
                       "texts_matching": [t for t in s["texts"] if re.search(r"(?i)legend|deklar|abgeleit|unbekannt|offen|geprüft|ausgeblendet|blank|hidden|zykl|cycle|focus|instanz|MOCKUP|STATUS|doppelt|gepunktet|gestrichelt|dashed|solid", t)]}
json.dump(res, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
for k, v in res.items():
    print(k, "dash", v["dasharrays"], "w", v["stroke_widths"][:8])
    for eid, a in v["edges"].items(): print("   ", eid, a)
