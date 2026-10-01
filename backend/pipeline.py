# backend/pipeline.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from model_adapter import LipSyncAdapter, VideoGenerationRequest, get_video_adapter


@dataclass
class VideoPipelineConfig:
    model_name: str = "demo-video-model"
    use_identity_lock: bool = True
    use_lip_sync: bool = False
    long_video_mode: bool = False


class VideoPipeline:
    def __init__(self, config: Optional[VideoPipelineConfig] = None):
        self.config = config or VideoPipelineConfig()
        self.adapter = get_video_adapter(self.config.model_name)
        self.lip_sync = LipSyncAdapter()

    def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        request = VideoGenerationRequest(
            prompt=payload.get("prompt", ""),
            duration=int(payload.get("duration", 8)),
            aspect_ratio=payload.get("aspect_ratio", "16:9"),
            negative_prompt=payload.get("negative_prompt", ""),
            character_name=payload.get("character_name"),
            reference_image_path=payload.get("reference_image_path"),
            voiceover_path=payload.get("voiceover_path"),
            has_reference_image=bool(payload.get("has_reference_image", False)),
            has_voiceover=bool(payload.get("has_voiceover", False)),
        )

        result = self.adapter.generate(request)

        if self.config.use_lip_sync or request.has_voiceover:
            result["lip_sync"] = self.lip_sync.sync(payload)

        result["meta"] = {
            **result.get("meta", {}),
            "model": self.config.model_name,
            "identity_locked": self.config.use_identity_lock,
            "lip_sync_enabled": self.config.use_lip_sync or request.has_voiceover,
            "long_video_mode": self.config.long_video_mode,
        }

        return result

    def apply_character_consistency(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "identity-locked",
            "character_name": payload.get("character_name", "default-character"),
            "method": "reference-image conditioning",
        }

    def apply_lip_sync(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.lip_sync.sync(payload)
