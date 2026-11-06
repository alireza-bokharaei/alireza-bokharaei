"""Builds the animated bilingual footer (SVG) for light and dark themes.

Edit the texts, colours or sizes below, then run:

    python scripts/gen_footer_svg.py

Persian is written as normal text with direction="rtl", so the browser
shapes and orders the letters correctly. No external font file is needed.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")

PERSIAN = "اگر پروژه‌هایم برایتان مفید بود، ستاره دادن فراموش نشه!"
ENGLISH = "If you find my projects useful, give it a star"

W, H = 840, 120

THEMES = {
    "dark": {
        "bg1": "#0D1117", "bg2": "#1B2440",
        "persian": "#FFFFFF", "english": "#9FB3D1",
        "accent": "#58A6FF", "star": "#FFD25A", "border": "#30363D",
    },
    "light": {
        "bg1": "#FFFFFF", "bg2": "#DDE6F4",
        "persian": "#14213D", "english": "#59636E",
        "accent": "#0969DA", "star": "#E68C14", "border": "#D0D7DE",
    },
}


def sparkle(cx, cy, r, color, cls):
    k = r * 0.22
    d = (f"M{cx},{cy - r} L{cx + k},{cy - k} L{cx + r},{cy} L{cx + k},{cy + k} "
         f"L{cx},{cy + r} L{cx - k},{cy + k} L{cx - r},{cy} L{cx - k},{cy - k} Z")
    return f'<path class="{cls}" d="{d}" fill="{color}"/>'


def footer_svg(t):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t['bg1']}"/>
      <stop offset="1" stop-color="{t['bg2']}"/>
    </linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <style>
    .fa {{ font-family: Tahoma, "Segoe UI", Vazirmatn, Arial, sans-serif; }}
    .en {{ font-family: "Segoe UI", Helvetica, Arial, sans-serif; }}
    .line {{ transform-box: fill-box; transform-origin: center; animation: grow 4s ease-in-out infinite; }}
    @keyframes grow {{ 0%,100% {{ transform: scaleX(0.4); opacity: .6; }} 50% {{ transform: scaleX(1); opacity: 1; }} }}
    .spark {{ transform-box: fill-box; transform-origin: center; animation: pulse 2.4s ease-in-out infinite; }}
    .spark.b {{ animation-delay: 1.2s; }}
    @keyframes pulse {{ 0%,100% {{ transform: scale(0.85); opacity: .7; }} 50% {{ transform: scale(1.1); opacity: 1; }} }}
    .en-line {{ animation: fade 4s ease-in-out infinite; }}
    @keyframes fade {{ 0%,100% {{ opacity: .6; }} 50% {{ opacity: 1; }} }}
    .shine {{ animation: sweep 5s ease-in-out infinite; }}
    @keyframes sweep {{ 0% {{ transform: translateX(-420px); }} 60%,100% {{ transform: translateX(840px); }} }}
  </style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="url(#bg)" stroke="{t['border']}"/>
  <rect class="line" x="170" y="18" width="500" height="2" rx="1" fill="{t['accent']}"/>
  <text class="fa" x="420" y="62" text-anchor="middle" direction="rtl" xml:lang="fa" font-size="24" font-weight="700" fill="{t['persian']}">{PERSIAN}</text>
  <text class="en en-line" x="420" y="92" text-anchor="middle" font-size="15" font-weight="600" fill="{t['english']}">{ENGLISH}</text>
  <rect class="line" x="170" y="104" width="500" height="2" rx="1" fill="{t['accent']}"/>
  {sparkle(46, 60, 11, t['star'], 'spark a')}
  {sparkle(794, 60, 11, t['star'], 'spark b')}
</svg>
'''


def main():
    for theme, colors in THEMES.items():
        out_dir = os.path.join(ASSETS, theme)
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "footer.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(footer_svg(colors))
        print("wrote", path)


if __name__ == "__main__":
    main()

