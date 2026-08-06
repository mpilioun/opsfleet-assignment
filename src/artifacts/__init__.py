from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from frontmatter import load

ARTIFACTS_DIR = Path(__file__).parent
SKILLS_DIR = ARTIFACTS_DIR / "skills"
PROMPTS_DIR = ARTIFACTS_DIR / "prompts"


class ArtifactTypes(StrEnum):
    SKILL = "skill"
    PROMPT = "prompt"


@dataclass
class Artifact:
    metadata: dict
    content: str


def read_artifact(artifact_type: ArtifactTypes, artifact_name: str) -> Artifact:
    match artifact_type:
        case ArtifactTypes.SKILL:
            artifact = load(SKILLS_DIR / artifact_name)
        case ArtifactTypes.PROMPT:
            artifact = load(PROMPTS_DIR / artifact_name)
        case _:
            msg = f"Unknown artifact type: {artifact_type}"
            raise ValueError(msg)

    return Artifact(metadata=artifact.metadata, content=artifact.content)


__all__ = [
    "SKILLS_DIR",
    "Artifact",
    "ArtifactTypes",
    "read_artifact",
]
