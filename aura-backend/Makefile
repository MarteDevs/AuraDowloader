.PHONY: install test lint typecheck format run dev

install:
	pip install -r requirements-dev.txt

test:
	pytest

lint:
	ruff check .

lint:fix:
	ruff check --fix .

typecheck:
	mypy

format:
	ruff format .

run:
	uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

dev: run
