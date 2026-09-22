# -*- coding: utf-8 -*-
"""
Проверка собранного сайта по чек-листу методики.
Запуск:  python tools/check.py   (из корня проекта)

Проверяет:
  1. валидность всего JSON-LD (json.loads);
  2. совпадение числа вопросов в FAQPage с числом блоков .faq-item;
  3. canonical ведёт на боевой домен и совпадает с путём файла;
  4. один <h1> на странице;
  5. дубли title / description между страницами;
  6. посторонние символы: украинские і ї є ґ, латиница внутри русских слов;
  7. баланс парных тегов main / section / div / table;
  8. объём текста на странице (методика: минимум 700 слов, о породе 900+);
  9. битые внутренние ссылки и отсутствующие картинки;
 10. наличие width/height и alt у всех <img>.
"""
import os
import re
import json
import sys
from html.parser import HTMLParser

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://pitomnik-siba-inu.ru"
MIN_WORDS = 700
MIN_WORDS_BREED = 900

errors, warnings = [], []


def err(page, msg):
    errors.append("%-46s %s" % (page, msg))


def warn(page, msg):
    warnings.append("%-46s %s" % (page, msg))


def pages():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "tools", "assets")]
        for fn in filenames:
            if fn.endswith(".html"):
                yield os.path.join(dirpath, fn)


class TagBalance(HTMLParser):
    VOID = {"img", "br", "hr", "meta", "link", "input", "source", "col"}

    def __init__(self):
        super().__init__()
        self.stack = []
        self.problems = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack:
            self.problems.append("закрывающий </%s> без открывающего" % tag)
        elif self.stack[-1] != tag:
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.problems.append("не закрыт <%s> внутри <%s>" % (self.stack[-1], tag))
                    self.stack.pop()
                self.stack.pop()
            else:
                self.problems.append("лишний </%s>" % tag)
        else:
            self.stack.pop()


def text_of(html):
    body = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", html)
    body = re.sub(r"(?s)<[^>]+>", " ", body)
    return re.sub(r"\s+", " ", body)


# Служебные файлы верификации (Яндекс.Вебмастер/Google Search Console)
# лежат прямо в корне сайта как HTML, но это не страницы — их не проверяем
# и не ждём в sitemap.
SKIP_FILES = {"yandex_fb3299ce897ad633.html"}

seen_title, seen_desc = {}, {}
all_urls = set()
checked = 0

files = sorted(p for p in pages() if os.path.relpath(p, ROOT).replace("\\", "/") not in SKIP_FILES)
for path in files:
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    url = "/" + rel.replace("index.html", "")
    if url != "/404.html":
        all_urls.add(url if url.endswith("/") or url.endswith(".html") else url + "/")

