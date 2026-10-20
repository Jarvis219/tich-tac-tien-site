#!/usr/bin/env python3
"""Builds every image in assets/ from the app repo and the original art.

Run from anywhere:  python3 scripts/build_assets.py   (needs Pillow with WebP support)

Inputs (override with environment variables):
  APP_DIR    the app repo, default ../tich-tac-tien next to this site
  ART_DIR    1254px originals of mascots, stickers and props, default ~/Downloads
  SHOTS_DIR  iPhone screenshots (1179x2556 PNG), default the capture folder used in October 2026
  IPAD_DIR   iPad screenshots (2048x2732 PNG; landscape captures are stored rotated)
  FONT       Baloo 2 TTF for the Open Graph images, default ../ngu-meter/docs/app-store/fonts/Baloo2.ttf

Writes:
  assets/icon.png (512), assets/apple-touch-icon.png (180), assets/favicon-32.png,
  assets/og-vi.png, assets/og-en.png (1200x630),
  assets/web/icon.webp, assets/mascots/*.webp, assets/stickers/*.webp, assets/props/*.webp,
  assets/screens/*.webp (iPhone 414x898, iPad <= 900px tall).
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(SITE, "assets")
APP = os.environ.get("APP_DIR", os.path.join(SITE, "..", "tich-tac-tien"))
XC = os.path.join(APP, "TichTacTien", "Resources", "Assets.xcassets")
ART = os.environ.get("ART_DIR", os.path.expanduser("~/Downloads"))
_SCRATCH = "/private/tmp/claude-501/-Users-jarvistran-Workplace-My-Project/9bc8a697-abde-45d8-a254-06d0175f6f5c/scratchpad"
SHOTS = os.environ.get("SHOTS_DIR", os.path.join(_SCRATCH, "live"))
IPAD = os.environ.get("IPAD_DIR", os.path.join(_SCRATCH, "ipad2", "air"))
FONT = os.environ.get("FONT", os.path.join(SITE, "..", "ngu-meter", "docs", "app-store", "fonts", "Baloo2.ttf"))

CREAM, INK = (255, 244, 220), (30, 27, 46)
GREEN, AMBER, PINK, LEMON = (46, 208, 107), (255, 176, 32), (255, 143, 177), (255, 228, 92)
PINK_SOFT, LEMON_SOFT, SKY_SOFT = (255, 214, 227), (255, 243, 179), (217, 238, 255)

# Only what the pages use (scripts/check_links.py reports missing files, not unused ones).
MASCOTS = ["idle", "happy", "payday", "toilet", "dead", "scrolling", "waiting", "late",
           "capitalist", "sleeping", "holiday"]
STICKERS = ["kaching", "certified", "offclock", "pending"]
PROPS = ["pho", "milktea", "blindbox", "iphone", "coin", "alarm", "hourglass"]
# name in assets/screens -> source file. Every iPhone shot is the Vietnamese UI.
IPHONE = {
    "salary": "02-onboarding-salary.png", "home": "05-home-ticking.png", "receipt": "08-session-receipt.png",
    "weekly": "10-weekly.png", "late": "12-late-result.png", "after-hours": "19-home-after-hours.png",
    "usd": "18-home-usd.png",
}


def font(size, weight="ExtraBold"):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def trimmed(path):
    """Open a transparent PNG and crop it to its visible pixels (alpha > 8), with a small margin."""
    im = Image.open(path).convert("RGBA")
    box = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    im = im.crop(box)
    pad = max(4, im.width // 60)
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    out.paste(im, (pad, pad))
    return out


def art_source(prefix, name):
    """Prefer the 1254px original; fall back to the 540px copy in the app's asset catalog."""
    big = os.path.join(ART, f"{prefix}_{name}.png")
    if os.path.exists(big):
        return big
    folder = "Mascot" if prefix == "mascot" else "Stickers"
    small = os.path.join(XC, folder, f"{prefix}_{name}.imageset", f"{prefix}_{name}.png")
    if os.path.exists(small):
        return small
    raise FileNotFoundError(big)


def export_art(prefix, names, folder, max_side):
    os.makedirs(os.path.join(OUT, folder), exist_ok=True)
    for n in names:
        im = trimmed(art_source(prefix, n))
        im.thumbnail((max_side, max_side), Image.LANCZOS)
        im.save(os.path.join(OUT, folder, f"{n.replace('_', '-')}.webp"), quality=84, method=6)


