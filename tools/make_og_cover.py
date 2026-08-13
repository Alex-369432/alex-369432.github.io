# -*- coding: utf-8 -*-
"""Генерирует assets/img/og-cover.jpg (1200x630) для превью в соцсетях/мессенджерах."""
from PIL import Image, ImageDraw, ImageFont
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "assets", "img")
SRC_PHOTO = os.path.join(IMG_DIR, "roditeli", "otec-crystal-family-1.jpg")
OUT = os.path.join(IMG_DIR, "og-cover.jpg")

W, H = 1200, 630
LEFT_W = 660
RIGHT_W = W - LEFT_W

BG = (250, 247, 242)        # --color-bg
TEXT_DARK = (36, 31, 26)    # --color-text
TEXT_MUTED = (107, 98, 89)  # --color-text-muted
ACCENT = (193, 80, 46)      # --color-accent
ACCENT_DARK = (156, 63, 36) # --color-accent-dark

FONTS = "C:/Windows/Fonts/"
f_title = ImageFont.truetype(FONTS + "georgiab.ttf", 74)
f_sub = ImageFont.truetype(FONTS + "arialbd.ttf", 42)
f_line = ImageFont.truetype(FONTS + "arial.ttf", 27)
f_line_b = ImageFont.truetype(FONTS + "arialbd.ttf", 27)
f_wm = ImageFont.truetype(FONTS + "arialbd.ttf", 24)

canvas = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(canvas)

# --- правая часть: фото ---
photo = Image.open(SRC_PHOTO).convert("RGB")
pw, ph = photo.size
target_ratio = RIGHT_W / H
src_ratio = pw / ph
if src_ratio > target_ratio:
    new_w = int(ph * target_ratio)
    x0 = (pw - new_w) // 2
    photo = photo.crop((x0, 0, x0 + new_w, ph))
else:
    new_h = int(pw / target_ratio)
    y0 = 0  # держим верх (морда собаки сверху кадра)
    photo = photo.crop((0, y0, pw, y0 + new_h))
photo = photo.resize((RIGHT_W, H), Image.LANCZOS)
canvas.paste(photo, (LEFT_W, 0))

# лёгкая тёмная подложка снизу фото для читаемости водяного знака
overlay = Image.new("RGBA", (RIGHT_W, 90), (0, 0, 0, 0))
odraw = ImageDraw.Draw(overlay)
for i in range(90):
    a = int(120 * (i / 90))
    odraw.line([(0, i), (RIGHT_W, i)], fill=(20, 15, 10, a))
canvas.paste(Image.alpha_composite(Image.new("RGBA", (RIGHT_W, 90), (0,0,0,0)), overlay).convert("RGB"), (LEFT_W, H - 90))
# переклеим как альфа-композит поверх фото корректно
base = canvas.crop((LEFT_W, H - 90, W, H)).convert("RGBA")
base = Image.alpha_composite(base, overlay)
canvas.paste(base.convert("RGB"), (LEFT_W, H - 90))

draw.text((LEFT_W + RIGHT_W - 20, H - 46), "pitomnik-siba-inu.ru", font=f_wm, fill=(255, 255, 255), anchor="ra")

# --- левая часть: текст ---
pad = 60
y = 150
draw.text((pad, y), "Nord Heart", font=f_title, fill=ACCENT_DARK)
title_w = draw.textlength("Nord Heart", font=f_title)
y2 = y + 100
draw.line([(pad, y2), (pad + max(title_w, 300), y2)], fill=ACCENT, width=4)

y3 = y2 + 40
draw.text((pad, y3), "Питомник сиба-ину", font=f_sub, fill=TEXT_DARK)

y4 = y3 + 70
draw.text((pad, y4), "Лобня, Московская область · с 2001 года", font=f_line, fill=TEXT_MUTED)

y5 = y4 + 42
draw.text((pad, y5), "Щенки с документами · от 70 000 ₽", font=f_line_b, fill=ACCENT_DARK)

canvas.save(OUT, "JPEG", quality=87, optimize=True)
print("Saved:", OUT, canvas.size, os.path.getsize(OUT), "bytes")
