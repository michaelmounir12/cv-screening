# AI-Powered Resume Screening Backend

A Django-based backend system for AI-powered resume screening using HuggingFace Transformers, SentenceTransformers, and FAISS for vector similarity search.

## Tech Stack

- **Django** - Web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and Celery broker
- **Celery** - Background task processing
- **HuggingFace Transformers** - NLP models
- **SentenceTransformers** - Text embeddings
- **FAISS** - Vector similarity search
- **Docker** - Containerization

## Architecture

The project follows **Clean Architecture** principles with:

- **Domain Layer** (`apps/resume_screening/domain/`) - Business entities and value objects
- **Application Layer** (`apps/resume_screening/application/`) - Use cases and application services
- **Infrastructure Layer** (`apps/resume_screening/infrastructure/`) - External services (AI, databases, etc.)
- **Repository Pattern** (`apps/core/repositories/`) - Data access abstraction
- **Service Pattern** (`apps/core/services/`) - Business logic abstraction

## Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Using Docker Compose

1. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```

2. Build and start services:
   ```bash
   docker-compose up --build
   ```

3. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. Create superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Local Development

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL and Redis (or use Docker):
   ```bash
   docker-compose up db redis -d
   ```

4. Configure `.env` file

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start development server:
   ```bash
   python manage.py runserver
   ```

7. Start Celery worker (in another terminal):
   ```bash
   celery -A config.celery worker --loglevel=info
   ```

## Project Structure

```
.
├── apps/
│   ├── core/                    # Core utilities
│   │   ├── repositories/        # Base repository pattern
│   │   └── services/           # Base service pattern
│   └── resume_screening/        # Main application
│       ├── domain/               # Domain entities
│       ├── application/          # Application services
│       ├── infrastructure/       # External services (AI, etc.)
│       └── tasks/                # Celery tasks
├── config/                        # Django configuration
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Key Features

- **Async SQLAlchemy** - Non-blocking database operations
- **Repository Pattern** - Clean data access layer
- **Service Pattern** - Business logic separation
- **Celery Tasks** - Background processing
- **Vector Search** - FAISS-based similarity matching
- **Text Embeddings** - SentenceTransformers integration

## API Endpoints

API endpoints will be available at `/api/v1/` (to be implemented).

## Development Guidelines

- **No business logic in routes** - All logic in services
- **Repository pattern** - Use repositories for data access
- **Async operations** - Use async/await for database operations
- **Type hints** - Use type hints for better code clarity
