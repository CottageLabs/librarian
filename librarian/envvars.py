import os
from pathlib import Path

from .cpaths import PROJ_HOME


def get_qdrant_data_path() -> Path:
    """Get Qdrant data path from environment variable or default."""
    default_path = PROJ_HOME / 'qdrant'
    env_value = os.getenv('QDRANT_DATA_PATH')

    if env_value:
        return Path(env_value)
    return default_path
