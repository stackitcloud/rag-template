.PHONY: lint coverage test

lint:
	poetry run flake8 .

test:
	poetry run python -m pytest tests

coverage:
	poetry run coverage run --omit *.pyc --omit *__init__.py --source src/rag_core -m pytest tests
	poetry run coverage report -m
	poetry run coverage html
