from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import CharacterProfile, GenerationJob, create_db_and_tables, get_db
from schemas import CharacterProfileResponse, JobStatusResponse
from storage import storage
from worker import celery_app

app = FastAPI(title="Video Generator API", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/storage", StaticFiles(directory="./storage"), name="storage")


@app.on_event("startup")
def startup() -> None:
    create_db_and_tables()


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "videogen-api",
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
    db: Session = Depends(get_db),
):
    if not prompt or len(prompt.strip()) < 3:
        raise HTTPException(status_code=400, detail="Prompt is required")

    if duration < 4 or duration > 60:
        raise HTTPException(status_code=400, detail="Duration must be between 4 and 60 seconds")

    job_id = os.urandom(8).hex()

    reference_info = None
    voiceover_info = None

    if reference_image is not None:
        reference_info = storage.save_upload(reference_image.file, "reference_images", reference_image.filename or "reference.png")

    if voiceover is not None:
        voiceover_info = storage.save_upload(voiceover.file, "voiceovers", voiceover.filename or "voiceover.wav")

    job = GenerationJob(
        job_id=job_id,
        prompt=prompt,
        negative_prompt=negative_prompt,
        duration=duration,
        aspect_ratio=aspect_ratio,
        status="queued",
        has_reference_image=reference_image is not None,
        has_voiceover=voiceover is not None,
        output_url=(reference_info.url if reference_info else (voiceover_info.url if voiceover_info else None)),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    payload = {
        "job_id": job_id,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "character_name": character_name,
        "has_reference_image": reference_image is not None,
        "has_voiceover": voiceover is not None,
        "reference_image_path": reference_info.path if reference_info else None,
        "voiceover_path": voiceover_info.path if voiceover_info else None,
    }

    celery_app.send_task("tasks.generate_video", kwargs={"payload": payload})

    return JSONResponse({
        "job_id": job_id,
        "status": "queued",
        "message": "Video generation started",
    })


@app.get("/jobs", response_model=List[JobStatusResponse])
def list_jobs(db: Session = Depends(get_db)) -> List[GenerationJob]:
    return db.query(GenerationJob).order_by(GenerationJob.created_at.desc()).all()


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str, db: Session = Depends(get_db)) -> GenerationJob:
    job = db.query(GenerationJob).filter(GenerationJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/characters")
def list_characters(db: Session = Depends(get_db)) -> List[CharacterProfileResponse]:
    profiles = db.query(CharacterProfile).order_by(CharacterProfile.created_at.desc()).all()
    return [
        CharacterProfileResponse(
            id=p.id,
            name=p.name,
            prompt=p.prompt,
            style=p.style,
            avatar_url=p.avatar_url,
        )
        for p in profiles
    ]


@app.post("/characters", response_model=CharacterProfileResponse)
async def create_character(
    name: str = Form(...),
    prompt: str = Form(...),
    style: str = Form("cinematic"),
    avatar: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db),
):
    existing = db.query(CharacterProfile).filter(CharacterProfile.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Character already exists")

    avatar_url = None
    if avatar is not None:
        saved = storage.save_upload(avatar.file, "avatars", avatar.filename or f"{name}.png")
        avatar_url = saved.url

    profile = CharacterProfile(
        name=name,
        prompt=prompt,
        style=style,
        avatar_url=avatar_url,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return CharacterProfileResponse(
        id=profile.id,
        name=profile.name,
        prompt=profile.prompt,
        style=profile.style,
        avatar_url=profile.avatar_url,
    )


@app.get("/demo")
def demo() -> Dict[str, Any]:
    return {
        "project": "Realistic Video Generator",
        "features": [
            "text-to-video",
            "image + prompt generation",
            "character consistency",
            "lip sync ready",
        ],
        "status": "backend database scaffold",
    }
