from direm.app.credits import COAUTHORS, PROJECT_OWNER
from direm.i18n import t


def render_credits(language_code: str = "en") -> str:
    lines = [
        f"{t(language_code, 'credits.owner')}:",
        f"- {PROJECT_OWNER}",
        "",
        f"{t(language_code, 'credits.coauthors')}:",
    ]
    lines.extend(f"- {coauthor.name} — {coauthor.role}" for coauthor in COAUTHORS)
    return "\n".join(lines)
