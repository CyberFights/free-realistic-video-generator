from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class GenerateVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=3)
    negative_prompt: str = ""
    duration: int = Field(default=8, ge=4, le=60)
    aspect_ratio: str = Field(default="16:9")
    character_name: Optional[str] = None


class CharacterProfileCreate(BaseModel):
    name: str = Field(..., min_length=2)
    prompt: str = Field(..., min_length=3)
    style: str = "cinematic"


class CharacterProfileResponse(BaseModel):
    id: int
    name: str
    prompt: str
    style: str
    avatar_url: Optional[str] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    output_url: Optional[str] = None
    error: Optional[str] = None
