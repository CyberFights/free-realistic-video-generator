# backend/model_adapter.py
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class VideoGenerationRequest:
    prompt: str
    duration: int = 8
    aspect_ratio: str = "16:9"
    negative_prompt: str = ""
    character_name: Optional[str] = None
    reference_image_path: Optional[str] = None
    voiceover_path: Optional[str] = None
    has_reference_image: bool = False
    has_voiceover: bool = False


class BaseVideoAdapter(ABC):
    @abstractmethod
    def generate(self, request: VideoGenerationRequest) -> Dict[str, Any]:
        raise NotImplementedError


class DemoVideoAdapter(BaseVideoAdapter):
    def __init__(self, model_name: str = "demo-video-model"):
        self.model_name = model_name

    def generate(self, request: VideoGenerationRequest) -> Dict[str, Any]:
        prompt = request.prompt
        if request.has_reference_image:
            prompt = f"{prompt} [image-conditioned identity locked character]"
        if request.has_voiceover:
            prompt = f"{prompt} [lip-sync audio applied]"

        return {
            "status": "completed",
            "prompt": prompt,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio,
            "output_url": f"https://example.com/generated/{request.prompt[:12].replace(' ', '-') or 'demo'}.mp4",
            "meta": {
                "model": self.model_name,
                "identity_locked": request.has_reference_image,
                "lip_sync_enabled": request.has_voiceover,
                "reference_image": request.has_reference_image,
                "voiceover": request.has_voiceover,
            },
            "steps": [
                "prompt normalization",
                "reference conditioning",
                "video generation",
                "lip sync",
                "post-processing",
            ],
        }


class ExternalVideoAdapter(BaseVideoAdapter):
    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    def generate(self, request: VideoGenerationRequest) -> Dict[str, Any]:
        return {
            "status": "not_implemented",
            "prompt": request.prompt,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio,
            "output_url": None,
            "meta": {
                "model": self.provider_name,
                "identity_locked": request.has_reference_image,
                "lip_sync_enabled": request.has_voiceover,
            },
            "steps": ["provider integration pending"],
        }


class LipSyncAdapter:
    def __init__(self, provider_name: str = "wav2lip"):
        self.provider_name = provider_name

    def sync(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not payload.get("has_voiceover"):
            return {"status": "not_required", "provider": self.provider_name}
        return {
            "status": "ready",
            "provider": self.provider_name,
            "method": "audio-driven mouth animation",
        }


def get_video_adapter(model_name: Optional[str] = None) -> BaseVideoAdapter:
    chosen = (model_name or os.getenv("VIDEO_MODEL_PROVIDER", "demo")).lower()

    if chosen in {"demo", "local", "stub"}:
        return DemoVideoAdapter(model_name=chosen)

    if chosen in {"huggingface", "diffusers", "wan", "cogvideox", "ltx"}:
        return ExternalVideoAdapter(provider_name=chosen)

    return DemoVideoAdapter(model_name=chosen)
