from direm.app.config import Settings
from direm.app.version import UNKNOWN, VersionMetadata


def build_version_metadata(settings: Settings, db_migration: str | None = None) -> VersionMetadata:
    return VersionMetadata(
        version=settings.direm_version or UNKNOWN,
        commit_sha=settings.direm_commit_sha or UNKNOWN,
        build_date=settings.direm_build_date or UNKNOWN,
        environment=settings.direm_env or UNKNOWN,
        db_migration=db_migration or UNKNOWN,
    )


def render_version(metadata: VersionMetadata) -> str:
    return "\n".join(
        [
            f"DIREM v{metadata.version}",
            f"Commit: {metadata.commit_sha}",
            f"Build: {metadata.build_date}",
            f"Environment: {metadata.environment}",
            f"DB migration: {metadata.db_migration}",
        ]
    )
