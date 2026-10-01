# backend/database.py
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./videogen.db")
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class CharacterProfile(Base):
    __tablename__ = "character_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    style: Mapped[str] = mapped_column(String(255), default="cinematic")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    jobs: Mapped[list["GenerationJob"]] = relationship(back_populates="character_profile")


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    negative_prompt: Mapped[str] = mapped_column(Text, default="")
    duration: Mapped[int] = mapped_column(Integer, default=8)
    aspect_ratio: Mapped[str] = mapped_column(String(16), default="16:9")
    status: Mapped[str] = mapped_column(String(64), default="queued")
    output_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    has_reference_image: Mapped[bool] = mapped_column(Boolean, default=False)
    has_voiceover: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    character_profile_id: Mapped[Optional[int]] = mapped_column(ForeignKey("character_profiles.id"), nullable=True)
    character_profile: Mapped[Optional[CharacterProfile]] = relationship(back_populates="jobs")


def create_db_and_tables() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
