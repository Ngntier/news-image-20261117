#!/usr/bin/env python3
"""news-image-20261117 - one image summing up Tuesday 17 November 2026.

Draws a newspaper front page (1024x1024 PNG) in pure Python standard
library only: a tiny raster canvas, an embedded 5x7 bitmap font, and a
hand-rolled PNG encoder (zlib). No Pillow, no font files, no network,
no randomness, no timestamps - the output is fully deterministic: two
runs write byte-identical files.

Layout: navy masthead with the date, a large lead panel (Ukraine's
strike on the Kerch Bridge), three panels below it (Trump in Manila
for ASEAN, tankers hit in the Strait of Hormuz, ULA's Vulcan failure),
and an ALSO TODAY strip with the day's other stories. Every headline,
name and number comes from a real report read on 17-18 November 2026;
the sources are listed in NEWS.md. Claims that could not be
independently verified (the Hormuz mine strikes) are captioned as
reported, not as confirmed fact.

Usage: python3 main.py
Writes entry.png to $MAKEFUN_OUTPUT_DIR, or /output when it exists,
otherwise ./entry.png
"""

import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 234)
NAVY = (14, 42, 74)
NAVY_DARK = (9, 26, 48)
GOLD = (242, 183, 5)
AMBER = (232, 200, 106)
RED = (179, 39, 30)
INK = (24, 24, 24)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)
BORDER = (20, 20, 20)

# 5x7 bitmap font. Each glyph is 7 rows of 5 characters; '#' is ink.
# Uppercase, digits and the punctuation the image needs. The text
# renderer uppercases input and maps anything unknown to a space.
FONT = {
    "A": (
        ".###.",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ),
    "B": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#...#",
        "#...#",
        "####.",
    ),
    "C": (
        ".####",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        ".####",
    ),
    "D": (
        "####.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "####.",
    ),
    "E": (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#####",
    ),
    "F": (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    "G": (
        ".####",
        "#....",
        "#....",
        "#.###",
        "#...#",
        "#...#",
        ".###.",
    ),
    "H": (
        "#...#",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ),
    "I": (
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "#####",
    ),
    "J": (
        "..###",
        "...#.",
        "...#.",
        "...#.",
        "...#.",
        "#..#.",
        ".##..",
    ),
    "K": (
        "#...#",
        "#..#.",
        "#.#..",
        "##...",
        "#.#..",
        "#..#.",
        "#...#",
    ),
    "L": (
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#####",
    ),
    "M": (
        "#...#",
        "##.##",
        "#.#.#",
        "#.#.#",
        "#...#",
        "#...#",
        "#...#",
    ),
}

