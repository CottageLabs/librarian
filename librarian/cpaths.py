from pathlib import Path

PROJ_HOME = Path.home().joinpath('.local/opt/librarian')
DB_SQLITE_PATH = PROJ_HOME / 'librarian.db'
DB_SQLITE_TMP_PATH = Path('/tmp/librarian.db')
CONFIG_PATH = PROJ_HOME / 'config.json'
