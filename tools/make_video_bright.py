"""
Bright, After Effects-style portfolio showreel (MP4, 1920x1080, 30 fps).

Motion-graphics toolkit, all drawn with Pillow/numpy and piped to ffmpeg:
  kinetic type (per-letter pop-up with overshoot), shape-layer wipes,
  zoom-blur + white-flash transitions, whip pans with motion blur,
  light leaks, lens-flare sweeps, 3D-tilted photo cards that fly in and
  float, shape bursts, animated counters.

Photos come from assets/images/stock (CC0, see CREDITS.md there); drawing
sheets come from assets/images/diagrams (tools/build_diagrams.py), rasterised
with headless Chrome. The video is written to a temporary file and only moved
into place once encoding has finished.

Usage:  python tools/make_video_bright.py     (needs Pillow, numpy, imageio-ffmpeg)
"""
import json
import math
import os
import random
import re
import shutil
import subprocess
import tempfile

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCK = os.path.join(ROOT, "assets", "images", "stock")
PORTRAIT = os.path.join(ROOT, "assets", "images", "profile", "portrait.jpg")   # optional
DIAGRAMS = os.path.join(ROOT, "assets", "images", "diagrams")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
OUT = os.path.join(ROOT, "assets", "video", "portfolio-showreel-bright.mp4")

W, H, FPS = 1920, 1080, 30

# bright palette
INK = (12, 24, 48)
INK_SOFT = (84, 98, 128)
WHITE = (255, 255, 255)
SOFT = (244, 248, 255)
BLUE = (37, 99, 255)
CYAN = (0, 196, 255)
LIME = (40, 210, 110)
YELLOW = (255, 204, 51)
CORAL = (255, 92, 108)
VIOLET = (130, 92, 255)

FONTS = "C:/Windows/Fonts"
font = lambda name, size: ImageFont.truetype(os.path.join(FONTS, name), size)
HEAVY = lambda s: font("ariblk.ttf", s)
BOLD = lambda s: font("segoeuib.ttf", s)
SANS = lambda s: font("segoeui.ttf", s)
MONO = lambda s: font("consolab.ttf", s)

# --------------------------------------------------------------------------
# content
# --------------------------------------------------------------------------

PROJECTS = [
    dict(n="01", cat="INDEPENDENT  ·  2025", name=["INDUSTRIAL FACILITY", "ELECTRICAL & CABLE TRAY"], accent=BLUE,
         facts=[("Distribution", "switchboard · MCC · panels"), ("Cable tray", "+ conduit, NEC clearances"), ("Navisworks", "clash detection")],
         hero="industrial-1.jpg", sheet="industrial-one-line.svg", sheet_cap="E-601 ONE-LINE",
         side=[("industrial-2.jpg", "PANELBOARD"), ("industrial-8.jpg", "EMT CONDUIT")]),
    dict(n="02", cat="INDEPENDENT  ·  SNOWDON TOWERS", name=["COMMERCIAL OFFICE", "ELECTRICAL MODEL"], accent=CORAL,
         facts=[("Lighting", "+ power devices"), ("Circuiting", "load classifications"), ("Panel", "schedules from the model")],
         hero="office-int.jpg", sheet="office-panel-schedule.svg", sheet_cap="E-501 PANEL SCHEDULE",
         side=[("office-3.jpg", "DEVICES"), ("office-4.jpg", "FLOOR BOXES")]),
    dict(n="03", cat="FMX  ·  BIM MODELER", name=["MULTI-BUILDING CAMPUS", "EQUIPMENT MODELING"], accent=VIOLET,
         facts=[("DWG", "to Revit, in place"), ("Equipment", "panels · HVAC · boilers"), ("Python", "QA rules")],
         hero="campus-4.jpg", sheet="campus-equipment-plan.svg", sheet_cap="M-101 EQUIPMENT PLAN",
         side=[("campus-2.jpg", "MECHANICAL ROOM"), ("campus-3.jpg", "BOILER ROOM")]),
    dict(n="04", cat="FMX  ·  BIM COORDINATOR", name=["BIM-TO-FACILITIES", "MODEL HANDOVER"], accent=CYAN,
         facts=[("IFC4", "export settings"), ("LOD", "+ required parameters"), ("No", "re-keying of asset data")],
         hero="handover-1.jpg", sheet="handover-coordinates.svg", sheet_cap="G-002 SHARED COORDINATES",
         side=[("industrial-4.jpg", "EQUIPMENT CHECK"), ("handover-3.jpg", "FACILITIES")]),
]
WORKFLOW = ["ALIGN", "MODEL", "STANDARDS", "QA/QC", "FEDERATE", "CLASH TEST", "ISSUE"]

