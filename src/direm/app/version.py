from dataclasses import dataclass


UNKNOWN = "unknown"


@dataclass(frozen=True)
class VersionMetadata:
    version: str
    commit_sha: str
    build_date: str
    environment: str
    db_migration: str = UNKNOWN
