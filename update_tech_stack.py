"""
Mengambil bahasa pemrograman yang benar-benar dipakai di semua repo publik
GitHub kamu, lalu mengganti baris Tech Stack di README.md dengan icon
yang sesuai (via skillicons.dev). Icon Git dan GitHub selalu ditambahkan
di akhir karena keduanya adalah tools, bukan bahasa pemrograman.
"""

import os
import re
import sys
import urllib.request
import json

USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "angelchelssa")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
README_PATH = "README.md"

# Pemetaan nama bahasa dari GitHub API ke id icon skillicons.dev
# Bahasa yang tidak ada di kamus ini otomatis diabaikan (tidak error).
LANGUAGE_TO_ICON = {
    "Java": "java",
    "HTML": "html",
    "CSS": "css",
    "JavaScript": "js",
    "TypeScript": "ts",
    "Python": "py",
    "C++": "cpp",
    "C": "c",
    "C#": "cs",
    "PHP": "php",
    "Dart": "dart",
    "Go": "go",
    "Ruby": "ruby",
    "Swift": "swift",
    "Kotlin": "kotlin",
    "Shell": "bash",
    "Vue": "vue",
    "Rust": "rust",
}

# Tools tetap yang selalu ditampilkan di akhir baris
STATIC_TOOLS = ["git", "github"]


def gh_get(url):
    req = urllib.request.Request(url)
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def get_top_languages(username, max_repos=100):
    repos = gh_get(f"https://api.github.com/users/{username}/repos?per_page={max_repos}")
    totals = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        name = repo["name"]
        try:
            langs = gh_get(f"https://api.github.com/repos/{username}/{name}/languages")
        except Exception:
            continue
        for lang, bytes_count in langs.items():
            totals[lang] = totals.get(lang, 0) + bytes_count

    # urutkan dari yang paling banyak dipakai
    sorted_langs = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    icons = []
    for lang, _ in sorted_langs:
        icon = LANGUAGE_TO_ICON.get(lang)
        if icon and icon not in icons:
            icons.append(icon)
    return icons


def update_readme(icons):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    all_icons = icons + [t for t in STATIC_TOOLS if t not in icons]
    icon_query = ",".join(all_icons)
    new_block = (
        "<!-- TECH-STACK:START -->\n"
        '<p align="center">\n'
        f'  <img src="https://skillicons.dev/icons?i={icon_query}" />\n'
        "</p>\n"
        "<!-- TECH-STACK:END -->"
    )

    pattern = re.compile(
        r"<!-- TECH-STACK:START -->.*?<!-- TECH-STACK:END -->", re.DOTALL
    )
    if not pattern.search(content):
        print("Marker TECH-STACK tidak ditemukan di README.md, tidak ada perubahan.")
        sys.exit(0)

    updated = pattern.sub(new_block, content)

    if updated != content:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(updated)
        print("README.md diperbarui dengan Tech Stack terbaru:", icon_query)
    else:
        print("Tidak ada perubahan pada Tech Stack.")


if __name__ == "__main__":
    icons = get_top_languages(USERNAME)
    update_readme(icons)