# --------------------------------------------------------------------------
# easing + small helpers
# --------------------------------------------------------------------------

clamp = lambda t: min(max(t, 0.0), 1.0)
def out_cubic(t): t = clamp(t); return 1 - (1 - t) ** 3
def in_out_cubic(t): t = clamp(t); return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def out_expo(t): t = clamp(t); return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)
def out_back(t, s=1.9): t = clamp(t) - 1; return t * t * ((s + 1) * t + s) + 1
def in_cubic(t): t = clamp(t); return t ** 3


def opacity(layer, a):
    if a >= .999:
        return layer
    out = layer.copy()
    out.putalpha(layer.getchannel("A").point(lambda v: int(v * max(a, 0))))
    return out


def gradient(w, h, stops, angle=0):
    """Linear gradient across `angle` degrees through colour stops [(pos, rgb), ...]."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle)
    t = (xx / w * math.cos(a) + yy / h * math.sin(a))
    t = (t - t.min()) / (t.max() - t.min() + 1e-6)
    pos = np.array([p for p, _ in stops], np.float32)
    cols = np.array([c for _, c in stops], np.float32)
    out = np.stack([np.interp(t, pos, cols[:, k]) for k in range(3)], -1)
    return Image.fromarray(out.astype(np.uint8))


def bright_grade(img):
    img = ImageEnhance.Brightness(img).enhance(1.07)
    img = ImageEnhance.Contrast(img).enhance(1.06)
    return ImageEnhance.Color(img).enhance(1.18)


def cover(img, w, h, zoom=1.0, fx=.5, fy=.5):
    """Crop-to-fill with zoom and focus point."""
    s = max(w / img.width, h / img.height) * zoom
    cw, ch = w / s, h / s
    x0 = (img.width - cw) * fx
    y0 = (img.height - ch) * fy
    return img.resize((w, h), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


_shadow_cache = {}
def drop_shadow(w, h, r, blur=26, alpha=70):
    key = (w, h, r, blur, alpha)
    if key not in _shadow_cache:
        pad = blur * 3
        s = Image.new("L", (w + pad * 2, h + pad * 2), 0)
        ImageDraw.Draw(s).rounded_rectangle((pad, pad, pad + w, pad + h), r, fill=alpha)
        s = s.filter(ImageFilter.GaussianBlur(blur))
        layer = Image.new("RGBA", s.size, (20, 40, 90, 0))
        layer.putalpha(s)
        _shadow_cache[key] = (layer, pad)
    return _shadow_cache[key]


def perspective_coeffs(dst, src):
    """Coefficients for Image.transform(PERSPECTIVE): maps output points dst -> input points src."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def tilt_y(layer, amount):
    """Fake 3D rotate around the vertical axis. amount in [-1, 1]; 0 = flat."""
    if abs(amount) < .004:
        return layer
    w, h = layer.size
    k = amount * .16
    sq = 1 - abs(amount) * .12
    lh, rh = h * (1 + k), h * (1 - k)
    ox = w * (1 - sq) / 2
    dst = [(ox, (h - lh) / 2), (w - ox, (h - rh) / 2), (w - ox, (h + rh) / 2), (ox, (h + lh) / 2)]
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    return layer.transform((w, h), Image.PERSPECTIVE, perspective_coeffs(dst, src), Image.BILINEAR)


# --------------------------------------------------------------------------
# kinetic type
# --------------------------------------------------------------------------

