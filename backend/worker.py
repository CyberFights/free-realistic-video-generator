from __future__ import annotations

import os
from typing import Any, Dict

from celery import Celery

from database import GenerationJob, SessionLocal
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
    job_id = payload.get("job_id")

    db = SessionLocal()
    try:
        if job_id:
            job = db.query(GenerationJob).filter(GenerationJob.job_id == job_id).first()
            if job:
                job.status = "processing"
                db.commit()
    finally:
        db.close()

    pipeline = VideoPipeline(
        VideoPipelineConfig(
            model_name="demo-video-model",
            use_identity_lock=True,
            use_lip_sync=bool(payload.get("has_voiceover", False)),
            long_video_mode=False,
        )
    )

    output = pipeline.generate(payload)

    db = SessionLocal()
    try:
        if job_id:
            job = db.query(GenerationJob).filter(GenerationJob.job_id == job_id).first()
            if job:
                job.status = output.get("status", "completed")
                job.output_url = output.get("output_url")
                db.commit()
    finally:
        db.close()

    return output
