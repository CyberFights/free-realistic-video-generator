from __future__ import annotations

import os
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from worker import celery_app

app = FastAPI(title="Video Generator API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JOB_STORE: Dict[str, Dict[str, Any]] = {}


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "videogen-api",
        "redis": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    }


@app.post("/generate")
async def generate_video(
    prompt: str = Form(...),
    negative_prompt: str = Form(""),
    duration: int = Form(8),
    aspect_ratio: str = Form("16:9"),
    character_name: Optional[str] = Form(None),
    reference_image: Optional[UploadFile] = File(default=None),
    voiceover: Optional[UploadFile] = File(default=None),
):
    if not prompt or len(prompt.strip()) < 3:
        raise HTTPException(status_code=400, detail="Prompt is required")

    if duration < 4 or duration > 60:
        raise HTTPException(status_code=400, detail="Duration must be between 4 and 60 seconds")

    job_id = str(uuid.uuid4())
    payload = {
        "job_id": job_id,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "character_name": character_name,
        "has_reference_image": reference_image is not None,
        "has_voiceover": voiceover is not None,
        "created_at": __import__("datetime").datetime.utcnow().isoformat(),
    }

    task = celery_app.send_task("tasks.generate_video", kwargs={"payload": payload})

    JOB_STORE[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "task_id": task.id,
        "output_url": None,
    }

    return JSONResponse({
        "job_id": job_id,
        "status": "queued",
        "message": "Video generation started",
    })


@app.get("/jobs")
def list_jobs() -> Dict[str, Any]:
    return {
        "jobs": list(JOB_STORE.values()),
        "count": len(JOB_STORE),
    }


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> Dict[str, Any]:
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@app.get("/demo")
def demo() -> Dict[str, Any]:
    return {
        "project": "Realistic Video Generator",
        "features": [
            "text-to-video",
            "image + prompt generation",
            "character consistency",
            "long-form clips",
            "lip sync ready",
        ],
        "status": "starter scaffold",
    }
