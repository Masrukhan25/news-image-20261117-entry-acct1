#!/usr/bin/env python3
"""Render the news-image-20261117 entry: a 1024x1024 front-page infographic
summing up Tuesday 17 November 2026 world news. Drawn entirely with PIL
shapes and DejaVu Sans text. Run: python3 draw.py [output.png]"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BG = (10, 26, 51)
PANEL = (19, 43, 82)
PANEL_LINE = (35, 64, 110)
WHITE = (255, 255, 255)
SUB = (195, 210, 234)
GOLD = (242, 183, 5)

SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

STORIES = [
    {
        "tag": "EUROPE / CONFLICT",
        "headline": "Ukraine hits Crimean Bridge again",
        "sub": "Second strike in two days; Russia hits Kyiv bridges too",
        "accent": (242, 183, 5),
        "icon": "bridge",
    },
    {
        "tag": "MIDDLE EAST / SHIPPING",
        "headline": "Tankers hit by mines near Hormuz",
        "sub": "Iran drone attack on US radar in Bahrain intercepted, no damage",
        "accent": (255, 107, 53),
        "icon": "tanker",
    },
    {
        "tag": "DIPLOMACY",
        "headline": "Xi, Trump & Putin to meet in Shenzhen",
        "sub": "Three-way summit confirmed for Thursday 19 November",
        "accent": (23, 195, 165),
        "icon": "summit",
    },
    {
        "tag": "ASIA-PACIFIC",
        "headline": "Japan scrambles fighter jets",
        "sub": "Suspected Russian aircraft violate airspace",
        "accent": (77, 163, 255),
        "icon": "jets",
    },
    {
        "tag": "EUROPE",
        "headline": "Estonia to shut Russia border",
        "sub": "Crossings close 1 December after foiled bomb plot",
        "accent": (160, 107, 255),
        "icon": "fence",
    },
    {
        "tag": "UNITED STATES",
        "headline": "Pentagon fails audit, 9th year in a row",
        "sub": "$4.8 trillion in assets could not be verified",
        "accent": (255, 92, 138),
        "icon": "ledger",
    },
]


def wrap(d, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(d, text, path, size, max_w, max_lines, min_size):
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if len(wrap(d, text, f, max_w)) <= max_lines:
            return f
        size -= 1
    return ImageFont.truetype(path, min_size)


def icon_bridge(d, x, y, w, h, c):
    d.line([(x + 6, y + 46), (x + w - 6, y + 46)], fill=WHITE, width=4)
    d.line([(x + 22, y + 16), (x + 22, y + 46)], fill=WHITE, width=4)
    d.line([(x + w - 22, y + 16), (x + w - 22, y + 46)], fill=WHITE, width=4)
    d.line([(x + 22, y + 16), (x + w // 2, y + 46)], fill=c, width=2)
    d.line([(x + w - 22, y + 16), (x + w // 2, y + 46)], fill=c, width=2)
    cx, cy = x + w // 2, y + 26
    for dx, dy in [(0, -10), (7, -7), (10, 0), (7, 7), (0, 10), (-7, 7),
                   (-10, 0), (-7, -7)]:
        d.line([(cx, cy), (cx + dx, cy + dy)], fill=GOLD, width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=GOLD)


def icon_tanker(d, x, y, w, h, c):
    d.polygon([(x + 6, y + 34), (x + w - 6, y + 34), (x + w - 14, y + 52),
               (x + 14, y + 52)], fill=c)
    d.rectangle([x + w - 32, y + 20, x + w - 14, y + 34], fill=WHITE)
    d.rectangle([x + w - 28, y + 12, x + w - 22, y + 20], fill=WHITE)
    for wy in (54, 60):
        for ax in range(x + 4, x + w - 12, 16):
            d.arc([ax, y + wy, ax + 16, y + wy + 10], start=180, end=360,
                  fill=WHITE, width=2)
    mx, my = x + 14, y + 14
    for dx, dy in [(0, -8), (6, -6), (8, 0), (6, 6), (0, 8), (-6, 6),
                   (-8, 0), (-6, -6)]:
        d.line([(mx, my), (mx + dx, my + dy)], fill=c, width=2)
    d.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=c)


def icon_summit(d, x, y, w, h, c):
    cols = [c, WHITE, GOLD]
    for i, col in enumerate(cols):
        px = x + 16 + i * 28
        d.line([(px, y + 12), (px, y + 54)], fill=WHITE, width=3)
        d.polygon([(px, y + 12), (px + 20, y + 18), (px, y + 24)], fill=col)
    d.line([(x + 6, y + 54), (x + w - 6, y + 54)], fill=WHITE, width=3)


def icon_jets(d, x, y, w, h, c):
    d.polygon([(x + 8, y + 50), (x + 30, y + 14), (x + 36, y + 42),
               (x + 50, y + 30), (x + 38, y + 52)], fill=WHITE)
    d.polygon([(x + 44, y + 40), (x + 60, y + 12), (x + 64, y + 32),
               (x + 74, y + 24), (x + 66, y + 42)], fill=c)
    d.line([(x + 4, y + 56), (x + 22, y + 56)], fill=WHITE, width=2)
    d.line([(x + 34, y + 58), (x + 52, y + 58)], fill=c, width=2)


def icon_fence(d, x, y, w, h, c):
    d.line([(x + 6, y + 22), (x + w - 6, y + 22)], fill=WHITE, width=3)
    d.line([(x + 6, y + 46), (x + w - 6, y + 46)], fill=WHITE, width=3)
    for bx in range(x + 10, x + w - 8, 13):
        d.line([(bx, y + 14), (bx, y + 56)], fill=WHITE, width=3)
        d.polygon([(bx - 3, y + 14), (bx + 3, y + 14), (bx, y + 8)], fill=WHITE)
    d.line([(x + 28, y + 26), (x + 60, y + 50)], fill=c, width=5)
    d.line([(x + 60, y + 26), (x + 28, y + 50)], fill=c, width=5)


def icon_ledger(d, x, y, w, h, c):
    d.rounded_rectangle([x + 8, y + 10, x + 52, y + 54], radius=4,
                        outline=WHITE, width=3)
    for ly in (22, 32, 42):
        d.line([(x + 16, y + ly), (x + 44, y + ly)], fill=SUB, width=2)
    d.line([(x + 20, y + 22), (x + 32, y + 34)], fill=c, width=3)
    d.line([(x + 32, y + 22), (x + 20, y + 34)], fill=c, width=3)
    d.ellipse([x + 52, y + 34, x + 78, y + 60], outline=c, width=4)
    d.line([(x + 72, y + 54), (x + 82, y + 64)], fill=c, width=4)


ICONS = {
    "bridge": icon_bridge,
    "tanker": icon_tanker,
    "summit": icon_summit,
    "jets": icon_jets,
    "fence": icon_fence,
    "ledger": icon_ledger,
}


def draw_panel(d, x, y, w, h, story):
    accent = story["accent"]
    d.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=PANEL,
                        outline=PANEL_LINE, width=2)
    d.rounded_rectangle([x, y, x + 7, y + h], radius=3, fill=accent)
    tx = x + 24
    tw = w - 48
    tag_f = ImageFont.truetype(SANS_B, 18)
    hl_f = fit_font(d, story["headline"], SANS_B, 33, tw, 2, 27)
    sub_f = fit_font(d, story["sub"], SANS, 21, tw, 2, 17)
    hl_lines = wrap(d, story["headline"], hl_f, tw)
    sub_lines = wrap(d, story["sub"], sub_f, tw)
    block = 22 + 44 + len(hl_lines) * 41 + 10 + len(sub_lines) * 29
    cy = y + (h - block) // 2
    d.text((tx, cy), story["tag"], font=tag_f, fill=accent)
    ICONS[story["icon"]](d, x + w - 108, cy - 8, 92, 66, accent)
    hy = cy + 66
    for line in hl_lines:
        d.text((tx, hy), line, font=hl_f, fill=WHITE)
        hy += 41
    sy = hy + 10
    for line in sub_lines:
        d.text((tx, sy), line, font=sub_f, fill=SUB)
        sy += 29


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    date_f = fit_font(d, "TUESDAY, 17 NOVEMBER 2026", SANS_B, 54, 850, 1, 40)
    d.text((32, 26), "TUESDAY, 17 NOVEMBER 2026", font=date_f, fill=WHITE)
    sub_f = ImageFont.truetype(SANS_B, 23)
    spaced = " ".join("WORLD NEWS IN ONE IMAGE")
    d.text((34, 102), spaced, font=sub_f, fill=GOLD)
    gx, gy, gr = 898, 30, 42
    d.ellipse([gx, gy, gx + 2 * gr, gy + 2 * gr], outline=GOLD, width=3)
    d.ellipse([gx + 15, gy, gx + 2 * gr - 15, gy + 2 * gr], outline=GOLD,
              width=2)
    d.line([(gx, gy + gr), (gx + 2 * gr, gy + gr)], fill=GOLD, width=2)
    d.rectangle([32, 146, 992, 149], fill=GOLD)
    margin, gap = 24, 16
    top = 166
    pw = (W - 2 * margin - gap) // 2
    ph = (1000 - top - 2 * gap) // 3
    for i, story in enumerate(STORIES):
        col, row = i % 2, i // 2
        px = margin + col * (pw + gap)
        py = top + row * (ph + gap)
        draw_panel(d, px, py, pw, ph, story)
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