class KText:
    """A word/line rendered once, animated per letter (slide up out of a mask with overshoot)."""

    def __init__(self, text, fnt, fill=INK, spacing=0, grad=None):
        d = ImageDraw.Draw(Image.new("L", (1, 1)))
        asc, desc = fnt.getmetrics()
        self.h = asc + desc
        widths = [d.textlength(c, font=fnt) for c in text]
        self.w = int(sum(widths) + spacing * max(len(text) - 1, 0)) + 4
        mask = Image.new("L", (self.w, self.h), 0)
        md = ImageDraw.Draw(mask)
        x, self.cuts = 0.0, []
        for c, cw in zip(text, widths):
            md.text((x, 0), c, font=fnt, fill=255)
            self.cuts.append((int(x), int(math.ceil(x + cw + spacing / 2)) + 2))
            x += cw + spacing
        colour = gradient(self.w, self.h, grad) if grad else Image.new("RGB", (self.w, self.h), fill)
        self.layer = colour.convert("RGBA")
        self.layer.putalpha(mask)
        self.chars = [(x0, self.layer.crop((x0, 0, min(x1, self.w), self.h))) for x0, x1 in self.cuts]

    def draw(self, frame, x, y, t, stagger=.03, dur=.55, out_t=None, anchor="l"):
        if anchor == "m":
            x -= self.w // 2
        elif anchor == "r":
            x -= self.w
        for i, (cx, tile) in enumerate(self.chars):
            p = out_back((t - i * stagger) / dur)
            if p <= 0:
                continue
            a = clamp((t - i * stagger) / (dur * .5))
            if out_t is not None and t > out_t:  # exit: slide up and away
                q = in_cubic((t - out_t - i * stagger * .5) / .35)
                p = 1 + q
                a *= 1 - q
            dy = int((1 - p) * self.h * .95)
            top = y + dy
            # clip to the line box so letters rise out of an invisible mask
            v0, v1 = max(0, y - top), min(tile.height, y + self.h + 6 - top)
            if v1 <= v0 or a <= 0:
                continue
            piece = tile.crop((0, v0, tile.width, v1))
            frame.alpha_composite(opacity(piece, a), (int(x + cx), int(top + v0)))


def fit_size(text, face, size, max_w):
    """Largest size <= `size` at which `text` fits in max_w pixels."""
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    while size > 20 and d.textlength(text, font=face(size)) > max_w:
        size -= 2
    return size


def pill(text, fnt, fg, bg, pad=(22, 10), outline=None):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = d.textlength(text, font=fnt)
    asc, desc = fnt.getmetrics()
    w, h = int(tw + pad[0] * 2), asc + desc + pad[1] * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=bg + (255,) if bg else None, outline=outline, width=2)
    dr.text((pad[0], pad[1]), text, font=fnt, fill=fg)
    return im


def pop(frame, layer, cx, cy, t, dur=.45):
    """Scale-pop a layer in with overshoot, centred at (cx, cy)."""
    p = out_back(t / dur, 2.4)
    if p <= .02:
        return
    w, h = max(1, int(layer.width * p)), max(1, int(layer.height * p))
    frame.alpha_composite(opacity(layer.resize((w, h), Image.BILINEAR), clamp(t / (dur * .4))), (int(cx - w / 2), int(cy - h / 2)))


# --------------------------------------------------------------------------
# light effects
# --------------------------------------------------------------------------

def make_leak():
    """Big soft warm/cool light-leak texture; a moving window of it is screen-blended over photos."""
    rng = np.random.default_rng(3)
    lw, lh = W * 2, H * 2
    yy, xx = np.mgrid[0:lh:4, 0:lw:4].astype(np.float32)
    acc = np.zeros(xx.shape + (3,), np.float32)
    for col in [(255, 190, 90), (255, 120, 150), (90, 210, 255), (255, 230, 140), (180, 140, 255)] * 2:
        cx, cy, r = rng.uniform(0, lw), rng.uniform(0, lh), rng.uniform(300, 700)
        acc += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))[..., None] * np.array(col) / 255 * rng.uniform(.5, 1)
    acc = np.clip(acc, 0, 1)
    return Image.fromarray((acc * 255).astype(np.uint8)).resize((lw, lh), Image.BILINEAR)


def screen(base, over, k=1.0):
    a = np.asarray(base, np.float32) / 255
    b = np.asarray(over, np.float32) / 255 * k
    return Image.fromarray(((1 - (1 - a) * (1 - b)) * 255).astype(np.uint8))


def leak_at(t, k=.55, speed=60):
    x = int((math.sin(t * .4) * .5 + .5) * W * .9 + t * speed) % W
    y = int((math.cos(t * .3) * .5 + .5) * H * .9)
    return LEAK.crop((x, y, x + W, y + H)), k


def make_flare():
    fw, fh = 1400, 260
    yy, xx = np.mgrid[0:fh, 0:fw].astype(np.float32)
    cx, cy = fw / 2, fh / 2
    streak = np.exp(-((yy - cy) ** 2) / (2 * 3.5 ** 2)) * np.exp(-((xx - cx) ** 2) / (2 * 380 ** 2))
    core = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * 30 ** 2))
    halo = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * 110 ** 2)) * .35
    rgb = np.stack([streak * .75 + core + halo * .9, streak * .9 + core + halo * .95, streak + core + halo], -1)
    return Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))


