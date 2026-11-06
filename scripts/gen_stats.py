"""Generates the GitHub stats cards (SVG) from the GitHub API.

Runs automatically with GitHub Actions (see .github/workflows/stats.yml),
so the numbers update by themselves: new repos, stars and commits are
picked up on every run. Only the Python standard library is used.
"""
import json
import os
import html
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "alireza-bokharaei")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

LANG_COLORS = {
    "Python": "#3572A5", "Shell": "#89E051", "Go": "#00ADD8", "JavaScript": "#F1E05A",
    "HTML": "#E34C26", "CSS": "#563D7C", "TypeScript": "#3178C6", "Dockerfile": "#384D54",
    "HCL": "#844FBA", "Ansible": "#EE0000", "Makefile": "#427819", "C": "#555555",
    "Java": "#B07219", "PowerShell": "#012456", "Jupyter Notebook": "#DA5B0B",
}
DEFAULT_COLOR = "#8B949E"


def request(url, data=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-stats"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers, data=data)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def api(path):
    return request("https://api.github.com" + path)


def all_repos():
    repos, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def contributions_this_year():
    """Uses GraphQL when a token is available (GitHub Actions provides one)."""
    if not TOKEN:
        return None
    year = datetime.now(timezone.utc).year
    query = """
    query($login: String!, $from: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from) {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
        }
      }
    }"""
    body = json.dumps({
        "query": query,
        "variables": {"login": USER, "from": f"{year}-01-01T00:00:00Z"},
    }).encode("utf-8")
    res = request("https://api.github.com/graphql", data=body)
    c = res["data"]["user"]["contributionsCollection"]
    return {
        "commits": c["totalCommitContributions"],
        "prs": c["totalPullRequestContributions"],
        "issues": c["totalIssueContributions"],
        "year": year,
    }


def recent_commits_from_events():
    """Fallback without token: counts commits in recent public push events."""
    try:
        events = api(f"/users/{USER}/events/public?per_page=100")
    except Exception:
        return 0
    return sum(len(e.get("payload", {}).get("commits", [])) for e in events if e.get("type") == "PushEvent")


def build_numbers():
    user = api(f"/users/{USER}")
    repos = all_repos()
    own = [r for r in repos if not r.get("fork")]
    stars = sum(r.get("stargazers_count", 0) for r in own)
    langs = {}
    for r in own:
        try:
            data = api(f"/repos/{USER}/{r['name']}/languages")
        except Exception:
            continue
        for lang, size in data.items():
            langs[lang] = langs.get(lang, 0) + size
    contrib = contributions_this_year()
    if contrib is None:
        contrib = {"commits": recent_commits_from_events(), "prs": 0, "issues": 0, "year": "recent"}
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)[:6]
    top = [(name, size * 100.0 / total) for name, size in top]
    return {
        "repos": len(own),
        "stars": stars,
        "followers": user.get("followers", 0),
        "commits": contrib["commits"],
        "prs": contrib["prs"],
        "issues": contrib["issues"],
        "year": contrib["year"],
        "langs": top,
    }


