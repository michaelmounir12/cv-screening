# AI-Powered Resume Screening Backend

A production-ready Django backend for AI-powered resume screening. Upload resumes, create job descriptions, and match candidates using semantic similarity, vector search, and skill extraction.

## Features

- **Resume Upload** — Single and batch PDF upload with text extraction (PyMuPDF/pdfplumber)
- **Semantic Search** — Natural language search over resumes using embeddings
- **Job Matching** — Rank resumes by cosine similarity against job descriptions
- **Skill Extraction** — Automatic skill keyword extraction via spaCy
- **Vector Index** — FAISS-powered similarity search with persistent index
- **Job CRUD** — Full create, read, update, delete for job postings
- **Caching** — Redis-backed cache for frequent job searches
- **Background Processing** — Celery for async text extraction and embedding generation
- **Logging & Error Handling** — Request logging middleware and structured error responses

## Tech Stack

| Component        | Technology              |
|-----------------|-------------------------|
| Framework       | Django 4.2              |
| Database        | PostgreSQL 15           |
| Cache / Broker  | Redis 7                 |
| Task Queue      | Celery                  |
| Embeddings      | SentenceTransformers (all-MiniLM-L6-v2) |
| Vector Search   | FAISS                   |
| PDF Processing  | PyMuPDF, pdfplumber     |
| NLP             | spaCy                   |
| Containerization| Docker, Docker Compose  |

## Architecture

Clean architecture with clear separation of concerns:

```
apps/resume_screening/
├── domain/           # Business entities and value objects
├── application/      # Use cases and application services
│   └── services/     # ResumeUploadService, MatchingService, etc.
├── infrastructure/   # External concerns
│   ├── ai/           # Embedding, FAISS vector index
│   ├── repositories/ # Data access (Resume, JobPosting)
│   └── services/     # PDF extraction, skill extraction, cache
├── tasks/            # Celery tasks
└── models.py         # Django ORM models
```

- **Repository pattern** — Data access abstraction
- **Service pattern** — Business logic in services, thin views
- **No business logic in routes** — Controllers delegate to services

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)

### Run with Docker

```bash
# Clone and enter project
cd "cv screening project"

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up --build

# In another terminal: run migrations
docker-compose exec web python manage.py migrate

# Optional: create admin user
docker-compose exec web python manage.py createsuperuser
```

API: **http://localhost:8000/api/v1/**  
Admin: **http://localhost:8000/admin/**

---

## Local Development

### 1. Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS
```

### 2. Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Database & Redis

```bash
docker-compose up db redis -d
```

### 4. Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work with Docker DB/Redis)
```

### 5. Migrations

```bash
python manage.py migrate
```

### 6. Run Services

**Terminal 1 — Django:**
```bash
python manage.py runserver
```

**Terminal 2 — Celery worker:**
```bash
celery -A config.celery worker --loglevel=info
```

**Optional — Celery Beat:**
```bash
celery -A config.celery beat --loglevel=info
```

---

## Configuration

Environment variables (`.env`):

| Variable            | Description                      | Default                          |
|---------------------|----------------------------------|----------------------------------|
| `SECRET_KEY`        | Django secret key                | (change in production)           |
| `DEBUG`             | Debug mode                       | `True`                           |
| `ALLOWED_HOSTS`     | Allowed hosts (comma-separated)  | `localhost,127.0.0.1`           |
| `DB_NAME`           | PostgreSQL database name         | `resume_screening`               |
| `DB_USER`           | PostgreSQL user                  | `postgres`                       |
| `DB_PASSWORD`       | PostgreSQL password              | `postgres`                       |
| `DB_HOST`           | PostgreSQL host                  | `localhost`                      |
| `DB_PORT`           | PostgreSQL port                  | `5432`                           |
| `REDIS_HOST`        | Redis host                       | `localhost`                      |
| `REDIS_PORT`        | Redis port                       | `6379`                           |
| `CELERY_BROKER_URL` | Celery broker URL                | `redis://localhost:6379/0`       |
| `CELERY_RESULT_BACKEND` | Celery result backend       | `redis://localhost:6379/0`       |
| `HF_MODEL_NAME`     | SentenceTransformer model        | `sentence-transformers/all-MiniLM-L6-v2` |
| `CORS_ALLOWED_ORIGINS` | CORS origins                 | `http://localhost:3000,...`      |

