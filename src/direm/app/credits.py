from dataclasses import dataclass


PROJECT_NAME = "DIREM"
PROJECT_OWNER = "1D1L1R"


@dataclass(frozen=True)
class Coauthor:
    name: str
    role: str


COAUTHORS = (
    Coauthor(name="Rein Hard V", role="architecture, scope lock, review"),
    Coauthor(name="Bushid Ronin V", role="implementation executor"),
)
