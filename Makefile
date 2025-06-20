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

IMAGE_TAG?=v1.0.0
REGISTRY?=

build_and_push:
	docker buildx build --platform linux/amd64 -t $(REGISTRY)/rag-backend:$(IMAGE_TAG)  -f rag-backend/Dockerfile --push  .
	docker buildx build --platform linux/amd64 -t $(REGISTRY)/admin-backend:$(IMAGE_TAG)  -f admin-backend/Dockerfile --push .
	docker buildx build --platform linux/amd64 -t $(REGISTRY)/document-extractor:$(IMAGE_TAG)  -f document-extractor/Dockerfile --push .
	docker buildx build --platform linux/amd64 -t $(REGISTRY)/frontend:$(IMAGE_TAG)  -f frontend/apps/chat-app/Dockerfile --push .
	docker buildx build --platform linux/amd64 -t $(REGISTRY)/admin-frontend:$(IMAGE_TAG)  -f frontend/apps/admin-app/Dockerfile --push .
    docker buildx build --platform linux/amd64 -t $(REGISTRY)/mcp-server:$(IMAGE_TAG)  -f mcp-server/Dockerfile --push .
