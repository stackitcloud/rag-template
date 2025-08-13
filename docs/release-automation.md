# Release & Helm Versioning — Monorepo Guide

> Automated, reviewable releases for **libs → services → images → Helm chart**, with immutable deployments. This file removes FluxCD specifics and shows a direct Helm/GitHub Actions path. Optional references to an env repo are generic.

---

## Why this setup

* **Deterministic versions**: compute `X.Y.Z` once, keep it through merge.
* **Immutable prod**: deploy by **image digest** (tags are convenience only).
* **Separation of concerns**: libs → images → chart packaging → deploy.
* **Human-in-the-loop**: release PR before publishing; optional approval for prod deploy.
* **Easy rollback**: previous chart + pinned digest.

---

## Versioning policy (Chart vs App)

`Chart.yaml` has two different version fields:

* **`appVersion`** — the **application** version you’re deploying. Set it to `X.Y.Z`.
* **`version`** — the **chart package** version. Must be **unique** on every publish.

**Rules**

1. On every **app release**: set `appVersion = X.Y.Z` and **bump chart `version` (patch)** — even if templates didn’t change.
2. **Chart-only, non-breaking** changes → **patch/minor** bump.
3. **Chart breaking** changes (values schema or behavior) → **major** bump.
4. **Never** deploy `latest` in prod. Default tag to `.Chart.AppVersion`; **pin by digest** in prod values.

**Examples**

* Probe tweak only → `version: 0.13.0 → 0.13.1`, `appVersion: 1.4.2`.
* New app `1.4.3`, no template change → `appVersion: 1.4.3`, `version: 0.13.1 → 0.13.2`.
* Values schema change → `version: 1.0.0`, `appVersion` stays at current app.

---

## Repo layout (suggested)

```
monorepo/
  libs/
    libA/
    libB/
  services/
    api/
      pyproject.toml
      Dockerfile
    worker/
      ...
  charts/
    myapp/
      Chart.yaml
      values.yaml
      templates/
        deployment.yaml
        service.yaml
  .github/workflows/
    prepare-release.yml
    publish-libs-on-merge.yml
    build-images.yml
    create-release.yml
    publish-chart.yml
    deploy-prod.yml   # optional direct Helm deploy with approval gate
```

---

## Step-by-step (CI/CD)

### Step 0 — Prereqs & hardening

* **Secrets**: `PYPI_TOKEN`, optional `TEST_PYPI_TOKEN`, and GHCR permissions via `GITHUB_TOKEN` (`packages: write`).
* **Tools**: Python+Poetry, Node (semantic-release), Docker Buildx, Helm ≥ 3.8 (OCI). Optional: Cosign.
* **Workflow settings**: `concurrency: { group: release, cancel-in-progress: true }`; permissions `contents: write`, `pull-requests: write`, `packages: write`.

### Step 1 — Prepare Release PR

Workflow: `.github/workflows/prepare-release.yml` (manual dispatch or rule you prefer)

1. Compute next version with **semantic-release dry-run** → write to `.version`.
2. Bump all **libs** to `X.Y.Z`; bump **service pins** under `[tool.poetry.group.prod.dependencies]`.
3. `poetry lock` per service.
4. **Update chart**: set `appVersion: X.Y.Z`; bump `version` **patch**; ensure templates default to `.Chart.AppVersion` and support digest pinning (below).
5. Open PR `chore/release-X.Y.Z` with all changes. Keep it to `chore/docs/build` to avoid version drift.

### Step 2 — Publish libs to PyPI (on merge)

Workflow: `.github/workflows/publish-libs-on-merge.yml`

* Trigger: `on: push` to `main` (with `paths` filters).
* Read `X.Y.Z` from `.version`; build & publish each `libs/*` with Poetry to PyPI.

### Step 3 — Build images & capture digests

Workflow: `.github/workflows/build-images.yml` (triggered by Step 2 success)

* Build & push images to GHCR tagged `:X.Y.Z` (optionally also `:latest`, but don’t use latest in prod).
* Capture **digests** for each service into `image-digests.json` and upload as artifact.

### Step 4 — Create GitHub Release/tag `vX.Y.Z`

Workflow: `.github/workflows/create-release.yml` (after Step 3)

* Create annotated tag & GitHub Release for `vX.Y.Z`; attach notes/SBOM if desired.

### Step 5 — Package & publish Helm chart(s)

Workflow: `.github/workflows/publish-chart.yml` (on release published)

* Ensure `Chart.yaml` already has `appVersion: X.Y.Z` and bumped `version` from Step 1.
* Optionally write a `values.prod.yaml` that sets per-service **`image.digest`** from the Step 3 artifact.
* `helm package charts/myapp` → `helm push` to `oci://ghcr.io/<org>/charts`.

### Step 6 — Deploy to prod (direct Helm with approval)