def flare(frame, t, dur, y=360, k=.9):
    """Lens flare streak sweeping left -> right over `dur` seconds."""
    p = in_out_cubic(t / dur)
    if not 0 < p < 1:
        return frame
    canvas = Image.new("RGB", (W, H))
    x = int(-FLARE.width / 2 + p * (W + FLARE.width) - FLARE.width / 2)
    canvas.paste(FLARE, (x, y - FLARE.height // 2))
    # secondary ghosts along the axis through the centre
    d = ImageDraw.Draw(canvas)
    fx = x + FLARE.width / 2
    for k2, r, col in ((.55, 46, (60, 90, 70)), (.25, 22, (40, 60, 90)), (-.2, 70, (50, 40, 70))):
        gx, gy = W / 2 + (W / 2 - fx) * k2, H / 2 + (H / 2 - y) * k2
        d.ellipse((gx - r, gy - r, gx + r, gy + r), fill=col)
    canvas = canvas.filter(ImageFilter.GaussianBlur(2))
    return screen(frame, canvas, k * math.sin(p * math.pi))


# --------------------------------------------------------------------------
# transitions
# --------------------------------------------------------------------------

def t_wipe(a, b, t, colors):
    """Shape-layer wipe: skewed colour bars sweep across, the next scene is revealed behind the last."""
    base = a if t < .5 else b
    out = base.copy()
    d = ImageDraw.Draw(out)
    S = 420
    span = W + 2 * S
    n = len(colors)
    for k, col in enumerate(colors):
        # all bars cover by t=.5 (the cut); top bars leave first so each colour shows on the way out
        lead = -S + in_out_cubic((t - k * .07) / .36) * span
        trail = -S + in_out_cubic((t - .5 - (n - 1 - k) * .07) / .36) * span if t > .5 else -S
        if lead <= -S + 1 or trail >= W + S - 1:
            continue
        d.polygon([(trail + S, 0), (lead + S, 0), (lead, H), (trail, H)], fill=col)
    return out


def zoom_blur(img, s):
    """Radial zoom blur of strength s in [0, 1] (average of scaled copies)."""
    if s < .02:
        return img
    acc = np.zeros((H, W, 3), np.float32)
    n = 7
    for i in range(n):
        z = 1 + s * .45 * i / (n - 1)
        cw, ch = W / z, H / z
        acc += np.asarray(img.resize((W, H), Image.BILINEAR, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2)), np.float32)
    return Image.fromarray((acc / n).astype(np.uint8))


def t_zoom(a, b, t):
    """Zoom-blur punch in, white flash at the cut, zoom-blur settle."""
    if t < .5:
        s = in_cubic(t / .5)
        img = zoom_blur(a, s)
    else:
        s = 1 - out_cubic((t - .5) / .5)
        img = zoom_blur(b, s)
    flash = max(0, 1 - abs(t - .5) / .22)
    return Image.blend(img, Image.new("RGB", (W, H), WHITE), flash * .92) if flash > 0 else img


def motion_blur_x(img, px):
    px = int(px)
    if px < 2:
        return img
    a = np.asarray(img, np.float32)
    c = np.cumsum(np.pad(a, ((0, 0), (px, 0), (0, 0)), mode="edge"), axis=1)
    out = (c[:, px:] - c[:, :-px]) / px
    return Image.fromarray(out.astype(np.uint8))


def t_whip(a, b, t):
    """Whip pan left with motion blur."""
    p = in_out_cubic(t)
    off = int(p * W)
    out = Image.new("RGB", (W, H))
    out.paste(a, (-off, 0))
    out.paste(b, (W - off, 0))
    speed = math.sin(p * math.pi)
    return motion_blur_x(out, speed * 140)


# --------------------------------------------------------------------------
# scenes: each returns (duration, render(t) -> RGB)
# --------------------------------------------------------------------------

def dotted_bg(base_rgb=SOFT, dot=(208, 220, 245)):
    img = Image.new("RGB", (W, H), base_rgb)
    d = ImageDraw.Draw(img)
    for y in range(30, H, 44):
        for x in range(30, W, 44):
            d.ellipse((x - 1.6, y - 1.6, x + 1.6, y + 1.6), fill=dot)
    return img


def pastel_blobs(img, seed, cols=(BLUE, CYAN, LIME, YELLOW, CORAL)):
    rng = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for c in cols:
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(220, 420)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c + (46,))
    layer = layer.filter(ImageFilter.GaussianBlur(120))
    out = img.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


