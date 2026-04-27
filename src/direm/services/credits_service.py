from direm.app.credits import COAUTHORS, PROJECT_OWNER


def render_credits() -> str:
    lines = [
        "Project Owner:",
        f"- {PROJECT_OWNER}",
        "",
        "Co-authors:",
    ]
    lines.extend(f"- {coauthor.name} — {coauthor.role}" for coauthor in COAUTHORS)
    return "\n".join(lines)
