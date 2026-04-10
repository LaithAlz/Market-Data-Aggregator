.PHONY: up down reset migrate run dashboard frontend test lint

# ── Infrastructure ────────────────────────────────────────────────────────────

up:
	docker compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 5

down:
	docker compose down

reset:
	docker compose down -v
	docker compose up -d
	@sleep 5
	$(MAKE) migrate

# ── Database ──────────────────────────────────────────────────────────────────

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(msg)"

# ── Application ───────────────────────────────────────────────────────────────

run:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

dashboard:
	python -m cli.dashboard

frontend:
	cd frontend && npm run dev

# ── Testing ───────────────────────────────────────────────────────────────────

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=. --cov-report=term-missing

# ── Dev setup ─────────────────────────────────────────────────────────────────

install:
	pip install -r requirements.txt

setup: install up migrate
	@echo "Setup complete. Copy .env.example to .env and fill in your Alpaca credentials."
	@echo "Then run: make run"