def burst(frame, cx, cy, t, seed, n=22, start=.3, radius=(330, 520)):
    """Shapes fly out from a point with ease-out, then float."""
    rng = random.Random(seed)
    d = ImageDraw.Draw(frame)
    for i in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(*radius)
        size = rng.uniform(8, 22)
        col = rng.choice([BLUE, CYAN, LIME, YELLOW, CORAL, VIOLET])
        kind = rng.choice(["circle", "ring", "square", "tri", "plus"])
        p = out_expo((t - start - i * .012) / 1.1)
        if p <= 0:
            continue
        wob = math.sin(t * 1.6 + i) * 8
        x = cx + math.cos(ang) * dist * p + wob
        y = cy + math.sin(ang) * dist * p + math.cos(t * 1.3 + i) * 8
        rot = t * 1.5 + i
        s = size * min(1, p * 1.4)
        if kind == "circle":
            d.ellipse((x - s / 2, y - s / 2, x + s / 2, y + s / 2), fill=col)
        elif kind == "ring":
            d.ellipse((x - s, y - s, x + s, y + s), outline=col, width=4)
        elif kind == "square":
            pts = [(x + s * .7 * math.cos(rot + k * math.pi / 2), y + s * .7 * math.sin(rot + k * math.pi / 2)) for k in range(4)]
            d.polygon(pts, fill=col)
        elif kind == "tri":
            pts = [(x + s * .8 * math.cos(rot + k * 2 * math.pi / 3), y + s * .8 * math.sin(rot + k * 2 * math.pi / 3)) for k in range(3)]
            d.polygon(pts, outline=col, width=4)
        else:
            d.line((x - s / 2, y, x + s / 2, y), fill=col, width=5)
            d.line((x, y - s / 2, x, y + s / 2), fill=col, width=5)


def scene_intro():
    dur = 5.6
    bg = pastel_blobs(dotted_bg(), 11)
    photo = bright_grade(Image.open(PORTRAIT).convert("RGB")) if os.path.exists(PORTRAIT) else None
    R = 330
    cx, cy = 1440, 540
    kicker = KText("BIM DESIGNER & COORDINATOR", MONO(28), BLUE, 6)
    first = KText("HARRISON", HEAVY(132), INK, 2)
    last = KText("FARBER", HEAVY(132), spacing=2, grad=[(0, BLUE), (.6, CYAN), (1, LIME)])
    sub = KText("PORTFOLIO  ·  2026", BOLD(34), INK_SOFT, 10)
    chips = [pill(s, BOLD(24), WHITE, c) for s, c in (("Revit Electrical", BLUE), ("Navisworks", CYAN), ("MEP coordination", LIME), ("Panel schedules", CORAL))]

    def render(t):
        frame = bg.copy().convert("RGBA")
        # portrait: circular reveal + rings + dashed orbit
        r = int(R * out_expo((t - .25) / 1.0))
        if r > 2:
            z = 1.12 - .08 * clamp(t / dur)
            if photo is not None:
                img = cover(photo, 2 * R, 2 * R, z, .5, .35)
            else:  # monogram badge
                img = gradient(2 * R, 2 * R, [(0, BLUE), (.6, CYAN), (1, LIME)], 35)
                ImageDraw.Draw(img).text((R, R), "HF", font=HEAVY(230), fill=WHITE, anchor="mm")
            mask = Image.new("L", (2 * R, 2 * R), 0)
            ImageDraw.Draw(mask).ellipse((R - r, R - r, R + r, R + r), fill=255)
            sh, pad = drop_shadow(2 * R, 2 * R, R, 34, 60)
            frame.alpha_composite(opacity(sh, r / R), (cx - R - pad, cy - R - pad + 20))
            frame.paste(img, (cx - R, cy - R), mask)
        d = ImageDraw.Draw(frame)
        for k, col in enumerate((BLUE, CYAN, LIME)):
            p = out_cubic((t - .5 - k * .15) / 1.4)
            if p > 0:
                rr = R + 18 + k * 26 + p * 10
                d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col + (int(255 * (1 - .4 * k)),), width=5 - k)
        a0 = t * 40
        if t > .8:
            ro = R + 84
            for s in range(0, 360, 15):
                d.arc((cx - ro, cy - ro, cx + ro, cy + ro), a0 + s, a0 + s + 6, fill=INK_SOFT + (140,), width=3)
        burst(frame, cx, cy, t, 5)
        # type
        kicker.draw(frame, 150, 270, t - .5, stagger=.015)
        first.draw(frame, 140, 320, t - .7)
        last.draw(frame, 140, 466, t - .9)
        p = out_expo((t - 1.4) / .7)
        d.rounded_rectangle((150, 680, 150 + int(320 * p), 690), 5, fill=BLUE)
        sub.draw(frame, 150, 712, t - 1.5, stagger=.02)
        x = 150
        for i, c in enumerate(chips):
            pop(frame, c, x + c.width / 2, 820 + c.height / 2, t - 1.9 - i * .12)
            x += c.width + 14
        return frame.convert("RGB")

    return dur, render


