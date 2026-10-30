import json
from dataclasses import dataclass
from typing import List

import requests

from virtex_launcher import config


@dataclass(frozen=True)
class Mod:
    id: str
    name: str
    version: str
    url: str
    description: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Mod":
        return cls(
            id=d["id"],
            name=d["name"],
            version=d["version"],
            url=d["url"],
            description=d.get("description", ""),
        )


def fetch_mods() -> tuple[List[Mod], str]:
    """Возвращает (моды, источник). Бросает если и сеть, и кэш недоступны."""
    try:
        r = requests.get(config.MODS_JSON_URL, timeout=config.REQUEST_TIMEOUT)
        r.raise_for_status()
        return [Mod.from_dict(x) for x in r.json()], "online"
    except Exception:
        if config.MODS_CACHE.exists():
            data = json.loads(config.MODS_CACHE.read_text(encoding="utf-8"))
            return [Mod.from_dict(x) for x in data], "cache"
        raise


def installed_ids() -> set[str]:
    if not config.MODS_DIR.exists():
        return set()
    return {p.name for p in config.MODS_DIR.iterdir() if p.is_dir()}
    {
  "id": "nickname_changer",
  "name": "Nickname Changer",
  "version": "1.0.0",
  "url": "https://example.com/mods/nickname-changer-1.16.5-fabric.jar",
  "filename": "nickname-changer-1.16.5-fabric.jar",
  "description": "Позволяет менять отображаемый ник без перезапуска игры. Для Fabric 1.16.5."
}