FONT.update({
    "N": (
        "#...#",
        "##..#",
        "##..#",
        "#.#.#",
        "#..##",
        "#..##",
        "#...#",
    ),
    "O": (
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    "P": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    "Q": (
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#..#.",
        ".##.#",
    ),
    "R": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#.#..",
        "#..#.",
        "#...#",
    ),
    "S": (
        ".####",
        "#....",
        "#....",
        ".###.",
        "....#",
        "....#",
        "####.",
    ),
    "T": (
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    "U": (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    "V": (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
    ),
    "W": (
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#.#.#",
        "##.##",
        "#...#",
    ),
    "X": (
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        ".#.#.",
        "#...#",
        "#...#",
    ),
    "Y": (
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    "Z": (
        "#####",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        "#####",
    ),
    "0": (
        ".###.",
        "#..##",
        "#.#.#",
        "##..#",
        "#...#",
        "#...#",
        ".###.",
    ),
    "1": (
        "..#..",
        ".##..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".###.",
    ),
    "2": (
        ".###.",
        "#...#",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#####",
    ),
    "3": (
        "####.",
        "....#",
        "....#",
        ".###.",
        "....#",
        "....#",
        "####.",
    ),
    "4": (
        "...#.",
        "..##.",
        ".#.#.",
        "#..#.",
        "#####",
        "...#.",
        "...#.",
    ),
    "5": (
        "#####",
        "#....",
        "####.",
        "....#",
        "....#",
        "#...#",
        ".###.",
    ),
    "6": (
        ".###.",
        "#....",
        "#....",
        "####.",
        "#...#",
        "#...#",
        ".###.",
    ),
    "7": (
        "#####",
        "....#",
        "...#.",
        "...#.",
        "..#..",
        "..#..",
        "..#..",
    ),
    "8": (
        ".###.",
        "#...#",
        "#...#",
        ".###.",
        "#...#",
        "#...#",
        ".###.",
    ),
    "9": (
        ".###.",
        "#...#",
        "#...#",
        ".####",
        "....#",
        "....#",
        ".###.",
    ),
    " ": (
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
    ".": (
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".##..",
        ".##..",
    ),
    ",": (
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".##..",
        ".##..",
        ".#...",
    ),
    "'": (
        "..#..",
        "..#..",
        "..#..",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
    "-": (
        ".....",
        ".....",
        ".....",
        ".###.",
        ".....",
        ".....",
        ".....",
    ),
    ":": (
        ".....",
        ".##..",
        ".##..",
        ".....",
        ".##..",
        ".##..",
        ".....",
    ),
    "/": (
        "....#",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        "#....",
    ),
    "(": (
        "...##",
        "..#..",
        ".#...",
        ".#...",
        ".#...",
        "..#..",
        "...##",
    ),
    ")": (
        "##...",
        "..#..",
        "...#.",
        "...#.",
        "...#.",
        "..#..",
        "##...",
    ),
    "&": (
        ".###.",
        "#...#",
        "#...#",
        ".#.#.",
        "#.#..",
        "#.#.#",
        ".##.#",
    ),
    "!": (
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".....",
        "..#..",
    ),
    "?": (
        ".###.",
        "#...#",
        "....#",
        "...#.",
        "..#..",
        ".....",
        "..#..",
    ),
    "%": (
        "##..#",
        "##.#.",
        "...#.",
        "..#..",
        ".#...",
        "#.##.",
        "#..##",
    ),
    "+": (
        ".....",
        "..#..",
        "..#..",
        "#####",
        "..#..",
        "..#..",
        ".....",
    ),
    "=": (
        ".....",
        ".....",
        "#####",
        ".....",
        "#####",
        ".....",
        ".....",
    ),
    "$": (
        "..#..",
        ".####",
        "#.#..",
        ".###.",
        "..#.#",
        "####.",
        "..#..",
    ),
    "*": (
        ".....",
        ".#.#.",
        "..#..",
        "#####",
        "..#..",
        ".#.#.",
        ".....",
    ),
})


def text_width(text, scale):
    """Pixel width of text at the given scale (6 font units per char)."""
    return len(text) * 6 * scale


class Canvas:
    """A plain RGB raster. All drawing is clipped to the canvas."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def _row(self, y, x0, x1, color):
        if y < 0 or y >= self.h:
            return
        x0 = max(0, x0)
        x1 = min(self.w, x1)
        if x1 <= x0:
            return
        i = (y * self.w + x0) * 3
        self.px[i:i + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(self.h, y1)):
            self._row(y, x0, x1, color)

    def rect_outline(self, x0, y0, x1, y1, color, t=1):
        self.fill_rect(x0, y0, x1, y0 + t, color)
        self.fill_rect(x0, y1 - t, x1, y1, color)
        self.fill_rect(x0, y0, x0 + t, y1, color)
        self.fill_rect(x1 - t, y0, x1, y1, color)

    def vgrad(self, x0, y0, x1, y1, top, bottom):
        """Vertical gradient, one flat band per row for smoothness."""
        h = y1 - y0
        if h <= 0:
            return
        for y in range(max(0, y0), min(self.h, y1)):
            t = (y - y0) / max(1, h - 1)
            col = tuple(int(top[c] + (bottom[c] - top[c]) * t)
                         for c in range(3))
            self._row(y, x0, x1, col)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self._row(cy + dy, cx - dx, cx + dx + 1, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            dx = int(rx * math.sqrt(max(0.0, 1.0 - (dy * dy) / float(ry * ry))))
            self._row(cy + dy, cx - dx, cx + dx + 1, color)

    def line(self, x0, y0, x1, y1, color):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            x = x0 + dx * i // steps
            y = y0 + dy * i // steps
            self.set(x, y, color)

    def thick_line(self, x0, y0, x1, y1, color, w=3):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        r = w // 2
        for i in range(steps + 1):
            x = x0 + dx * i // steps
            y = y0 + dy * i // steps
            self.circle(x, y, r, color)

    def poly(self, pts, color):
        """Scanline fill of a simple polygon (even-odd rule)."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0, y1 = min(ys), max(ys)
        n = len(pts)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x0, ya = pts[i]
                x1, yb = pts[(i + 1) % n]
                if (ya <= y < yb) or (yb <= y < ya):
                    t = (y - ya) / (yb - ya)
                    xs.append(int(x0 + t * (x1 - x0)))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self._row(y, xs[j], xs[j + 1] + 1, color)

    def text(self, x, y, s, scale, color):
        """Draw uppercase text, left aligned, at integer scale."""
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                glyph = FONT[" "]
            for gy in range(7):
                row = glyph[gy]
                for gx in range(5):
                    if row[gx] == "#":
                        self.fill_rect(cx + gx * scale, y + gy * scale,
                                       cx + (gx + 1) * scale,
                                       y + (gy + 1) * scale, color)
            cx += 6 * scale
        return cx

    def text_centered(self, cx, y, s, scale, color):
        w = text_width(s.upper(), scale)
        self.text(cx - w // 2, y, s, scale, color)


def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF))


def write_png(cv, path):
    """Encode the canvas as a deterministic PNG (filter 0, level 9)."""
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
           _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
           _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# --- scene helpers -------------------------------------------------------

def smoke(cv, cx, cy, s=1.0, dark=False):
    """A cluster of smoke puffs rising from (cx, cy)."""
    base = (74, 74, 74) if dark else (110, 110, 110)
    mid = (96, 96, 96) if dark else (140, 140, 140)
    light = (120, 120, 120) if dark else (170, 170, 170)
    puffs = [(-30, 4, 22, base), (-6, -16, 28, mid), (20, 2, 24, base),
             (4, 12, 20, mid), (34, -12, 18, light), (-14, -34, 26, light),
             (10, -40, 22, mid)]
    for dx, dy, r, col in puffs:
        cv.circle(cx + int(dx * s), cy + int(dy * s), int(r * s), col)


def flames(cv, cx, cy, s=1.0):
    """Stylised flame tongues rising from a base point."""
    tongues = [(-24, 14, -44), (-8, 18, -60), (10, 16, -48), (26, 12, -34)]
    for dx, w, tip in tongues:
        x = cx + int(dx * s)
        w = int(w * s)
        tip = int(tip * s)
        cv.poly([(x - w, cy), (x + w, cy),
                 (x + w // 3, cy + tip), (x - w // 4, cy + tip // 2)],
                (255, 122, 26))
    cv.poly([(cx - 12, cy), (cx + 12, cy), (cx + 4, cy - 34),
             (cx - 4, cy - 18)], (255, 194, 26))


def caption_bar(cv, x0, y0, x1, y1, lines):
    """Dark bar with one or two lines of white text, left aligned."""
    cv.fill_rect(x0, y0, x1, y1, NAVY)
    cv.fill_rect(x0, y0, x1, y0 + 3, GOLD)
    y = y0 + 6
    for text, scale, color in lines:
        cv.text(x0 + 14, y, text, scale, color)
        y += 7 * scale + 3


def panel_frame(cv, x0, y0, x1, y1):
    cv.rect_outline(x0, y0, x1, y1, BORDER, 3)


# --- scenes ---------------------------------------------------------------

def draw_masthead(cv):
    cv.fill_rect(16, 16, 1008, 128, NAVY)
    cv.fill_rect(16, 124, 1008, 128, GOLD)
    cv.text(40, 36, "17 NOVEMBER 2026", 7, WHITE)
    cv.text(40, 92, "THE WORLD IN ONE IMAGE", 4, AMBER)
    # Small globe at the right: blue disc, meridians, equator.
    cv.circle(936, 72, 36, (30, 74, 122))
    cv.circle(936, 72, 30, (64, 140, 190))
    cv.line(936, 42, 936, 102, (247, 243, 234))
    cv.line(906, 72, 966, 72, (247, 243, 234))
    cv.ellipse(936, 72, 14, 30, (247, 243, 234))


def draw_kerch(cv):
    x0, y0, x1, y1 = 16, 144, 1008, 488
    cv.vgrad(x0, y0, x1, 360, (43, 58, 103), (224, 123, 57))
    cv.circle(880, 268, 34, (232, 150, 60))
    cv.circle(880, 268, 26, GOLD)
    # Sea with wave dashes.
    cv.fill_rect(x0, 360, x1, 424, (22, 50, 79))
    for wy in (372, 388, 404):
        for wx in range(28, 1000, 52):
            cv.fill_rect(wx, wy, wx + 26, wy + 3, (46, 90, 136))
    # Bridge towers and cables.
    for tx in (170, 800):
        cv.fill_rect(tx, 200, tx + 16, 312, (58, 58, 58))
        cv.fill_rect(tx - 6, 236, tx + 22, 244, (58, 58, 58))
    for x in (60, 260, 420):
        cv.line(178, 202, x, 296, (107, 107, 107))
    for x in (700, 900, 960):
        cv.line(808, 202, x, 296, (107, 107, 107))
    # Deck: two standing spans, one fallen slab in the gap.
    cv.fill_rect(x0, 296, 470, 312, (46, 46, 46))
    cv.fill_rect(560, 296, x1, 312, (46, 46, 46))
    cv.fill_rect(x0, 296, 470, 299, GOLD)
    cv.fill_rect(560, 296, x1, 299, GOLD)
    cv.poly([(470, 296), (486, 296), (542, 356), (526, 360)],
            (58, 58, 58))
    cv.fill_rect(500, 360, 532, 368, (40, 40, 40))
    # Fire and smoke at the break.
    cv.circle(515, 322, 20, (255, 122, 26))
    cv.circle(515, 322, 12, (255, 194, 26))
    flames(cv, 515, 330, 0.8)
    smoke(cv, 505, 238, 0.7)
    # A small ship passing under the bridge.
    cv.poly([(620, 385), (700, 385), (690, 400), (630, 400)],
            (122, 31, 31))
    cv.fill_rect(655, 372, 685, 385, WHITE)
    cv.fill_rect(640, 368, 652, 385, (46, 46, 46))
    cv.line(670, 372, 670, 356, (46, 46, 46))
    caption_bar(cv, x0, 424, x1, y1, [
        ("KERCH BRIDGE HIT", 5, WHITE),
        ("UKRAINE STRIKE COLLAPSES ROAD SPAN", 2, AMBER),
    ])
    panel_frame(cv, x0, y0, x1, y1)


def draw_manila(cv):
    x0, y0, x1, y1 = 16, 504, 336, 800
    cv.vgrad(x0, y0, x1, 640, (191, 227, 242), (253, 243, 208))
    cv.circle(280, 566, 20, GOLD)
    # Skyline.
    buildings = [(24, 600, 52, 92), (84, 576, 40, 116), (132, 612, 48, 80),
                 (188, 588, 44, 104), (240, 604, 52, 88), (296, 580, 32, 112)]
    for bx, by, bw, bh in buildings:
        cv.fill_rect(bx, by, bx + bw, by + bh, (91, 122, 153))
        for wy in range(by + 12, by + bh - 8, 18):
            for wx in range(bx + 8, bx + bw - 8, 16):
                cv.fill_rect(wx, wy, wx + 6, wy + 8, AMBER)
    cv.fill_rect(x0, 692, x1, 728, (46, 74, 99))
    # Three flag poles: US, Philippines, ASEAN (simplified, stylised).
    for px, kind in ((64, "us"), (160, "ph"), (256, "asean")):
        cv.fill_rect(px, 560, px + 4, 692, (60, 60, 60))
        fx, fy = px + 4, 560
        if kind == "us":
            for i in range(7):
                cv.fill_rect(fx, fy + i * 6, fx + 64, fy + i * 6 + 3,
                             RED if i % 2 == 0 else WHITE)
            cv.fill_rect(fx, fy, fx + 28, fy + 18, NAVY)
            for sy in (fy + 4, fy + 10, fy + 15):
                for sx in (fx + 5, fx + 14, fx + 23):
                    cv.set(sx, sy, WHITE)
        elif kind == "ph":
            cv.fill_rect(fx, fy, fx + 64, fy + 21, (0, 82, 165))
            cv.fill_rect(fx, fy + 21, fx + 64, fy + 42, (206, 17, 38))
            cv.poly([(fx, fy), (fx, fy + 42), (fx + 28, fy + 21)], WHITE)
            cv.circle(fx + 12, fy + 21, 5, GOLD)
        else:
            cv.fill_rect(fx, fy, fx + 64, fy + 42, (0, 82, 165))
            cv.circle(fx + 32, fy + 21, 14, RED)
            cv.circle(fx + 32, fy + 21, 9, (0, 82, 165))
    caption_bar(cv, x0, 728, x1, y1, [
        ("TRUMP IN MANILA", 3, WHITE),
        ("ASEAN SUMMIT IN MANILA", 2, AMBER),
    ])
    panel_frame(cv, x0, y0, x1, y1)


def draw_hormuz(cv):
    x0, y0, x1, y1 = 352, 504, 672, 800
    cv.vgrad(x0, y0, x1, 620, (232, 163, 76), (122, 74, 43))
    cv.circle(620, 560, 18, (242, 183, 5))
    # Sea.
    cv.fill_rect(x0, 620, x1, 728, (27, 58, 92))
    for wy in (640, 664, 688, 710):
        for wx in range(x0 + 12, x1 - 20, 46):
            cv.fill_rect(wx, wy, wx + 24, wy + 3, (60, 104, 150))
    # Distant tanker silhouette.
    cv.fill_rect(380, 640, 470, 656, (24, 44, 66))
    cv.fill_rect(410, 628, 430, 640, (24, 44, 66))
    # Tanker on fire, mid-frame.
    cv.poly([(430, 668), (610, 668), (598, 690), (442, 690)], (122, 31, 31))
    cv.fill_rect(500, 648, 560, 668, WHITE)
    cv.fill_rect(516, 632, 532, 648, (46, 46, 46))
    cv.fill_rect(560, 660, 600, 668, (46, 46, 46))
    cv.circle(540, 656, 16, (255, 122, 26))
    cv.circle(540, 656, 9, (255, 194, 26))
    flames(cv, 540, 664, 0.7)
    smoke(cv, 540, 590, 0.9, dark=True)
    caption_bar(cv, x0, 728, x1, y1, [
        ("TANKERS HIT", 3, WHITE),
        ("IN HORMUZ", 3, WHITE),
        ("REPORTED - NOT VERIFIED", 2, AMBER),
    ])
    panel_frame(cv, x0, y0, x1, y1)


def draw_vulcan(cv):
    x0, y0, x1, y1 = 688, 504, 1008, 800
    cv.vgrad(x0, y0, x1, 728, (11, 16, 38), (27, 42, 82))
    stars = [(712, 530), (760, 548), (820, 524), (880, 540), (940, 522),
             (984, 560), (720, 600), (980, 620), (740, 660), (960, 680),
             (800, 580), (900, 610), (730, 700), (860, 690)]
    for sx, sy in stars:
        cv.fill_rect(sx, sy, sx + 3, sy + 3, WHITE)
    # Debris trail of lost satellites.
    for i, (dx, dy) in enumerate([(760, 560), (790, 580), (820, 600),
                                  (850, 620), (880, 640)]):
        cv.fill_rect(dx, dy, dx + 10, dy + 5, (180, 180, 180))
        cv.fill_rect(dx + 12, dy + 2, dx + 14, dy + 3, (180, 180, 180))
    # Rocket ascending, flame and smoke below.
    cv.fill_rect(836, 560, 860, 640, (232, 232, 232))
    cv.poly([(836, 560), (860, 560), (848, 532)], (200, 60, 50))
    cv.poly([(836, 620), (836, 648), (824, 640)], (180, 60, 50))
    cv.poly([(860, 620), (860, 648), (872, 640)], (180, 60, 50))
    cv.fill_rect(842, 580, 854, 592, (27, 42, 82))
    flames(cv, 848, 648, 0.9)
    smoke(cv, 848, 700, 0.7)
    # A small intact satellite, upper right.
    cv.fill_rect(920, 560, 936, 572, (200, 200, 200))
    cv.fill_rect(900, 562, 920, 570, (90, 140, 200))
    cv.fill_rect(936, 562, 956, 570, (90, 140, 200))
    caption_bar(cv, x0, 728, x1, y1, [
        ("VULCAN FAILS", 3, WHITE),
        ("40 AMAZON SATELLITES LOST", 2, AMBER),
    ])
    panel_frame(cv, x0, y0, x1, y1)


def draw_ticker(cv):
    x0, y0, x1, y1 = 16, 816, 1008, 1008
    cv.fill_rect(x0, y0, x1, 856, NAVY)
    cv.text(x0 + 16, 824, "ALSO TODAY", 4, WHITE)
    cv.fill_rect(x0, 856, x1, 859, GOLD)
    items = [
        (x0, 872, "JPMORGAN OUTAGE", "SOFTWARE BUG HITS US BANKS"),
        (520, 872, "NVIDIA EARNINGS", "AFTER THE BELL"),
        (x0, 944, "UK SANCTIONS", "ISRAELI SETTLEMENT FIRMS"),
        (520, 944, "JAPAN SCRAMBLES JETS", "AFTER AIRSPACE VIOLATION"),
    ]
    for cx, cy, lead, detail in items:
        cv.fill_rect(cx + 8, cy + 8, cx + 22, cy + 22, GOLD)
        cv.text(cx + 32, cy + 6, lead, 3, NAVY)
        cv.text(cx + 32, cy + 32, detail, 2, GREY)
    panel_frame(cv, x0, y0, x1, y1)


def build():
    cv = Canvas(W, H, PAPER)
    cv.rect_outline(0, 0, W, H, BORDER, 4)
    draw_masthead(cv)
    draw_kerch(cv)
    draw_manila(cv)
    draw_hormuz(cv)
    draw_vulcan(cv)
    draw_ticker(cv)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else "."
    path = os.path.join(out_dir, "entry.png")
    size = write_png(build(), path)
    print("wrote", path, size, "bytes")


if __name__ == "__main__":
    main()