def screens():
    out = os.path.join(OUT, "screens")
    os.makedirs(out, exist_ok=True)
    for name, src in IPHONE.items():
        im = Image.open(os.path.join(SHOTS, src)).convert("RGB")
        im = im.resize((414, round(im.height * 414 / im.width)), Image.LANCZOS)
        im.save(os.path.join(out, f"{name}.webp"), quality=80, method=6)
    for name, src, landscape in (("ipad-portrait", "p-04-home.png", False), ("ipad-landscape", "l-04-home.png", True)):
        im = Image.open(os.path.join(IPAD, src)).convert("RGB")
        if landscape and im.height > im.width:  # the simulator saved the landscape capture rotated 90° clockwise
            im = im.rotate(90, expand=True)
        h = 900 if not landscape else 675
        im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
        im.save(os.path.join(out, f"{name}.webp"), quality=80, method=6)


def icons():
    icon = Image.open(os.path.join(XC, "AppIcon.appiconset", "icon.png")).convert("RGB")
    icon.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "icon.png"), optimize=True)
    icon.resize((180, 180), Image.LANCZOS).save(os.path.join(OUT, "apple-touch-icon.png"), optimize=True)
    icon.resize((32, 32), Image.LANCZOS).save(os.path.join(OUT, "favicon-32.png"), optimize=True)
    os.makedirs(os.path.join(OUT, "web"), exist_ok=True)
    icon.resize((192, 192), Image.LANCZOS).save(os.path.join(OUT, "web", "icon.webp"), quality=88, method=6)


def sticker_box(size, fill, radius, shadow=8, border=6):
    """A sticker-book panel: colour fill, thick ink outline, hard offset shadow."""
    w, h = size
    im = Image.new("RGBA", (w + shadow, h + shadow), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([shadow, shadow, w + shadow - 1, h + shadow - 1], radius=radius, fill=INK)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=fill, outline=INK, width=border)
    return im


def og_image(lang, title, tagline, counter, unit_line):
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # Soft sunburst behind the mascot, like the app icon.
    cx, cy = 930, 360
    for i in range(0, 32, 2):
        a0, a1 = 2 * math.pi * i / 32, 2 * math.pi * (i + 1) / 32
        d.polygon([(cx, cy), (cx + 1500 * math.cos(a0), cy + 1500 * math.sin(a0)),
                   (cx + 1500 * math.cos(a1), cy + 1500 * math.sin(a1))], fill=(255, 236, 190))

    icon = Image.open(os.path.join(XC, "AppIcon.appiconset", "icon.png")).convert("RGB").resize((132, 132), Image.LANCZOS)
    frame = sticker_box((144, 144), INK, 34, shadow=7, border=0)
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 131, 131], radius=30, fill=255)
    frame.paste(icon, (6, 6), mask)
    frame = frame.rotate(5, resample=Image.BICUBIC, expand=True)
    img.paste(frame, (60, 46), frame)

    tf, gf, cf, sf = font(84), font(40, "Bold"), font(70), font(28, "SemiBold")
    d.text((236, 92), title, font=tf, fill=INK)
    y = 236
    for line in tagline.split("\n"):
        d.text((66, y), line, font=gf, fill=INK)
        y += 50

    # The ticking counter as a white sticker card.
    tw = d.textlength(counter, font=cf)
    card = sticker_box((int(tw) + 70, 116), (255, 255, 255), 28)
    cd = ImageDraw.Draw(card)
    cd.text((35, 58), counter, font=cf, fill=GREEN, anchor="lm")
    card = card.rotate(-2, resample=Image.BICUBIC, expand=True)
    img.paste(card, (56, y + 18), card)
    d.text((70, y + 162), unit_line, font=sf, fill=(80, 74, 96))

    mascot = trimmed(art_source("mascot", "payday"))
    mascot.thumbnail((440, 440), Image.LANCZOS)
    img.paste(mascot, (cx - mascot.width // 2, cy - mascot.height // 2 + 10), mascot)
    for name, pos, side, rot in (("coin", (1080, 70), 90, 15), ("milktea", (720, 470), 120, -10), ("pho", (1040, 470), 130, 8)):
        p = trimmed(art_source("prop", name))
        p.thumbnail((side, side), Image.LANCZOS)
        p = p.rotate(rot, resample=Image.BICUBIC, expand=True)
        img.paste(p, pos, p)
    img.save(os.path.join(OUT, f"og-{lang}.png"), optimize=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    icons()
    export_art("mascot", MASCOTS, "mascots", 480)
    export_art("sticker", STICKERS, "stickers", 320)
    export_art("prop", PROPS, "props", 240)
    screens()
    og_image("vi", "Tích Tắc Tiền", "Từng giây tích tắc,\ntừng đồng về túi.", "548.775 đ", "29,7 đ mỗi giây · miễn phí · offline")
    og_image("en", "Tick Tock Cash", "Your salary, paid out\none second at a time.", "₫548,775", "29.7 đồng a second · free · offline")
    print("assets built")
