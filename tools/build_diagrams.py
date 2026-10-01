"""
Construction-document recreations for the portfolio projects (assets/images/diagrams).

Client deliverables can't be published, so these recreate the *document types*
each project produced, drawn to real CAD/Revit conventions:

  * ANSI D sheet (34" x 22") with a vertical title block, zone numbers, revisions
  * black linework; architectural background in halftone grey, as on real E-sheets
  * Revit-style view titles, grid bubbles, room tags and keyed notes
  * standard one-line symbols (breakers, transformers, motors, ground)
  * the Revit "Branch Panel" schedule layout
  * the Navisworks HTML clash-report layout

Title blocks carry the standard NOT FOR CONSTRUCTION / ISSUED FOR REVIEW stamp.

Usage:  python tools/build_diagrams.py
"""
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images", "diagrams")

SW, SH = 2200, 1424          # ANSI D at ~64.7 px/in
DX0, DY0, DX1, DY1 = 46, 46, 1836, 1378   # drawing area inside the border
TB = 1850                   # title block left edge
K, GREY, LGREY, HALF = "#000000", "#6b6b6b", "#b5b5b5", "#9a9a9a"
RED, GREEN = "#d62020", "#1f9d3a"
ARIAL = "Arial, Helvetica, sans-serif"
NARROW = "'Arial Narrow', Arial, Helvetica, sans-serif"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------

def t(x, y, s, size=13, anchor="start", weight="normal", fill=K, font=ARIAL, rot=None, italic=False):
    tr = f' transform="rotate({rot} {x} {y})"' if rot is not None else ""
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{fill}"{st}{tr}>{esc(s)}</text>')


def ln(x1, y1, x2, y2, w=1, c=K, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}"{d}/>'


