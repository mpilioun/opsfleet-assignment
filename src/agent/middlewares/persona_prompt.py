from langchain.agents.middleware import dynamic_prompt
from langchain.agents.middleware.types import ModelRequest

from src.agent.utils.persona import get_active_persona
from src.artifacts import ArtifactTypes, read_artifact

DEFAULT_PERSONA = read_artifact(ArtifactTypes.PROMPT, "retail_agent_persona.md").content


@dynamic_prompt
async def persona_prompt(request: ModelRequest) -> str:
    """Prepend the live persona (Store, falling back to the artifact default) ahead
    of whatever the framework/skills/memory middleware already put in the system
    message - additive, so it never discards the skills index or loaded memory.
    """
    persona_text = await get_active_persona(request.runtime.store, DEFAULT_PERSONA)
    existing = request.system_message.content if request.system_message else ""
    if not existing:
        return persona_text
    return f"{persona_text}\n\n{existing}"
