"""MILE-003 TASK-021 hand mockups (C-Varianten nach TASK-022). Candidate visual rules, NOT printer output.

Deterministic SVG text; no <pattern>, <use>, <image>, href or script (VP-05 NO_ACTIVE_SVG_CONTENT kept).
Only existing VG anchors are used as glyphs: ⌹ resource, ⌼ evidence, ⬠ boundary, 𝗜 integration, 𝗥 runtime, 𝗣 provider.
"""
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

FONT = "Helvetica, Arial, sans-serif"
INK, MUTED, LINE, PAPER = "#111827", "#4b5563", "#9ca3af", "#ffffff"


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.parts = w, h, []
        self.parts.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="{PAPER}"/>')
        self.title = title

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=13, weight="normal", fill=INK, anchor="start", italic=False):
        st = ' font-style="italic"' if italic else ''
        self.add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{st}>{escape(s)}</text>')

    def rect(self, x, y, w, h, stroke=LINE, fill="none", sw=1, dash=None, rx=0):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def hatch(self, x, y, w, h, gap=8, stroke=LINE):
        # explicit clipped diagonal lines '/', like VP-07 PV-5 (no <pattern>)
        for k in range(-int(h), int(w), gap):
            x1, y1, x2, y2 = x + k, y + h, x + k + h, y
            if x1 < x: y1, x1 = y + h - (x - x1), x
            if x2 > x + w: y2, x2 = y + (x2 - (x + w)), x + w
            if x1 <= x2: self.line(x1, y1, x2, y2, stroke=stroke, sw=0.8)

    def arrow(self, x1, y1, x2, y2, style="solid", sw=1.6, shorten=0):
        ang = math.atan2(y2 - y1, x2 - x1)
        x2s, y2s = x2 - shorten * math.cos(ang), y2 - shorten * math.sin(ang)
        x1s, y1s = x1 + shorten * math.cos(ang), y1 + shorten * math.sin(ang)
        if style == "double":
            nx, ny = -math.sin(ang) * 2.6, math.cos(ang) * 2.6
            self.line(x1s + nx, y1s + ny, x2s + nx - 8 * math.cos(ang), y2s + ny - 8 * math.sin(ang), sw=sw)
            self.line(x1s - nx, y1s - ny, x2s - nx - 8 * math.cos(ang), y2s - ny - 8 * math.sin(ang), sw=sw)
        else:
            dash = {"solid": None, "dashed": "8 5", "dotted": "2 4"}[style]
            self.line(x1s, y1s, x2s - 6 * math.cos(ang), y2s - 6 * math.sin(ang), sw=sw, dash=dash)
        a1, a2 = ang + math.radians(152), ang - math.radians(152)
        self.add(f'<path d="M{x2s:.1f},{y2s:.1f} L{x2s + 11 * math.cos(a1):.1f},{y2s + 11 * math.sin(a1):.1f} '
                 f'L{x2s + 11 * math.cos(a2):.1f},{y2s + 11 * math.sin(a2):.1f} Z" fill="{INK}"/>')

    def label(self, x, y, s, size=11, weight="normal"):
        w = len(s) * size * 0.58 + 8
        self.rect(x - 4, y - size, w, size + 6, stroke="none", fill="#ffffff")
        self.text(x, y, s, size, weight)

    def banner(self, rid, variant, rule):
        self.rect(16, 12, self.w - 32, 54, stroke=INK, sw=2, dash="10 6")
        self.text(32, 36, f"MOCKUP — kein Printer-Output · {rid} · {variant}", 16, "bold")
        self.text(32, 56, rule, 12, fill=MUTED)

    def footer(self, s):
        self.line(16, self.h - 40, self.w - 16, self.h - 40, stroke=LINE, sw=1)
        self.text(24, self.h - 18, s, 11, fill=MUTED)

    def node(self, x, y, w, h, glyph, label, sub=None):
        self.rect(x, y, w, h, stroke=MUTED, fill="#f3f4f6", sw=1.4, rx=8)
        self.text(x + 14, y + h / 2 + 7, glyph, 20, "bold")
        self.text(x + 44, y + h / 2 + (0 if sub else 5), label, 13, "bold")
        if sub:
            self.text(x + 44, y + h / 2 + 16, sub, 10, fill=MUTED)

    def render(self):
        body = "\n".join(self.parts)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" '
                f'data-mockup="true" data-kind="mile003-candidate">\n<title>{escape(self.title)}</title>\n{body}\n</svg>\n')


