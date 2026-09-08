#!/usr/bin/env python3
"""Regenerates assets/stats.svg and assets/stats-mobile.svg from live GitHub data.

Run by .github/workflows/update-stats.yml on a schedule so the profile's
GitHub Stats card never goes stale and never depends on a third-party
rate-limited service. Uses only public REST endpoints (no PAT required) --
the default GITHUB_TOKEN can't see private repos, so counts here are
public-repo-only by design.
"""
import json
import os
import urllib.request

USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "ahmedrazasahoo")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

BAR_GRADIENTS = ["barBlue", "barGreen", "barPurple", "barCyan"]


def api_get(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def fetch_data():
    user = api_get(f"/users/{USERNAME}")
    repos = []
    page = 1
    while True:
        batch = api_get(f"/users/{USERNAME}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    non_fork = [r for r in repos if not r.get("fork")]
    total_stars = sum(r.get("stargazers_count", 0) for r in non_fork)

    lang_counts = {}
    for r in non_fork:
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    total_lang_repos = sum(lang_counts.values()) or 1
    top_langs = sorted(lang_counts.items(), key=lambda kv: kv[1], reverse=True)[:4]
    languages = [
        {"name": name, "pct": round(count / total_lang_repos * 100, 1)}
        for name, count in top_langs
    ]

    return {
        "public_repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "total_stars": total_stars,
        "languages": languages,
    }


def render_desktop(data):
    bars = []
    y = 104
    for lang, grad in zip(data["languages"], BAR_GRADIENTS):
        bar_w = round(564 * lang["pct"] / 100)
        bars.append(f'''
    <text x="368" y="{y}" font-size="14" font-weight="600" fill="#F8FAFC">{lang["name"]}</text>
    <text x="932" y="{y}" font-size="13" font-weight="500" fill="#94A3B8" text-anchor="end">{lang["pct"]}%</text>
    <rect x="368" y="{y + 8}" width="564" height="10" rx="5" fill="#ffffff" fill-opacity="0.08"/>
    <rect x="368" y="{y + 8}" width="{bar_w}" height="10" rx="5" fill="url(#{grad})"/>''')
        y += 40

    return f'''<svg width="1000" height="300" viewBox="0 0 1000 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg3" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B1120"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>
    <filter id="blob3" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="45"/>
    </filter>
    <filter id="cardShadow3" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
    <linearGradient id="cardStroke3" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.05"/>
    </linearGradient>
    <linearGradient id="barBlue" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3B82F6"/><stop offset="100%" stop-color="#60A5FA"/>
    </linearGradient>
    <linearGradient id="barGreen" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#16A34A"/><stop offset="100%" stop-color="#4ADE80"/>
    </linearGradient>
    <linearGradient id="barPurple" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#7C3AED"/><stop offset="100%" stop-color="#A78BFA"/>
    </linearGradient>
    <linearGradient id="barCyan" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0891B2"/><stop offset="100%" stop-color="#22D3EE"/>
    </linearGradient>
  </defs>

  <rect width="1000" height="300" fill="url(#bg3)"/>
  <circle cx="90"  cy="40"  r="110" fill="#2563EB" opacity="0.45" filter="url(#blob3)"/>
  <circle cx="950" cy="60"  r="120" fill="#22C55E" opacity="0.40" filter="url(#blob3)"/>
  <circle cx="520" cy="280" r="130" fill="#7C3AED" opacity="0.35" filter="url(#blob3)"/>

  <g font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">

    <rect x="40" y="40" width="280" height="220" rx="20" fill="#ffffff" fill-opacity="0.08" stroke="url(#cardStroke3)" stroke-width="1.5" filter="url(#cardShadow3)"/>
    <text x="70" y="80" font-size="14" font-weight="600" fill="#94A3B8" letter-spacing="1">GITHUB OVERVIEW</text>

    <text x="70" y="130" font-size="34" font-weight="700" fill="#F8FAFC">{data["public_repos"]}</text>
    <text x="70" y="152" font-size="13" font-weight="500" fill="#93C5FD">Public repositories</text>

    <text x="70" y="195" font-size="34" font-weight="700" fill="#F8FAFC">{data["total_stars"]}</text>
    <text x="70" y="217" font-size="13" font-weight="500" fill="#6EE7B7">Total stars</text>

    <text x="70" y="245" font-size="15" font-weight="600" fill="#D8B4FE">{data["followers"]} followers &#8226; {data["following"]} following</text>

    <rect x="340" y="40" width="620" height="220" rx="20" fill="#ffffff" fill-opacity="0.08" stroke="url(#cardStroke3)" stroke-width="1.5" filter="url(#cardShadow3)"/>
    <text x="368" y="72" font-size="14" font-weight="600" fill="#94A3B8" letter-spacing="1">MOST USED LANGUAGES</text>
    {"".join(bars)}
  </g>
</svg>
'''


def render_mobile(data):
    bars = []
    y = 250
    for lang, grad in zip(data["languages"], BAR_GRADIENTS):
        bar_w = round(300 * lang["pct"] / 100)
        bars.append(f'''
    <text x="40" y="{y}" font-size="15" font-weight="600" fill="#F8FAFC">{lang["name"]}</text>
    <text x="340" y="{y}" font-size="13" font-weight="500" fill="#94A3B8" text-anchor="end">{lang["pct"]}%</text>
    <rect x="40" y="{y + 8}" width="300" height="12" rx="6" fill="#ffffff" fill-opacity="0.08"/>
    <rect x="40" y="{y + 8}" width="{bar_w}" height="12" rx="6" fill="url(#{grad}M)"/>''')
        y += 54

    return f'''<svg width="380" height="460" viewBox="0 0 380 460" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg3m" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B1120"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>
    <filter id="blob3m" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="40"/>
    </filter>
    <filter id="cardShadow3m" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
    <linearGradient id="cardStroke3m" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.05"/>
    </linearGradient>
    <linearGradient id="barBlueM" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3B82F6"/><stop offset="100%" stop-color="#60A5FA"/>
    </linearGradient>
    <linearGradient id="barGreenM" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#16A34A"/><stop offset="100%" stop-color="#4ADE80"/>
    </linearGradient>
    <linearGradient id="barPurpleM" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#7C3AED"/><stop offset="100%" stop-color="#A78BFA"/>
    </linearGradient>
    <linearGradient id="barCyanM" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0891B2"/><stop offset="100%" stop-color="#22D3EE"/>
    </linearGradient>
  </defs>

  <rect width="380" height="460" fill="url(#bg3m)"/>
  <circle cx="40"  cy="30"  r="90" fill="#2563EB" opacity="0.40" filter="url(#blob3m)"/>
  <circle cx="350" cy="60"  r="100" fill="#22C55E" opacity="0.35" filter="url(#blob3m)"/>
  <circle cx="200" cy="440" r="100" fill="#7C3AED" opacity="0.32" filter="url(#blob3m)"/>

  <g font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">

    <rect x="16" y="16" width="348" height="150" rx="20" fill="#ffffff" fill-opacity="0.08" stroke="url(#cardStroke3m)" stroke-width="1.5" filter="url(#cardShadow3m)"/>
    <text x="40" y="50" font-size="14" font-weight="600" fill="#94A3B8" letter-spacing="1">GITHUB OVERVIEW</text>

    <text x="40" y="94" font-size="32" font-weight="700" fill="#F8FAFC">{data["public_repos"]}</text>
    <text x="40" y="114" font-size="13" font-weight="500" fill="#93C5FD">Public repositories</text>

    <text x="200" y="94" font-size="32" font-weight="700" fill="#F8FAFC">{data["total_stars"]}</text>
    <text x="200" y="114" font-size="13" font-weight="500" fill="#6EE7B7">Total stars</text>

    <text x="40" y="148" font-size="14" font-weight="600" fill="#D8B4FE">{data["followers"]} followers &#8226; {data["following"]} following</text>

    <rect x="16" y="182" width="348" height="262" rx="20" fill="#ffffff" fill-opacity="0.08" stroke="url(#cardStroke3m)" stroke-width="1.5" filter="url(#cardShadow3m)"/>
    <text x="40" y="216" font-size="14" font-weight="600" fill="#94A3B8" letter-spacing="1">MOST USED LANGUAGES</text>
    {"".join(bars)}
  </g>
</svg>
'''


def main():
    data = fetch_data()
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(repo_root, "assets", "stats.svg"), "w") as f:
        f.write(render_desktop(data))
    with open(os.path.join(repo_root, "assets", "stats-mobile.svg"), "w") as f:
        f.write(render_mobile(data))
    print(f"Regenerated stats for {USERNAME}: {data}")


if __name__ == "__main__":
    main()
