from __future__ import annotations

import os
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from worker import celery_app

app = FastAPI(title="Video Generator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerationRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    duration: int = 8
    aspect_ratio: str = "16:9"
    character_name: Optional[str] = None

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/generate")
async def generate_video(
    prompt: str = Form(...),
    negative_prompt: str = Form(""),
    duration: int = Form(8),
    aspect_ratio: str = Form("16:9"),
    character_name: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(default=None),
):
    if not prompt or len(prompt.strip()) < 3:
        raise HTTPException(status_code=400, detail="Prompt is required")

    job_id = str(uuid.uuid4())
    payload = {
        "job_id": job_id,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "character_name": character_name,
        "has_image": image is not None,
    }

    celery_app.send_task("tasks.generate_video", kwargs={"payload": payload})

    return JSONResponse({
        "job_id": job_id,
        "status": "queued",
        "message": "Video generation started"
    })

@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> Dict[str, Any]:
    return {
        "job_id": job_id,
        "status": "queued",
        "output_url": None,
        "message": "Demo job status endpoint"
    }
