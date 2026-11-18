#!/usr/bin/env python3
"""v2: newspaper front-page formula for news-image-20261117.
Renders a 1024x1024 PNG front page: masthead, 3 hero stories,
numbered grid stories 4-15, world map with dots, briefs 16-22, footer.
All text is drawn with PIL from verified facts only. No network."""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
CARD = (255, 253, 246)
NAVY = (22, 35, 63)
GOLD = (201, 162, 39)
INK = (28, 28, 28)
GREY = (96, 92, 82)
BORDER = (198, 190, 168)
SEA = (221, 232, 238)
LAND = (233, 221, 195)
LAND_EDGE = (172, 157, 122)
RED = (192, 57, 43)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

OUT = sys.argv[1] if len(sys.argv) > 1 else "entry.png"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def badge(d, cx, cy, r, num, fill, fg=(255, 255, 255), outline=None):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
              outline=outline if outline else fill, width=1)
    f = F(SANS_B, 11 if len(str(num)) < 2 else 9)
    tw = d.textlength(str(num), font=f)
    d.text((cx - tw / 2, cy - f.size / 2 - 1), str(num), font=f, fill=fg)


# ---------------------------------------------------------------- map data
MAP = (16, 796, 394, 956)  # x0, y0, x1, y1


def ll(lon, lat):
    x0, y0, x1, y1 = MAP
    x = x0 + (lon + 180) / 360.0 * (x1 - x0)
    y = y0 + (90 - lat) / 180.0 * (y1 - y0)
    return (x, y)


def poly(d, pts, **kw):
    d.polygon([ll(lo, la) for lo, la in pts], **kw)


NORTH_AMERICA = [(-168, 66), (-160, 58), (-152, 58), (-145, 60), (-140, 70),
                 (-130, 71), (-125, 72), (-120, 70), (-110, 68), (-100, 69),
                 (-90, 69), (-85, 66), (-82, 66), (-80, 73), (-76, 72),
                 (-70, 62), (-65, 60), (-60, 55), (-55, 52), (-59, 47),
                 (-65, 44), (-70, 42), (-74, 39), (-76, 35), (-80, 32),
                 (-81, 26), (-84, 30), (-89, 29), (-93, 30), (-97, 26),
                 (-100, 21), (-105, 20), (-110, 23), (-114, 29), (-117, 33),
                 (-122, 37), (-124, 42), (-124, 48), (-128, 52), (-132, 57),
                 (-140, 60), (-150, 60), (-158, 58), (-165, 60), (-168, 66)]
GREENLAND = [(-58, 64), (-52, 60), (-44, 60), (-40, 64), (-32, 68),
             (-24, 70), (-20, 74), (-30, 76), (-45, 76), (-58, 75),
             (-60, 70), (-58, 64)]
SOUTH_AMERICA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
                 (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
                 (-70, -50), (-66, -55), (-68, -52), (-65, -45), (-62, -41),
                 (-58, -35), (-52, -32), (-48, -28), (-41, -23), (-39, -17),
                 (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0),
                 (-52, 4), (-56, 6), (-61, 8), (-66, 10), (-72, 11),
                 (-77, 10), (-79, 9)]
EUROPE = [(-10, 36), (-9, 43), (-2, 48), (-4, 49), (-1, 51), (2, 51),
          (4, 53), (7, 54), (8, 57), (10, 59), (6, 60), (5, 62), (10, 64),
          (13, 66), (18, 69), (24, 71), (30, 70), (34, 68), (40, 67),
          (44, 68), (50, 69), (55, 68), (60, 69), (64, 68), (68, 66),
          (62, 60), (58, 55), (53, 51), (48, 48), (44, 47), (40, 47),
          (38, 46), (35, 45), (33, 44), (29, 44), (26, 40), (23, 38),
          (22, 37), (21, 40), (19, 41), (16, 44), (13, 45), (10, 44),
          (7, 44), (3, 43), (0, 40), (-2, 37), (-6, 36), (-10, 36)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
          (-12, 8), (-8, 4), (-4, 5), (2, 6), (6, 4), (9, 4), (12, 0),
          (13, -5), (12, -10), (13, -15), (12, -18), (14, -22), (16, -28),
          (18, -32), (20, -35), (25, -34), (28, -32), (32, -28), (35, -24),
          (36, -20), (40, -15), (40, -10), (42, -5), (44, -2), (46, 0),
          (48, 2), (51, 11), (48, 11), (44, 11), (43, 12), (40, 15),
          (38, 18), (37, 20), (35, 23), (33, 27), (32, 31), (30, 32),
          (25, 32), (20, 32), (15, 32), (10, 34), (5, 37), (0, 36),
          (-6, 35)]