def clip(cx, cy, w, h, tx, ty, pad=4):
    """Point where the ray from the box centre (cx, cy) towards (tx, ty) leaves a w x h box, plus padding."""
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (w / 2 + pad) / abs(dx) if dx else float("inf")
    sy = (h / 2 + pad) / abs(dy) if dy else float("inf")
    t = min(sx, sy)
    return cx + dx * t, cy + dy * t


ORDER = ["m:parser", "m:resolver", "m:validator", "m:printer"]
MARKED = {("m:resolver", "m:parser"): "d-rp", ("m:validator", "m:resolver"): "d-vr",
          ("m:printer", "m:validator"): "d-pv", ("m:parser", "m:validator"): "d-fb"}
CHECKED_EMPTY = {("m:printer", "m:parser")}
HIDDEN_COL = "m:printer"


def v05(variant):
    s = Svg(940, 620, f"MOCKUP V-05 {variant}")
    rule = ("Kandidat: vier Zellzustände textlich unterscheiden; ausgeblendete Spalte mit Namen nennen" if variant == "A"
            else "Kandidat: unbekannte Zellen schraffiert, geprüft leer weiß mit Vermerk; ausgeblendete Spalte als benannter Streifen" if variant == "B"
            else "Kandidat (korrigiert nach TASK-022): wie B, aber „geprüft“ nur für die erklärte Zelle, nicht für die Zeile")
    s.banner("V-05", f"Variante {variant}", rule)
    s.text(32, 98, "DSM (IR/FAD, Reihenfolge deklariert) · Fall DSM-03 / ARC-03 · Modell dsm-modules.json", 13, "bold")
    x0, y0, cw, ch, hw = 170, 140, 150, 64, 140
    cols = [c for c in ORDER if c != HIDDEN_COL]
    for j, c in enumerate(cols):
        s.text(x0 + j * cw + cw / 2, y0 - 12, c, 12, "bold", anchor="middle")
    sx = x0 + len(cols) * cw
    s.rect(sx, y0, 26, ch * 4, stroke=LINE, fill="#ffffff")
    s.add(f'<text x="{sx + 17}" y="{y0 + ch * 2}" font-family="{FONT}" font-size="11" fill="{MUTED}" text-anchor="middle" '
          f'transform="rotate(-90 {sx + 17} {y0 + ch * 2})">ausgeblendet: {HIDDEN_COL}</text>')
    for i, r in enumerate(ORDER):
        y = y0 + i * ch
        s.text(x0 - 12, y + ch / 2 + 5, r, 12, "bold", anchor="end")
        for j, c in enumerate(cols):
            x = x0 + j * cw
            if r == c:
                s.rect(x, y, cw, ch, stroke=LINE, fill="#e5e7eb")
                s.text(x + cw / 2, y + ch / 2 + 4, "Element", 11, fill=MUTED, anchor="middle")
                continue
            key = (r, c)
            if key in MARKED:
                s.rect(x, y, cw, ch, stroke=LINE)
                s.text(x + 10, y + 24, f"{MARKED[key]} · dependsOn", 12)
                if ORDER.index(r) < ORDER.index(c):
                    s.text(x + 10, y + 44, "Rückkopplung", 10, fill=MUTED, italic=True)
            elif key in CHECKED_EMPTY:
                s.rect(x, y, cw, ch, stroke=INK, sw=1.4)
                s.text(x + 10, y + 26, "keine · geprüft", 12, "bold")
                s.text(x + 10, y + 44, "Vollständigkeit: Zeile printer" if variant != "C" else "erklärt: nur diese Zelle", 10, fill=MUTED)
            else:
                if variant == "A":
                    s.rect(x, y, cw, ch, stroke=LINE)
                    s.text(x + 10, y + 36, "offen (nicht erhoben)", 11, fill=MUTED, italic=True)
                else:
                    s.rect(x, y, cw, ch, stroke=LINE)
                    s.hatch(x, y, cw, ch)
    ly = y0 + ch * 4 + 40
    s.text(32, ly, "LEGENDE · Kandidat, kein Urteil", 13, "bold")
    s.text(32, ly + 22, "Zelle (Zeile, Spalte): Zeile erhält Input von Spalte = Zeile dependsOn Spalte (IR/FAD).", 12)
    s.text(32, ly + 42, "„d-xx · dependsOn“ = deklarierte Abhängigkeit  ·  " + ("„keine · geprüft“ = als vollständig erklärte Zeile ohne Eintrag" if variant != "C"
                         else "„keine · geprüft“ = für genau dieses Paar erhoben, keine Abhängigkeit"), 12)
    s.text(32, ly + 62, ("„offen (nicht erhoben)“ = unbekannt, nicht leer" if variant == "A"
                         else "Schraffur = unbekannt (nicht erhoben), nicht leer"), 12)
    s.text(32, ly + 82, "Streifen rechts = ausgeblendete Spalte, mit Namen; graue Diagonale = Element selbst" if variant != "C"
           else "Streifen rechts = ausgeblendete Spalte, mit Namen (ihre Zellen, auch unbekannte, sind nicht gezeigt); graue Diagonale = Element selbst", 12)
    s.footer("„geprüft leer“ setzt eine Vollständigkeitserklärung voraus (Lücke G-01). Text und Linien statt Farbe. Keine neuen VG-Anker.")
    return s.render()


