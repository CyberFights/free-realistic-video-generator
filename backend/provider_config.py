from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ProviderConfig:
    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    model: Optional[str] = None


def get_provider_config() -> Dict[str, ProviderConfig]:
    return {
        "demo": ProviderConfig(
            name="demo",
            enabled=True,
            api_key=os.getenv("DEMO_API_KEY"),
            endpoint=os.getenv("DEMO_ENDPOINT"),
            model=os.getenv("DEMO_MODEL", "demo-video-model"),
        ),
        "huggingface": ProviderConfig(
            name="huggingface",
            enabled=os.getenv("HF_ENABLED", "false").lower() == "true",
            api_key=os.getenv("HF_TOKEN"),
            endpoint=os.getenv("HF_ENDPOINT"),
            model=os.getenv("HF_MODEL"),
        ),
        "wan": ProviderConfig(
            name="wan",
            enabled=os.getenv("WAN_ENABLED", "false").lower() == "true",
            api_key=os.getenv("WAN_API_KEY"),
            endpoint=os.getenv("WAN_ENDPOINT"),
            model=os.getenv("WAN_MODEL"),
        ),
        "cogvideox": ProviderConfig(
            name="cogvideox",
            enabled=os.getenv("COGVIDEOX_ENABLED", "false").lower() == "true",
            api_key=os.getenv("COGVIDEOX_API_KEY"),
            endpoint=os.getenv("COGVIDEOX_ENDPOINT"),
            model=os.getenv("COGVIDEOX_MODEL"),
        ),

    }


def get_active_provider_name() -> str:
    config = get_provider_config()
    for name in ["wan", "cogvideox", "huggingface", "demo"]:
        if config.get(name) and config[name].enabled:
            return name
    return "demo"
