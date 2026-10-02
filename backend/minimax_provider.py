from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import httpx

from provider_contract import GenerationRequest, GenerationProvider, get_provider


class MiniMaxProvider(GenerationProvider):
    name = "minimax"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.minimax.io"):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY is not set")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate_video(self, request: GenerationRequest) -> Dict[str, Any]:
        payload = {
            "model": os.getenv("MINIMAX_MODEL", "MiniMax-H3-Max"),
            "content": [{
                "type": "text",
                "text": request.prompt,
            }],
            "resolution": self._map_resolution(request.aspect_ratio),
            "duration": max(4, min(int(request.duration), 30)),
            "ratio": self._map_ratio(request.aspect_ratio),
        }

        if request.negative_prompt:
            payload["negative_prompt"] = request.negative_prompt

        try:
            response = httpx.post(
                f"{self.base_url}/v2/video_generation",
                headers=self._headers(),
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "status": "queued" if data.get("status") in {"queued", "processing"} else "completed",
                "provider": self.name,
                "raw": data,
                "output_url": data.get("data", {}).get("video_url") or data.get("video_url"),
                "meta": {
                    "model": payload["model"],
                    "duration": payload["duration"],
                    "aspect_ratio": request.aspect_ratio,
                    "resolution": payload["resolution"],
                    "ratio": payload["ratio"],
                },
            }
        except Exception as exc:
            return {
                "status": "error",
                "provider": self.name,
                "error": str(exc),
                "output_url": None,
            }

    def generate_from_image(self, request: GenerationRequest) -> Dict[str, Any]:
        if not request.reference_image_path:
            return self.generate_video(request)

        payload = {
            "model": os.getenv("MINIMAX_MODEL", "MiniMax-H3-Max"),
            "content": [{
                "type": "text",
                "text": request.prompt,
            }],
            "reference_image": request.reference_image_path,
            "resolution": self._map_resolution(request.aspect_ratio),
            "duration": max(4, min(int(request.duration), 30)),
            "ratio": self._map_ratio(request.aspect_ratio),
        }

        try:
            response = httpx.post(
                f"{self.base_url}/v2/video_generation",
                headers=self._headers(),
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "status": "queued" if data.get("status") in {"queued", "processing"} else "completed",
                "provider": self.name,
                "raw": data,
                "output_url": data.get("data", {}).get("video_url") or data.get("video_url"),
            }
        except Exception as exc:
            return {
                "status": "error",
                "provider": self.name,
                "error": str(exc),
                "output_url": None,
            }

    def sync_lips(self, video_path: str, audio_path: str) -> Dict[str, Any]:
        return {
            "status": "not_implemented",
            "provider": self.name,
            "message": "Lip sync requires a separate model or post-processing pipeline.",
            "video_path": video_path,
            "audio_path": audio_path,
        }

    def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "not_configured", "provider": self.name}
        return {"status": "ok", "provider": self.name, "message": "MiniMax API key is present"}

    @staticmethod
    def _map_resolution(aspect_ratio: str) -> str:
        ratio = (aspect_ratio or "16:9").lower()
        if ratio in {"9:16", "portrait"}:
            return "768P"
        return "768P"

    @staticmethod
    def _map_ratio(aspect_ratio: str) -> str:
        ratio = (aspect_ratio or "16:9").lower()
        if ratio == "9:16":
            return "9:16"
        return "16:9"


def get_provider(provider_name: Optional[str] = None):
    name = (provider_name or os.getenv("VIDEO_MODEL_PROVIDER", "demo")).lower()

    if name == "minimax":
        return MiniMaxProvider()
    if name == "demo":
        from provider_contract import DemoProvider
        return DemoProvider()
    return get_provider("demo")
