# Free Realistic Video Generator

A Railway-ready starter project for a free/open-source realistic AI video generator with:
- text-to-video
- image + text-to-video
- character profile creation
- identity consistency
- long video generation
- lip sync support

This repository is a production-style starter scaffold, not a closed-source SaaS mirror. It is designed to help you launch a working app on Railway with a modular architecture that can evolve into a real model pipeline.

## Stack
- Frontend: Next.js + Tailwind
- API: FastAPI
- Background jobs: Celery + Redis
- Database: PostgreSQL
- Storage: object storage / Railway volume
- Video pipeline: pluggable model adapters (Wan, CogVideoX, LTX-Video, Wav2Lip, SyncTalk)

## Repository structure
- `frontend/` - Next.js app
- `backend/` - FastAPI API + job worker
- `scripts/` - helper scripts
- `docker-compose.yml` - local development
- `.env.example` - environment variables

## Quick start

### 1) Copy environment variables
```bash
cp .env.example .env
```

### 2) Run local services
```bash
docker compose up --build
```

### 3) Start frontend
```bash
cd frontend
npm install
npm run dev
```

### 4) Start backend API (if not using docker compose)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5) Start worker
```bash
cd backend
source .venv/bin/activate
celery -A worker worker --loglevel=info
```

## Railway deployment

This project is designed to work on Railway with these services:
- `web` service for frontend
- `api` service for FastAPI backend
- `worker` service for Celery jobs
- Redis service
- Postgres service
- optional S3-compatible bucket for generated videos

Environment variables expected on Railway:
```bash
REDIS_URL=redis://...
DATABASE_URL=postgresql://...
NEXT_PUBLIC_API_URL=https://your-api.up.railway.app
API_BASE_URL=https://your-api.up.railway.app
SECRET_KEY=change-me
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=...
S3_ENDPOINT=...
```

## Model pipeline

The starter includes a modular `VideoPipeline` abstraction so you can swap in open-source generation models:
- text-to-video models
- image-conditioned video generation
- character identity adapters
- lip sync models

The default implementation is intentionally a placeholder "demo pipeline" that simulates generation, so the project can be run immediately and later upgraded to real models.

## Features included in the scaffold
- prompt form for text-to-video requests
- optional image upload for image + text prompts
- job tracking with polling
- generated asset metadata
- architecture ready for long videos and lip sync

## Production upgrade roadmap
1. Replace stub pipeline with real open-source model runtime
2. Add character profile database entries and LoRA/IP-Adapter embeddings
3. Add FFmpeg scene concatenation for long clips
4. Add Wav2Lip / SyncTalk integration for audio-driven lip sync
5. Add storage, authentication, billing, and project management

## Licensing
MIT

## Notes
This project is intentionally scoped as a realistic starter and deployment scaffold. It is designed to be extended into a real AI video product.
