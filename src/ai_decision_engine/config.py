from pathlib import Path
from typing import Any
import yaml


def load_domain_config(domain: str) -> dict[str, Any]:
    config_path = Path(__file__).parent / "domains" / domain / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"No config found for domain '{domain}' at {config_path}")
    with config_path.open() as f:
        return yaml.safe_load(f)