def v01():
    s = Svg(940, 520, "MOCKUP V-01")
    s.banner("V-01", "Variante A", "Kandidat: Linienart folgt der gebundenen Herkunft, nicht dem Prädikat; unbekannte Herkunft nie durchgezogen")
    for k, (title, case) in enumerate([("Herkunft gebunden", "C4-02"), ("Herkunft nicht gebunden", "C4-03")]):
        ox = 24 + k * 460
        s.rect(ox, 84, 440, 300, stroke=LINE, rx=6)
        s.text(ox + 16, 108, f"{title} · Fall {case}", 13, "bold")
        s.node(ox + 20, 130, 170, 56, "𝗥", "c4:api", "Container")
        s.node(ox + 250, 300, 170, 56, "𝗣", "c4:db", "Container")
        if k == 0:
            s.node(ox + 20, 220, 170, 56, "𝗜", "c4:order-controller", "Komponente")
            s.arrow(ox + 190, 248, ox + 250, 318, "solid")
            s.text(ox + 196, 296, "e1", 11, fill=MUTED)
            s.arrow(ox + 190, 160, ox + 300, 300, "dashed")
            s.text(ox + 252, 216, "e2 · abgeleitet", 11)
        else:
            s.arrow(ox + 190, 160, ox + 300, 300, "dotted")
            s.text(ox + 252, 216, "e2 · Herkunft ?", 11)
    s.text(32, 412, "LEGENDE · Kandidat, kein Urteil", 13, "bold")
    s.line(32, 432, 92, 432); s.text(104, 436, "durchgezogen = deklariert (Herkunft gebunden: declared)", 12)
    s.line(32, 452, 92, 452, dash="8 5"); s.text(104, 456, "gestrichelt = abgeleitet (Herkunft gebunden: derived, Strategie UnlessAny)", 12)
    s.line(32, 472, 92, 472, dash="2 4"); s.text(104, 476, "gepunktet = Herkunft nicht gebunden (unknown) — nie wie deklariert gezeichnet", 12)
    s.footer("Setzt eine typisierte Relationsherkunft voraus (Lücke G-02). Linienarten aus dem VP-07-Satz; Pfeilspitze bleibt neutral.")
    return s.render()


