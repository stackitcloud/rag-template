.PHONY: lint test

lint:
	cd rag-core-library;make lint
	cd admin-backend;make lint
	cd rag-backend;make lint
	cd document-extractor;make lint	

update-lock:
	cd rag-core-library;make update-lock
	cd admin-backend;poetry lock --regenerate
	cd rag-backend;poetry lock --regenerate
	cd document-extractor;poetry lock --regenerate

black:
	cd rag-core-library;make black
	cd admin-backend;black .
	cd rag-backend;black .
	cd document-extractor;black .