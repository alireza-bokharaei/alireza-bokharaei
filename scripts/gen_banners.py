"""Builds the animated banners "Looking For" and "Certifications & Progress".

Edit the text, colours and percentages in scripts/content/*.json, then run:

    python scripts/gen_banners.py

The animations are plain SVG/CSS, so they run in GitHub and browsers.
Only the Python standard library is used.
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "content")
ASSETS = os.path.join(HERE, "..", "assets")

THEMES = {
    "dark": {
        "bg": ("#0B1020", "#161E33"), "title": "#F4F7FB", "sub": "#B8C4DA",
        "card": "#1A2236", "stroke": "#2E3A55", "track": "#2A3450", "accent": "#58A6FF",
    },
    "light": {
        "bg": ("#F3F6FC", "#DCE5F5"), "title": "#14213D", "sub": "#374357",
        "card": "#FFFFFF", "stroke": "#D5DDEB", "track": "#E3E9F3", "accent": "#0969DA",
    },
}


def load(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as f:
        return json.load(f)


def esc(text):
    return html.escape(str(text))


def looking_svg(data, theme):
    t = THEMES[theme]
    rows = []
    for i, item in enumerate(data["items"]):
        y = 74 + i * 38
        delay = i * 0.5
        rows.append(f'''
  <g class="row" style="animation-delay:{delay:.1f}s">
    <rect x="40" y="{y - 20}" width="760" height="30" rx="15" fill="{t['card']}" stroke="{t['stroke']}"/>
    <circle cx="58" cy="{y - 5}" r="6" fill="{item['color']}"/>
    <text x="78" y="{y}" font-size="17" font-weight="700" fill="{t['title']}">{esc(item['head'])}</text>
    <text x="330" y="{y}" font-size="15" fill="{t['sub']}">{esc(item['desc'])}</text>
  </g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 230" width="840" height="230">
  <defs>
    <linearGradient id="bg{theme}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg'][0]}"/><stop offset="1" stop-color="{t['bg'][1]}"/></linearGradient>
  </defs>
  <style>
    text {{ font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; }}
    .head {{ animation: glow 3s ease-in-out infinite; }}
    @keyframes glow {{ 0%,100% {{ opacity: .85; }} 50% {{ opacity: 1; }} }}
    .row {{ opacity: 1; animation: slide 8s infinite; }}
    @keyframes slide {{
      0% {{ opacity: 0; transform: translateX(-24px); }}
      8%, 78% {{ opacity: 1; transform: translateX(0); }}
      92%, 100% {{ opacity: 0; transform: translateX(24px); }}
    }}
  </style>
  <rect width="840" height="230" rx="20" fill="url(#bg{theme})"/>
  <text class="head" x="40" y="40" font-size="22" font-weight="800" fill="{t['title']}">{esc(data['title'])}</text>
  <rect x="40" y="48" width="70" height="3" rx="1.5" fill="{data['accent']}"/>{''.join(rows)}
</svg>
'''


def percent_font(pct_text):
    return 15 if len(pct_text) <= 3 else 12


def certs_svg(data, theme):
    t = THEMES[theme]
    cards = []
    items = data["items"]
    done = sum(1 for c in items if c["status"].lower() == "done")
    for i, c in enumerate(items):
        x = 26 + i * 164
        delay = i * 0.35
        pct = max(0, min(100, int(c["percent"])))
        pct_text = f"{pct}%"
        fill_w = 128 * pct / 100
        col = c["color"]
        cards.append(f'''
  <g class="card" style="animation-delay:{delay:.2f}s">
    <rect x="{x}" y="72" width="150" height="150" rx="18" fill="{t['card']}" stroke="{t['stroke']}" stroke-width="1.5"/>
    <rect x="{x}" y="72" width="150" height="8" rx="4" fill="{col}"/>
    <circle cx="{x + 75}" cy="128" r="28" fill="{col}" opacity="0.18"/>
    <circle cx="{x + 75}" cy="128" r="20" fill="none" stroke="{col}" stroke-width="3" class="ring"/>
    <text x="{x + 75}" y="133" text-anchor="middle" font-size="{percent_font(pct_text)}" font-weight="800" fill="{col}">{pct_text}</text>
    <text x="{x + 75}" y="172" text-anchor="middle" font-size="14" font-weight="700" fill="{t['title']}">{esc(c['name'])}</text>
    <text x="{x + 75}" y="190" text-anchor="middle" font-size="11" fill="{t['sub']}">{esc(c['status'])} | {esc(c['when'])}</text>
    <rect x="{x + 11}" y="200" width="128" height="6" rx="3" fill="{t['track']}"/>
    <rect class="bar" x="{x + 11}" y="200" width="{fill_w:.1f}" height="6" rx="3" fill="{col}" style="animation-delay:{delay + 0.6:.2f}s"/>
    <rect class="shine" x="{x}" y="72" width="150" height="150" rx="18" fill="url(#sheen)" style="animation-delay:{delay + 1.2:.2f}s"/>
  </g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 260" width="840" height="260">
  <defs>
    <linearGradient id="bg{theme}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg'][0]}"/><stop offset="1" stop-color="{t['bg'][1]}"/></linearGradient>
    <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/><stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0.35"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
  </defs>
  <style>
    text {{ font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; }}
    .head {{ animation: glow 3s ease-in-out infinite; }}
    @keyframes glow {{ 0%,100% {{ opacity: .85; }} 50% {{ opacity: 1; }} }}
    .card {{ transform-box: fill-box; transform-origin: center; opacity: 1; animation: flip 7s ease-in-out infinite; }}
    @keyframes flip {{
      0% {{ opacity: 0; transform: perspective(600px) rotateY(-70deg) translateY(10px); }}
      12%, 70% {{ opacity: 1; transform: perspective(600px) rotateY(0deg) translateY(0); }}
      85%, 100% {{ opacity: 0; transform: perspective(600px) rotateY(70deg) translateY(10px); }}
    }}
    .ring {{ stroke-dasharray: 126; stroke-dashoffset: 126; animation: spin 7s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
    @keyframes spin {{ 0%,15% {{ stroke-dashoffset: 126; }} 45%,100% {{ stroke-dashoffset: 0; }} }}
    .bar {{ transform-box: fill-box; transform-origin: left center; transform: scaleX(0); animation: grow 7s ease-out infinite; }}
    @keyframes grow {{ 0%,15% {{ transform: scaleX(0); }} 45%,100% {{ transform: scaleX(1); }} }}
    .shine {{ opacity: 0; animation: sweep 7s ease-in-out infinite; transform-box: fill-box; }}
    @keyframes sweep {{ 0%,40% {{ opacity: 0; transform: translateX(-160px); }} 50% {{ opacity: 1; }} 60%,100% {{ opacity: 0; transform: translateX(160px); }} }}
  </style>
  <rect width="840" height="260" rx="22" fill="url(#bg{theme})"/>
  <text class="head" x="28" y="42" font-size="22" font-weight="800" fill="{t['title']}">{esc(data['title'])}</text>
  <rect x="28" y="50" width="80" height="3" rx="1.5" fill="{t['accent']}"/>
  <text x="812" y="42" text-anchor="end" font-size="14" fill="{t['sub']}">{done} done | {len(items) - done} in progress</text>{''.join(cards)}
</svg>
'''


def main():
    looking = load("looking.json")
    certs = load("certs.json")
    for theme in THEMES:
        d = os.path.join(ASSETS, theme)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "looking-for.svg"), "w", encoding="utf-8") as f:
            f.write(looking_svg(looking, theme))
        with open(os.path.join(d, "certs.svg"), "w", encoding="utf-8") as f:
            f.write(certs_svg(certs, theme))
    print("banners updated")


if __name__ == "__main__":
    main()