POS_A = {"wi:b": (40, 150), "wi:c": (250, 150), "wi:d": (460, 150), "wi:a": (670, 150)}
POS_B = {"wi:a": (380, 120), "wi:b": (120, 280), "wi:d": (640, 280), "wi:c": (380, 440)}
EDGES = [("wi:b", "wi:a"), ("wi:c", "wi:a"), ("wi:d", "wi:b"), ("wi:d", "wi:c"), ("wi:a", "wi:d")]
CYCLE = {("wi:a", "wi:d"): "Z1", ("wi:d", "wi:b"): "Z2", ("wi:b", "wi:a"): "Z3"}


def v09(variant):
    h = 600 if variant == "A" else 680
    s = Svg(940, h, f"MOCKUP V-09 {variant}")
    rule = ("Kandidat: Zyklenkanten doppelt und nummeriert (farbfrei), berechneter Zeuge als Statuszeile; Layout wie Printer"
            if variant == "A" else "Kandidat: wie A, aber direkte Kanten ohne gemeinsame Stränge; Status trennt ‚nicht abarbeitbar‘ von ‚Nummerierung‘")
    s.banner("V-09", f"Variante {variant}", rule)
    s.rect(24, 82, 892, 40, stroke=INK, sw=1.4)
    s.text(36, 107, "STATUS (berechnet, Kandidat): Zyklus nachgewiesen — Zeuge Z1 a→d, Z2 d→b, Z3 b→a — Plan nicht abarbeitbar", 13, "bold")
    if variant == "A":
        pos, w, hh = POS_A, 180, 56
        for n, (x, y) in pos.items():
            s.node(x, y, w, hh, "⌹", n)
        lanes = {e: 250 + k * 48 for k, e in enumerate(EDGES)}
        for (a, b), ly in lanes.items():
            ax, bx = pos[a][0] + w / 2 + (EDGES.index((a, b)) % 3 - 1) * 14, pos[b][0] + w / 2 + (EDGES.index((a, b)) % 3 - 1) * 14
            style = "double" if (a, b) in CYCLE else "solid"
            sw = 1.4
            if style == "double":
                for off in (-2.6, 2.6):
                    s.line(ax + off, 206, ax + off, ly, sw=sw); s.line(ax + off, ly + off, bx + off, ly + off, sw=sw); s.line(bx + off, ly, bx + off, 214, sw=sw)
            else:
                s.line(ax, 206, ax, ly, sw=sw); s.line(ax, ly, bx, ly, sw=sw); s.line(bx, ly, bx, 214, sw=sw)
            s.add(f'<path d="M{bx:.1f},{206} L{bx - 6:.1f},{218} L{bx + 6:.1f},{218} Z" fill="{INK}"/>')
            lab = f"e{EDGES.index((a, b)) + 1}" + (f" · {CYCLE[(a, b)]}" if (a, b) in CYCLE else "")
            s.label(min(ax, bx) + 22, ly - 8, lab, 11, "bold" if (a, b) in CYCLE else "normal")
        ly0 = 500
    else:
        pos, w, hh = POS_B, 170, 56
        for n, (x, y) in pos.items():
            s.node(x, y, w, hh, "⌹", n)
        def center(n):
            x, y = pos[n]; return x + w / 2, y + hh / 2
        labels = []
        for (a, b) in EDGES:
            (x1, y1), (x2, y2) = center(a), center(b)
            cyc = (a, b) in CYCLE
            sx1, sy1 = clip(x1, y1, w, hh, x2, y2); sx2, sy2 = clip(x2, y2, w, hh, x1, y1, pad=6)
            s.arrow(sx1, sy1, sx2, sy2, "double" if cyc else "solid", sw=1.4)
            t = 0.38 if (a, b) == ("wi:c", "wi:a") else 0.5
            mx, my = sx1 + (sx2 - sx1) * t, sy1 + (sy2 - sy1) * t
            labels.append((mx + 10, my - 10, f"e{EDGES.index((a, b)) + 1}" + (f" · {CYCLE[(a, b)]}" if cyc else ""), cyc))
        for x, y, lab, cyc in labels:
            s.label(x, y, lab, 11, "bold" if cyc else "normal")
        s.text(36, 540, "Nicht gemeint: ‚falsch nummeriert‘ — die Darstellung hängt von keiner Knotennummerierung ab.", 12, italic=True, fill=MUTED)
        ly0 = 570
    s.text(32, ly0, "LEGENDE · Kandidat, kein Urteil", 13, "bold")
    s.line(32, ly0 + 20, 92, ly0 + 20); s.text(104, ly0 + 24, "einfach = Abhängigkeit (X requires Y, Pfeil zu Y)", 12)
    s.line(32, ly0 + 38, 92, ly0 + 38); s.line(32, ly0 + 43, 92, ly0 + 43); s.text(104, ly0 + 44, "doppelt + Z-Nummer = Kante des berechneten Zeugenzyklus (analyze.cycle-gate, Kandidat)", 12)
    s.footer("Setzt eine berechnete Zyklusprüfung voraus (Lücke G-05). Farbfrei: Linienart und Beschriftung. Fall DAG-03 / DAG-01.")
    return s.render()


