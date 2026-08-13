# -*- coding: utf-8 -*-
"""Приводит og:image/twitter: к единой og-cover.jpg на всех HTML-страницах сибы."""
import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OG_COVER_URL = "https://pitomnik-siba-inu.ru/assets/img/og-cover.jpg"

files = glob.glob(os.path.join(ROOT, "**", "index.html"), recursive=True) + [os.path.join(ROOT, "404.html")]
files = [f for f in files if os.path.exists(f)]

changed = []
skipped = []

for path in files:
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    if "og:image" not in text:
        skipped.append((path, "no og:image"))
        continue

    m_title = re.search(r'<meta property="og:title" content="([^"]*)">', text)
    m_desc = re.search(r'<meta property="og:description" content="([^"]*)">', text)
    og_title = m_title.group(1) if m_title else "Nord Heart — питомник сиба-ину"
    og_desc = m_desc.group(1) if m_desc else "Питомник сиба-ину Nord Heart. Москва и Московская область."

    # 1) заменить сам og:image на og-cover, убрать старую строку целиком (со своими отступами)
    text, n1 = re.subn(
        r'[ \t]*<meta property="og:image" content="[^"]*">\n',
        f'<meta property="og:image" content="{OG_COVER_URL}">\n'
        f'<meta property="og:image:width" content="1200">\n'
        f'<meta property="og:image:height" content="630">\n'
        f'<meta property="og:image:alt" content="{og_title}">\n'
        f'<meta property="og:locale" content="ru_RU">\n',
        text, count=1
    )

    # 2) twitter:card -> summary_large_image (если ещё не такой)
    text, n2 = re.subn(
        r'<meta name="twitter:card" content="[^"]*">',
        '<meta name="twitter:card" content="summary_large_image">',
        text, count=1
    )

    # 3) добавить twitter:title/description/image сразу после twitter:card, если их ещё нет
    if 'name="twitter:title"' not in text:
        text, n3 = re.subn(
            r'(<meta name="twitter:card" content="summary_large_image">\n)',
            r'\1'
            f'<meta name="twitter:title" content="{og_title}">\n'
            f'<meta name="twitter:description" content="{og_desc}">\n'
            f'<meta name="twitter:image" content="{OG_COVER_URL}">\n',
            text, count=1
        )
    else:
        n3 = 0

    if n1 == 0:
        skipped.append((path, "og:image line not matched by regex"))
        continue

    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    changed.append(path)

print(f"Изменено файлов: {len(changed)}")
for p in changed:
    print("  OK:", os.path.relpath(p, ROOT))
if skipped:
    print(f"Пропущено: {len(skipped)}")
    for p, reason in skipped:
        print("  SKIP:", os.path.relpath(p, ROOT), "-", reason)