for path in files:
    checked += 1
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    html = open(path, encoding="utf-8").read()

    # --- 1. JSON-LD
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    faq_declared = 0
    for b in blocks:
        try:
            data = json.loads(b)
        except Exception as e:
            err(rel, "невалидный JSON-LD: %s" % e)
            continue
        if data.get("@type") == "FAQPage":
            faq_declared += len(data.get("mainEntity", []))

    # --- 2. FAQPage vs .faq-item
    faq_actual = html.count('class="faq-item"')
    if faq_declared != faq_actual:
        err(rel, "FAQPage: в разметке %d вопросов, блоков на странице %d"
            % (faq_declared, faq_actual))

    # --- 3. canonical
    # У 404 canonical быть НЕ должно: страница отдаётся по любому несуществующему
    # адресу, и canonical на саму себя склеивал бы все опечатки в один URL.
    # Ниже по коду исключение для 404 уже есть — здесь оно тоже нужно,
    # иначе скрипт требует canonical там, где его быть не должно.
    m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if not m:
        if rel != "404.html":
            err(rel, "нет canonical")
    else:
        canon = m.group(1)
        if not canon.startswith(SITE):
            err(rel, "canonical на чужой домен: %s" % canon)
        expected = SITE + "/" + rel.replace("index.html", "")
        if rel != "404.html" and canon != expected:
            err(rel, "canonical %s не совпадает с путём (ожидался %s)" % (canon, expected))

    # --- 4. один h1
    h1 = len(re.findall(r"<h1[ >]", html))
    if h1 != 1:
        err(rel, "h1 на странице: %d (должен быть ровно 1)" % h1)

    # --- 5. дубли title / description
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', html)
    if t:
        title = t.group(1).strip()
        # Методика, Этап 5: title 45–65 знаков. Раньше здесь стояло «длиннее 70»,
        # то есть предупреждение не срабатывало на половине отклонений от нормы.
        if not (45 <= len(title) <= 65):
            warn(rel, "title %d знаков (норма 45–65)" % len(title))
        if title in seen_title:
            err(rel, "дубль title с %s" % seen_title[title])
        seen_title[title] = rel
    else:
        err(rel, "нет title")
    if d:
        desc = d.group(1).strip()
        # Тот же случай: допуск 100–200 пропускал явно длинные описания,
        # которые Яндекс и Google обрезают в выдаче. Норма методички — 120–160.
        if not (120 <= len(desc) <= 160):
            warn(rel, "description %d знаков (норма 120–160)" % len(desc))
        if desc in seen_desc:
            err(rel, "дубль description с %s" % seen_desc[desc])
        seen_desc[desc] = rel
    else:
        err(rel, "нет description")

    # --- 6. посторонние символы
    bad = set(re.findall(r"[іїєґІЇЄҐ]", html))
    if bad:
        err(rel, "украинские буквы в тексте: %s" % " ".join(sorted(bad)))
    body_text = text_of(html)
    mixed = set(re.findall(r"\b(?=\w*[А-Яа-яЁё])(?=\w*[A-Za-z])\w+\b", body_text))
    mixed = {w for w in mixed if not re.fullmatch(r"[A-Za-z]+", w)}
    if mixed:
        err(rel, "латиница внутри русских слов: %s" % ", ".join(sorted(mixed)[:6]))

    # --- 7. баланс тегов
    tb = TagBalance()
    tb.feed(html)
    if tb.problems:
        err(rel, "структура тегов: %s" % "; ".join(tb.problems[:3]))
    if tb.stack:
        err(rel, "незакрытые теги: %s" % ", ".join(tb.stack[:5]))

    # --- 8. объём текста
    words = len(body_text.split())
    # Подстраницы кластера «О породе» — от 900 слов (методика), остальные — от 700.
    is_breed_sub = rel.startswith("o-porode/") and rel != "o-porode/index.html"
    limit = MIN_WORDS_BREED if is_breed_sub else MIN_WORDS
    if rel not in ("404.html", "politika-konfidentsialnosti/index.html"):
        if words < limit:
            err(rel, "мало текста: %d слов (нужно от %d)" % (words, limit))
        elif words < limit + 100:
            warn(rel, "текста впритык: %d слов" % words)

    # --- 9. внутренние ссылки и картинки
    for href in set(re.findall(r'href="(/[^"#?]*)"', html)):
        if href.startswith("/assets/"):
            if not os.path.exists(os.path.join(ROOT, href.lstrip("/"))):
                err(rel, "нет файла: %s" % href)
        elif href.endswith("/") or href.endswith(".html"):
            if href not in all_urls and href != "/":
                err(rel, "битая внутренняя ссылка: %s" % href)
    for src in set(re.findall(r'<img[^>]+src="([^"]+)"', html)):
        if src.startswith("/") and not os.path.exists(os.path.join(ROOT, src.lstrip("/"))):
            err(rel, "нет картинки: %s" % src)

    # --- 10. атрибуты img (пиксель Метрики — скрытый трекер, не контент, пропускаем)
    for tag in re.findall(r"<img[^>]*>", html):
        if "mc.yandex.ru/watch" in tag:
            continue
        if 'alt="' not in tag:
            err(rel, "img без alt: %s" % tag[:70])
        elif re.search(r'alt="\s*"', tag):
            warn(rel, "пустой alt: %s" % tag[:70])
        if 'width="' not in tag or 'height="' not in tag:
            warn(rel, "img без width/height: %s" % tag[:70])

# --- sitemap
sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
sm_urls = set(re.findall(r"<loc>%s([^<]*)</loc>" % re.escape(SITE), sm))
missing = all_urls - sm_urls
if missing:
    err("sitemap.xml", "нет в карте сайта: %s" % ", ".join(sorted(missing)))
extra = sm_urls - all_urls
if extra:
    err("sitemap.xml", "в карте есть несуществующие: %s" % ", ".join(sorted(extra)))

print("Проверено страниц: %d\n" % checked)
if errors:
    print("ОШИБКИ (%d):" % len(errors))
    for e in errors:
        print("  ERR ", e)
else:
    print("Ошибок нет.")
if warnings:
    print("\nПредупреждения (%d):" % len(warnings))
    for w in warnings:
        print("  WARN", w)
sys.exit(1 if errors else 0)
