from direm.app.config import Settings
from direm.services.version_service import build_version_metadata, render_version


def test_version_metadata_falls_back_to_unknown() -> None:
    settings = Settings(
        DIREM_VERSION="",
        DIREM_COMMIT_SHA="",
        DIREM_BUILD_DATE="",
        DIREM_ENV="",
    )

    metadata = build_version_metadata(settings)

    assert metadata.version == "unknown"
    assert metadata.commit_sha == "unknown"
    assert metadata.build_date == "unknown"
    assert metadata.environment == "unknown"
    assert metadata.db_migration == "unknown"


def test_render_version_format() -> None:
    settings = Settings(_env_file=None)
    output = render_version(build_version_metadata(settings))

    assert "DIREM v0.1.0" in output
    assert "Commit: unknown" in output
    assert "Build: unknown" in output
    assert "Environment: local" in output
    assert "DB migration: unknown" in output
