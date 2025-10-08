from pathlib import Path

PROJ_HOME = Path.home().joinpath('.local/opt/re-mind')

QDRANT_DATA_PATH = PROJ_HOME / 'qdrant'
DB_SQLITE_PATH = PROJ_HOME / 're-mind.db'
DB_SQLITE_TMP_PATH = Path('/tmp/re-mind.db')