def scene_section(title, kick, cols, sub=None, dur=2.6):
    bg = gradient(W, H, cols, angle=25)
    t1 = KText(title, HEAVY(132), WHITE, 3)
    k1 = KText(kick, MONO(30), WHITE, 10)
    s1 = KText(sub, BOLD(34), WHITE, 4) if sub else None

    def render(t):
        frame = bg.copy().convert("RGBA")
        d = ImageDraw.Draw(frame)
        # rotating outline shapes
        for i, (x, y, r) in enumerate(((260, 220, 120), (1680, 860, 170), (1580, 180, 70), (300, 900, 90))):
            p = out_back((t - i * .08) / .6)
            if p <= 0:
                continue
            rot = t * (25 if i % 2 else -25) + i * 30
            rr = r * p
            if i % 2:
                pts = [(x + rr * math.cos(math.radians(rot + k * 120)), y + rr * math.sin(math.radians(rot + k * 120))) for k in range(3)]
                d.polygon(pts, outline=(255, 255, 255, 150), width=6)
            else:
                pts = [(x + rr * math.cos(math.radians(rot + k * 90)), y + rr * math.sin(math.radians(rot + k * 90))) for k in range(4)]
                d.polygon(pts, outline=(255, 255, 255, 120), width=6)
        k1.draw(frame, W // 2, 380, t - .1, stagger=.015, anchor="m", out_t=dur - .55)
        t1.draw(frame, W // 2, 430, t - .25, stagger=.035, anchor="m", out_t=dur - .5)
        if s1:
            s1.draw(frame, W // 2, 640, t - .6, stagger=.015, anchor="m", out_t=dur - .45)
        p = out_expo((t - .5) / .6)
        lw = int(260 * p)
        d.rounded_rectangle((W // 2 - lw, 615, W // 2 + lw, 621), 3, fill=WHITE)
        return frame.convert("RGB")

    return dur, render


def load_photo(name):
    return bright_grade(Image.open(os.path.join(STOCK, name)).convert("RGB"))


def load_sheet(name, tmp):
    """Rasterise a drawing sheet (SVG) with headless Chrome."""
    src = os.path.join(DIAGRAMS, name)
    w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', open(src, encoding="utf-8").read(2000)).groups())
    out = os.path.join(tmp, name + ".png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
                    f"--screenshot={out}", "file:///" + src.replace(os.sep, "/")], check=True, capture_output=True)
    return Image.open(out).convert("RGB")


def scene_project_hero(p, photo):
    dur = 3.6
    num = KText(p["n"], HEAVY(220), spacing=0, grad=[(0, p["accent"]), (1, CYAN if p["accent"] != CYAN else BLUE)])
    lab = KText(f"PROJECT {p['n']}  /  {p['cat']}", MONO(24), p["accent"], 5)
    lines = [KText(s, HEAVY(fit_size(s, HEAVY, 66, 640)), INK, 1) for s in p["name"]]
    fact_font_big, fact_font = HEAVY(44), BOLD(24)

    def render(t):
        z = 1.16 - .12 * out_cubic(t / dur)
        img = cover(photo, W, H, z, .5 + .04 * math.sin(t * .5), .5)
        lk, k = leak_at(t + int(p["n"]) * 3)
        img = screen(img, lk, k * .7)
        img = flare(img, t - .5, 2.2, y=300)
        frame = img.convert("RGBA")
        # white panel slides in from the left
        pw = 820
        px = int(-pw + out_expo((t - .05) / .8) * pw)
        panel = Image.new("RGBA", (pw, H), (255, 255, 255, 236))
        frame.alpha_composite(panel, (px, 0))
        d = ImageDraw.Draw(frame)
        d.rectangle((px + pw - 12, 0, px + pw, H), fill=p["accent"])
        ox = px + 110
        num.draw(frame, ox - 10, 110, t - .35, stagger=.08)
        lab.draw(frame, ox, 380, t - .55, stagger=.012)
        for i, L in enumerate(lines):
            L.draw(frame, ox, 430 + i * 84, t - .7 - i * .12, stagger=.022)
        # facts with counting numbers
        for i, (val, unit) in enumerate(p["facts"]):
            q = out_cubic((t - 1.3 - i * .15) / .9)
            if q <= 0:
                continue
            nums = re.findall(r"[\d,]+", val)
            shown = val
            for nstr in nums:
                n = int(nstr.replace(",", ""))
                shown = shown.replace(nstr, f"{math.ceil(n * q):,}", 1)
            y = 700 + i * 92
            a = int(255 * clamp(q * 2))
            d.rounded_rectangle((ox, y + 8, ox + 8, y + 64), 4, fill=p["accent"] + (a,))
            d.text((ox + 28, y), shown, font=fact_font_big, fill=INK + (a,))
            tw = d.textlength(shown, font=fact_font_big)
            d.text((ox + 40 + tw, y + 20), unit, font=fact_font, fill=INK_SOFT + (a,))
        return frame.convert("RGB")

    return dur, render


def scene_project_collage(p, sheet_img, side_imgs):
    dur = 3.8
    bg = pastel_blobs(dotted_bg(), int(p["n"]) * 7, cols=(p["accent"], CYAN, YELLOW))
    slots = [(110, 190, 1000, 640), (1170, 190, 640, 300), (1170, 530, 640, 300)]
    caps = [p["sheet_cap"]] + [c for _, c in p["side"]]
    cards = [(x, y, w, h, img) for (x, y, w, h), img in zip(slots, [sheet_img] + side_imgs)]
    name = " ".join(p["name"])
    title = KText(name, HEAVY(fit_size(name, HEAVY, 54, 1700)), INK, 1)
    lab = KText(f"PROJECT {p['n']}  /  {p['cat']}", MONO(22), p["accent"], 5)
    chip = [pill(c, BOLD(20), WHITE, p["accent"]) for c in caps]
    flow = [pill(s, MONO(18), INK, None, (16, 7), outline=(190, 205, 235)) for s in WORKFLOW]
    flow_on = [pill(s, MONO(18), WHITE, p["accent"], (16, 7)) for s in WORKFLOW]

    def render(t):
        frame = bg.copy().convert("RGBA")
        lab.draw(frame, 110, 70, t - .05, stagger=.01)
        title.draw(frame, 108, 100, t - .15, stagger=.015)
        for i, (x, y, w, h, img) in enumerate(cards):
            p_in = out_back((t - .2 - i * .16) / .75, 1.4)
            if p_in <= 0:
                continue
            bob = math.sin(t * 1.8 + i * 1.3) * 6
            zoom = (1.04 - .03 * clamp(t / dur)) if i == 0 else (1.12 - .08 * clamp(t / dur))
            face = cover(img, w, h, zoom).convert("RGBA")
            face.putalpha(rounded_mask(w, h, 22))
            face = tilt_y(face, (1 - p_in) * (1 if i else -1) * 1.0 + math.sin(t + i) * .04)
            # fly in from below/right
            dx = int((1 - p_in) * (300 if i else -300))
            dy = int((1 - p_in) * 260 + bob)
            sh, pad = drop_shadow(w, h, 22)
            frame.alpha_composite(opacity(sh, clamp(p_in)), (x + dx - pad, y + dy - pad + 22))
            frame.alpha_composite(opacity(face, clamp(p_in * 1.6)), (x + dx, y + dy))
            c = chip[i]
            pop(frame, c, x + dx + 24 + c.width / 2, y + dy + h - 24 - c.height / 2, t - .7 - i * .16)
        # workflow track with progress
        x = 110
        y = 930
        prog = clamp((t - .6) / (dur - 1.0)) * len(flow)
        d = ImageDraw.Draw(frame)
        d.line((110, y + 19, 1810, y + 19), fill=(205, 215, 238), width=3)
        d.line((110, y + 19, 110 + int(1700 * clamp(prog / len(flow))), y + 19), fill=p["accent"], width=5)
        gap = (1700 - sum(f.width for f in flow)) / (len(flow) - 1)
        for i, f in enumerate(flow):
            layer = flow_on[i] if prog > i else f
            pop(frame, layer, x + f.width / 2, y + 19, t - .4 - i * .05, .35)
            x += f.width + gap
        return frame.convert("RGB")

    return dur, render


def scene_outro():
    dur = 5.6
    bg = gradient(W, H, [(0, BLUE), (.55, CYAN), (1, LIME)], angle=30)
    k = KText("MODEL  /  COORDINATE  /  DELIVER", MONO(28), WHITE, 8)
    t1 = KText("LET'S BUILD", HEAVY(140), WHITE, 3)
    t2 = KText("TOGETHER", HEAVY(140), WHITE, 3)
    name = KText("HARRISON FARBER  ·  BIM DESIGNER & COORDINATOR", BOLD(36), WHITE, 2)
    link = pill("linkedin.com/in/harrison-farber-7b383943b", MONO(26), BLUE, WHITE, (28, 14))
    mail = KText("harrisonfarber38@gmail.com  ·  Overland Park, Kansas", BOLD(28), WHITE, 1)

    def render(t):
        frame = bg.copy().convert("RGBA")
        burst(frame, W // 2, H // 2, t, 21, n=30, start=.1, radius=(520, 900))
        k.draw(frame, W // 2, 200, t - .1, stagger=.012, anchor="m")
        t1.draw(frame, W // 2, 250, t - .25, stagger=.04, anchor="m")
        t2.draw(frame, W // 2, 420, t - .45, stagger=.04, anchor="m")
        name.draw(frame, W // 2, 640, t - .9, stagger=.01, anchor="m")
        pop(frame, link, W // 2, 760, t - 1.3)
        mail.draw(frame, W // 2, 840, t - 1.5, stagger=.006, anchor="m")
        return frame.convert("RGB")

    return dur, render


# --------------------------------------------------------------------------
# timeline
# --------------------------------------------------------------------------

def build(tmp):
    scenes = [scene_intro(), ("zoom", .6),
              scene_section("SELECTED PROJECTS", "BIM DESIGNER  ·  COORDINATOR", [(0, BLUE), (1, CYAN)],
                            "ELECTRICAL MODELS  ·  MEP COORDINATION  ·  MODEL QA")]
    for i, p in enumerate(PROJECTS):
        sheet_img = load_sheet(p["sheet"], tmp)
        side = [load_photo(f) for f, _ in p["side"]]
        scenes += [("wipe", .8, [p["accent"], YELLOW, WHITE] if i else [WHITE, YELLOW, p["accent"]]),
                   scene_project_hero(p, load_photo(p["hero"])), ("whip", .5), scene_project_collage(p, sheet_img, side)]
    scenes += [("wipe", .8, [CYAN, WHITE, BLUE]), scene_outro()]
    return scenes


def main():
    global LEAK, FLARE
    LEAK, FLARE = make_leak(), make_flare()
    tmp = tempfile.mkdtemp(prefix="showreel-")
    items = build(tmp)
    # lay out scenes; a transition overlaps the end of one scene with the start of the next
    timeline, t = [], 0.0
    pending = None
    for it in items:
        if isinstance(it[0], str):
            pending = it
            continue
        dur, fn = it
        if pending and timeline:
            t -= pending[1]
        timeline.append(dict(start=t, dur=dur, fn=fn, trans=pending))
        t += dur
        pending = None
    total = t
    n = int(total * FPS)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # encode to a temporary file; an interrupted render never leaves a broken OUT behind
    part = OUT + ".part.mp4"
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", part]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(n):
        T = f / FPS
        act = [s for s in timeline if s["start"] <= T < s["start"] + s["dur"]]
        if len(act) == 2 and act[1]["trans"]:
            a, b = act
            tr = b["trans"]
            p = (T - b["start"]) / tr[1]
            fa, fb = a["fn"](T - a["start"]), b["fn"](T - b["start"])
            if tr[0] == "wipe":
                frame = t_wipe(fa, fb, p, tr[2])
            elif tr[0] == "zoom":
                frame = t_zoom(fa, fb, p)
            else:
                frame = t_whip(fa, fb, p)
        else:
            s = act[-1]
            frame = s["fn"](T - s["start"])
        edge = min(T / .4, (total - T) / .6, 1)
        if edge < 1:
            frame = Image.blend(Image.new("RGB", (W, H), WHITE), frame, max(edge, 0))
        proc.stdin.write(frame.tobytes())
        if f % (FPS * 5) == 0:
            print(f"  {T:5.1f}s / {total:.1f}s", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed; previous video left untouched")
    os.replace(part, OUT)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"wrote {os.path.relpath(OUT, ROOT)}  ({total:.1f}s, {os.path.getsize(OUT) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
