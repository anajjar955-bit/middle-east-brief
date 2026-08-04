#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Arabic Middle East brief (index.html) from public RSS feeds.
Runs in GitHub Actions (cloud) so it works whether or not the laptop is on."""
import datetime, html, re, sys

try:
    import feedparser
except ImportError:
    sys.stderr.write("feedparser missing\n"); sys.exit(1)

RIYADH = datetime.timezone(datetime.timedelta(hours=3))
now = datetime.datetime.now(RIYADH)

AR_DAYS = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']  # Monday=0
AR_MONTHS = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
             'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
weekday = AR_DAYS[now.weekday()]
date_str = f"{weekday}، {now.day} {AR_MONTHS[now.month - 1]} {now.year} · بتوقيت الرياض"
today_iso = now.strftime('%Y-%m-%d')

FEEDS = [
    ('BBC عربي', 'https://feeds.bbci.co.uk/arabic/rss.xml'),
    ('BBC عربي – الشرق الأوسط', 'https://feeds.bbci.co.uk/arabic/middleeast/rss.xml'),
    ('سكاي نيوز عربية', 'https://www.skynewsarabia.com/rss.xml'),
    ('RT عربية', 'https://arabic.rt.com/rss/'),
    ('الجزيرة', 'https://www.aljazeera.net/xml/rss/all.xml'),
    ('العربية', 'https://www.alarabiya.net/feed/rss2/ar.xml'),
]

KEYWORDS = ['إسرائيل', 'اسرائيل', 'غزة', 'إيران', 'ايران', 'لبنان', 'حزب الله',
            'الحوثي', 'الحوثيين', 'اليمن', 'الضفة', 'القدس', 'حماس', 'نتنياهو',
            'طهران', 'بيروت', 'الشرق الأوسط', 'سوريا', 'العراق', 'رفح',
            'خان يونس', 'صنعاء', 'الاحتلال', 'المقاومة', 'الضربات']


def clean(t):
    t = re.sub('<[^>]+>', '', t or '')
    return html.unescape(t).strip()


items, seen = [], set()
for source, url in FEEDS:
    try:
        d = feedparser.parse(url)
    except Exception:
        continue
    for e in d.entries:
        title = clean(e.get('title', ''))
        if not title or title in seen:
            continue
        seen.add(title)
        summary = clean(e.get('summary', e.get('description', '')))
        ts = None
        if e.get('published_parsed'):
            ts = datetime.datetime(*e.published_parsed[:6], tzinfo=datetime.timezone.utc)
        blob = title + ' ' + summary
        items.append({'title': title, 'link': e.get('link', ''), 'summary': summary,
                      'source': source, 'ts': ts,
                      'relevant': any(k in blob for k in KEYWORDS)})

rel = [i for i in items if i['relevant']]
pool = rel if len(rel) >= 6 else items
pool.sort(key=lambda i: i['ts'] or datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
          reverse=True)
top = pool[:12]

if not top:
    sys.stderr.write("No items fetched; leaving site unchanged.\n")
    sys.exit(0)


def esc(s):
    return html.escape(s or '', quote=True)


cards = []
for i in top:
    tm = i['ts'].astimezone(RIYADH).strftime('%H:%M') if i['ts'] else ''
    meta = ' · '.join(x for x in [i['source'], tm] if x)
    summ = i['summary']
    if len(summ) > 300:
        summ = summ[:300].rstrip() + '…'
    link = esc(i['link'])
    p = f'<p>{esc(summ)}</p>' if summ else ''
    cards.append(
        f'<div class="item">\n'
        f'  <a class="ttl" href="{link}" target="_blank" rel="noopener">{esc(i["title"])}</a>\n'
        f'  <div class="meta">{esc(meta)}</div>\n'
        f'  {p}\n'
        f'</div>')

cards_html = "\n".join(cards)

DOC = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>موجز حرب الشرق الأوسط — {now.day} {AR_MONTHS[now.month - 1]} {now.year}</title>
<style>
  :root{{
    --surface-1:#fcfcfb; --page:#f9f9f7;
    --text-primary:#0b0b0b; --text-secondary:#52514e; --muted:#898781;
    --grid:#e1e0d9; --baseline:#c3c2b7; --border:rgba(11,11,11,0.10);
    --series-1:#2a78d6; --series-2:#eb6834; --critical:#d03b3b; --good:#0ca30c;
  }}
  @media (prefers-color-scheme: dark){{
    :root{{
      --surface-1:#1a1a19; --page:#0d0d0d;
      --text-primary:#ffffff; --text-secondary:#c3c2b7; --muted:#898781;
      --grid:#2c2c2a; --baseline:#383835; --border:rgba(255,255,255,0.10);
      --series-1:#3987e5; --series-2:#d95926; --critical:#d03b3b; --good:#0ca30c;
      color-scheme:dark;
    }}
  }}
  *{{box-sizing:border-box}}
  body{{margin:0; background:var(--page); color:var(--text-primary);
    font-family:"Segoe UI",system-ui,-apple-system,"Noto Naskh Arabic",sans-serif;
    line-height:1.85; -webkit-font-smoothing:antialiased;}}
  .wrap{{max-width:860px; margin:0 auto; padding:32px 22px 60px}}
  header{{border-bottom:2px solid var(--baseline); padding-bottom:18px; margin-bottom:20px}}
  .kicker{{color:var(--series-1); font-weight:700; font-size:14px; letter-spacing:.3px}}
  h1{{font-size:30px; margin:6px 0 6px; line-height:1.3}}
  .date{{color:var(--muted); font-size:15px}}
  .item{{background:var(--surface-1); border:1px solid var(--border); border-radius:12px;
    padding:16px 18px; margin:14px 0}}
  .item .ttl{{font-size:18px; font-weight:700; color:var(--text-primary); text-decoration:none;
    display:block; line-height:1.5}}
  .item .ttl:hover{{color:var(--series-1)}}
  .item .meta{{color:var(--muted); font-size:13px; margin:6px 0 8px; font-variant-numeric:tabular-nums}}
  .item p{{font-size:15.5px; color:var(--text-secondary); margin:0}}
  .note{{background:color-mix(in srgb,var(--series-2) 10%,transparent); border:1px solid var(--border);
    border-radius:10px; padding:12px 16px; font-size:14px; color:var(--text-secondary); margin:8px 0 18px}}
  a{{color:var(--series-1); text-decoration:none}} a:hover{{text-decoration:underline}}
  footer{{margin-top:34px; padding-top:16px; border-top:1px solid var(--border);
    color:var(--muted); font-size:13px}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="kicker">موجز الرصد اليومي · حرب الشرق الأوسط</div>
    <h1>أبرز عناوين الشرق الأوسط في آخر 24 ساعة</h1>
    <div class="date">{esc(date_str)}</div>
  </header>

  <p class="note">‫هذه النشرة تُجمَّع آلياً من خلاصات الأخبار (RSS) لمصادر عامة مثل الجزيرة وBBC عربي، وتُحدَّث تلقائياً عبر السحابة. العناوين والملخّصات كما وردت في مصادرها، وقد تتغير أو تحتاج تحقّقاً.</p>

{cards_html}

  <footer>‫تقرير آلي (RSS) · «موجز حرب الشرق الأوسط» · {esc(date_str)}. المصادر: الجزيرة، BBC عربي.</footer>
</div>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(DOC)
import os
os.makedirs('archive', exist_ok=True)
with open(f'archive/{today_iso}.html', 'w', encoding='utf-8') as f:
    f.write(DOC)

print(f"Wrote index.html with {len(top)} items for {today_iso}")
