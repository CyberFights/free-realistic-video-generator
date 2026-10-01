from __future__ import annotations

import os
import time
from typing import Any, Dict

from celery import Celery

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
)

@celery_app.task(name="tasks.generate_video")
def generate_video(payload: Dict[str, Any]) -> Dict[str, Any]:
    job_id = payload.get("job_id", "unknown")
    prompt = payload.get("prompt", "")
    duration = payload.get("duration", 8)
    aspect_ratio = payload.get("aspect_ratio", "16:9")

    time.sleep(5)

    return {
        "job_id": job_id,
        "status": "completed",
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "output_url": f"https://example.com/generated/{job_id}.mp4",
        "message": "Demo pipeline completed. Replace with real generation model.",
    }
