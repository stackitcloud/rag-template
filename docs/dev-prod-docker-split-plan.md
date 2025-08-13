# Dev/Prod Docker Split – Migration Plan

This document outlines the changes to move this repository to two Dockerfiles per service:

- Development: Dockerfile.dev (source-based, fast iteration)
- Production: Dockerfile (package-based, reproducible, minimal)

Goal: keep dependency versions identical between dev and prod while optimizing for fast local development and safe production builds.

## Current state (summary)

- Single Dockerfile per service, parameterized with build args for dev behavior.
- Services import local libs via directory layout/PYTHONPATH in containers.
- Tilt uses docker_build with live_update and narrowed ignore rules.
- Services: services/rag-backend, services/admin-backend, services/document-extractor, services/mcp-server.
- Local libs: libs/rag-core-api, libs/rag-core-lib, libs/admin-api-lib, libs/extractor-api-lib.

## Target design

- Dev images: do not install local libs as packages; copy lib sources and use PYTHONPATH; include debug tooling.
- Prod images: install local libs as packages (no PYTHONPATH hacks), pinned dependencies, no dev extras.
- Tilt references Dockerfile.dev; Helm/CI use production Dockerfile.

## Service → library mapping

- rag-backend: rag-core-api, rag-core-lib
- admin-backend: admin-api-lib, rag-core-lib
- document-extractor: extractor-api-lib
- mcp-server: no local libs

## Changes required (overview)

1. Add Dockerfile.dev to each Python service.
2. Simplify existing Dockerfile to production-only.
3. Choose a production installation strategy for local libs:
   - Option A (recommended if possible): publish libs to an internal package registry and depend by version.
   - Option B (no registry): build wheels for libs during the image build and install them.
4. Update Tiltfile to use Dockerfile.dev and remove dev build args.
5. Ensure identical Python/runtime dependency versions between dev/prod.
6. Update documentation (README) to explain the split.
7. (Optional) CI/CD updates for building/publishing libs and images.

---

## Detailed step-by-step

### Step 1: Create Dockerfile.dev per service

For each service under services/*:

- Base: same Python base image used in prod.
- Install system packages needed for dev (build tools if necessary).
- Configure a single shared venv (or system site-packages) consistent with prod.
- Install service third-party dependencies without packaging the service itself (no-root/install editable is fine).
- Copy only the local libs this service uses under /app/libs/* and set PYTHONPATH to include service src and those libs' src folders.
- Include debug tooling (e.g., debugpy) and any dev-only linters/formatters if desired.
- Entrypoint: same as prod (uvicorn/etc.), plus conditional debug attach if Tilt debug is enabled.

Notes:

- Keep the base image and Python minor version identical to prod to maintain runtime parity.
- Keep layer order optimized for Tilt live_update (requirements before source copy where possible).

### Step 2: Convert existing Dockerfile to production

For each service:

- Remove dev build args, debug packages, and PYTHONPATH modifications.
- Install only runtime dependencies.
- Install local libs as packages (see Step 3) so imports do not rely on PYTHONPATH.
- Use a minimal runtime image (multi-stage if needed) to reduce size/attack surface.
- Ensure deterministic installs (do not run lock updates during build).

### Step 3: Production install strategy for local libs

Pick one of the two approaches:

Option A: Publish versioned libs to a registry (preferred)

- Ensure each lib has proper package metadata (name, version) in pyproject.
- Set up a CI job to build and publish the libs on tag (e.g., vX.Y.Z per lib) to a private index.
- In each service pyproject, declare dependencies on those libs by version.
- Commit poetry.lock and use it in Docker builds to guarantee pinning.

Pros: Cleanest prod images, reproducible, simple Dockerfiles, easy CVE scanning.

Option B: Build and install wheels in Docker build (no external registry)

- In each service Dockerfile (build stage):
  - Copy only the required libs for that service.
  - Build wheels for those libs (PEP 517) and store them in a local wheelhouse.
  - Install wheels into the final image.
- Keep service third-party dependencies pinned (use the service’s poetry.lock to install/export pinned requirements).
- Consider exporting pinned requirements from each lib (constraints) to avoid accidental unpinned resolves.

Pros: Works without a registry. Cons: a bit more Dockerfile logic.

### Step 4: Update Tiltfile

- For each docker_build, point to Dockerfile.dev for the service (remove dev build args).
- Keep existing live_update syncs and ignore lists.
- No PYTHONPATH/env overrides in Helm; Dockerfile.dev sets them.

### Step 5: Keep runtime parity

- Use the same Python base image tag in Dockerfile and Dockerfile.dev.
- Ensure the same dependency versions:
  - Dev: install using the same lock (poetry install without updating the lock).
  - Prod: install using the same lock or pinned wheels.
- Avoid “latest” floating versions in prod.

### Step 6: Documentation updates

- README: add a short section describing Dockerfile vs Dockerfile.dev usage.
- Note for contributors how to add new third-party deps (poetry add) and how local libs are handled in dev vs prod.

### Step 7: CI/CD updates

- Images: build production images with Dockerfile (no dev tooling).
- Tests: run unit tests in CI against the production Docker image or a dedicated test image derived from prod.
- If Option A (publish libs): add a release workflow to publish libs to the registry and bump service dependencies.
- If Option B (build wheels): ensure CI builds succeed from a clean checkout (no network to private registries required).

---

## Open decisions

- Choose between Option A (publish libs) and Option B (build wheels in Docker).
- Decide whether to keep Poetry as the installer in prod or export to requirements and install via pip. Either is fine if you do not regenerate locks during builds.

## Migration checklist

- [ ] Approve Option A or Option B for production lib installs.
- [ ] Add Dockerfile.dev to all Python services.
- [ ] Simplify existing Dockerfiles to production-only.
- [ ] Update Tiltfile to use Dockerfile.dev and remove dev build args.
- [ ] Verify services run under Tilt and in prod (Helm).
- [ ] Update README with dev/prod split and contributor guidance.
- [ ] Update CI: build/test/publish as decided.

## Notes specific to this repo

- Services and their required libs:
  - rag-backend → rag-core-api, rag-core-lib
  - admin-backend → admin-api-lib, rag-core-lib
  - document-extractor → extractor-api-lib
  - mcp-server → no local libs
- Frontend and infrastructure are unaffected by this change.
- Keep the recently added Tilt ignore rules; they still apply with Dockerfile.dev.
