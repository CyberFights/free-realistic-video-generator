from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class VideoPipelineConfig:
    model_name: str = "demo-video-model"
    use_identity_lock: bool = True
    use_lip_sync: bool = False
    long_video_mode: bool = False


class VideoPipeline:
    def __init__(self, config: Optional[VideoPipelineConfig] = None):
        self.config = config or VideoPipelineConfig()

    def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = payload.get("prompt", "")
        duration = payload.get("duration", 8)
        aspect_ratio = payload.get("aspect_ratio", "16:9")
        has_reference_image = payload.get("has_reference_image", False)
        has_voiceover = payload.get("has_voiceover", False)

        if has_reference_image:
            prompt = f"{prompt} [image-conditioned motion and identity consistent character]"

        if has_voiceover:
            prompt = f"{prompt} [voiceover audio provided, lip sync step enabled]"

        return {
            "job_id": payload.get("job_id", "demo-job"),
            "status": "completed",
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "output_url": f"https://example.com/generated/{payload.get('job_id', 'demo-job')}.mp4",
            "meta": {
                "model": self.config.model_name,
                "identity_locked": self.config.use_identity_lock,
                "lip_sync_enabled": self.config.use_lip_sync or has_voiceover,
                "long_video_mode": self.config.long_video_mode,
                "reference_image": has_reference_image,
                "voiceover": has_voiceover,
            },
            "steps": [
                "prompt normalization",
                "reference conditioning",
                "video generation",
                "post-processing",
            ],
        }

    def apply_character_consistency(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "identity-locked",
            "character_name": payload.get("character_name", "default-character"),
            "method": "reference-image conditioning",
        }

    def apply_lip_sync(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "lip-synced",
            "voiceover": payload.get("has_voiceover", False),
            "method": "Wav2Lip / SyncTalk integration ready",
        }
