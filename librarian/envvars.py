import os
from pathlib import Path

from .cpaths import PROJ_HOME


def get_qdrant_data_path() -> Path:
    """Get Qdrant data path from environment variable or default."""
    env_value = os.getenv('QDRANT_DATA_PATH')

    if env_value:
        return Path(env_value)
    return PROJ_HOME / 'qdrant'
