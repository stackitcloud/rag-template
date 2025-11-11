.PHONY: lint test

lint:
	cd libs;make lint
	cd services/admin-backend;make lint
	cd services/rag-backend;make lint
	cd services/document-extractor;make lint

update-lock:
	cd libs;make update-lock
	cd services/admin-backend;poetry lock --no-update
	cd services/rag-backend;poetry lock --no-update
	cd services/document-extractor;poetry lock --no-update

black:
	cd libs;make black
	cd services/admin-backend;black .
	cd services/rag-backend;black .
	cd services/document-extractor;black .

IMAGE_TAG?=v1.0.0
REGISTRY?=

build_and_push:
	docker buildx build --platform linux/amd64 -t $(REGISTRY)/rag-backend:$(IMAGE_TAG) -t $(REGISTRY)/rag-backend:latest -f services/rag-backend/Dockerfile --push  .
	docker buildx build --platform linux/amd64 -t $(REGISTRY)/admin-backend:$(IMAGE_TAG) -t $(REGISTRY)/admin-backend:latest -f services/admin-backend/Dockerfile --push .
	docker buildx build --platform linux/amd64 -t $(REGISTRY)/document-extractor:$(IMAGE_TAG) -t $(REGISTRY)/document-extractor:latest -f services/document-extractor/Dockerfile --push .
	docker buildx build --platform linux/amd64 -t $(REGISTRY)/frontend:$(IMAGE_TAG) -t $(REGISTRY)/frontend:latest -f services/frontend/apps/chat-app/Dockerfile --push .
	docker buildx build --platform linux/amd64 -t $(REGISTRY)/admin-frontend:$(IMAGE_TAG) -t $(REGISTRY)/admin-frontend:latest -f services/frontend/apps/admin-app/Dockerfile --push .
	docker buildx build --platform linux/amd64 -t $(REGISTRY)/mcp-server:$(IMAGE_TAG) -t $(REGISTRY)/mcp-server:latest -f services/mcp-server/Dockerfile --push .