ASIA = [(30, 36), (36, 36), (40, 38), (44, 40), (48, 38), (52, 40),
        (56, 38), (60, 40), (64, 38), (68, 40), (72, 42), (76, 44),
        (80, 46), (85, 48), (90, 50), (95, 52), (100, 55), (105, 56),
        (110, 58), (115, 59), (120, 60), (125, 62), (130, 62), (135, 60),
        (140, 60), (142, 56), (140, 50), (142, 45), (140, 42), (138, 38),
        (135, 35), (131, 33), (128, 34), (126, 38), (122, 38), (121, 32),
        (120, 28), (118, 25), (115, 22), (111, 21), (108, 18), (106, 14),
        (104, 9), (101, 8), (99, 10), (97, 15), (94, 17), (92, 21),
        (90, 22), (88, 22), (86, 20), (84, 19), (81, 16), (79, 13),
        (77, 9), (76, 13), (74, 16), (72, 20), (69, 22), (67, 24),
        (64, 25), (61, 25), (58, 26), (56, 27), (54, 26), (52, 28),
        (50, 29), (48, 30), (45, 29), (43, 28), (41, 30), (39, 31),
        (37, 33), (35, 35), (33, 36), (30, 36)]
ARABIA = [(43, 29), (46, 29), (49, 30), (52, 27), (55, 25), (58, 22),
          (56, 19), (54, 16), (51, 14), (48, 14), (45, 13), (43, 15),
          (41, 18), (39, 21), (38, 25), (40, 28), (43, 29)]
INDIA = [(68, 23), (70, 21), (72, 19), (74, 15), (76, 9), (78, 8),
         (80, 10), (80, 14), (82, 17), (85, 19), (88, 22), (86, 21),
         (82, 20), (78, 20), (74, 22), (70, 23), (68, 23)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 36), (140, 38),
         (141, 41), (142, 44), (144, 44), (142, 42), (140, 39), (138, 36),
         (136, 34), (133, 33), (130, 31)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 54),
      (0, 51), (-2, 50), (-5, 50)]
