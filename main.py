#!/usr/bin/env python3
"""The World in One Day - Sunday 22 November 2026.

Draws a newspaper front page summing up the world news of Sunday
22 November 2026 and writes it to /output/entry.png.

Pure Python 3.13 standard library: the PNG bytes are encoded by hand
(zlib + struct), the letters come from a small built-in 5x7 bitmap
font, and every scene is drawn from scratch with simple shapes.
No network, no randomness, no time input: two runs write identical
bytes. Run:  python3 main.py [/output/entry.png]
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 227)
INK = (20, 20, 20)
WHITE = (255, 253, 245)
RED = (176, 30, 36)
DARKRED = (140, 20, 26)
BLUE = (31, 78, 121)
SKY = (183, 216, 240)
SEA = (64, 130, 180)
GREEN = (30, 122, 70)
EARTH_GREEN = (46, 139, 87)
EARTH_BLUE = (58, 130, 190)
ORANGE = (224, 110, 30)
FLAME = (240, 140, 30)
YELLOW = (240, 200, 60)
GREY = (120, 120, 120)
LIGHTGREY = (210, 210, 205)
DARKGREY = (70, 70, 70)
BROWN = (122, 84, 52)
STEEL = (51, 82, 107)
PURPLE = (91, 45, 142)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, one row per string, "1" = filled pixel.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
}
BLANK = ("00000",) * 7


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap_text(s, max_px, scale):
    """Greedy word wrap; returns a list of lines that fit max_px."""
    words = s.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_px or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * w * h)

    def put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, color)

    def frame(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.put(xx, yy, color)
                else:
                    if r * r - 2 * r <= d2 <= r * r:
                        self.put(xx, yy, color)

    def ring(self, cx, cy, r, color, t=3):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d2 <= r * r:
                    self.put(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        xs = [x0, x1, x2]
        ys = [y0, y1, y2]
        for yy in range(min(ys), max(ys) + 1):
            row = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    row.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(row) >= 2:
                for xx in range(int(min(row)), int(max(row)) + 1):
                    self.put(xx, yy, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)


# ---------------------------------------------------------------- png
def png_bytes(canvas):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * canvas.w * 3:(y + 1) * canvas.w * 3]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat) + chunk(b"IEND", b""))

# ---------------------------------------------------------------- scenes
# Each scene draws inside a box (x, y, w, h) with simple flat shapes.

def scene_cop31(c, x, y, w, h):
    c.rect(x, y, w, h, SKY)
    c.rect(x, y + h - 26, w, 26, EARTH_GREEN)
    # Earth
    c.circle(x + 62, y + 52, 34, EARTH_BLUE)
    c.circle(x + 50, y + 42, 12, EARTH_GREEN)
    c.circle(x + 72, y + 60, 14, EARTH_GREEN)
    c.circle(x + 62, y + 52, 34, INK, fill=False)
    # smokestack
    c.rect(x + 150, y + 30, 22, 62, DARKGREY)
    c.rect(x + 146, y + 24, 30, 8, INK)
    c.circle(x + 168, y + 16, 7, GREY)
    c.circle(x + 180, y + 8, 5, LIGHTGREY)
    # clock: talks in overtime
    c.circle(x + 250, y + 52, 30, WHITE)
    c.ring(x + 250, y + 52, 30, INK, 3)
    c.line(x + 250, y + 52, x + 250, y + 30, INK, 3)
    c.line(x + 250, y + 52, x + 268, y + 60, INK, 3)
    # conference flags row
    for i, col in enumerate((RED, BLUE, GREEN, YELLOW, PURPLE)):
        fx = x + 320 + i * 26
        c.vline(fx, y + 44, 48, INK, 2)
        c.triangle(fx, y + 44, fx, y + 58, fx + 20, y + 51, col)


def scene_hormuz(c, x, y, w, h):
    c.rect(x, y, w, h, SKY)
    c.circle(x + 410, y + 18, 16, YELLOW)
    # refinery on the left
    c.rect(x + 8, y + 52, 60, 40, DARKGREY)
    c.rect(x + 76, y + 34, 14, 58, GREY)
    c.rect(x + 96, y + 44, 14, 48, GREY)
    c.triangle(x + 30, y + 52, x + 48, y + 14, x + 66, y + 52, FLAME)
    c.triangle(x + 44, y + 52, x + 56, y + 30, x + 68, y + 52, YELLOW)
    # sea
    c.rect(x, y + h - 34, w, 34, SEA)
    c.hline(x + 10, y + h - 22, 120, WHITE, 2)
    c.hline(x + 300, y + h - 12, 140, WHITE, 2)
    # tanker
    c.rect(x + 150, y + h - 52, 220, 20, DARKRED)
    c.rect(x + 320, y + h - 72, 48, 20, WHITE)
    c.rect(x + 330, y + h - 84, 28, 12, INK)
    c.rect(x + 160, y + h - 66, 16, 14, INK)
    c.triangle(x + 240, y + h - 52, x + 256, y + h - 80, x + 272, y + h - 52,
               FLAME)


def scene_mexico(c, x, y, w, h):
    c.rect(x, y, w, h, (232, 222, 200))
    # badge star
    cx, cy = x + 70, y + 50
    c.circle(cx, cy, 30, YELLOW)
    c.ring(cx, cy, 30, INK, 3)
    for dx, dy in ((0, -16), (0, 16), (-15, -8), (15, 8), (-15, 8), (15, -8)):
        c.line(cx, cy, cx + dx, cy + dy, INK, 3)
    c.circle(cx, cy, 5, INK)
    # handcuffs
    c.ring(x + 210, y + 50, 26, INK, 5)
    c.ring(x + 290, y + 50, 26, INK, 5)
    c.line(x + 236, y + 50, x + 264, y + 50, INK, 5)
    c.circle(x + 210, y + 50, 6, GREY)
    c.circle(x + 290, y + 50, 6, GREY)
    # bars at the bottom
    for i in range(9):
        bx = x + 20 + i * 48
        c.vline(bx, y + h - 26, 26, INK, 6)


def scene_shenzhen(c, x, y, w, h):
    c.rect(x, y, w, h, SKY)
    # skyline
    base = y + h - 34
    for i, bh in enumerate((46, 70, 58, 86, 64, 78, 52)):
        bx = x + 12 + i * 62
        c.rect(bx, base - bh, 48, bh, STEEL)
        for wy in range(3):
            for wx in range(2):
                c.rect(bx + 8 + wx * 22, base - bh + 8 + wy * 16, 10, 8,
                       YELLOW)
    c.rect(x, base, w, 34, (200, 190, 170))
    # table
    c.rect(x + 130, y + 68, 200, 10, BROWN)
    c.rect(x + 140, y + 78, 8, 18, BROWN)
    c.rect(x + 314, y + 78, 8, 18, BROWN)
    # three leaders at the table
    for i, col in enumerate((BLUE, RED, DARKGREY)):
        fx = x + 170 + i * 60
        c.circle(fx, y + 40, 14, (232, 190, 160))
        c.rect(fx - 18, y + 54, 36, 14, col)
        c.rect(fx - 4, y + 54, 8, 22, WHITE)


def scene_markets(c, x, y, w, h):
    c.rect(x, y, w, h, WHITE)
    # grid
    for gy in range(4):
        c.hline(x + 10, y + 14 + gy * 22, w - 20, LIGHTGREY, 1)
    # falling red line with arrowhead
    pts = [(x + 16, y + 14), (x + 90, y + 26), (x + 160, y + 22),
           (x + 230, y + 44), (x + 300, y + 40), (x + 380, y + 66),
           (x + 430, y + 62)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        c.line(ax, ay, bx, by, RED, 4)
    c.triangle(x + 430, y + 62, x + 414, y + 52, x + 414, y + 72, RED)
    # chip
    c.rect(x + 330, y + 8, 52, 52, INK)
    c.rect(x + 342, y + 20, 28, 28, GREEN)
    for i in range(4):
        c.hline(x + 322, y + 16 + i * 12, 8, INK, 3)
        c.hline(x + 382, y + 16 + i * 12, 8, INK, 3)


def scene_ukraine(c, x, y, w, h):
    c.rect(x, y, w, h, (226, 214, 196))
    # city skyline
    base = y + h - 30
    for i, bh in enumerate((40, 62, 48, 74, 56, 44)):
        bx = x + 10 + i * 52
        c.rect(bx, base - bh, 42, bh, DARKGREY)
    # smoke columns
    c.circle(x + 90, y + 18, 12, GREY)
    c.circle(x + 104, y + 8, 9, LIGHTGREY)
    c.circle(x + 240, y + 22, 11, GREY)
    # explosion starburst
    ex, ey = x + 170, y + 34
    for dx, dy in ((-18, 0), (18, 0), (0, -14), (0, 14),
                   (-12, -10), (12, -10), (-12, 10), (12, 10)):
        c.line(ex, ey, ex + dx, ey + dy, ORANGE, 4)
    c.circle(ex, ey, 8, YELLOW)
    # sea + burning ship
    c.rect(x, base, w, 30, SEA)
    c.rect(x + 300, base + 6, 130, 14, INK)
    c.rect(x + 340, base - 6, 30, 12, WHITE)
    c.triangle(x + 360, base + 6, x + 372, base - 18, x + 384, base + 6,
               FLAME)


SCENES = (scene_cop31, scene_hormuz, scene_mexico,
          scene_shenzhen, scene_markets, scene_ukraine)

PANELS = [
    ("CLIMATE - ANTALYA", GREEN,
     "COP31 TALKS IN OVERTIME",
     "COP31 DEADLOCKED ON FOSSIL FUELS, TALKS ENTER SECOND DAY OF OVERTIME"),
    ("MIDDLE EAST - HORMUZ", (179, 64, 31),
     "IRAN STRIKES BAHRAIN SITE",
     "TANKERS ATTACKED IN THE STRAIT OF HORMUZ, TEHRAN SETS CONDITIONS"),
    ("AMERICAS - MEXICO", BLUE,
     "EL CHAPO ISIDRO CAPTURED",
     "CARTEL BOSS HELD IN SINALOA, 11 DEAD IN THE RAID"),
    ("DIPLOMACY - SHENZHEN", PURPLE,
     "TRUMP, XI AND PUTIN MEET",
     "THREE LEADERS AGREE TO BEGIN NUCLEAR-RISK TALKS"),
    ("MARKETS - WALL STREET", RED,
     "AI SELL-OFF HITS STOCKS",
     "S&P 500 DOWN 3.7% IN A DAY, NIKKEI FALLS 5.1%"),
    ("EUROPE - UKRAINE", STEEL,
     "MISSILE HITS KRYVYI RIH",
     "2 KILLED IN ZELENSKYY'S HOMETOWN, UKRAINE SETS RUSSIAN SHIP ABLAZE"),
]


def draw_panel(c, x, y, w, h, kicker, color, headline, caption, scene):
    c.rect(x, y, w, h, WHITE)
    c.frame(x, y, w, h, INK, 3)
    # kicker strip
    c.rect(x, y, w, 30, color)
    c.text(x + 10, y + 8, kicker, 2, WHITE)
    # headline, up to two lines
    lines = wrap_text(headline, w - 20, 3)
    for i, line in enumerate(lines[:2]):
        c.text(x + 10, y + 40 + i * 26, line, 3, INK)
    # scene
    sy = y + 96
    scene(c, x + 10, sy, w - 20, 100)
    c.frame(x + 10, sy, w - 20, 100, INK, 2)
    # caption, up to two lines
    clines = wrap_text(caption, w - 20, 2)
    for i, line in enumerate(clines[:2]):
        c.text(x + 10, y + 206 + i * 17, line, 2, INK)


def build():
    c = Canvas(W, H, PAPER)
    c.frame(6, 6, W - 12, H - 12, INK, 5)
    # masthead
    c.text_center(W // 2, 24, "THE WORLD IN ONE DAY", 5, INK)
    c.hline(24, 76, W - 48, INK, 3)
    c.rect(24, 86, W - 48, 56, RED)
    c.text_center(W // 2, 96, "SUNDAY 22 NOVEMBER 2026", 5, WHITE)
    c.hline(24, 150, W - 48, INK, 3)
    c.text_center(W // 2, 158, "SIX STORIES FROM AROUND THE WORLD", 2, INK)
    # panels: 2 columns x 3 rows
    px, py = 16, 180
    pw, ph = 488, 264
    for i, (kicker, color, headline, caption) in enumerate(PANELS):
        x = px + (i % 2) * (pw + 16)
        y = py + (i // 2) * (ph + 14)
        draw_panel(c, x, y, pw, ph, kicker, color, headline, caption,
                   SCENES[i])
    return c


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    canvas = build()
    data = png_bytes(canvas)
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (out, len(data), W, H))


if __name__ == "__main__":
    main()