def v12():
    s = Svg(940, 560, "MOCKUP V-12")
    s.banner("V-12", "Variante A", "Kandidat: Instanz als benannte Grenze; instanzübergreifende Kante schraffiert markiert und benannt (keine Statusfarbe)")
    bands = [("bpmn:i1", 92, ["bpmn:i1/tok-stock", "bpmn:i1/tok-credit"]), ("bpmn:i2", 300, ["bpmn:i2/tok-credit"])]
    for inst, y, toks in bands:
        s.rect(24, y, 892, 170, stroke=INK, sw=1.4, dash="10 5", rx=10)
        s.text(40, y + 24, f"⬠  Instanz {inst}", 14, "bold")
        for k, t in enumerate(toks):
            s.node(48, y + 36 + k * 66, 210, 56, "⌼", t.split('/')[-1], t)
    s.rect(560, 142, 150, 56, stroke=INK, sw=1.6, rx=4)
    s.text(635, 166, "Join (AND)", 13, "bold", anchor="middle")
    s.text(635, 184, "bpmn:join · i1", 10, fill=MUTED, anchor="middle")
    s.node(760, 142, 140, 56, "⌼", "ship", "Aktivität")
    s.arrow(258, 156, 560, 162, "solid", shorten=0)
    s.arrow(258, 222, 560, 180, "solid", shorten=0)
    s.arrow(710, 170, 760, 170, "solid", shorten=0)
    # cross-instance edge from i2/tok-credit to the i1 join
    s.arrow(258, 364, 610, 198, "dashed", shorten=0)
    s.rect(390, 262, 150, 40, stroke=INK, sw=1.2, fill="#ffffff")
    s.hatch(390, 262, 150, 40, gap=7, stroke="#6b7280")
    s.rect(402, 270, 126, 24, stroke=INK, sw=0.8, fill="#ffffff")
    s.text(465, 287, "instanzübergreifend", 11, "bold", anchor="middle")
    s.text(32, 500, "LEGENDE · Kandidat, kein Urteil  —  Grenze ⬠ = Instanzzugehörigkeit · durchgezogen = Eingang aus derselben Instanz · "
                    "gestrichelt + schraffierte Marke = Eingang aus fremder Instanz", 11)
    s.footer("Setzt eine typisierte Instanzbindung voraus (Lücke G-08). Schraffur nach VP-07 PV-5 (Linien, kein Muster). Fall BPMN-03.")
    return s.render()