AUSTRALIA = [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (142, -39), (145, -38), (147, -39), (150, -37), (153, -32),
             (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
             (140, -17), (136, -15), (135, -12), (132, -12), (130, -13),
             (126, -14), (122, -17), (118, -20), (113, -22)]
NEW_ZEALAND = [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
               (175, -41), (172, -43), (169, -46), (167, -45)]

# (num, lon, lat, dx, dy) — dx/dy nudge the dot so clusters don't overlap;
# a thin leader line joins the dot to its true position.
DOTS = [
    (1, 36.0, 45.0, -4, 0),
    (2, 50.5, 26.0, 0, 0),
    (3, 114.0, 22.5, 0, 0),
    (4, 140.0, 38.0, 0, 0),
    (5, 30.0, -2.0, 0, 0),
    (6, 116.0, 40.0, 5, -7),
    (7, 34.5, 31.8, -4, 6),
    (8, 36.0, 32.5, 15, -13),
    (9, 2.3, 48.9, -3, 4),
    (10, 45.0, 12.8, 12, 14),
    (11, 6.1, 46.2, -1, -19),
    (12, -80.0, 37.0, -17, 14),
    (13, -74.0, 40.5, 13, -13),
    (14, 25.0, 58.5, 6, -8),
    (15, -77.0, 38.9, 0, 0),
]

# ---------------------------------------------------------------- content
HEROES = [
    dict(num=1, color=(169, 50, 38), kicker="UKRAINE WAR",
         head="Ukraine strikes Crimean Bridge for a second day",
         sub="A section of the road bridge collapses; Zelenskyy hails an "
             "\u2018unprecedented operation\u2019. Russia hits Kyiv bridges."),
    dict(num=2, color=(31, 97, 141), kicker="IRAN WAR",
         head="Iran fires drones at a US radar in Bahrain",
         sub="Tehran says it hit the Sheikh Isa radar; Bahrain says all "
             "drones were intercepted, no damage."),
    dict(num=3, color=(125, 102, 8), kicker="DIPLOMACY \u00b7 APEC",
         head="APEC leaders gather ahead of a Trump\u2013Xi\u2013Putin summit",
         sub="The first three-way summit is set for Thursday in Shenzhen; "
             "denuclearisation, Iran, Ukraine and trade on the agenda."),
]

GRID = [
    dict(num=4, color=(146, 43, 33), kicker="JAPAN \u00b7 AIRSPACE",
         head="Suspected Russian jets enter Japanese airspace",
         sub="Tokyo scrambles fighters and protests."),
    dict(num=5, color=(30, 132, 73), kicker="EUROPE \u00b7 MIGRATION",
         head="Five EU states plan a migrant return hub in Rwanda",
         sub="First transfers in 2027; rights groups object."),
    dict(num=6, color=(125, 60, 152), kicker="CANADA \u00b7 CHINA",
         head="Xi and Carney agree new tariff cuts",
         sub="China cuts duties on C$400m of pork and seafood; Canada "
             "extends steel relief."),
    dict(num=7, color=(169, 50, 38), kicker="ISRAEL \u00b7 POLITICS",
         head="Netanyahu faces inquiry calls over election-day arrests",
         sub="His office is alleged to have tipped police against Arab "
             "party workers."),
    dict(num=8, color=(31, 97, 141), kicker="UNITED KINGDOM \u00b7 WEST BANK",
         head="UK sanctions eight settlement builders",
         sub="Freezes target West Bank builders and a group accused of "
             "blocking Gaza aid."),
    dict(num=9, color=(125, 102, 8), kicker="FRANCE \u00b7 COURTS",
         head="Depardieu drops appeal and accepts assault conviction",
         sub="Actor withdraws his challenge to a sexual assault conviction "
             "in a Paris court."),
    dict(num=10, color=(146, 43, 33), kicker="YEMEN \u00b7 WAR",
         head="Houthis advance as Yemeni forces retreat to defend Aden",
         sub="Forces pull back from the Red Sea coast to defend Aden."),
    dict(num=11, color=(30, 132, 73), kicker="GLOBAL \u00b7 ARMS",
         head="Geneva talks on \u2018killer robots\u2019 open",
         sub="Delegates of 128 states meet at the UN in Geneva to weigh a "
             "treaty banning lethal autonomous weapons."),
    dict(num=12, color=(125, 60, 152), kicker="UNITED STATES \u00b7 SECURITY",
         head="US officials say Iran weighs a \u2018dirty bomb\u2019 plot",
         sub="US intelligence says Iran is developing plans to target Trump "
             "aides; the claim is unconfirmed."),
    dict(num=13, color=(17, 122, 101), kicker="ASIA \u00b7 TECHNOLOGY",
         head="US moves to close AI chip loophole",
         sub="Commerce acts to stop China renting US computing power."),
    dict(num=14, color=(31, 97, 141), kicker="EUROPE",
         head="Estonia to shut Russia border",
         sub="Crossings close 1 December after a foiled bomb plot on a "
             "drone plant."),
    dict(num=15, color=(146, 43, 33), kicker="UNITED STATES",
         head="Pentagon fails audit for ninth year",
         sub="$4.8 trillion in assets could not be verified."),
]

BRIEFS = [
    (16, "Gaza", "UK, Australia, Canada and Italy urge Israel to open Gaza crossings."),
    (17, "Hormuz", "Third US carrier, USS Theodore Roosevelt, joins the Gulf force."),
    (18, "Trump", "Arrives in Manila for the ASEAN summit before his China meetings."),
    (19, "Microsoft", "Explains last week\u2019s global outage \u2014 a latent defect knocked out 80% of servers."),
    (20, "White House", "Orders every federal agency to get its approval before any employee testifies to Congress."),
    (21, "Health", "Thirteen babies born with measles in the US as cases reach their highest total since 1991."),
    (22, "Fuel", "US petrol averages $3.78 a gallon, down about 20 cents in a week."),
]

# ---------------------------------------------------------------- icons
def icon_box(d, x, y, s, bg):
    d.rectangle([x, y, x + s, y + s], fill=bg, outline=BORDER, width=1)


def draw_icon(d, num, x, y, s):
    """Simple drawn icon inside a square at (x, y) of size s."""
    import math
    cx, cy = x + s // 2, y + s // 2
    if num == 4:  # jet + red sun
        d.ellipse([x + 6, y + 6, x + 18, y + 18], fill=(192, 57, 43))
        d.polygon([(x + 12, cy + 2), (x + 44, cy - 4), (x + 44, cy + 4),
                   (x + 12, cy + 8)], fill=(60, 60, 60))
        d.polygon([(x + 20, cy + 2), (x + 28, cy - 8), (x + 32, cy + 2)],
                  fill=(60, 60, 60))
        d.polygon([(x + 20, cy + 6), (x + 28, cy + 14), (x + 32, cy + 6)],
                  fill=(60, 60, 60))
    elif num == 5:  # house + arrow
        d.polygon([(x + 10, cy + 2), (cx, y + 8), (x + s - 10, cy + 2),
                   (x + s - 10, cy + 8), (x + 10, cy + 8)], fill=(125, 102, 8))
        d.rectangle([x + 14, cy + 6, x + s - 14, y + s - 8], fill=(180, 150, 90))
        d.rectangle([cx - 4, cy + 12, cx + 4, y + s - 8], fill=(60, 45, 30))
        d.line([x + s - 12, cy - 8, x + s - 4, cy - 8, x + s - 4, cy],
               fill=(30, 132, 73), width=2)
    elif num == 6:  # chart + arrow
        d.line([x + 10, y + s - 12, x + 20, y + s - 22, x + 28, y + s - 18,
                x + 38, y + 12], fill=(30, 132, 73), width=3)
        d.polygon([(x + 38, y + 12), (x + 32, y + 14), (x + 38, y + 20)],
                  fill=(30, 132, 73))
        d.rectangle([x + 10, y + s - 10, x + 14, y + s - 8], fill=(192, 57, 43))
        d.rectangle([x + 20, y + s - 10, x + 24, y + s - 8], fill=(192, 57, 43))
    elif num == 7:  # ballot box
        d.rectangle([x + 10, cy - 2, x + s - 10, y + s - 10], fill=(125, 60, 152))
        d.rectangle([x + 8, cy - 8, x + s - 8, cy - 2], fill=(90, 40, 115))
        d.line([x + 16, cy + 8, x + 22, cy + 16, x + 34, cy - 2],
               fill=(255, 255, 255), width=3)
    elif num == 8:  # house + prohibition
        d.polygon([(x + 10, cy), (cx, y + 8), (x + s - 10, cy),
                   (x + s - 10, cy + 6), (x + 10, cy + 6)], fill=(90, 90, 90))
        d.rectangle([x + 13, cy + 4, x + s - 13, y + s - 8], fill=(200, 190, 170))
        d.ellipse([x + 26, y + 24, x + 44, y + 42], outline=(192, 57, 43), width=3)
        d.line([x + 28, y + 40, x + 42, y + 26], fill=(192, 57, 43), width=3)
    elif num == 9:  # courthouse
        d.polygon([(x + 8, cy - 4), (cx, y + 8), (x + s - 8, cy - 4)],
                  fill=(125, 102, 8))
        for i in range(3):
            px = x + 13 + i * 11
            d.rectangle([px, cy + 2, px + 5, y + s - 12], fill=(120, 110, 95))
        d.rectangle([x + 8, y + s - 12, x + s - 8, y + s - 8], fill=(120, 110, 95))
    elif num == 10:  # dunes + sun
        d.ellipse([x + 32, y + 8, x + 44, y + 20], fill=(230, 180, 60))
        d.polygon([(x + 6, y + s - 8), (x + 18, cy + 4), (x + 30, y + s - 8)],
                  fill=(210, 170, 110))
        d.polygon([(x + 22, y + s - 8), (x + 36, cy + 8), (x + 46, y + s - 8)],
                  fill=(190, 150, 95))
    elif num == 11:  # robot
        d.rectangle([x + 13, cy - 6, x + s - 13, y + s - 10], fill=(120, 130, 140),
                    outline=(70, 80, 90), width=1)
        d.line([cx, y + 8, cx, cy - 6], fill=(70, 80, 90), width=2)
        d.ellipse([cx - 3, y + 5, cx + 3, y + 11], fill=(192, 57, 43))
        d.ellipse([x + 19, cy + 2, x + 25, cy + 8], fill=(192, 57, 43))
        d.ellipse([x + 31, cy + 2, x + 37, cy + 8], fill=(192, 57, 43))
        d.line([x + 20, cy + 16, x + 36, cy + 16], fill=(70, 80, 90), width=2)
    elif num == 12:  # shield + trefoil
        d.polygon([(cx, y + 8), (x + s - 10, y + 14), (x + s - 10, cy + 6),
                   (cx, y + s - 8), (x + 10, cy + 6), (x + 10, y + 14)],
                  outline=(31, 97, 141), width=3)
        d.ellipse([cx - 3, cy - 2, cx + 3, cy + 4], fill=(192, 57, 43))
        for ang in (90, 210, 330):
            r = math.radians(ang)
            ex, ey = cx + 9 * math.cos(r), cy + 9 * math.sin(r)
            d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(192, 57, 43))
    elif num == 13:  # chip
        d.rectangle([x + 14, y + 14, x + s - 14, y + s - 14], fill=(31, 97, 141),
                    outline=(20, 60, 90), width=1)
        d.rectangle([x + 20, y + 20, x + s - 20, y + s - 20], fill=(180, 220, 240))
        for i in range(3):
            d.line([x + 14 + i * 9, y + 8, x + 14 + i * 9, y + 14],
                   fill=(60, 60, 60), width=2)
            d.line([x + 14 + i * 9, y + s - 14, x + 14 + i * 9, y + s - 8],
                   fill=(60, 60, 60), width=2)
    elif num == 14:  # border fence
        for i in range(5):
            px = x + 10 + i * 8
            d.line([px, y + 10, px, y + s - 10], fill=(70, 70, 70), width=2)
        d.line([x + 8, y + 14, x + s - 8, y + 14], fill=(70, 70, 70), width=2)
        d.line([x + 8, y + s - 14, x + s - 8, y + s - 14], fill=(70, 70, 70), width=2)
        d.line([x + 14, y + 18, x + 38, y + 38], fill=(146, 43, 33), width=3)
        d.line([x + 38, y + 18, x + 14, y + 38], fill=(146, 43, 33), width=3)
    elif num == 15:  # ledger + magnifier
        d.rectangle([x + 8, y + 12, x + 32, y + s - 10], fill=(255, 255, 255),
                    outline=(70, 70, 70), width=2)
        for i in range(3):
            d.line([x + 12, y + 18 + i * 7, x + 28, y + 18 + i * 7],
                   fill=(31, 97, 141), width=2)
        d.ellipse([x + 28, y + 24, x + 44, y + 40], outline=(192, 57, 43), width=3)
        d.line([x + 41, y + 37, x + 47, y + 43], fill=(192, 57, 43), width=3)


