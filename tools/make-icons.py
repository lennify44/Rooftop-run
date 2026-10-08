"""Draws the home-screen icons (icons/*.png) in the game's palette: python3 tools/make-icons.py
Everything important stays inside the middle 80 % so Android can crop it to a circle (maskable)."""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 1024                                    # drawn large, scaled down for each size


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw():
    img = Image.new('RGB', (S, S))
    px = ImageDraw.Draw(img)
    top, bottom = (0x26, 0x1a, 0x36), (0x6a, 0x3a, 0x52)          # dusk sky
    for y in range(S):
        px.line([(0, y), (S, y)], fill=lerp(top, bottom, y / S))
    px.ellipse([560, 250, 820, 510], fill=(0xff, 0x7a, 0x3d))        # setting sun
    city = (0x2a, 0x20, 0x36)
    for x, w, h in [(0, 150, 360), (130, 120, 300), (240, 160, 420), (390, 110, 330), (480, 170, 390),
                    (640, 130, 300), (760, 150, 440), (900, 124, 340)]:
        px.rectangle([x, S - h, x + w, S], fill=city)
    concrete, side = (0xd8, 0xcc, 0xbe), (0x9a, 0x8a, 0x80)
    for x, y, w in [(170, 640, 110), (420, 560, 90), (650, 600, 80)]:  # pillars to jump between
        px.rectangle([x, y, x + w, S], fill=side)
        px.rectangle([x, y, x + w, y + 22], fill=concrete)
    # runner mid-jump between the first two pillars
    ink = (0xf3, 0xec, 0xe2)
    px.ellipse([318, 368, 368, 418], fill=ink)                         # head
    px.line([(340, 420), (310, 500)], fill=ink, width=30)              # body
    px.line([(330, 445), (390, 420)], fill=ink, width=22)              # arm forward
    px.line([(325, 450), (270, 470)], fill=ink, width=22)              # arm back
    px.line([(310, 500), (370, 530), (360, 590)], fill=ink, width=24)  # front leg
    px.line([(310, 500), (250, 540)], fill=ink, width=24)              # back leg
    px.arc([215, 470, 495, 900], 196, 252, fill=(0x5e, 0xe6, 0xd0), width=12)   # jump trail behind the runner
    return img


big = draw()
os.makedirs(os.path.join(ROOT, 'icons'), exist_ok=True)
for name, size in [('icon-512.png', 512), ('icon-192.png', 192), ('apple-touch-icon.png', 180), ('favicon-32.png', 32)]:
    big.resize((size, size), Image.LANCZOS).save(os.path.join(ROOT, 'icons', name), optimize=True)
print('icons written to', os.path.join(ROOT, 'icons'))
