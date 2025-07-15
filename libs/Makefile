.PHONY: lint update-lock black test

lint:
	cd rag-core-lib;make lint
	cd rag-core-api;make lint
	cd admin-api-lib;make lint
	cd extractor-api-lib;make lint

update-lock:
	cd rag-core-lib;poetry lock --no-update
	cd rag-core-api;poetry lock --no-update
	cd admin-api-lib;poetry lock --no-update
	cd extractor-api-lib;poetry lock --no-update
	poetry lock --no-update

black:
	cd rag-core-lib;black .
	cd rag-core-api;black .
	cd admin-api-lib;black .
	cd extractor-api-lib;black .
