# -*- coding: utf-8 -*-
"""Сводная статистика по собранному сайту — цифры для SEO_AUDIT.md."""
import os
import re
import json
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = []
schema = Counter()
faq_pages = 0
total_words = 0

for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in (".git", "tools", "assets")]
    for f in fn:
        if not f.endswith(".html"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
        h = open(p, encoding="utf-8").read()
        b = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", h)
        b = re.sub(r"(?s)<[^>]+>", " ", b)
        w = len(re.sub(r"\s+", " ", b).split())
        total_words += w
        # Страница может быть без title/description (404 и т.п.) — не падаем,
        # такие случаи ловит check.py, а статистика должна собираться всегда.
        _t = re.search(r"<title>(.*?)</title>", h, re.S)
        _d = re.search(r'<meta name="description" content="([^"]*)"', h)
        t = _t.group(1) if _t else "(нет title)"
        d = _d.group(1) if _d else "(нет description)"
        has_faq = False
        for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            ty = json.loads(blk).get("@type")
            schema[ty] += 1
            if ty == "FAQPage":
                has_faq = True
        if has_faq:
            faq_pages += 1
        rows.append((rel, w, len(t), len(d), os.path.getsize(p)))

rows.sort(key=lambda r: -r[1])
print("%-54s %6s %6s %6s %8s" % ("страница", "слов", "title", "desc", "КБ"))
for r in rows:
    print("%-54s %6d %6d %6d %8.1f" % (r[0], r[1], r[2], r[3], r[4] / 1024))

print("\nВсего страниц: %d, слов: %d, в среднем %d на страницу"
      % (len(rows), total_words, total_words // len(rows)))
print("Страниц с разметкой FAQPage: %d" % faq_pages)
print("Schema.org: %s" % dict(schema))

img_dir = os.path.join(ROOT, "assets", "img")
img_bytes = sum(os.path.getsize(os.path.join(r, f))
                for r, _, fs in os.walk(img_dir) for f in fs)
img_count = sum(len(fs) for _, _, fs in os.walk(img_dir))
css = os.path.getsize(os.path.join(ROOT, "assets", "css", "style.css"))
js = os.path.getsize(os.path.join(ROOT, "assets", "js", "main.js"))
print("Изображений: %d файлов, %.1f МБ" % (img_count, img_bytes / 1048576))
print("CSS: %.1f КБ, JS: %.1f КБ" % (css / 1024, js / 1024))
