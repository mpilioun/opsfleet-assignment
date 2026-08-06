from deepagents import FilesystemPermission
from deepagents.backends import CompositeBackend, StateBackend
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.backends.store import StoreBackend
from langgraph.store.base import BaseStore

from src.agent.utils.agent_config import get_user_id
from src.artifacts import SKILLS_DIR

MEMORY_PATH = "/memory/"
SKILLS_PATH = "/skills/"
PREFERENCES_FILE = f"{MEMORY_PATH}preferences.md"


def build_backend(store: BaseStore | None) -> CompositeBackend:
    """Ephemeral state by default; /memory/ persists per-user in the Store; /skills/
    is a read-only view of the artifacts/skills/ directory on disk.
    """
    return CompositeBackend(
        default=StateBackend(),
        routes={
            MEMORY_PATH: StoreBackend(
                namespace=lambda _runtime: ("user_prefs", get_user_id()),
                store=store,
            ),
            SKILLS_PATH: FilesystemBackend(root_dir=SKILLS_DIR, virtual_mode=True),
        },
    )


SKILLS_READ_ONLY_PERMISSION = FilesystemPermission(
    operations=["write"], paths=[f"{SKILLS_PATH}**"], mode="deny"
)