POS_C = {"wi:a": (380, 186), "wi:b": (120, 346), "wi:d": (640, 346), "wi:c": (380, 506)}


def v09c():
    s = Svg(940, 780, "MOCKUP V-09 C")
    s.banner("V-09", "Variante C", "Kandidat (korrigiert nach TASK-022): Zyklenkomponente markieren; jede Kante auf einem Zyklus doppelt; Zeuge nur als Beispiel")
    s.rect(24, 82, 892, 58, stroke=INK, sw=1.4)
    s.text(36, 104, "STATUS (berechnet, Kandidat): Plan nicht abarbeitbar · Zyklenkomponente K1 = {a, b, c, d} · 5 von 5 Kanten auf Zyklen", 13, "bold")
    s.text(36, 126, "Elementare Zyklen: a→d→b→a und a→d→c→a  ·  Beispielzeuge Z1 a→d, Z2 d→b, Z3 b→a", 12)
    s.rect(96, 158, 748, 428, stroke=INK, sw=1, rx=12)
    s.text(112, 180, "K1 · Zyklenkomponente (berechnet, Kandidat)", 12, "bold")
    pos, w, hh = POS_C, 170, 56
    for n, (x, y) in pos.items():
        s.node(x, y, w, hh, "⌹", n)
    def center(n):
        x, y = pos[n]; return x + w / 2, y + hh / 2
    labels = []
    for (a, b) in EDGES:
        (x1, y1), (x2, y2) = center(a), center(b)
        sx1, sy1 = clip(x1, y1, w, hh, x2, y2); sx2, sy2 = clip(x2, y2, w, hh, x1, y1, pad=6)
        s.arrow(sx1, sy1, sx2, sy2, "double", sw=1.4)
        t = 0.38 if (a, b) == ("wi:c", "wi:a") else 0.5
        mx, my = sx1 + (sx2 - sx1) * t, sy1 + (sy2 - sy1) * t
        wit = (a, b) in CYCLE
        labels.append((mx + 10, my - 10, f"e{EDGES.index((a, b)) + 1}" + (f" · {CYCLE[(a, b)]}" if wit else ""), wit))
    for x, y, lab, wit in labels:
        s.label(x, y, lab, 11, "bold" if wit else "normal")
    s.text(36, 612, "Nicht gemeint: ‚falsch nummeriert‘ — die Darstellung hängt von keiner Knotennummerierung ab.", 12, italic=True, fill=MUTED)
    ly0 = 640
    s.text(32, ly0, "LEGENDE · Kandidat, kein Urteil", 13, "bold")
    s.line(32, ly0 + 18, 92, ly0 + 18); s.line(32, ly0 + 23, 92, ly0 + 23)
    s.text(104, ly0 + 24, "doppelt = Kante liegt auf mindestens einem Zyklus (Teil von K1); Pfeil zu Y bei X requires Y", 12)
    s.text(104, ly0 + 44, "Z-Nummer = Kante des Beispielzeugen; weitere Zyklen nennt der Status", 12)
    s.line(32, ly0 + 60, 92, ly0 + 60); s.text(104, ly0 + 64, "einfach = Kante auf keinem Zyklus (in diesem Plan keine)", 12)
    s.text(104, ly0 + 84, "Rahmen K1 = starke Zusammenhangskomponente: jeder Knoten erreicht jeden anderen", 12)
    s.footer("Setzt eine berechnete Zyklusprüfung voraus (Lücke G-05). Farbfrei: Linienart, Rahmen und Beschriftung. Fall DAG-03 / DAG-01.")
    return s.render()