---

## API Reference

Base URL: `/api/v1/`

### Resumes

| Method | Endpoint                      | Description                         |
|--------|-------------------------------|-------------------------------------|
| POST   | `/resumes/upload/`            | Upload single PDF                   |
| POST   | `/resumes/upload/batch/`      | Batch upload (max 50 PDFs)          |
| GET    | `/resumes/<uuid>/`            | Get resume by ID                    |

### Jobs

| Method | Endpoint                | Description                |
|--------|-------------------------|----------------------------|
| POST   | `/jobs/`                | Create job posting         |
| GET    | `/jobs/list/`           | List jobs (paginated)      |
| GET    | `/jobs/<uuid>/`         | Get job by ID              |
| PUT    | `/jobs/<uuid>/`         | Update job                 |
| DELETE | `/jobs/<uuid>/`         | Delete job                 |

### Matching & Search

| Method | Endpoint    | Description                            |
|--------|-------------|----------------------------------------|
| POST   | `/match/`   | Match resumes to job (by ID or text)   |
| POST   | `/rank/`    | Rank resumes with similarity scores    |
| POST   | `/search/`  | Semantic search over resumes           |

### Examples

**Upload resume:**
```bash
curl -X POST -F "file=@resume.pdf" http://localhost:8000/api/v1/resumes/upload/
```

**Batch upload:**
```bash
curl -X POST -F "files=@resume1.pdf" -F "files=@resume2.pdf" http://localhost:8000/api/v1/resumes/upload/batch/
```

**Create job:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"title":"Senior Python Developer","description":"5+ years Python, Django, PostgreSQL"}' \
  http://localhost:8000/api/v1/jobs/
```

**Match resumes to job:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"job_id":"<job-uuid>","k":5}' \
  http://localhost:8000/api/v1/match/
```

**Semantic search:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"Python developer with Django experience","k":10}' \
  http://localhost:8000/api/v1/search/
```

**Rank resumes:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"job_id":"<job-uuid>","k":5}' \
  http://localhost:8000/api/v1/rank/
```

---

## Project Structure

```
.
├── apps/
│   ├── core/                      # Shared utilities
│   │   ├── repositories/          # Base repository
│   │   └── database.py            # SQLAlchemy async (optional)
│   └── resume_screening/
│       ├── models.py              # Resume, JobPosting
│       ├── views.py               # API views
│       ├── serializers.py
│       ├── urls.py
│       ├── domain/                # Entities
│       ├── application/services/  # Business logic
│       ├── infrastructure/
│       │   ├── ai/                # Embedding, FAISS
│       │   ├── repositories/      # DB access
│       │   └── services/          # PDF, skills, cache
│       ├── tasks/                 # Celery tasks
│       └── migrations/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── middleware.py              # Logging, error handling
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Celery Tasks

| Task                        | Description                              |
|-----------------------------|------------------------------------------|
| `extract_resume_text_task`  | Extract text from PDF, extract skills, queue embedding |
| `generate_resume_embedding_task` | Generate embedding, add to FAISS index |
| `rebuild_vector_index_task` | Rebuild FAISS index from DB              |

Trigger index rebuild:
```python
from apps.resume_screening.tasks import rebuild_vector_index_task
rebuild_vector_index_task.delay()
```

---

## Processing Pipeline

1. **Upload** — PDF saved, DB record created, Celery task queued  
2. **Extract** — PyMuPDF/pdfplumber extracts text  
3. **Skills** — spaCy + regex extract skill keywords  
4. **Embed** — SentenceTransformers generates 384-dim vector  
5. **Index** — Vector stored in FAISS, persisted to disk  

Matching uses cosine similarity (L2-normalized inner product) via FAISS.

---

## Development Guidelines

- Keep business logic in services; views stay thin
- Use repositories for data access
- Add type hints to new code
- Run `black` and `flake8` before committing

---

## License

MIT