Workflow: `.github/workflows/deploy-prod.yml` (manual dispatch or `on: release` + environment gate)

* Inputs: `chartVersion`, `appVersion` (from release), and the Step 3 `image-digests.json` artifact.
* Command:

  ```bash
  helm upgrade --install myapp oci://ghcr.io/<org>/charts/myapp \
    --version <chartVersion> \
    --namespace prod \
    -f values/prod.yaml \
    --set services.api.image.digest=$(jq -r .api.digest image-digests.json) \
    --set services.worker.image.digest=$(jq -r .worker.digest image-digests.json)
  ```
* Protect with **environment approvals** in GitHub.

### Step 7 — Rollback

* `helm rollback <release> <rev>` to revert chart+values.
* To force exact bits, set previous **digest** via `--set services.api.image.digest=sha256:...`.

---

## Helm snippets

### `Chart.yaml`

```yaml
apiVersion: v2
name: myapp
version: 0.13.0        # chart version (bump every chart change)
appVersion: 1.4.2      # application version (X.Y.Z)
```

### `values.yaml` (partial)

```yaml
image:
  repository: ghcr.io/org/myapp
  tag: ""     # leave empty → default to .Chart.AppVersion in templates
  digest: ""  # set in prod via overrides

services:
  api:
    image:
      repository: ghcr.io/org/api
      tag: ""
      digest: ""
  worker:
    image:
      repository: ghcr.io/org/worker
      tag: ""
      digest: ""
```

### `templates/deployment.yaml` (image line)

```yaml
image: "{{ .Values.services.api.image.repository }}:{{ default .Chart.AppVersion .Values.services.api.image.tag }}{{- if .Values.services.api.image.digest }}@{{ .Values.services.api.image.digest }}{{- end }}"
```

---

## CI guardrails (copy/paste)

### A) Auto-bump chart patch & set `appVersion` in the Release PR

```bash
set -euo pipefail
VERSION=$(cat .version)
for chart in charts/*/Chart.yaml; do
  [ -f "$chart" ] || continue
  old_chart=$(yq '.version' "$chart")
  new_chart=$(python - <<EOF
from packaging.version import Version
v = Version("$old_chart")
print(f"{v.major}.{v.minor}.{v.micro+1}")
EOF
)
  yq -i \
    '.appVersion = str(env(VERSION)) | .version = str(env(new_chart))' \
    "$chart"
done
```

### B) PR check: chart changed ⇒ version bumped

`.github/workflows/chart-bump-check.yml`

```yaml
name: chart-bump-check
on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - 'charts/**'
permissions:
  contents: read
jobs:
  ensure-bumped:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Detect chart changes vs Chart.yaml bump
        run: |
          BASE_SHA="${{ github.event.pull_request.base.sha }}"
          HEAD_SHA="${{ github.event.pull_request.head.sha }}"
          CHANGED=$(git diff --name-only "$BASE_SHA" "$HEAD_SHA" -- charts/ | grep -v 'Chart.yaml' || true)
          if [ -n "$CHANGED" ]; then
            if git diff --name-only "$BASE_SHA" "$HEAD_SHA" -- charts/**/Chart.yaml | grep -q Chart.yaml; then
              echo "Chart.yaml changed — OK"
            else
              echo "::error::Chart files changed but Chart.yaml version not bumped"; exit 1
            fi
          else
            echo "No chart changes besides Chart.yaml"
          fi
```

### C) Capture image digests (build job)

```bash
VERSION=$(cat .version)
: > image-digests.json
for svc in api worker; do
  ref="ghcr.io/org/${svc}:${VERSION}"
  digest=$(docker buildx imagetools inspect "$ref" --format '{{json .Manifest.Digest}}' | jq -r .)
  tmp=$(mktemp)
  jq --arg s "$svc" --arg t "$VERSION" --arg d "$digest" \
     '.[$s] = {"tag": $t, "digest": $d}' \
     image-digests.json > "$tmp"
  mv "$tmp" image-digests.json
done
```

---

## Troubleshooting

* **Helm won’t let me push the same chart version** → bump `Chart.yaml: version` (must be unique).
* **Pods updated but wrong image pulled** → ensure prod sets **`image.digest`**; tags alone can drift.
* **PyPI 403** → verify package ownership, token scope, and `tool.poetry.name` matches PyPI name.
* **Semantic-release computed a different version after merge** → use a **release freeze** label, PR-only `chore/docs/build` changes, and workflow **concurrency**.

---

## FAQ

* **Can I use chart `version` inside `values.yaml`?** No. Helm doesn’t template values. Use `.Chart.AppVersion` **in templates** and default to it when `values.image.tag` is empty.
* **Can `chart.version` equal `appVersion`?** Possible, but impractical. You’ll block chart-only fixes. Prefer decoupled versions.
* **Still want `latest`?** Keep it only as a convenience tag. **Never** use it for prod deploys.