def v12b():
    s = Svg(940, 620, "MOCKUP V-12 B")
    s.banner("V-12", "Variante B", "Kandidat (korrigiert nach TASK-022): behauptete Paarung als eigene Aussage; Modellfluss von der Spur getrennt")
    for inst, y, h in (("bpmn:i1", 84, 200), ("bpmn:i2", 340, 100)):
        s.rect(24, y, 600, h, stroke=INK, sw=1.4, rx=10)
        s.text(40, y + 22, f"⬠  Instanz {inst} · Spur", 14, "bold")
    s.node(48, 116, 210, 56, "⌼", "tok-stock", "bpmn:i1/tok-stock")
    s.node(48, 196, 210, 56, "⌼", "tok-credit", "bpmn:i1/tok-credit")
    s.text(270, 228, "nicht Teil von J1", 11, fill=MUTED, italic=True)
    s.node(48, 372, 210, 56, "⌼", "tok-credit", "bpmn:i2/tok-credit")
    s.rect(404, 112, 200, 72, stroke=INK, sw=1.6, rx=4)
    s.text(504, 134, "Join (AND) · Aussage J1", 13, "bold", anchor="middle")
    s.text(504, 152, "Scope bpmn:i1", 10, fill=MUTED, anchor="middle")
    s.text(504, 170, "Eingänge: i1/tok-stock + i2/tok-credit", 9, fill=MUTED, anchor="middle")
    s.arrow(258, 144, 404, 144, "solid", shorten=0)
    s.arrow(258, 400, 470, 184, "dashed", shorten=0)
    s.rect(244, 294, 236, 36, stroke=INK, sw=1.2, fill="#ffffff")
    s.hatch(244, 294, 236, 36, gap=7, stroke="#6b7280")
    s.rect(256, 301, 212, 22, stroke=INK, sw=0.8, fill="#ffffff")
    s.text(362, 316, "instanzübergreifend · Regelverstoß", 11, "bold", anchor="middle")
    s.rect(650, 84, 266, 200, stroke=LINE, sw=1, rx=10)
    s.text(666, 106, "Prozessmodell · keine Spur", 13, "bold")
    s.node(676, 130, 214, 56, "⌼", "ship", "kein Token in der Spur")
    s.line(604, 148, 668, 152, sw=1)
    s.add(f'<path d="M676,152 L666,147 L666,157 Z" fill="{INK}"/>')
    s.text(666, 214, "Join → ship nur laut Modell;", 11, fill=MUTED)
    s.text(666, 230, "ein Start von ship ist nicht belegt.", 11, fill=MUTED)
    s.rect(24, 456, 892, 30, stroke=INK, sw=1)
    s.text(36, 476, "BEFUND (Kandidat): J1 paart bpmn:i1/tok-stock mit bpmn:i2/tok-credit → instanzübergreifend → Regelverstoß (Token je Instanz)", 12, "bold")
    s.text(32, 512, "LEGENDE · Kandidat, kein Urteil", 13, "bold")
    s.text(32, 532, "Durchgezogener Rahmen ⬠ = Instanz (Spur) · durchgezogener Pfeil = Eingang aus derselben Instanz", 12)
    s.text(32, 550, "gestrichelt + schraffierte Marke = Eingang aus fremder Instanz = Regelverstoß · dünner Pfeil rechts = Modellfluss, keine Ausführung", 12)
    s.footer("Setzt eine typisierte Instanzbindung voraus (Lücke G-08). Schraffur nach VP-07 PV-5 (Linien, kein Muster). Fall BPMN-03.")
    return s.render()


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    files = {"M-05A.svg": v05("A"), "M-05B.svg": v05("B"), "M-01A.svg": v01(),
             "M-09A.svg": v09("A"), "M-09B.svg": v09("B"), "M-12A.svg": v12(),
             "M-05C.svg": v05("C"), "M-09C.svg": v09c(), "M-12B.svg": v12b()}
    for name, svg in files.items():
        for bad in ("<pattern", "<use", "<image", "href", "<script"):
            assert bad not in svg, (name, bad)
        (out / name).write_text(svg, encoding="utf-8")
    print("written", sorted(files))


if __name__ == "__main__":
    main(sys.argv[1])
