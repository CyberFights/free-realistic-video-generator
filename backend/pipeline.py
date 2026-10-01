from __future__ import annotations

import os
from typing import Any, Dict

from celery import Celery

from pipeline import VideoPipeline, VideoPipelineConfig

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "videogen",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,
)


@celery_app.task(name="tasks.generate_video")
def generate_video(payload: Dict[str, Any]) -> Dict[str, Any]:
    pipeline = VideoPipeline(
        VideoPipelineConfig(
            model_name="wan-2.1-demo",
            use_identity_lock=True,
            use_lip_sync=payload.get("has_voiceover", False),
        )
    )

    output = pipeline.generate(payload)
    return output