def stats_svg(n, theme):
    dark = theme == "dark"
    bg1, bg2 = ("#0D1117", "#161B22") if dark else ("#FFFFFF", "#F3F6FA")
    fg = "#E6EDF3" if dark else "#1F2328"
    muted = "#8B949E" if dark else "#59636E"
    accent = "#58A6FF" if dark else "#0969DA"
    border = "#30363D" if dark else "#D0D7DE"
    rows = [
        ("Public repositories", n["repos"]),
        ("Total stars", n["stars"]),
        (f"Commits ({n['year']})", n["commits"]),
        ("Pull requests", n["prs"]),
        ("Issues", n["issues"]),
        ("Followers", n["followers"]),
    ]
    items = []
    for i, (label, value) in enumerate(rows):
        x = 40 + (i % 3) * 250
        y = 92 + (i // 3) * 70
        items.append(
            f'<g class="item" style="animation-delay:{i * 0.15:.2f}s">'
            f'<text class="num" x="{x}" y="{y}" font-size="30" font-weight="800" fill="{accent}">{value}</text>'
            f'<text x="{x}" y="{y + 22}" font-size="14" fill="{muted}">{html.escape(label)}</text></g>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 240" width="840" height="240">
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient></defs>
  <style>
    text {{ font-family: "Segoe UI", Arial, sans-serif; }}
    .item {{ opacity: 1; animation: rise 0.8s ease-out both; }}
    .num {{ animation: pulse 2.8s ease-in-out infinite; }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(12px) scale(0.96); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes pulse {{ 0%,100% {{ opacity: .85; }} 50% {{ opacity: 1; }} }}
    .glow {{ animation: glow 3s ease-in-out infinite; }}
    @keyframes glow {{ 0%,100% {{ stroke-opacity: .25; }} 50% {{ stroke-opacity: .9; }} }}
    .sweep {{ animation: sweep 5s linear infinite; }}
    @keyframes sweep {{ from {{ transform: translateX(-300px); }} to {{ transform: translateX(900px); }} }}
  </style>
  <rect x="0.75" y="0.75" width="838.5" height="238.5" rx="16" fill="url(#bg)" stroke="{border}"/>
  <rect class="glow" x="0.75" y="0.75" width="838.5" height="238.5" rx="16" fill="none" stroke="{accent}" stroke-width="1.5"/>
  <rect class="sweep" x="0" y="0" width="160" height="240" fill="{accent}" opacity="0.06"/>
  <text x="40" y="50" font-size="20" font-weight="800" fill="{fg}">{html.escape(USER)} · GitHub Stats</text>
  <text x="800" y="50" text-anchor="end" font-size="12" fill="{muted}">updated {datetime.now(timezone.utc).strftime('%Y-%m-%d')}</text>
  {''.join(items)}
</svg>
'''


def langs_svg(n, theme):
    dark = theme == "dark"
    bg1, bg2 = ("#0D1117", "#161B22") if dark else ("#FFFFFF", "#F3F6FA")
    fg = "#E6EDF3" if dark else "#1F2328"
    muted = "#8B949E" if dark else "#59636E"
    border = "#30363D" if dark else "#D0D7DE"
    track = "#21262D" if dark else "#E7ECF3"
    bars, legend = [], []
    x = 40
    for name, pct in n["langs"]:
        w = 760 * pct / 100.0
        color = LANG_COLORS.get(name, DEFAULT_COLOR)
        bars.append(f'<rect class="seg" x="{x:.1f}" y="70" width="{w:.1f}" height="14" fill="{color}"/>')
        x += w
    for i, (name, pct) in enumerate(n["langs"]):
        lx = 40 + (i % 3) * 260
        ly = 124 + (i // 3) * 30
        color = LANG_COLORS.get(name, DEFAULT_COLOR)
        legend.append(
            f'<circle cx="{lx + 6}" cy="{ly - 5}" r="6" fill="{color}"/>'
            f'<text x="{lx + 20}" y="{ly}" font-size="15" font-weight="700" fill="{fg}">{html.escape(name)}</text>'
            f'<text x="{lx + 200}" y="{ly}" text-anchor="end" font-size="15" fill="{muted}">{pct:.1f}%</text>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 200" width="840" height="200">
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient></defs>
  <style>
    text {{ font-family: "Segoe UI", Arial, sans-serif; }}
    .seg {{ transform-box: fill-box; transform-origin: left center; animation: grow 1.2s ease-out both; }}
    @keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
  </style>
  <rect x="0.75" y="0.75" width="838.5" height="198.5" rx="16" fill="url(#bg)" stroke="{border}"/>
  <text x="40" y="45" font-size="18" font-weight="800" fill="{fg}">Most Used Languages</text>
  <rect x="40" y="70" width="760" height="14" rx="7" fill="{track}"/>
  <g style="clip-path: inset(0 round 7px)">{''.join(bars)}</g>
  {''.join(legend)}
</svg>
'''


def main():
    numbers = build_numbers()
    out_root = os.path.abspath(ROOT)
    for theme in ("light", "dark"):
        d = os.path.join(out_root, theme)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "stats.svg"), "w", encoding="utf-8") as f:
            f.write(stats_svg(numbers, theme))
        with open(os.path.join(d, "langs.svg"), "w", encoding="utf-8") as f:
            f.write(langs_svg(numbers, theme))
    print("stats updated:", json.dumps(numbers, ensure_ascii=False))


if __name__ == "__main__":
    main()
