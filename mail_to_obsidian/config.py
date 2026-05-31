import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_SENDER_FILTER = "my@remarkable.com"


@dataclass(frozen=True)
class Config:
    username: str
    password: str
    subfolder: str
    output_dir: Path
    sender_filter: str


def load_dotenv(dotenv_path: Path = Path(".env")) -> None:
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)
