.PHONY: lint coverage

lint:
	flake8 --config=pyproject.toml --format=dashboard --title="RAG Core Lint Report" --debug src/rag_core/*

coverage:
	coverage run --omit *.pyc --omit *__init__.py --source src/rag_core -m pytest tests
	coverage report -m
	coverage html