def pl(pts, w=1, c=K, fill="none", dash=None, close=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    tag = "polygon" if close else "polyline"
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<{tag} points="{p}" fill="{fill}" stroke="{c}" stroke-width="{w}"{d}/>'


def rc(x, y, w, h, sw=1, c=K, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{c}" stroke-width="{sw}"{d}/>'


def ci(x, y, r, sw=1, c=K, fill="none"):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>'


def hexagon(x, y, r, label, size=12):
    pts = [(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    return pl(pts, 1.2, close=True, fill="#fff") + t(x, y + size * .36, label, size, "middle", "bold")


def tag_box(x, y, label, size=12, pad=6):
    w = len(label) * size * .62 + pad * 2
    return rc(x - w / 2, y - size * .9, w, size * 1.6, 1, fill="#fff") + t(x, y + size * .35, label, size, "middle", "bold", font=NARROW)


def hatch(x, y, w, h, gap=12, c=GREY, cid="h"):
    """Diagonal hatch clipped to a rectangle."""
    lines = []
    for k in range(-int(h), int(w) + 1, gap):
        lines.append(ln(x + k, y + h, x + k + h, y, .7, c))
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
            f'<g clip-path="url(#{cid})">{"".join(lines)}</g>')


def view_title(x, y, num, sheet, name, scale, width=420):
    """Revit view title: detail-number bubble, view name on a heavy line, scale below."""
    return (ci(x, y, 22, 1.6) + ln(x - 22, y, x + 22, y, 1) + t(x, y - 5, num, 14, "middle", "bold")
            + t(x, y + 16, sheet, 10, "middle") + ln(x + 22, y, x + 22 + width, y, 3)
            + t(x + 34, y - 8, name.upper(), 18, weight="bold") + t(x + 34, y + 20, f"SCALE: {scale}", 12))


def grid(x, y, label, r=19, side="top"):
    return ci(x, y, r, 1.4, fill="#fff") + t(x, y + 6, label, 17, "middle", "bold")


def north(x, y):
    return (ci(x, y, 30, 1.2) + pl([(x, y - 44), (x + 12, y + 8), (x, y - 2), (x - 12, y + 8)], 1, close=True, fill=K)
            + t(x, y + 50, "PLAN NORTH", 10, "middle", "bold"))


def notes(x, y, title, items, width=380, size=12):
    s = t(x, y, title, 14, weight="bold") + ln(x, y + 6, x + width, y + 6, 1.5)
    yy = y + 30
    for i, it in enumerate(items):
        s += hexagon(x + 12, yy - 4, 11, str(i + 1), 10)
        words, line, lines = it.split(), "", []
        for w in words:
            if len(line) + len(w) > width / (size * .52):
                lines.append(line); line = w
            else:
                line = (line + " " + w).strip()
        lines.append(line)
        for k, l in enumerate(lines):
            s += t(x + 32, yy + k * (size + 4), l.upper(), size - 1, font=NARROW)
        yy += len(lines) * (size + 4) + 10
    return s


# --------------------------------------------------------------------------
# sheet + document frames
# --------------------------------------------------------------------------

def sheet(number, title, project, body, scale="AS NOTED", date="2025-06-12"):
    zones_x = 8
    zones_y = 6
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SW}" height="{SH}" viewBox="0 0 {SW} {SH}">',
         f'<title>{esc(number)} {esc(title)}</title>', rc(0, 0, SW, SH, 0, fill="#fff"),
         rc(18, 18, SW - 36, SH - 36, 1), rc(32, 32, SW - 64, SH - 64, 3)]
    for i in range(zones_x):
        x = 32 + (i + .5) * (TB - 32) / zones_x
        s += [t(x, 28, str(zones_x - i), 11, "middle"), t(x, SH - 21, str(zones_x - i), 11, "middle")]
        if i:
            xx = 32 + i * (TB - 32) / zones_x
            s += [ln(xx, 18, xx, 32), ln(xx, SH - 32, xx, SH - 18)]
    for j in range(zones_y):
        y = 32 + (j + .5) * (SH - 64) / zones_y
        s += [t(25, y + 4, "ABCDEF"[j], 11, "middle"), t(SW - 25, y + 4, "ABCDEF"[j], 11, "middle")]
    s.append(f"<g>{body}</g>")
    # vertical title block
    x0, x1 = TB, SW - 32
    w = x1 - x0
    s.append(ln(x0, 32, x0, SH - 32, 3))
    y = 32
    def row(h, inner=""):
        nonlocal y
        out = inner + ln(x0, y + h, x1, y + h, 1.5)
        y += h
        return out
    s.append(row(130, t(x0 + 20, y + 44, "HARRISON FARBER", 22, weight="bold") + t(x0 + 20, y + 68, "BIM DESIGNER / COORDINATOR", 13)
                 + t(x0 + 20, y + 92, "OVERLAND PARK, KANSAS", 12, fill=GREY) + t(x0 + 20, y + 112, "harrisonfarber38@gmail.com", 12, fill=GREY)))
    s.append(row(90, t(x0 + 20, y + 24, "CONSULTANT", 10, fill=GREY) + t(x0 + 20, y + 52, "ELECTRICAL BIM", 15, weight="bold") + t(x0 + 20, y + 74, "REVIT  ·  NAVISWORKS MANAGE", 12)))
    s.append(row(150, t(x0 + 20, y + 24, "PROJECT", 10, fill=GREY)
                 + "".join(t(x0 + 20, y + 54 + k * 24, l, 16, weight="bold") for k, l in enumerate(project))))
    # stamp
    s.append(row(170, rc(x0 + 20, y + 18, w - 40, 134, 2, RED) + t(x0 + w / 2, y + 60, "NOT FOR", 22, "middle", "bold", RED)
                 + t(x0 + w / 2, y + 88, "CONSTRUCTION", 22, "middle", "bold", RED)
                 + t(x0 + w / 2, y + 122, "ISSUED FOR REVIEW", 13, "middle", "bold", fill=RED)))
    # revisions
    rev = t(x0 + 20, y + 22, "REVISIONS", 10, fill=GREY)
    for k, (n, d, desc) in enumerate([("1", "2025-05-02", "COORDINATION ISSUE"), ("2", date, "ISSUED FOR REVIEW")]):
        yy = y + 46 + k * 24
        rev += pl([(x0 + 30, yy - 12), (x0 + 42, yy + 6), (x0 + 18, yy + 6)], 1, close=True) + t(x0 + 30, yy + 3, n, 10, "middle", "bold")
        rev += t(x0 + 56, yy + 2, d, 11) + t(x0 + 150, yy + 2, desc, 11)
    s.append(row(110, rev))
    # meta grid
    meta = [("DATE", date), ("SCALE", scale), ("DRAWN BY", "HF"), ("CHECKED BY", "HF"), ("PROJECT NO.", "25-014"), ("MODEL", "LOD 350")]
    m = ""
    for k, (a, b) in enumerate(meta):
        cx = x0 + (k % 2) * w / 2
        cy = y + (k // 2) * 54
        m += t(cx + 14, cy + 20, a, 10, fill=GREY) + t(cx + 14, cy + 42, b, 13, weight="bold")
        if k % 2 == 0:
            m += ln(x0 + w / 2, cy, x0 + w / 2, cy + 54)
        m += ln(x0, cy + 54, x1, cy + 54, .8)
    s.append(m); y += 162
    # sheet title + number at the bottom
    s.append(ln(x0, SH - 230, x1, SH - 230, 1.5))
    s.append(t(x0 + 20, SH - 204, "SHEET TITLE", 10, fill=GREY))
    tl = title.upper().split(" / ")
    s += [t(x0 + 20, SH - 174 + k * 24, l, 16, weight="bold") for k, l in enumerate(tl)]
    s.append(ln(x0, SH - 120, x1, SH - 120, 1.5))
    s.append(t(x0 + 20, SH - 96, "SHEET NUMBER", 10, fill=GREY))
    s.append(t(x0 + w / 2, SH - 46, number, 52, "middle", "bold"))
    s.append("</svg>")
    return "\n".join(s)


def document(title, subtitle, body, w=1700, h=1100, footer=""):
    """Plain report page (Navisworks / QA / standards documents)."""
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
         f'<title>{esc(title)}</title>', rc(0, 0, w, h, 0, fill="#fff"),
         t(60, 74, title, 30, weight="bold"), t(60, 104, subtitle, 15, fill=GREY), ln(60, 122, w - 60, 122, 1.5, LGREY),
         body,
         ln(60, h - 56, w - 60, h - 56, 1, LGREY),
         t(60, h - 30, footer or "Page 1 of 1", 12, fill=GREY),
         t(w - 60, h - 30, "Harrison Farber · BIM Designer / Coordinator", 12, "end", fill=GREY), "</svg>"]
    return "\n".join(s)


def table(x, y, cols, rows, rh=30, head_fill="#e6e6e6", size=13, bold_first=False, zebra=False):
    """cols: [(title, width, align)]"""
    s = []
    total = sum(c[1] for c in cols)
    s.append(rc(x, y, total, rh, 1, fill=head_fill))
    cx = x
    for title, w, al in cols:
        s.append(t(cx + (w / 2 if al == "middle" else (w - 8 if al == "end" else 8)), y + rh * .66, title, size - 1, al, "bold", font=NARROW))
        cx += w
    for r, row in enumerate(rows):
        yy = y + rh * (r + 1)
        s.append(rc(x, yy, total, rh, .8, fill="#f4f4f4" if zebra and r % 2 else "#fff"))
        cx = x
        for k, ((title, w, al), cell) in enumerate(zip(cols, row)):
            fill = K
            if isinstance(cell, tuple):
                cell, fill = cell
            s.append(t(cx + (w / 2 if al == "middle" else (w - 8 if al == "end" else 8)), yy + rh * .66, cell, size, al,
                       "bold" if bold_first and k == 0 else "normal", fill, NARROW))
            cx += w
    cx = x
    for _, w, _ in cols[:-1]:
        cx += w
        s.append(ln(cx, y, cx, y + rh * (len(rows) + 1), .8))
    return "".join(s)


# --------------------------------------------------------------------------
# shared plan background: production building (industrial project)
# --------------------------------------------------------------------------

def bay_grid(x0, y0, nx, ny, bx, by, labels_x="12345678", labels_y="ABCDEF", beams=True):
    s = []
    xs = [x0 + i * bx for i in range(nx)]
    ys = [y0 + j * by for j in range(ny)]
    for i, x in enumerate(xs):
        s.append(ln(x, y0 - 60, x, ys[-1] + 40, .8, GREY, "28 6 4 6"))
        s.append(grid(x, y0 - 80, labels_x[i]))
    for j, y in enumerate(ys):
        s.append(ln(x0 - 60, y, xs[-1] + 40, y, .8, GREY, "28 6 4 6"))
        s.append(grid(x0 - 80, y, labels_y[j]))
    for x in xs:
        for y in ys:
            s.append(rc(x - 7, y - 7, 14, 14, 1, HALF, "#cfcfcf"))
    if beams:
        for y in ys:
            s.append(ln(xs[0], y - 4, xs[-1], y - 4, .6, HALF) + ln(xs[0], y + 4, xs[-1], y + 4, .6, HALF))
    # dimension string along the top
    for i in range(nx - 1):
        a, b = xs[i], xs[i + 1]
        s.append(ln(a, y0 - 130, b, y0 - 130, .8) + ln(a, y0 - 138, a, y0 - 122, .8) + ln(b, y0 - 138, b, y0 - 122, .8))
        s.append(ln(a - 5, y0 - 125, a + 5, y0 - 135, 1.2) + ln(b - 5, y0 - 125, b + 5, y0 - 135, 1.2))
        s.append(t((a + b) / 2, y0 - 136, "30'-0\"", 12, "middle"))
    return "".join(s), xs, ys


def tray(points, width=22, label=None, lpos=None, c=K):
    """Ladder cable tray: double line with rungs."""
    s = []
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        nx, ny = -uy * width / 2, ux * width / 2
        s.append(ln(x1 + nx, y1 + ny, x2 + nx, y2 + ny, 1.6, c) + ln(x1 - nx, y1 - ny, x2 - nx, y2 - ny, 1.6, c))
        k = 0.0
        while k < L:
            px, py = x1 + ux * k, y1 + uy * k
            s.append(ln(px + nx, py + ny, px - nx, py - ny, .6, c))
            k += 14
    for (x, y) in points[1:-1]:
        s.append(rc(x - width / 2, y - width / 2, width, width, 1.6, c, "#fff"))
    if label:
        s.append(label if lpos is None else "")
    return "".join(s)


# --------------------------------------------------------------------------
# INDUSTRIAL FACILITY
# --------------------------------------------------------------------------

PROJ_IND = ["LIGHT-INDUSTRIAL", "PRODUCTION FACILITY", "ELECTRICAL DISTRIBUTION"]


def breaker(x, y, label, vertical=True, side="right"):
    s = rc(x - 10, y - 10, 20, 20, 1.6, fill="#fff")
    if label:
        s += t(x + 18 if side == "right" else x - 18, y + 5, label, 12, "start" if side == "right" else "end", font=NARROW)
    return s


def xfmr(x, y, r=26):
    return ci(x, y - r * .6, r, 1.6, fill="#fff") + ci(x, y + r * .6, r, 1.6, fill="none")


def ground(x, y):
    return ln(x, y, x, y + 14, 1.2) + ln(x - 14, y + 14, x + 14, y + 14, 1.4) + ln(x - 9, y + 20, x + 9, y + 20, 1.4) + ln(x - 4, y + 26, x + 4, y + 26, 1.4)


def motor(x, y, label):
    return ci(x, y, 20, 1.6, fill="#fff") + t(x, y + 6, "M", 16, "middle", "bold") + t(x + 30, y + 5, label, 12, font=NARROW)


def one_line():
    b = []
    b.append(view_title(90, 1300, "1", "E-601", "Power distribution one-line diagram", "NTS", 560))
    # utility
    ux = 860
    b.append(t(ux, 96, "UTILITY 13.2KV PRIMARY", 13, "middle", "bold"))
    b.append(ln(ux, 104, ux, 130, 1.6) + xfmr(ux, 166) + t(ux + 44, 160, "UTILITY XFMR (BY UTILITY CO.)", 12, font=NARROW)
             + t(ux + 44, 178, "2500 KVA, 13.2KV - 480Y/277V", 12, font=NARROW))
    b.append(ln(ux, 208, ux, 250, 1.6) + rc(ux - 16, 250, 32, 32, 1.6, fill="#fff") + t(ux, 272, "M", 14, "middle", "bold")
             + t(ux + 26, 272, "CT/PT UTILITY METERING", 12, font=NARROW))
    b.append(ln(ux, 282, ux, 318, 1.6) + breaker(ux, 330, "3000A/3P MAIN, LSIG"))
    # switchboard bus
    bx0, bx1, by = 220, 1540, 390
    b.append(ln(ux, 340, ux, by, 1.6))
    b.append(ln(bx0, by, bx1, by, 6))
    b.append(t(bx0, by - 16, "MSB  ·  MAIN SWITCHBOARD  ·  3000A, 480Y/277V, 3Ø, 4W, 65KAIC", 14, weight="bold"))
    b.append(ln(ux + 80, by, ux + 80, by + 40, 1.2) + ground(ux + 80, by + 40) + t(ux + 80, by + 92, "GROUND ELECTRODE SYSTEM", 11, "middle", font=NARROW))
    feeders = [
        (280, "800A/3P", "(2) SETS 4#350KCMIL, 1#1/0G, 3\"C", "MCC-1", "mcc"),
        (760, "250A/3P", "4#250KCMIL, 1#4G, 2-1/2\"C", "T-1", "xf150"),
        (1120, "125A/3P", "4#1/0, 1#6G, 2\"C", "T-2", "xf75"),
        (1460, "400A/3P", "4#600KCMIL, 1#3G, 3-1/2\"C", "DP-1", "dp"),
    ]
    for x, brk, cable, name, kind in feeders:
        b.append(ln(x, by, x, by + 50, 1.6) + breaker(x, by + 62, brk))
        b.append(ln(x, by + 72, x, by + 230, 1.6))
        b.append(t(x - 12, by + 200, cable, 11, "start", font=NARROW, rot=-90))
        if kind == "mcc":
            b.append(rc(x - 90, by + 230, 180, 300, 1.6, fill="#fff") + t(x, by + 256, "MCC-1", 15, "middle", "bold")
                     + t(x, by + 274, "800A, 480V, 3Ø, 65KAIC", 11, "middle", font=NARROW) + ln(x - 90, by + 284, x + 90, by + 284, 1))
            for k, (hp, nm, sz) in enumerate([("40HP", "CONVEYOR LINE 1", "SIZE 3"), ("50HP", "AIR COMPRESSOR AC-1", "SIZE 4"), ("15HP", "EXHAUST FAN EF-3", "SIZE 2"), ("25HP", "PROCESS PUMP P-2", "SIZE 3")]):
                yy = by + 310 + k * 54
                b.append(rc(x - 76, yy - 16, 60, 32, 1) + t(x - 46, yy + 5, sz, 10, "middle", font=NARROW))
                b.append(ln(x - 16, yy, x + 120, yy, 1.2) + motor(x + 140, yy, f"{hp} · {nm}"))
        elif kind.startswith("xf"):
            kva, lp, lpd = ("150", "LP-1", "400A MLO, 208Y/120V") if kind == "xf150" else ("75", "RP-1", "225A MLO, 208Y/120V")
            b.append(xfmr(x, by + 264))
            b.append(t(x + 40, by + 250, f"{name}  {kva} KVA", 13, weight="bold", font=NARROW) + t(x + 40, by + 268, "480V Δ - 208Y/120V, K-13", 11, font=NARROW))
            b.append(ln(x, by + 300, x, by + 330, 1.2) + ground(x + 24, by + 290))
            b.append(ln(x, by + 330, x, by + 380, 1.6) + breaker(x, by + 392, "MCB"))
            b.append(ln(x, by + 402, x, by + 440, 1.6) + rc(x - 70, by + 440, 140, 60, 1.6, fill="#fff")
                     + t(x, by + 466, lp, 15, "middle", "bold") + t(x, by + 486, lpd, 11, "middle", font=NARROW))
        else:
            b.append(rc(x - 90, by + 230, 180, 70, 1.6, fill="#fff") + t(x, by + 258, "DP-1", 15, "middle", "bold") + t(x, by + 280, "400A MCB, 480Y/277V", 11, "middle", font=NARROW))
            for k, (nm, a) in enumerate([("PP-1", "225A"), ("LH-1", "100A"), ("SPARE", "")]):
                xx = x - 60 + k * 60
                b.append(ln(xx, by + 300, xx, by + 360, 1.2) + breaker(xx, by + 330, None))
                if nm != "SPARE":
                    b.append(rc(xx - 26, by + 360, 52, 40, 1.2, fill="#fff") + t(xx, by + 385, nm, 11, "middle", "bold"))
                    b.append(t(xx, by + 416, a, 10, "middle", font=NARROW))
                else:
                    b.append(t(xx, by + 380, "SPARE", 10, "middle", font=NARROW))
    b.append(notes(1180, 980, "KEYED NOTES", [
        "Equipment shown is modeled as Revit electrical equipment families with nameplate data in type parameters.",
        "Feeder sizes per load calculation; conductor and conduit sizes scheduled from the model.",
        "Provide arc-flash labels on MSB, MCC-1 and DP-1 per NFPA 70E.",
        "Bond transformer secondaries to the building grounding electrode system.",
    ], 560))
    return sheet("E-601", "Electrical / One-line diagram", PROJ_IND, "".join(b), "NTS")


def tray_plan():
    b = []
    g, xs, ys = bay_grid(250, 300, 6, 4, 280, 260)
    b.append(g)
    # exterior walls (halftone architectural background)
    b.append(rc(xs[0] - 20, ys[0] - 20, xs[-1] - xs[0] + 40, ys[-1] - ys[0] + 40, 6, HALF))
    # electrical room
    er = (xs[0] - 20, ys[0] - 20, 250, 220)
    b.append(rc(*er, 3, HALF) + t(er[0] + 125, er[1] + 120, "ELEC 101", 14, "middle", "bold", HALF))
    # process piping (halftone, other trade)
    b.append(ln(xs[0], ys[2] - 60, xs[-1], ys[2] - 60, 7, "#cfcfcf") + t(xs[-1] - 10, ys[2] - 74, "PROCESS WATER (BY OTHERS)", 11, "end", fill=HALF))
    # tray routing
    route = [(xs[0] + 200, ys[0] + 120), (xs[3] + 140, ys[0] + 120), (xs[3] + 140, ys[2] + 130), (xs[5] - 120, ys[2] + 130)]
    b.append(tray(route, 24))
    b.append(tray([(xs[1] + 140, ys[0] + 120), (xs[1] + 140, ys[3] - 40)], 18))
    # equipment
    for (x, y, w, h, n) in [(xs[5] - 120, ys[2] + 90, 120, 80, "MCC-1"), (xs[1] + 100, ys[3] - 40, 80, 50, "PP-1"), (xs[0] + 40, ys[0] + 20, 140, 60, "MSB")]:
        b.append(rc(x, y, w, h, 2, fill="#fff") + hatch(x, y, w, h, 10, GREY, "eq" + n) + t(x + w / 2, y + h / 2 + 5, n, 13, "middle", "bold"))
    # conduit drops to machines
    for k, x in enumerate([xs[2] + 40, xs[2] + 200, xs[4] - 60]):
        b.append(ln(x, ys[2] + 142, x, ys[3] - 20, 1.4, dash="10 5") + ci(x, ys[3] - 12, 8, 1.4, fill="#fff"))
        b.append(t(x + 12, ys[3] + 18, ["CONV-1", "AC-1", "P-2"][k], 11, font=NARROW))
    # tray tags
    b.append(tag_box(xs[2], ys[0] + 84, "CT-1  24\"W x 6\"D LADDER  BOT @ 14'-0\" AFF", 12))
    b.append(tag_box(xs[3] + 300, ys[1] + 60, "CT-1  OFFSET DN  BOT @ 12'-6\" AFF", 12))
    b.append(tag_box(xs[1] + 260, ys[2] + 30, "CT-2  18\"W  BOT @ 14'-0\" AFF", 12))
    # keyed note hexes
    for (x, y, n) in [(xs[3] + 170, ys[2] - 40, "1"), (xs[2] + 20, ys[0] + 160, "2"), (xs[5] - 60, ys[2] + 70, "3")]:
        b.append(hexagon(x, y, 14, n, 12))
    b.append(north(1760, 1180))
    b.append(view_title(90, 1300, "1", "E-201", "Level 1 - cable tray & power plan", "1/16\" = 1'-0\"", 560))
    b.append(notes(720, 1140, "KEYED NOTES", [
        "Tray offsets down to clear 6\" process water main; coordinated in Navisworks, clash group CT-PW resolved.",
        "Trapeze hangers at 8'-0\" O.C. maximum, attached to bar joists - not to piping supports.",
        "Maintain 12\" clear above tray for cable pulling and 36\" clear access on one side.",
    ], 600))
    return sheet("E-201", "Level 1 / Cable tray & power plan", PROJ_IND, "".join(b), "1/16\" = 1'-0\"")


def elec_room():
    b = []
    x0, y0, W, H = 260, 220, 1120, 760     # room interior, 1/4" scale ~ 16px/ft
    b.append(rc(x0 - 14, y0 - 14, W + 28, H + 28, 14, "#7d7d7d", "#7d7d7d") + rc(x0, y0, W, H, 0, fill="#fff"))
    # door (6'-0" pair) bottom wall
    dx = x0 + W - 260
    b.append(rc(dx, y0 + H - 2, 192, 18, 0, fill="#fff"))
    b.append(ln(dx, y0 + H, dx, y0 + H - 96, 1.4) + f'<path d="M{dx} {y0 + H - 96} A96 96 0 0 1 {dx + 96} {y0 + H}" fill="none" stroke="{K}" stroke-width=".8"/>')
    b.append(ln(dx + 192, y0 + H, dx + 192, y0 + H - 96, 1.4) + f'<path d="M{dx + 192} {y0 + H - 96} A96 96 0 0 0 {dx + 96} {y0 + H}" fill="none" stroke="{K}" stroke-width=".8"/>')
    b.append(t(dx + 96, y0 + H + 50, "PAIR 3'-0\" DOORS, PANIC HARDWARE (NEC 110.26(C)(3))", 11, "middle", font=NARROW))
    eq = [  # x, y, w, h, name, clearance depth px (42" = 56px), label
        (x0 + 40, y0, 440, 64, "MSB", 56, "MAIN SWITCHBOARD 3000A"),
        (x0 + 560, y0, 220, 64, "MCC-1", 56, "MOTOR CONTROL CENTER"),
        (x0 + W - 100, y0 + 120, 100, 180, "T-1", 48, "150 KVA"),
        (x0 + W - 100, y0 + 360, 100, 140, "T-2", 48, "75 KVA"),
        (x0, y0 + 300, 30, 110, "DP-1", 56, ""),
        (x0, y0 + 460, 24, 80, "LP-1", 48, ""),
        (x0, y0 + 580, 24, 80, "RP-1", 48, ""),
    ]
    for (x, y, w, h, n, dep, lab) in eq:
        b.append(rc(x, y, w, h, 2.2, fill="#fff"))
        # working space in front (NEC 110.26 depth, min 30" width)
        if y == y0:
            zx, zy, zw, zh = x, y + h, max(w, 40), dep
        elif x >= x0 + W - 110:
            zx, zy, zw, zh = x - dep, y, dep, max(h, 40)
        else:
            zx, zy, zw, zh = x + w, y - 4, dep, max(h + 8, 40)
        b.append(rc(zx, zy, zw, zh, 1, K, "none", "6 4") + hatch(zx, zy, zw, zh, 9, LGREY, "ws" + n))
        cx, cy = x + w / 2, y + h / 2
        if w > 60:
            b.append(t(cx, cy - 2, n, 15, "middle", "bold") + t(cx, cy + 16, lab, 10, "middle", font=NARROW))
        else:
            b.append(t(x + w + dep + 10, cy + 5, n, 13, "start", "bold"))
    # dimensions for clearances
    def dim_v(x, ya, yb, label):
        return (ln(x, ya, x, yb, .8) + ln(x - 6, ya, x + 6, ya, .8) + ln(x - 6, yb, x + 6, yb, .8)
                + ln(x - 5, ya + 5, x + 5, ya - 5, 1.3) + ln(x - 5, yb + 5, x + 5, yb - 5, 1.3)
                + t(x - 8, (ya + yb) / 2, label, 11, "middle", rot=-90))
    b.append(dim_v(x0 + 500, y0 + 64, y0 + 120, "3'-6\" MIN"))
    b.append(dim_v(x0 + 800, y0 + 64, y0 + 120, "3'-6\" MIN"))
    b.append(t(x0 + W - 160, y0 + 320, "3'-0\" MIN", 11, "middle", font=NARROW))
    # housekeeping pad note + cable tray entry
    b.append(tray([(x0 + 260, y0 - 14), (x0 + 260, y0 - 120)], 24))
    b.append(tag_box(x0 + 420, y0 - 90, "CT-1 ENTRY  BOT @ 14'-0\" AFF", 11))
    b.append(t(x0 + W / 2 - 120, y0 + H / 2 + 40, "ELEC 101", 20, "middle", "bold", HALF))
    # legend
    lx, ly = 1440, 260
    b.append(t(lx, ly, "LEGEND", 14, weight="bold") + ln(lx, ly + 6, lx + 340, ly + 6, 1.5))
    b.append(rc(lx, ly + 24, 50, 30, 1, K, "none", "6 4") + hatch(lx, ly + 24, 50, 30, 9, LGREY, "lg1") + t(lx + 64, ly + 44, "NEC 110.26 WORKING SPACE", 12, font=NARROW))
    b.append(rc(lx, ly + 70, 50, 30, 2.2, fill="#fff") + t(lx + 64, ly + 90, "ELECTRICAL EQUIPMENT (MODELED)", 12, font=NARROW))
    b.append(notes(1440, 420, "KEYED NOTES", [
        "Working space depth per NEC 110.26(A)(1), Condition 2 at 480V: 3'-6\". 208V equipment: 3'-0\".",
        "Working space modeled as a clearance solid in each equipment family so Navisworks flags intrusions.",
        "Width of working space not less than 30\" or the width of the equipment.",
        "4\" concrete housekeeping pads under MSB, MCC-1 and transformers.",
    ], 360))
    b.append(view_title(90, 1300, "1", "E-401", "Enlarged electrical room plan", "1/4\" = 1'-0\"", 520))
    return sheet("E-401", "Enlarged plans / Electrical room 101", PROJ_IND, "".join(b), "1/4\" = 1'-0\"")


def iso(x, y, z, ox=900, oy=760, s=1.0):
    c = math.cos(math.radians(30))
    return ox + (x - y) * c * s, oy + (x + y) * .5 * s - z * s


def tray3d():
    """Revit-style 3D coordination view: beams, joists, pipe, tray with trapeze hangers."""
    b = []
    def box3(x, y, z, dx, dy, dz, fill_top, fill_l, fill_r, sw=1):
        P = lambda a, b_, c: iso(a, b_, c)
        top = [P(x, y, z + dz), P(x + dx, y, z + dz), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
        left = [P(x, y + dy, z), P(x + dx, y + dy, z), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
        right = [P(x + dx, y, z), P(x + dx, y + dy, z), P(x + dx, y + dy, z + dz), P(x + dx, y, z + dz)]
        return pl(top, sw, K, fill_top, close=True) + pl(left, sw, K, fill_l, close=True) + pl(right, sw, K, fill_r, close=True)
    # steel beams along x at two y lines (top at z=400)
    for yb in (-40, 420):
        b.append(box3(-320, yb, 340, 1040, 18, 60, "#d9d9d9", "#bdbdbd", "#a8a8a8"))
    # joists along y
    for xj in range(-280, 700, 120):
        b.append(box3(xj, -40, 400, 8, 478, 26, "#e4e4e4", "#c8c8c8", "#b4b4b4", .6))
    # process pipe (cylinder approximated by a box, cyan-grey)
    b.append(box3(-320, 150, 250, 1040, 26, 26, "#cfe3ea", "#a9c8d3", "#8fb4c1"))
    # cable tray with offset down under the pipe
    def tray_seg(x, y, z, dx, dy):
        out = box3(x, y, z, dx, dy, 4, "#f2f2f2", "#d8d8d8", "#c4c4c4", .8)
        out += box3(x, y, z, dx, 3, 14, "#bfbfbf", "#a6a6a6", "#999", .8) + box3(x, y + dy - 3, z, dx, 3, 14, "#bfbfbf", "#a6a6a6", "#999", .8)
        return out
    b.append(tray_seg(-300, 60, 300, 380, 60))
    b.append(tray_seg(80, 60, 210, 60, 60))        # dropped section under the pipe
    b.append(tray_seg(140, 60, 300, 520, 60))
    for xh in (-240, -60, 110, 300, 500):
        z = 210 if 80 <= xh <= 140 else 300
        for yy in (50, 130):
            a, c = iso(xh, yy, z), iso(xh, yy, 400)
            b.append(ln(a[0], a[1], c[0], c[1], 1.2))
        a, c = iso(xh, 50, z - 4), iso(xh, 130, z - 4)
        b.append(ln(a[0], a[1], c[0], c[1], 3))
    # conduits
    for k in range(3):
        a, c = iso(-300, 300 + k * 12, 330), iso(720, 300 + k * 12, 330)
        b.append(ln(a[0], a[1], c[0], c[1], 3, "#555"))
    # callouts
    def call(px, py, pz, tx, ty, txt):
        a = iso(px, py, pz)
        return ln(a[0], a[1], tx, ty, .8) + ci(a[0], a[1], 3, 1, fill=K) + t(tx + (6 if tx > a[0] else -6), ty + 4, txt, 13, "start" if tx > a[0] else "end", font=NARROW)
    b.append(call(110, 90, 214, 1300, 940, "CT-1 OFFSET DOWN 1'-6\" UNDER PROCESS WATER (CLASH CT-PW-07 RESOLVED)"))
    b.append(call(-200, 160, 276, 300, 520, "6\" PROCESS WATER (BY OTHERS)"))
    b.append(call(300, 50, 350, 1320, 560, "TRAPEZE HANGER, 1/2\" ALL-THREAD, 8'-0\" O.C."))
    b.append(call(600, -30, 400, 1340, 420, "W16x31 STEEL BEAM, TOS +17'-0\""))
    b.append(call(-100, 312, 330, 260, 1010, "(3) 2\" EMT FEEDERS TO MCC-1"))
    b.append(view_title(90, 1300, "1", "E-701", "3D view - cable tray coordination", "NTS", 560))
    return sheet("E-701", "3D views / Cable tray coordination", PROJ_IND, "".join(b), "NTS")


def clash_report():
    """Navisworks Manage clash report (HTML tabular layout)."""
    w, h = 1700, 1100
    b = []
    b.append(t(60, 160, "Test: CT-TRAY vs STRUCT + PIPING", 18, weight="bold"))
    b.append(t(60, 186, "Tolerance: 0.000 ft  ·  Type: Hard  ·  Status: OK  ·  Clashes: 23", 14, fill=GREY))
    b.append(table(60, 210, [("Clashes", 180, "middle"), ("New", 120, "middle"), ("Active", 120, "middle"), ("Reviewed", 120, "middle"),
                             ("Approved", 120, "middle"), ("Resolved", 120, "middle"), ("Type", 140, "middle"), ("Status", 140, "middle")],
                   [["23", "0", "0", "0", "0", (("23", GREEN)), "Hard", "OK"]], 32, size=14))
    cols = [("Image", 170, "middle"), ("Clash Name", 120, "start"), ("Status", 100, "start"), ("Distance", 100, "end"), ("Grid Location", 140, "start"),
            ("Description", 100, "start"), ("Date Found", 120, "start"), ("Item 1", 380, "start"), ("Item 2", 350, "start")]
    rows = [
        ("Clash1", "-0.417", "C-3 : Level 1", "Cable Tray : Ladder 24\" : Element ID 418822", "Structural Framing : W16X31 : Element ID 220871"),
        ("Clash2", "-0.250", "C-4 : Level 1", "Cable Tray : Ladder 24\" : Element ID 418836", "Pipe : Process Water 6\" : Element ID 305512"),
        ("Clash3", "-0.188", "B-4 : Level 1", "Conduit : EMT 2\" : Element ID 421106", "Structural Framing : 24K7 Joist : Element ID 221540"),
        ("Clash4", "-0.146", "D-5 : Level 1", "Cable Tray Fitting : Horizontal Bend : Element ID 418901", "Duct : Rectangular 30x18 : Element ID 337210"),
    ]
    y0 = 300
    total = sum(c[1] for c in cols)
    b.append(rc(60, y0, total, 34, 1, fill="#d9d9d9"))
    cx = 60
    for title, cw, al in cols:
        b.append(t(cx + 8 if al != "middle" else cx + cw / 2, y0 + 23, title, 13, "start" if al != "middle" else "middle", "bold", font=NARROW) if al != "end" else t(cx + cw - 8, y0 + 23, title, 13, "end", "bold", font=NARROW))
        cx += cw
    rh = 130
    for r, (nm, dist, grid_, i1, i2) in enumerate(rows):
        y = y0 + 34 + r * rh
        b.append(rc(60, y, total, rh, .8, fill="#fff"))
        # thumbnail: grey shaded view with red (item 1) and green (item 2)
        ix, iy = 68, y + 10
        b.append(rc(ix, iy, 154, 110, .8, fill="#3a3a3a"))
        g_ = [(10, 70, 150, 40, 18), (10, 30, 150, 80, 22), (40, 10, 70, 110, 14), (10, 55, 150, 55, 26)][r]
        r_ = [(30, 20, 120, 100), (20, 90, 140, 20), (10, 60, 150, 50), (60, 10, 90, 110)][r]
        b.append(f'<g transform="translate({ix} {iy})"><clipPath id="th{r}"><rect width="154" height="110"/></clipPath><g clip-path="url(#th{r})">'
                 f'<line x1="{g_[0]}" y1="{g_[1]}" x2="{g_[2]}" y2="{g_[3]}" stroke="{GREEN}" stroke-width="{g_[4]}"/>'
                 f'<line x1="{r_[0]}" y1="{r_[1]}" x2="{r_[2]}" y2="{r_[3]}" stroke="{RED}" stroke-width="12"/></g></g>')
        cx = 60 + 170
        cells = [nm, "Resolved", dist, grid_, "Hard", "2025/05/19"]
        for (title, cw, al), cell in zip(cols[1:7], cells):
            colr = GREEN if cell == "Resolved" else K
            if al == "end":
                b.append(t(cx + cw - 8, y + 40, cell, 13, "end", fill=colr, font=NARROW))
            else:
                b.append(t(cx + 8, y + 40, cell, 13, fill=colr, font=NARROW))
            cx += cw
        for k, (txt, cw) in enumerate(((i1, 380), (i2, 350))):
            parts = txt.split(" : ")
            lines = [("Element ID", parts[2].replace("Element ID ", "")), ("Layer", "Level 1"), ("Item Name", parts[1]), ("Item Type", parts[0])]
            for j, (a, v) in enumerate(lines):
                b.append(t(cx + 8, y + 30 + j * 22, f"{a}: ", 12, weight="bold", font=NARROW) + t(cx + 92, y + 30 + j * 22, v, 12, font=NARROW))
            cx += cw
        cx2 = 60
        for _, cw, _ in cols[:-1]:
            cx2 += cw
            b.append(ln(cx2, y, cx2, y + rh, .8))
    b.append(t(60, y0 + 34 + len(rows) * rh + 34, "Showing 4 of 23 clashes. All clashes grouped by grid location, assigned to the electrical model and re-tested after reroute.", 13, fill=GREY))
    return document("Clash Report", "Navisworks Manage  ·  Industrial facility federated model (ARCH + STRUCT + MECH + ELEC)  ·  Report date 2025/05/21", "".join(b), w, h,
                    "Navisworks Manage · Clash Detective · HTML (Tabular) report · Page 1 of 1")


# --------------------------------------------------------------------------
# COMMERCIAL OFFICE (Snowdon Towers sample)
# --------------------------------------------------------------------------

PROJ_OFF = ["COMMERCIAL OFFICE BUILDING", "SNOWDON TOWERS (SAMPLE)", "ELECTRICAL MODEL"]


def office_arch(x0=200, y0=200):
    """Halftone architectural background for level 3."""
    W_, H_ = 1340, 900
    s = [rc(x0, y0, W_, H_, 8, HALF)]
    walls = [  # interior partitions
        (x0, y0 + 360, x0 + 420, y0 + 360), (x0 + 420, y0, x0 + 420, y0 + 360),
        (x0 + 420, y0 + 520, x0 + 420, y0 + H_), (x0, y0 + 520, x0 + 420, y0 + 520),
        (x0 + 860, y0, x0 + 860, y0 + 280), (x0 + 1100, y0, x0 + 1100, y0 + 280), (x0 + 860, y0 + 280, x0 + W_, y0 + 280),
        (x0 + 1100, y0 + 660, x0 + W_, y0 + 660), (x0 + 1100, y0 + 660, x0 + 1100, y0 + H_),
    ]
    for a in walls:
        s.append(ln(*a, 4, HALF))
    # core: stair + elevator
    s.append(rc(x0 + 560, y0 + 380, 220, 200, 4, HALF) + "".join(ln(x0 + 560, y0 + 400 + k * 18, x0 + 670, y0 + 400 + k * 18, .6, LGREY) for k in range(9)))
    s.append(rc(x0 + 680, y0 + 400, 80, 80, 1.5, HALF) + ln(x0 + 680, y0 + 400, x0 + 760, y0 + 480, .8, HALF) + ln(x0 + 760, y0 + 400, x0 + 680, y0 + 480, .8, HALF))
    rooms = [(x0 + 210, y0 + 190, "CONFERENCE", "301"), (x0 + 210, y0 + 720, "COPY / WORK", "308"), (x0 + 640, y0 + 140, "OPEN OFFICE", "302"),
             (x0 + 980, y0 + 140, "OFFICE", "303"), (x0 + 1220, y0 + 140, "ELEC", "304"), (x0 + 870, y0 + 470, "OPEN OFFICE", "305"), (x0 + 1220, y0 + 780, "BREAK", "306")]
    for x, y, n, num in rooms:
        s.append(t(x, y, n, 13, "middle", "bold", HALF) + rc(x - 22, y + 8, 44, 22, 1, HALF) + t(x, y + 24, num, 12, "middle", fill=HALF))
    # column grid
    for i, x in enumerate([x0, x0 + 446, x0 + 893, x0 + W_]):
        s.append(ln(x, y0 - 70, x, y0 - 10, .8, GREY, "20 5 4 5") + grid(x, y0 - 90, str(i + 1)))
    for j, y in enumerate([y0, y0 + 450, y0 + H_]):
        s.append(ln(x0 - 70, y, x0 - 10, y, .8, GREY, "20 5 4 5") + grid(x0 - 90, y, "ABC"[j]))
    return "".join(s), (x0, y0, W_, H_)


def troffer(x, y, tag="A", ckt=None):
    s = rc(x - 26, y - 13, 52, 26, 1.6, fill="#fff") + ln(x - 26, y - 13, x + 26, y + 13, .6) + ln(x - 26, y + 13, x + 26, y - 13, .6)
    if ckt:
        s += t(x + 30, y - 14, f"{tag}", 11, weight="bold", font=NARROW) + t(x + 30, y - 2, str(ckt), 10, font=NARROW)
    return s


def homerun(x, y, label, dx=34, dy=-34):
    return (f'<path d="M{x} {y} q {dx * .6} {dy * .1} {dx} {dy}" fill="none" stroke="{K}" stroke-width="1.4"/>'
            + pl([(x + dx - 9, y + dy + 1), (x + dx + 2, y + dy - 2), (x + dx - 3, y + dy + 9)], 1.4, close=True, fill=K)
            + t(x + dx + 6, y + dy - 4, label, 12, weight="bold", font=NARROW))


def lighting_plan():
    arch, (x0, y0, W_, H_) = office_arch()
    b = [arch]
    # open office 302/305 fixtures, circuits 1 and 3
    for r, yy in enumerate(range(y0 + 330, y0 + H_ - 60, 120)):
        for c_, xx in enumerate(range(x0 + 480, x0 + 1060, 130)):
            if x0 + 540 < xx < x0 + 800 and y0 + 360 < yy < y0 + 600:
                continue
            ckt = 1 if r < 2 else 3
            b.append(troffer(xx, yy, "A", ckt))
            if c_:
                b.append(f'<path d="M{xx - 104} {yy} q 52 -18 78 0" fill="none" stroke="{K}" stroke-width="1"/>')
    b.append(homerun(x0 + 1040, y0 + 330, "LP-3A-1"))
    b.append(homerun(x0 + 1040, y0 + 570, "LP-3A-3"))
    # conference 301: downlights circuit 5
    for xx in range(x0 + 80, x0 + 400, 90):
        for yy in (y0 + 110, y0 + 270):
            b.append(ci(xx, yy, 13, 1.6, fill="#fff") + ci(xx, yy, 5, 1))
    b.append(t(x0 + 92, y0 + 92, "B  5", 11, weight="bold", font=NARROW) + homerun(x0 + 350, y0 + 110, "LP-3A-5", 30, -40))
    # private office 303
    for xx in (x0 + 940, x0 + 1020):
        b.append(troffer(xx, y0 + 220, "A", 7))
    b.append(homerun(x0 + 1046, y0 + 220, "LP-3A-7", 30, 30))
    # emergency fixtures (hatched)
    for xx, yy in [(x0 + 610, y0 + 330), (x0 + 870, y0 + 690)]:
        b.append(rc(xx - 26, yy - 13, 52, 26, 1.6, fill="#000"))
        b.append(t(xx + 30, yy - 14, "A-EM", 11, weight="bold", font=NARROW) + t(xx + 30, yy - 2, "9", 10, font=NARROW))
    # switches
    for xx, yy, l in [(x0 + 440, y0 + 380, "a"), (x0 + 400, y0 + 340, "$OS"), (x0 + 880, y0 + 250, "$")]:
        b.append(t(xx, yy, "$" if l == "a" else l, 18, "middle", "bold") + (t(xx + 10, yy + 6, "a", 11, font=NARROW) if l == "a" else ""))
    # panel
    b.append(rc(x0 + 1150, y0 + 230, 120, 26, 2, fill="#000") + t(x0 + 1210, y0 + 222, "LP-3A", 12, "middle", "bold"))
    # fixture schedule
    fx = 1560
    b.append(t(fx - 1340 + 1340, 0, "", 1))
    sched = [("A", "2x4 LED FLAT PANEL, 4000K, 40W, 120V", "LITHONIA CPX"), ("A-EM", "TYPE A WITH 90-MIN EMERGENCY DRIVER", "LITHONIA CPX EL"),
             ("B", "6\" LED DOWNLIGHT, 3000K, 18W", "GOTHAM EVO"), ("OS", "CEILING OCCUPANCY SENSOR, DUAL-TECH", "SENSOR SWITCH")]
    b.append(t(200, 1170, "LIGHT FIXTURE SCHEDULE", 14, weight="bold"))
    b.append(table(200, 1182, [("TYPE", 90, "middle"), ("DESCRIPTION", 400, "start"), ("BASIS OF DESIGN", 200, "start"), ("VOLTS", 80, "middle"), ("MOUNTING", 130, "start")],
                   [[a, d, m, "120", "RECESSED" if a != "OS" else "CEILING"] for a, d, m in sched], 28, size=12))
    b.append(notes(1180, 1170, "GENERAL NOTES", ["Fixtures circuited in the Revit model; circuit numbers shown are generated from the electrical circuit."], 520))
    b.append(north(1720, 210))
    b.append(view_title(1180, 1320, "1", "E-301", "Level 3 - lighting plan", "1/8\" = 1'-0\"", 460))
    return sheet("E-301", "Level 3 / Lighting plan", PROJ_OFF, "".join(b), "1/8\" = 1'-0\"")


def duplex(x, y, rot=0, gfci=False):
    s = f'<g transform="rotate({rot} {x} {y})">' + ci(x, y, 11, 1.6, fill="#fff") + ln(x - 6, y - 4, x + 6, y - 4, 1.4) + ln(x - 6, y + 4, x + 6, y + 4, 1.4) + ln(x, y - 11, x, y - 22, 1.6) + "</g>"
    if gfci:
        s += t(x + 14, y + 4, "GFI", 9, weight="bold", font=NARROW)
    return s


def power_plan():
    arch, (x0, y0, W_, H_) = office_arch()
    b = [arch]
    # perimeter receptacles in open office
    for k, xx in enumerate(range(x0 + 470, x0 + 1080, 120)):
        b.append(duplex(xx, y0 + H_ - 16, 180) + t(xx, y0 + H_ - 40, str(2 + 2 * (k // 3)), 10, "middle", font=NARROW))
    # floor boxes
    for xx, yy in [(x0 + 520, y0 + 700), (x0 + 700, y0 + 700), (x0 + 880, y0 + 700), (x0 + 1000, y0 + 380)]:
        b.append(rc(xx - 14, yy - 14, 28, 28, 1.6, fill="#fff") + duplex(xx, yy) + t(xx + 18, yy - 16, "FB", 10, weight="bold", font=NARROW) + t(xx + 18, yy - 4, "14", 10, font=NARROW))
    # conference
    for xx, yy, r in [(x0 + 16, y0 + 120, 90), (x0 + 16, y0 + 260, 90), (x0 + 404, y0 + 190, 270), (x0 + 200, y0 + 344, 0)]:
        b.append(duplex(xx, yy, r) + t(xx + 18, yy + 20, "8", 10, font=NARROW))
    b.append(rc(x0 + 300, y0 + 250, 28, 28, 1.6, fill="#fff") + duplex(x0 + 314, y0 + 264) + t(x0 + 336, y0 + 260, "FB 8", 10, weight="bold", font=NARROW))
    # break room with GFI and dedicated refrigerator
    for xx in (x0 + 1150, x0 + 1210, x0 + 1270):
        b.append(duplex(xx, y0 + H_ - 16, 180, True) + t(xx, y0 + H_ - 40, "10", 10, "middle", font=NARROW))
    b.append(duplex(x0 + W_ - 16, y0 + 760, 90) + t(x0 + W_ - 50, y0 + 750, "12 (REFR.)", 10, "end", font=NARROW))
    # copy room
    for xx in (x0 + 100, x0 + 260):
        b.append(duplex(xx, y0 + H_ - 16, 180) + t(xx, y0 + H_ - 40, "6", 10, "middle", font=NARROW))
    b.append(homerun(x0 + 1080, y0 + H_ - 16, "RP-3A-2,4,6", 30, -50))
    b.append(homerun(x0 + 1016, y0 + 366, "RP-3A-14", 30, -40))
    b.append(homerun(x0 + 418, y0 + 190, "RP-3A-8", 30, -40))
    b.append(rc(x0 + 1150, y0 + 230, 120, 26, 2, fill="#000") + t(x0 + 1210, y0 + 222, "RP-3A", 12, "middle", "bold"))
    sym = [("DUPLEX RECEPTACLE, 20A, 125V, NEMA 5-20R, +18\" AFF", "dup"), ("GFCI DUPLEX RECEPTACLE, +6\" ABOVE COUNTER", "gfi"),
           ("FLUSH FLOOR BOX, POWER + DATA", "fb"), ("HOMERUN TO PANEL; NUMBERS ARE CIRCUITS", "hr")]
    b.append(t(200, 1170, "SYMBOL LEGEND", 14, weight="bold") + ln(200, 1176, 900, 1176, 1.5))
    for k, (txt, kind) in enumerate(sym):
        yy = 1206 + k * 34
        if kind == "dup":
            b.append(duplex(222, yy))
        elif kind == "gfi":
            b.append(duplex(222, yy, 0, True))
        elif kind == "fb":
            b.append(rc(208, yy - 14, 28, 28, 1.6, fill="#fff") + duplex(222, yy))
        else:
            b.append(homerun(206, yy + 10, "", 30, -18))
        b.append(t(270, yy + 5, txt, 12, font=NARROW))
    b.append(notes(1180, 1150, "GENERAL NOTES", ["Devices circuited in Revit to panel RP-3A; panel schedule E-501 updates automatically.",
                                                 "Workstation feeds through floor boxes; furniture whips by furniture vendor."], 520))
    b.append(north(1720, 210))
    b.append(view_title(1180, 1320, "2", "E-302", "Level 3 - power plan", "1/8\" = 1'-0\"", 460))
    return sheet("E-302", "Level 3 / Power plan", PROJ_OFF, "".join(b), "1/8\" = 1'-0\"")


def panel_schedule():
    """Revit 'Branch Panel' schedule template layout."""
    b = []
    x0, y0, Wt = 140, 130, 1560
    b.append(rc(x0, y0, Wt, 40, 1.5, fill="#fff") + t(x0 + Wt / 2, y0 + 28, "Branch Panel: LP-3A", 20, "middle", "bold"))
    hdr_l = [("Location:", "ELEC 304"), ("Supply From:", "T-3 (via DP-3)"), ("Mounting:", "Surface"), ("Enclosure:", "Type 1")]
    hdr_r = [("Volts:", "208/120 Wye"), ("Phases:", "3"), ("Wires:", "4"), ("Mains Type:", "MCB"), ("Mains Rating:", "225 A"), ("MCB Rating:", "225 A")]
    hh = 6 * 26 + 10
    b.append(rc(x0, y0 + 40, Wt, hh, 1.2))
    for k, (a, v) in enumerate(hdr_l):
        b.append(t(x0 + 14, y0 + 70 + k * 26, a, 14, weight="bold", font=NARROW) + t(x0 + 140, y0 + 70 + k * 26, v, 14, font=NARROW))
    for k, (a, v) in enumerate(hdr_r):
        b.append(t(x0 + 1100, y0 + 70 + k * 26, a, 14, weight="bold", font=NARROW) + t(x0 + 1240, y0 + 70 + k * 26, v, 14, font=NARROW))
    b.append(t(x0 + 520, y0 + 70, "Notes:", 14, weight="bold", font=NARROW) + t(x0 + 580, y0 + 70, "Lighting and receptacles, level 3 north. A.I.C. rating 22,000.", 14, font=NARROW))
    cols = [("CKT", 60, "middle"), ("Circuit Description", 290, "start"), ("Trip", 70, "middle"), ("Poles", 70, "middle"),
            ("A", 150, "middle"), ("B", 150, "middle"), ("C", 150, "middle"),
            ("Poles", 70, "middle"), ("Trip", 70, "middle"), ("Circuit Description", 290, "start"), ("CKT", 60, "middle")]
    left = [("LTG - OPEN OFFICE 302", 1840, "L"), ("LTG - OPEN OFFICE 305", 1720, "L"), ("LTG - CONFERENCE 301", 640, "L"),
            ("LTG - OFFICE 303", 480, "L"), ("LTG - EMERGENCY", 380, "L"), ("LTG - CORRIDOR / CORE", 860, "L"),
            ("SPARE", 0, ""), ("SPARE", 0, ""), ("SPACE", 0, "")]
    right = [("RECEPT - OPEN OFFICE N", 1080, "R"), ("RECEPT - OPEN OFFICE S", 1080, "R"), ("RECEPT - COPY 308", 1500, "R"),
             ("RECEPT - CONFERENCE 301", 720, "R"), ("RECEPT - BREAK 306 (GFI)", 1800, "R"), ("REFRIGERATOR - BREAK 306", 1200, "R"),
             ("FLOOR BOXES - 305", 1260, "R"), ("SPARE", 0, ""), ("SPACE", 0, "")]
    rows = []
    phase_vals = []
    ph_tot = [0, 0, 0]
    for i, (l, r) in enumerate(zip(left, right)):
        ph = i % 3
        cells = ["", "", ""]
        va = l[1] + r[1]
        ph_tot[ph] += va
        phase_vals.append((i, ph, l[1], r[1]))
        trip_l = "20 A" if l[0] != "SPACE" else ""
        trip_r = "20 A" if r[0] != "SPACE" else ""
        rows.append([str(2 * i + 1), l[0], trip_l, "1" if trip_l else "", *cells, "1" if trip_r else "", trip_r, r[0], str(2 * i + 2)])
    ty = y0 + 40 + hh + 14
    b.append(table(x0, ty, cols, rows, 32, "#ffffff", 14, zebra=False))
    pa = x0 + 60 + 290 + 70 + 70
    for i, ph, lv, rv in phase_vals:
        cx_ = pa + ph * 150
        yy = ty + 32 * (i + 1) + 21
        b.append(ln(cx_ + 75, ty + 32 * (i + 1), cx_ + 75, ty + 32 * (i + 2), .5, LGREY))
        if lv:
            b.append(t(cx_ + 70, yy, f"{lv} VA", 13, "end", font=NARROW))
        if rv:
            b.append(t(cx_ + 145, yy, f"{rv} VA", 13, "end", font=NARROW))
    tot_y = ty + 32 * (len(rows) + 1)
    b.append(rc(x0, tot_y, Wt, 64, 1.2))
    cx_a = x0 + 60 + 290 + 70 + 70
    b.append(t(cx_a - 14, tot_y + 26, "Total Load:", 14, "end", "bold", font=NARROW) + t(cx_a - 14, tot_y + 52, "Total Amps:", 14, "end", "bold", font=NARROW))
    for k, v in enumerate(ph_tot):
        x = cx_a + k * 150 + 75
        b.append(t(x, tot_y + 26, f"{v} VA", 14, "middle", font=NARROW) + t(x, tot_y + 52, f"{v / 120:.0f} A", 14, "middle", font=NARROW))
    # load classification table
    ly = tot_y + 90
    lt = sum(x[1] for x in left)
    rt = sum(x[1] for x in right)
    cls_rows = [["Lighting", f"{lt} VA", "125.00%", f"{lt * 1.25:.0f} VA"],
                ["Receptacle", f"{rt} VA", "80.00%" if rt > 10000 else "100.00%", f"{min(rt, 10000) + (rt - 10000) * .5 if rt > 10000 else rt:.0f} VA"]]
    b.append(table(x0, ly, [("Load Classification", 260, "start"), ("Connected Load", 190, "end"), ("Demand Factor", 170, "end"), ("Estimated Demand", 190, "end")],
                   cls_rows, 30, "#ffffff", 14))
    est = lt * 1.25 + (min(rt, 10000) + (rt - 10000) * .5 if rt > 10000 else rt)
    px = x0 + 900
    b.append(t(px, ly + 22, "Panel Totals", 15, weight="bold", font=NARROW))
    for k, (a, v) in enumerate([("Total Conn. Load:", f"{lt + rt} VA"), ("Total Est. Demand:", f"{est:.0f} VA"), ("Total Conn.:", f"{(lt + rt) / (208 * 1.732):.0f} A"), ("Total Est. Demand:", f"{est / (208 * 1.732):.0f} A")]):
        b.append(t(px + 220, ly + 50 + k * 26, a, 14, "end", "bold", font=NARROW) + t(px + 240, ly + 50 + k * 26, v, 14, font=NARROW))
    b.append(view_title(90, 1300, "1", "E-501", "Panel schedules", "NTS", 400))
    b.append(notes(1180, 1170, "NOTE", ["Schedule is a live Revit panel schedule view; values come from the circuited model."], 560))
    return sheet("E-501", "Schedules / Panel schedule LP-3A", PROJ_OFF, "".join(b), "NTS")


# --------------------------------------------------------------------------
# CAMPUS + HANDOVER (FMX)
# --------------------------------------------------------------------------

PROJ_CAMP = ["MULTI-BUILDING CAMPUS", "BUILDING E - CENTRAL PLANT", "EQUIPMENT MODEL"]


def equipment_plan():
    b = []
    x0, y0, W_, H_ = 220, 220, 1240, 880
    # DWG background (halftone)
    b.append(rc(x0, y0, W_, H_, 7, HALF))
    for a in [(x0 + 460, y0, x0 + 460, y0 + H_), (x0 + 920, y0, x0 + 920, y0 + 520), (x0 + 920, y0 + 520, x0 + W_, y0 + 520),
              (x0, y0 + 600, x0 + 460, y0 + 600), (x0 + 220, y0 + 600, x0 + 220, y0 + H_)]:
        b.append(ln(*a, 4, HALF))
    # Revit room tags (bounded rooms)
    rooms = [(x0 + 230, y0 + 290, "BOILER ROOM", "E101", "1,840 SF"), (x0 + 690, y0 + 440, "CHILLER ROOM", "E102", "2,610 SF"),
             (x0 + 1160, y0 + 410, "MAIN ELECTRICAL", "E103", "980 SF"), (x0 + 1080, y0 + 740, "PUMP ROOM", "E104", "1,120 SF"),
             (x0 + 110, y0 + 740, "STORAGE", "E105", "410 SF"), (x0 + 340, y0 + 740, "OFFICE", "E106", "300 SF")]
    for x, y, n, num, area in rooms:
        b.append(rc(x - 70, y - 30, 140, 66, 1, fill="#fff") + t(x, y - 8, n, 12, "middle", "bold") + ln(x - 70, y + 2, x + 70, y + 2, .6)
                 + t(x, y + 20, num, 13, "middle", "bold") + t(x, y + 50, area, 10, "middle", fill=GREY))
    # equipment (modeled families) with tags
    eq = [(x0 + 70, y0 + 80, 150, 100, "B-1"), (x0 + 260, y0 + 80, 150, 100, "B-2"), (x0 + 560, y0 + 120, 160, 120, "CH-1"), (x0 + 740, y0 + 120, 160, 120, "CH-2"),
          (x0 + 980, y0 + 40, 220, 50, "SWBD-E"), (x0 + 980, y0 + 140, 30, 90, "EP-E1"), (x0 + 980, y0 + 270, 30, 90, "EP-E2"),
          (x0 + 960, y0 + 560, 80, 50, "P-1"), (x0 + 1080, y0 + 560, 80, 50, "P-2"), (x0 + 560, y0 + 640, 260, 140, "AHU-E1")]
    for x, y, w, h, n in eq:
        b.append(rc(x, y, w, h, 2, fill="#fff") + ln(x, y, x + w, y + h, .6) + ln(x + w, y, x, y + h, .6))
        tx, ty = (x + w + 30, y + h / 2) if w < 60 else (x + w / 2, y + h + 26)
        b.append(tag_box(tx, ty, n, 12))
    b.append(notes(1500, 260, "KEYED NOTES", ["Background: client DWG floor plan, linked and pinned.",
                                              "Rooms bounded and tagged in Revit; area must match DWG within 1%.",
                                              "Equipment placed at true location with asset parameters filled.",
                                              "Level ID and coordinates checked by QA script before acceptance."], 300, 12))
    b.append(north(1730, 1080))
    b.append(view_title(90, 1300, "1", "M-101", "Building E level 1 - equipment location plan", "1/8\" = 1'-0\"", 640))
    return sheet("M-101", "Building E / Equipment location plan", PROJ_CAMP, "".join(b), "1/8\" = 1'-0\"")


def qa_report():
    """Spreadsheet-style output of the Python model-QA script."""
    w, h = 1700, 1100
    b = []
    cols = [("Building", 230, "start"), ("Model file", 270, "start"), ("Rule", 260, "start"), ("Element ID", 130, "end"),
            ("Category", 170, "start"), ("Level", 120, "start"), ("Result", 110, "middle"), ("Detail", 290, "start")]
    rows = [
        ("Bldg A - Admin", "CMP_A_ARCH_R24.rvt", "All rules (6)", "-", "-", "-", ("PASS", GREEN), "0 issues"),
        ("Bldg B - Science", "CMP_B_ARCH_R24.rvt", "All rules (6)", "-", "-", "-", ("PASS", GREEN), "0 issues"),
        ("Bldg C - Library", "CMP_C_ARCH_R24.rvt", "Overlapping rooms", "512334", "Rooms", "L2", ("FAIL", RED), "Overlaps room 512340 by 14 SF"),
        ("Bldg C - Library", "CMP_C_ARCH_R24.rvt", "Overlapping rooms", "512340", "Rooms", "L2", ("FAIL", RED), "Duplicate of 512334"),
        ("Bldg C - Library", "CMP_C_ARCH_R24.rvt", "Equipment outside room", "601877", "Elec. Equipment", "L1", ("FAIL", RED), "Panel EP-C3 not in any room"),
        ("Bldg D - Gym", "CMP_D_ARCH_R24.rvt", "All rules (6)", "-", "-", "-", ("PASS", GREEN), "0 issues"),
        ("Bldg E - Central plant", "CMP_E_MEP_R24.rvt", "Unplaced room", "710045", "Rooms", "-", ("FAIL", RED), "Room 'E107' not placed"),
        ("Bldg E - Central plant", "CMP_E_MEP_R24.rvt", "Mismatched level ID", "722310", "Mech. Equipment", "L1", ("FAIL", RED), "Hosted to 'Level 1 (old)'"),
        ("Bldg E - Central plant", "CMP_E_MEP_R24.rvt", "Mismatched level ID", "722318", "Mech. Equipment", "L1", ("FAIL", RED), "Hosted to 'Level 1 (old)'"),
        ("Bldg E - Central plant", "CMP_E_MEP_R24.rvt", "Missing asset parameter", "722311", "Mech. Equipment", "L1", ("FAIL", RED), "AssetTag empty (B-2)"),
        ("Bldg E - Central plant", "CMP_E_MEP_R24.rvt", "Missing asset parameter", "730002", "Elec. Equipment", "L1", ("FAIL", RED), "SerialNumber empty (EP-E2)"),
        ("Bldg F - Dorm", "CMP_F_ARCH_R24.rvt", "All rules (6)", "-", "-", "-", ("PASS", GREEN), "0 issues"),
    ]
    # Excel-like column letters + row numbers
    total = sum(c[1] for c in cols)
    x0, y0 = 90, 160
    b.append(rc(x0 - 40, y0 - 28, total + 40, 28, .8, fill="#efefef"))
    cx = x0
    for k, (_, cw, _) in enumerate(cols):
        b.append(t(cx + cw / 2, y0 - 9, "ABCDEFGH"[k], 12, "middle", fill=GREY))
        cx += cw
    for r in range(len(rows) + 1):
        b.append(rc(x0 - 40, y0 + r * 34, 40, 34, .8, fill="#efefef") + t(x0 - 20, y0 + r * 34 + 22, str(r + 1), 12, "middle", fill=GREY))
    b.append(table(x0, y0, cols, rows, 34, "#dde7f3", 13, zebra=True))
    sy = y0 + 34 * (len(rows) + 1) + 40
    b.append(t(x0, sy, "Summary", 16, weight="bold"))
    b.append(table(x0, sy + 14, [("Buildings checked", 220, "middle"), ("Rules per model", 220, "middle"), ("Issues found", 220, "middle"), ("Models accepted", 220, "middle"), ("Run time", 220, "middle")],
                   [["6", "6", ("9", RED), ("4 of 6", GREEN), "48 s"]], 34, "#dde7f3", 14))
    return document("model_qa_report.xlsx", "Output of qa_check.py (Python) run against 6 campus building models · sheet: Issues", "".join(b), w, h,
                    "Generated by qa_check.py · Page 1 of 1")


def standards_doc():
    """Page from the team's BIM standards: required parameters and LOD per equipment type."""
    w, h = 1700, 1100
    b = []
    b.append(t(60, 160, "Section 4.2  Required parameters and LOD by equipment type", 18, weight="bold"))
    b.append(t(60, 186, "Every model delivered to a client project must meet this table before it is accepted (see 4.1 Model setup checklist).", 14, fill=GREY))
    cols = [("Equipment type", 250, "start"), ("Revit category", 210, "start"), ("LOD", 80, "middle"), ("Asset Tag", 110, "middle"), ("Manufacturer", 120, "middle"),
            ("Model", 90, "middle"), ("Serial No.", 110, "middle"), ("Rating / Capacity", 150, "middle"), ("Voltage", 100, "middle"), ("Room", 80, "middle"), ("IFC class", 280, "start")]
    Y = ("●", K)
    O = ("○", GREY)
    rows = [
        ("Switchboard", "Electrical Equipment", "350", Y, Y, Y, Y, Y, Y, Y, "IfcElectricDistributionBoard"),
        ("Panelboard", "Electrical Equipment", "350", Y, Y, Y, Y, Y, Y, Y, "IfcElectricDistributionBoard"),
        ("Transformer", "Electrical Equipment", "350", Y, Y, Y, Y, Y, Y, Y, "IfcTransformer"),
        ("Motor control center", "Electrical Equipment", "350", Y, Y, Y, Y, Y, Y, Y, "IfcElectricDistributionBoard"),
        ("Lighting fixture", "Lighting Fixtures", "300", O, Y, Y, O, Y, Y, Y, "IfcLightFixture"),
        ("Boiler", "Mechanical Equipment", "350", Y, Y, Y, Y, Y, Y, Y, "IfcBoiler"),
        ("Air handling unit", "Mechanical Equipment", "350", Y, Y, Y, Y, Y, Y, Y, "IfcUnitaryEquipment"),
        ("Pump", "Mechanical Equipment", "300", Y, Y, Y, Y, Y, Y, Y, "IfcPump"),
        ("Room", "Rooms", "-", O, O, O, O, O, O, Y, "IfcSpace"),
    ]
    b.append(table(60, 210, cols, rows, 36, "#e6e6e6", 14, zebra=True))
    ny = 210 + 36 * (len(rows) + 1) + 40
    b.append(t(60, ny, "● required    ○ optional", 14, fill=GREY))
    b.append(t(60, ny + 44, "Section 4.3  Naming conventions", 18, weight="bold"))
    for k, line in enumerate(["Model file:  <SITE>_<BLDG>_<DISCIPLINE>_R<YEAR>.rvt     e.g. CMP_E_MEP_R24.rvt",
                              "Equipment mark:  <TYPE>-<BLDG><SEQ>     e.g. EP-E2, AHU-E1, B-2",
                              "Shared coordinates:  acquired from the site survey model; survey point locked, project base point at grid A/1."]):
        b.append(t(80, ny + 78 + k * 28, line, 14, font="Consolas, monospace"))
    return document("BIM Standards - Model Requirements v2.1", "Model standards written as BIM Coordinator · baseline for every new client project", "".join(b), w, h,
                    "BIM Standards v2.1 · Section 4 · Page 12")


def coordinates_sheet():
    b = []
    # site plan with three buildings, survey point and project base point
    b.append(rc(200, 220, 1300, 900, 1, LGREY, "none", "14 8"))
    b.append(t(210, 212, "PROPERTY LINE", 11, fill=GREY))
    blds = [(320, 330, 380, 240, "BLDG A", 0), (860, 300, 300, 420, "BLDG B", 0), (420, 720, 520, 260, "BLDG E", 0)]
    for x, y, w, h, n, _ in blds:
        b.append(rc(x, y, w, h, 3, K, "#f2f2f2") + t(x + w / 2, y + h / 2 + 6, n, 18, "middle", "bold"))
    # project base point (circle with X) at bldg E grid A/1
    px, py = 420, 980
    b.append(ci(px, py, 20, 1.8, fill="#fff") + ln(px - 14, py - 14, px + 14, py + 14, 1.6) + ln(px + 14, py - 14, px - 14, py + 14, 1.6))
    b.append(t(px + 30, py + 34, "PROJECT BASE POINT", 13, weight="bold") + t(px + 30, py + 52, "BLDG E, GRID A/1  ·  N/S 0'-0\"  E/W 0'-0\"", 12, font=NARROW))
    # survey point (triangle in circle)
    sx, sy = 260, 1080
    b.append(ci(sx, sy, 20, 1.8, fill="#fff") + pl([(sx, sy - 14), (sx + 13, sy + 9), (sx - 13, sy + 9)], 1.6, close=True))
    b.append(t(sx + 30, sy - 8, "SURVEY POINT (LOCKED)", 13, weight="bold") + t(sx + 30, sy + 10, "N 1,084,512.30  E 2,231,077.85  ELEV 1,021.50'", 12, font=NARROW))
    # true north vs project north
    nx, ny = 1650, 360
    b.append(ln(nx, ny + 120, nx, ny - 40, 2) + pl([(nx, ny - 60), (nx - 10, ny - 36), (nx + 10, ny - 36)], 1, close=True, fill=K) + t(nx, ny - 70, "PROJECT NORTH", 12, "middle", "bold"))
    a = math.radians(12)
    ex, ey = nx + 160 * math.sin(a), ny + 120 - 160 * math.cos(a)
    b.append(ln(nx, ny + 120, ex, ey, 2, dash="10 6") + t(ex + 6, ey - 8, "TRUE NORTH", 12, weight="bold"))
    b.append(f'<path d="M{nx} {ny + 20} A100 100 0 0 1 {nx + 100 * math.sin(a):.1f} {ny + 120 - 100 * math.cos(a):.1f}" fill="none" stroke="{K}"/>' + t(nx + 28, ny + 30, "12°", 13, weight="bold"))
    # linked models table
    b.append(t(1560, 620, "LINKED MODELS", 14, weight="bold"))
    b.append(table(1560, 632, [("MODEL", 150, "start"), ("POSITIONING", 120, "start")],
                   [["SITE_SURVEY", "HOST"], ["BLDG_A_ARCH", "SHARED"], ["BLDG_B_ARCH", "SHARED"], ["BLDG_E_ARCH", "SHARED"], ["BLDG_E_MEP", "SHARED"], ["BLDG_E_ELEC", "SHARED"]], 28, size=12))
    b.append(notes(1560, 860, "KEYED NOTES", ["Coordinates acquired from the survey model; all links placed 'By Shared Coordinates'.",
                                              "Navisworks federated model uses the same shared origin, so every discipline aligns.",
                                              "Base points are clipped and pinned after setup."], 240, 11))
    b.append(view_title(90, 1300, "1", "G-002", "Campus site - shared coordinate setup", "1\" = 60'-0\"", 600))
    return sheet("G-002", "General / Shared coordinates", ["MULTI-BUILDING CAMPUS", "COORDINATION MODEL", "SITE SETUP"], "".join(b), "1\" = 60'-0\"")


def data_map():
    w, h = 1700, 1100
    b = []
    b.append(t(60, 160, "IFC4 export settings", 18, weight="bold"))
    sets = [("IFC version", "IFC4 Reference View [Design Transfer View]"), ("File type", "IFC"), ("Space boundaries", "1st level"),
            ("Export base quantities", "Yes"), ("Export IFC common property sets", "Yes"), ("Export user defined property sets", "FMX_Asset_Psets.txt"),
            ("Classification", "OmniClass Table 23"), ("Coordinate base", "Shared coordinates"), ("Split walls / columns by level", "Yes")]
    b.append(table(60, 176, [("Setting", 340, "start"), ("Value", 420, "start")], [[a, v] for a, v in sets], 32, "#e6e6e6", 14, zebra=True))
    b.append(t(880, 160, "Parameter mapping (FMX_Asset_Psets.txt)", 18, weight="bold"))
    rows = [("PropertySet:", "FMX_Asset", "I", "IfcElectricDistributionBoard,IfcTransformer"),
            ("", "AssetTag", "Text", "Mark"), ("", "Manufacturer", "Text", "Manufacturer"), ("", "ModelNumber", "Text", "Model"),
            ("", "SerialNumber", "Text", "FMX_SerialNumber"), ("", "RatedCurrent", "Real", "Mains"), ("", "RatedVoltage", "Text", "Distribution System"),
            ("", "Room", "Text", "Room: Number"), ("", "InstallDate", "Text", "FMX_InstallDate")]
    b.append(table(880, 176, [("", 120, "start"), ("IFC property", 200, "start"), ("Type", 80, "start"), ("Revit parameter", 360, "start")], rows, 32, "#e6e6e6", 14, zebra=True))
    # flow strip
    fy = 600
    steps = [("Revit model", "LOD 300-400 · shared coordinates"), ("QA gate", "standards 4.1-4.3 · qa_check.py"), ("IFC4 export", "settings + FMX_Asset Psets"), ("Facilities system", "asset per element · no re-keying")]
    for k, (a, s2) in enumerate(steps):
        x = 60 + k * 400
        b.append(rc(x, fy, 340, 110, 1.6, fill="#fff") + t(x + 170, fy + 48, a, 20, "middle", "bold") + t(x + 170, fy + 78, s2, 13, "middle", fill=GREY))
        if k < 3:
            b.append(ln(x + 342, fy + 55, x + 396, fy + 55, 2) + pl([(x + 396, fy + 55), (x + 384, fy + 48), (x + 384, fy + 62)], 1, close=True, fill=K))
    b.append(t(60, 790, "Verification sample (Building E)", 18, weight="bold"))
    b.append(table(60, 806, [("Revit Mark", 160, "start"), ("IFC entity", 300, "start"), ("GlobalId", 300, "start"), ("Facilities asset", 220, "start"), ("Fields matched", 180, "middle")],
                   [["EP-E1", "IfcElectricDistributionBoard", "2N1qZ8$fH9XxP0kE7wQ3aB", "E-ELEC-EP-E1", ("8 / 8", GREEN)],
                    ["SWBD-E", "IfcElectricDistributionBoard", "0cS4uLm2r1Yv$9Hd3TqK7e", "E-ELEC-SWBD-E", ("8 / 8", GREEN)],
                    ["AHU-E1", "IfcUnitaryEquipment", "3Fh8$kq0P5Wz1Lr9mXcV2d", "E-MECH-AHU-E1", ("8 / 8", GREEN)]], 32, "#e6e6e6", 14))
    return document("Model handover - IFC4 export and data mapping", "BIM-to-Facilities handover pilot · export configuration and verification", "".join(b), w, h,
                    "BIM-to-Facilities handover pilot · Page 1 of 1")


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT, f))
    files = {
        "industrial-one-line.svg": one_line(),
        "industrial-tray-plan.svg": tray_plan(),
        "industrial-elec-room.svg": elec_room(),
        "industrial-3d-tray.svg": tray3d(),
        "industrial-clash-report.svg": clash_report(),
        "office-lighting-plan.svg": lighting_plan(),
        "office-power-plan.svg": power_plan(),
        "office-panel-schedule.svg": panel_schedule(),
        "campus-equipment-plan.svg": equipment_plan(),
        "campus-qa-report.svg": qa_report(),
        "handover-standards.svg": standards_doc(),
        "handover-coordinates.svg": coordinates_sheet(),
        "handover-data-map.svg": data_map(),
    }
    for name, svg in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"{name:30s} {len(svg) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
