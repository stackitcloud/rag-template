.PHONY: lint test

lint:
	cd rag-core-lib;make lint
	cd rag-core-api;make lint
	cd admin-api-lib;make lint
	cd extractor-api-lib;make lint

update-lock:
	cd rag-core-lib;poetry lock --regenerate
	cd rag-core-api;poetry lock --regenerate
	cd admin-api-lib;poetry lock --regenerate
	cd extractor-api-lib;poetry lock --regenerate
	poetry lock --regenerate

black:
	cd rag-core-lib;black .
	cd rag-core-api;black .
	cd admin-api-lib;black .
	cd extractor-api-lib;black .