"""
Menyusun Learning Roadmap secara otomatis berdasarkan urutan bahasa
pemrograman yang PERTAMA KALI muncul di repo GitHub kamu, diurutkan dari
repo yang paling lama dibuat ke yang paling baru.

Catatan: ini adalah perkiraan berdasarkan histori GitHub, bukan urutan
belajar yang sebenarnya (misalnya kalau kamu belajar sesuatu sebelum
sempat membuat repo untuk itu, urutan di sini tidak akan menangkapnya).
"""

import os
import re
import sys
import urllib.request
import json

USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "angelchelssa")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
README_PATH = "README.md"

# Nama tampilan untuk tiap bahasa (dipakai sebagai label node diagram)
DISPLAY_NAME = {
    "Java": "Java",
    "HTML": "HTML",
    "CSS": "CSS",
    "JavaScript": "JavaScript",
    "TypeScript": "TypeScript",
    "Python": "Python",
    "C++": "C++",
    "C": "C",
    "C#": "C#",
    "PHP": "PHP",
    "Dart": "Dart",
    "Go": "Go",
    "Ruby": "Ruby",
    "Swift": "Swift",
    "Kotlin": "Kotlin",
    "Shell": "Shell",
    "Vue": "Vue",
    "Rust": "Rust",
    "Jupyter Notebook": "Python (ML)",
}


def gh_get(url):
    req = urllib.request.Request(url)
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def get_chronological_languages(username, max_repos=100):
    repos = gh_get(
        f"https://api.github.com/users/{username}/repos"
        f"?per_page={max_repos}&sort=created&direction=asc"
    )
    ordered_languages = []
    for repo in repos:
        if repo.get("fork") or repo.get("private"):
            continue
        lang = repo.get("language")
        if not lang:
            continue
        display = DISPLAY_NAME.get(lang)
        if display and display not in ordered_languages:
            ordered_languages.append(display)
    return ordered_languages


def build_mermaid(languages):
    if not languages:
        languages = ["Java"]

    node_ids = [chr(ord("A") + i) for i in range(len(languages))]
    lines = ["```mermaid", "graph LR"]

    if len(node_ids) == 1:
        lines.append(f"    {node_ids[0]}[{languages[0]}]")
    else:
        for i in range(len(node_ids) - 1):
            lines.append(
                f"    {node_ids[i]}[{languages[i]}] --> {node_ids[i+1]}[{languages[i+1]}]"
            )

    lines.append("")
    for node_id in node_ids:
        lines.append(f"    style {node_id} fill:#1f2937,stroke:#2F81F7,color:#fff")
    lines.append("```")
    return "\n".join(lines)


def update_readme(mermaid_block):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    new_block = (
        "<!-- LEARNING-ROADMAP:START -->\n"
        f"{mermaid_block}\n"
        "<!-- LEARNING-ROADMAP:END -->"
    )

    pattern = re.compile(
        r"<!-- LEARNING-ROADMAP:START -->.*?<!-- LEARNING-ROADMAP:END -->", re.DOTALL
    )
    if not pattern.search(content):
        print("Marker LEARNING-ROADMAP tidak ditemukan di README.md.")
        sys.exit(0)

    updated = pattern.sub(new_block, content)

    if updated != content:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(updated)
        print("README.md diperbarui dengan Learning Roadmap terbaru.")
    else:
        print("Tidak ada perubahan pada Learning Roadmap.")


if __name__ == "__main__":
    languages = get_chronological_languages(USERNAME)
    mermaid_block = build_mermaid(languages)
    update_readme(mermaid_block)
