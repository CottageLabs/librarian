import json

from .cpaths import CONFIG_PATH
from .constants import DEFAULT_COLLECTION_NAME


def _load_config() -> dict:
    try:
        content = CONFIG_PATH.read_text(encoding='utf-8')
    except FileNotFoundError:
        return {}
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {}
    if isinstance(data, dict):
        return data
    return {}


def _save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding='utf-8')


def get_collection_name() -> str:
    """Return the configured collection name or fall back to the default."""
    config = _load_config()
    value = config.get('collection_name', '').strip()
    if value:
        return value
    return DEFAULT_COLLECTION_NAME


def save_collection_name(name: str) -> None:
    """Persist the collection name in the configuration file."""
    sanitized = name.strip()
    if not sanitized:
        sanitized = DEFAULT_COLLECTION_NAME
    config = _load_config()
    config['collection_name'] = sanitized
    _save_config(config)
