#!/usr/bin/env python3
"""Regenerates the live profile cards (assets/profile/*.svg) from live data.

Run by .github/workflows/update-stats.yml on a schedule so the profile's
stats never go stale and never depend on a third-party rate-limited
service (github-readme-stats, github-profile-trophy, and
github-readme-streak-stats were all confirmed broken at various points).
Fetches the numbers here; scripts/profile_cards.py draws the SVGs.
Uses only public REST/GraphQL endpoints (no PAT required) -- the default
GITHUB_TOKEN can't see private repos or private contributions, so
repo/star counts and the contribution/streak numbers are all
public-only by design.
"""
import json
import os
import urllib.request

from profile_cards import render_live_cards
from datetime import datetime, timedelta

USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "ahmedrazasahoo")
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def api_get(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def graphql(query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Content-Type": "application/json"},
    )
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


# GitHub's contributionCalendar only accepts a <=1 year from/to window per
# call, hence the year-by-year looping in fetch_contribution_stats() below.
CALENDAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_contribution_stats(created_at):
    created = datetime.strptime(created_at[:10], "%Y-%m-%d")
    now = datetime.utcnow()

    all_time_total = 0
    days = {}
    cursor = created
    while cursor < now:
        window_end = min(cursor + timedelta(days=365), now)
        data = graphql(CALENDAR_QUERY, {
            "login": USERNAME,
            "from": cursor.strftime("%Y-%m-%dT00:00:00Z"),
            "to": window_end.strftime("%Y-%m-%dT23:59:59Z"),
        })
        cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        all_time_total += cal["totalContributions"]
        for week in cal["weeks"]:
            for d in week["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
        cursor = window_end

    # Streaks span the whole history, not just the last (possibly
    # days-long) calendar window.
    history = sorted(days.items())
    i = len(history) - 1
    if history and history[i][1] == 0:
        i -= 1
    current_streak = 0
    while i >= 0 and history[i][1] > 0:
        current_streak += 1
        i -= 1

    longest_streak = 0
    run = 0
    for _, count in history:
        if count > 0:
            run += 1
            longest_streak = max(longest_streak, run)
        else:
            run = 0

    return {
        "total_contributions": all_time_total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
    }


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
        "created_at": user.get("created_at"),
    }


def main():
    data = fetch_data()
    data.update(fetch_contribution_stats(data["created_at"]))
    cards = render_live_cards(data)
    print(f"Regenerated {', '.join(cards)} for {USERNAME}: {data}")


if __name__ == "__main__":
    main()
