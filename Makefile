.PHONY: install db migrate dev test down

install:
	uv sync

db:
	docker compose up -d db adminer

migrate:
	uv run alembic upgrade head

dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 3000

test:
	uv run pytest -q

down:
	docker compose down
