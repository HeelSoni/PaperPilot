---
title: PaperPilot Backend
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# PaperPilot Backend API

FastAPI backend for the PaperPilot Smart Research Paper Recommender.

## API Endpoints

- `GET /` — Health check
- `GET /health` — Health status
- `POST /search` — Semantic paper search
- `POST /summarize` — AI paper summarization
- `GET /recommend/{paper_id}` — Paper recommendations
- `GET /trends/{topic}` — Research trends
- `GET/POST/DELETE /reading-list` — Reading list management