# ---------------------------------------------------------------- hero art
def hero_art(d, num, x, y, w, h):
    import math
    if num == 1:  # bridge over water, smoke + blast at mid-span
        d.rectangle([x, y, x + w, y + h], fill=(215, 230, 239))
        d.rectangle([x, y + h - 20, x + w, y + h], fill=(46, 109, 164))
        for i in range(6):
            wx = x + 12 + i * 52
            d.arc([wx, y + h - 18, wx + 34, y + h - 2], 180, 360,
                  fill=(255, 255, 255), width=2)
        # deck, broken at mid-span (collapse gap)
        d.rectangle([x, y + 46, x + w // 2 - 28, y + 52], fill=(70, 70, 70))
        d.rectangle([x + w // 2 + 28, y + 46, x + w, y + 52], fill=(70, 70, 70))
        d.arc([x + 40, y - 6, x + w - 40, y + 52], 180, 360,
              fill=(176, 58, 46), width=6)
        d.rectangle([x + w // 2 - 5, y + 18, x + w // 2 + 5, y + 46],
                    fill=(90, 90, 90))
        for sx, sy, r in [(x + w // 2 - 26, y + 12, 11), (x + w // 2 - 8, y + 4, 13),
                          (x + w // 2 + 14, y + 12, 10)]:
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(120, 120, 120))
        bx, by = x + w // 2 + 6, y + 26
        for ang in range(0, 360, 30):
            r = math.radians(ang)
            d.line([bx, by, bx + 13 * math.cos(r), by + 13 * math.sin(r)],
                   fill=(230, 140, 30), width=2)
        d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 200, 60))
        for dx, dy in [(x + 60, y + 58), (x + w - 70, y + 60),
                       (x + w // 2 + 40, y + 58)]:
            d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 255, 255))
    elif num == 2:  # radar dish + drones
        d.rectangle([x, y, x + w, y + h], fill=(220, 235, 245))
        d.ellipse([x + w - 62, y + 6, x + w - 30, y + 38], fill=(250, 225, 140))
        d.rectangle([x, y + h - 14, x + w, y + h], fill=(201, 184, 150))
        rx, ry = x + 62, y + 46
        d.pieslice([rx - 30, ry - 30, rx + 30, ry + 30], 180, 360,
                   fill=(240, 240, 240), outline=(90, 90, 90), width=2)
        d.line([rx, ry, rx + 26, ry - 24], fill=(90, 90, 90), width=2)
        d.rectangle([rx - 3, ry, rx + 3, y + h - 14], fill=(90, 90, 90))
        for dx, dy, s in [(x + 150, y + 18, 1.0), (x + 210, y + 34, 0.8),
                          (x + 265, y + 14, 0.9)]:
            d.ellipse([dx - 7 * s, dy - 3 * s, dx + 7 * s, dy + 3 * s],
                      fill=(50, 50, 50))
            d.line([dx - 11 * s, dy - 6 * s, dx + 11 * s, dy - 6 * s],
                   fill=(50, 50, 50), width=2)
            d.line([dx - 11 * s, dy + 6 * s, dx + 11 * s, dy + 6 * s],
                   fill=(50, 50, 50), width=2)
        for i in range(0, 130, 14):
            d.line([x + 150 + i, y + 30 + i // 6, x + 158 + i, y + 31 + i // 6],
                   fill=(140, 140, 140), width=1)
    else:  # three flags + skyline
        d.rectangle([x, y, x + w, y + h], fill=(223, 233, 242))
        for bx, bw, bh in [(x + 8, 34, 22), (x + 48, 26, 30), (x + 80, 40, 18),
                           (x + 200, 30, 26), (x + 236, 36, 20), (x + 278, 28, 30)]:
            d.rectangle([bx, y + h - 16 - bh, bx + bw, y + h - 16],
                        fill=(170, 180, 195))
        d.rectangle([x, y + h - 16, x + w, y + h], fill=(176, 140, 100))
        for i, code in enumerate(("US", "CN", "RU")):
            px = x + 58 + i * 108
            d.line([px, y + 10, px, y + h - 16], fill=(60, 60, 60), width=3)
            fx, fy = px + 3, y + 12
            if code == "US":
                for s in range(5):
                    d.rectangle([fx, fy + s * 7, fx + 62, fy + s * 7 + 3],
                                fill=(176, 58, 46) if s % 2 == 0 else (255, 255, 255))
                d.rectangle([fx, fy, fx + 26, fy + 18], fill=(31, 60, 120))
            elif code == "CN":
                d.rectangle([fx, fy, fx + 62, fy + 34], fill=(222, 40, 40))
                d.ellipse([fx + 6, fy + 6, fx + 18, fy + 18], fill=(255, 220, 60))
            else:
                d.rectangle([fx, fy, fx + 62, fy + 11], fill=(255, 255, 255))
                d.rectangle([fx, fy + 11, fx + 62, fy + 22], fill=(31, 97, 141))
                d.rectangle([fx, fy + 22, fx + 62, fy + 34], fill=(192, 57, 43))
            label = ("TRUMP", "XI", "PUTIN")[i]
            f = F(SANS_B, 10)
            tw = d.textlength(label, font=f)
            d.rectangle([px - 8, y + h - 14, px - 8 + tw + 12, y + h - 2],
                        fill=(30, 30, 30))
            d.text((px - 2, y + h - 14), label, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- build
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.rectangle([0, 0, W, 106], fill=NAVY)
    d.text((14, 10), "THE DAY IN WORLD NEWS", font=F(SANS_B, 13), fill=GOLD)
    d.text((12, 30), "Tuesday 17 November 2026", font=F(SERIF_B, 48),
           fill=(255, 255, 255))
    d.text((1010, 10), "22 STORIES \u00b7 4 CONTINENTS \u00b7 ONE DAY",
           font=F(SANS_B, 13), fill=(255, 255, 255), anchor="ra")
    legend = [("N. America", (192, 57, 43)), ("Europe", (52, 120, 180)),
              ("Africa", (30, 132, 73)), ("Asia", (20, 143, 119))]
    for i, (name, col) in enumerate(legend):
        row, ci = i // 2, i % 2
        f = F(SANS, 11)
        tw = d.textlength(name, font=f)
        x = 1010 if ci == 1 else 1010 - 118
        y = 40 + row * 18
        d.ellipse([x - tw - 14, y + 2, x - tw - 4, y + 12], fill=col)
        d.text((x - tw, y), name, font=f, fill=(220, 220, 220))
    d.rectangle([0, 104, W, 107], fill=GOLD)

    # ---- heroes
    hx, hy, hw, hh, gap = 12, 114, 324, 208, 14
    for i, s in enumerate(HEROES):
        x = hx + i * (hw + gap)
        d.rectangle([x, hy, x + hw, hy + hh], fill=CARD, outline=BORDER, width=1)
        hero_art(d, s["num"], x + 1, hy + 1, hw - 2, 76)
        badge(d, x + 16, hy + 16, 11, s["num"], NAVY, outline=GOLD)
        d.text((x + 12, hy + 84), s["kicker"], font=F(SANS_B, 13), fill=s["color"])
        ycur = hy + 104
        hsize = 22
        hlines = wrap(d, s["head"], F(SERIF_B, hsize), hw - 24)
        while len(hlines) > 2 and hsize > 17:
            hsize -= 1
            hlines = wrap(d, s["head"], F(SERIF_B, hsize), hw - 24)
        for line in hlines:
            d.text((x + 12, ycur), line, font=F(SERIF_B, hsize), fill=INK)
            ycur += hsize + 5
        ycur += 4
        for line in wrap(d, s["sub"], F(SANS, 13), hw - 24):
            d.text((x + 12, ycur), line, font=F(SANS, 13), fill=(60, 58, 50))
            ycur += 16

    # ---- numbered grid 4-15
    gx, gy, cw, chh = 12, 330, 244, 140
    for i, s in enumerate(GRID):
        x = gx + (i % 4) * (cw + 8)
        y = gy + (i // 4) * (chh + 6)
        d.rectangle([x, y, x + cw, y + chh], fill=CARD, outline=BORDER, width=1)
        badge(d, x + 13, y + 13, 11, s["num"], s["color"])
        d.text((x + 30, y + 6), s["kicker"], font=F(SANS_B, 11), fill=s["color"])
        icon_box(d, x + 10, y + 32, 50, (240, 234, 220))
        draw_icon(d, s["num"], x + 10, y + 32, 50)
        ycur = y + 30
        for line in wrap(d, s["head"], F(SANS_B, 14), cw - 78)[:3]:
            d.text((x + 68, ycur), line, font=F(SANS_B, 14), fill=INK)
            ycur += 18
        ycur = y + 88
        for line in wrap(d, s["sub"], F(SANS, 11), cw - 20)[:3]:
            d.text((x + 10, ycur), line, font=F(SANS, 11), fill=(60, 58, 50))
            ycur += 14

    # ---- bottom rule + section headers
    d.rectangle([12, 768, W - 12, 771], fill=NAVY)
    d.text((16, 774), "WHERE IT HAPPENED", font=F(SANS_B, 15), fill=INK)
    d.text((16, 790), "numbers = stories 1\u201315", font=F(SANS, 11), fill=GREY)
    d.text((410, 774), "ALSO ON TUESDAY 17 NOVEMBER", font=F(SANS_B, 15), fill=INK)

    # ---- map
    x0, y0, x1, y1 = MAP
    d.rectangle([x0, y0, x1, y1], fill=SEA, outline=BORDER, width=1)
    for pts in (NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, EUROPE, AFRICA,
                ASIA, ARABIA, INDIA, JAPAN, UK, AUSTRALIA, NEW_ZEALAND):
        poly(d, pts, fill=LAND, outline=LAND_EDGE)
    for lo, la in [(100, 0), (110, -3), (122, -6), (130, -4)]:
        cx, cy = ll(lo, la)
        d.ellipse([cx - 4, cy - 2, cx + 4, cy + 2], fill=LAND, outline=LAND_EDGE)
    for num, lon, lat, dx, dy in DOTS:
        tx, ty = ll(lon, lat)
        if dx or dy:
            d.line([tx, ty, tx + dx, ty + dy], fill=(120, 120, 120), width=1)
    for num, lon, lat, dx, dy in DOTS:
        tx, ty = ll(lon, lat)
        badge(d, tx + dx, ty + dy, 8, num, RED)

    # ---- briefs, two columns
    cols = [BRIEFS[:4], BRIEFS[4:]]
    for ci, col in enumerate(cols):
        bx = 410 + ci * 306
        ycur = 796
        for num, label, text in col:
            badge(d, bx + 10, ycur + 9, 9, num, (14, 124, 102))
            lf = F(SANS_B, 11)
            bf = F(SANS, 11)
            full = label + ": " + text
            lines = wrap(d, full, bf, 262)
            ly = ycur
            for li, line in enumerate(lines[:3]):
                if li == 0:
                    lab = label + ":"
                    d.text((bx + 26, ly), lab, font=lf, fill=INK)
                    rest = line[len(lab):].strip()
                    d.text((bx + 26 + d.textlength(lab, font=lf) + 4, ly),
                           rest, font=bf, fill=(50, 48, 42))
                else:
                    d.text((bx + 26, ly), line, font=bf, fill=(50, 48, 42))
                ly += 14
            ycur = max(ycur + 36, ly + 8)

    # ---- footer
    d.rectangle([12, 962, W - 12, 964], fill=NAVY)
    d.text((12, 970),
           "Every story happened or was first reported on Tuesday 17 November 2026. "
           "Disputed claims are attributed.",
           font=F(SANS, 12), fill=GREY)
    d.text((12, 988),
           "Sources: Reuters \u00b7 Al Jazeera \u00b7 CNN \u00b7 NPR \u00b7 AP. "
           "Original drawings.",
           font=F(SANS, 12), fill=GREY)

    img.save(OUT)
    print("wrote", OUT, img.size, "bytes:",
          __import__("os").path.getsize(OUT))


if __name__ == "__main__":
    main()
