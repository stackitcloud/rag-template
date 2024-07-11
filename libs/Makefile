.PHONY: lint coverage

lint:
	poetry run flake8 --config=pyproject.toml  --format=dashboard --title="RAG Core Lint Report" --debug ./*

coverage:
	poetry run coverage run --omit *.pyc --omit *__init__.py --source src/rag_core -m pytest tests
	poetry run coverage report -m
	poetry run coverage html
