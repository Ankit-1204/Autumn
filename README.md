## Autumn

FastAPI + Celery workflow backend with a React (Vite) frontend. Dockerized with Postgres, RabbitMQ, and Redis.

### Stack
- Backend: FastAPI, SQLAlchemy, Alembic, Celery, Redis Pub/Sub
- Frontend: React + Vite
- Infra: Postgres, RabbitMQ, Redis, Docker Compose

### Project structure
- `backend/`: FastAPI app, Celery worker, DB models/migrations
- `autumn/`: React/Vite frontend
- `docker-compose.yml`: Full stack (db, rabbitmq, redis, backend, worker, frontend)

### Environment variables

Backend (`backend/.env`):
