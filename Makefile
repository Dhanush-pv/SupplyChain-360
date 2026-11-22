.PHONY: install up down logs test lint sample demo ingest clean

install:
	python -m pip install -e ".[dev]"

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f minio

test:
	pytest -q

lint:
	ruff check .

# Regenerate the tiny SYNTHETIC sample files in data/sample/
sample:
	python scripts/generate_sample_data.py

# Ingest the synthetic sample into MinIO (requires `make up`)
demo:
	python -m supplychain360.cli --config config/datasets.sample.yaml

# Ingest the real datasets placed under data/raw/ (requires `make up`)
ingest:
	python -m supplychain360.cli

clean:
	docker compose down
