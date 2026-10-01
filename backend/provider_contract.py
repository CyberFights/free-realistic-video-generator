from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class GenerationRequest:
    prompt: str
    negative_prompt: str = ""
    duration: int = 8
    aspect_ratio: str = "16:9"
    character_name: Optional[str] = None
    reference_image_path: Optional[str] = None
    voiceover_path: Optional[str] = None
    has_reference_image: bool = False
    has_voiceover: bool = False


class GenerationProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate_video(self, request: GenerationRequest) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_from_image(self, request: GenerationRequest) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def sync_lips(self, video_path: str, audio_path: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        raise NotImplementedError


class DemoProvider(GenerationProvider):
    name = "demo"

    def generate_video(self, request: GenerationRequest) -> Dict[str, Any]:
        return {
            "status": "completed",
            "provider": self.name,
            "output_url": f"https://example.com/generated/{request.prompt[:20].replace(' ', '-') or 'demo'}.mp4",
            "meta": {
                "model": "demo-video-model",
                "identity_locked": request.has_reference_image,
                "lip_sync_enabled": request.has_voiceover,
                "duration": request.duration,
                "aspect_ratio": request.aspect_ratio,
            },
            "steps": [
                "prompt normalization",
                "reference conditioning",
                "video generation",
                "lip sync",
                "post-processing",
            ],
        }

    def generate_from_image(self, request: GenerationRequest) -> Dict[str, Any]:
        return self.generate_video(request)

    def sync_lips(self, video_path: str, audio_path: str) -> Dict[str, Any]:
        return {
            "status": "ready",
            "provider": self.name,
            "video_path": video_path,
            "audio_path": audio_path,
            "method": "demo lip-sync stub",
        }

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "provider": self.name, "message": "demo provider is active"}


class HuggingFaceProvider(GenerationProvider):
    name = "huggingface"

    def generate_video(self, request: GenerationRequest) -> Dict[str, Any]:
        return {
            "status": "not_implemented",
            "provider": self.name,
            "message": "Hugging Face provider integration pending",
            "output_url": None,
        }

    def generate_from_image(self, request: GenerationRequest) -> Dict[str, Any]:
        return self.generate_video(request)

    def sync_lips(self, video_path: str, audio_path: str) -> Dict[str, Any]:
        return {"status": "not_implemented", "provider": self.name}

    def health_check(self) -> Dict[str, Any]:
        return {"status": "not_configured", "provider": self.name}


class WanProvider(GenerationProvider):
    name = "wan"

    def generate_video(self, request: GenerationRequest) -> Dict[str, Any]:
        return {"status": "not_implemented", "provider": self.name, "output_url": None}

    def generate_from_image(self, request: GenerationRequest) -> Dict[str, Any]:
        return self.generate_video(request)

    def sync_lips(self, video_path: str, audio_path: str) -> Dict[str, Any]:
        return {"status": "not_implemented", "provider": self.name}

    def health_check(self) -> Dict[str, Any]:
        return {"status": "not_configured", "provider": self.name}


class CogVideoXProvider(GenerationProvider):
    name = "cogvideox"

    def generate_video(self, request: GenerationRequest) -> Dict[str, Any]:
        return {"status": "not_implemented", "provider": self.name, "output_url": None}

    def generate_from_image(self, request: GenerationRequest) -> Dict[str, Any]:
        return self.generate_video(request)

    def sync_lips(self, video_path: str, audio_path: str) -> Dict[str, Any]:
        return {"status": "not_implemented", "provider": self.name}

    def health_check(self) -> Dict[str, Any]:
        return {"status": "not_configured", "provider": self.name}


def get_provider(provider_name: Optional[str] = None) -> GenerationProvider:
    name = (provider_name or os.getenv("VIDEO_MODEL_PROVIDER", "demo")).lower()

    if name == "huggingface":
        return HuggingFaceProvider()
    if name == "wan":
        return WanProvider()
    if name == "cogvideox":
        return CogVideoXProvider()
    return DemoProvider()
