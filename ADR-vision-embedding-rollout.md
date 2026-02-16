# ADR: Vision Embedding Rollout (Flag-Gated)

- Status: Accepted
- Date: 2026-02-16

## Context

STACKIT published a vision-capable embedder. We want to integrate image-native retrieval into the existing RAG pipeline without destabilizing production traffic.

The current platform already supports `IMAGE` as a content type, but image ingestion/retrieval behavior is not yet consistently routed through a dedicated vision lane end-to-end.

## Decision

Roll out vision support behind explicit feature flags that default to `false`:

- `VISION_IMAGE_LANE_ENABLED=false`
- `VISION_EMBEDDING_ENABLED=false`
- `VISION_IMAGE_RETRIEVER_ENABLED=false`

Flags are exposed via Helm values and config maps for backend, admin-backend, and extractor.

## Consequences

### Positive

- No behavior change on merge while flags stay off.
- Safe staged rollout with reversible steps.
- Easier incident response by disabling a specific lane.

### Negative

- Temporary configuration overhead while both legacy and vision paths exist.
- Additional test matrix during rollout.

## Rollout Notes

- Keep all three flags `false` until the final rollout PR is merged and staging is validated.
- Enable in sequence on staging:
  1. `VISION_IMAGE_LANE_ENABLED`
  2. `VISION_EMBEDDING_ENABLED`
  3. `VISION_IMAGE_RETRIEVER_ENABLED`
- Promote to production only after mixed-modality retrieval checks pass.

## Telemetry Baseline (No Behavior Change in This ADR)

Track these counters from the first behavior PR onward:

- `vision.image_documents_ingested_total`
- `vision.image_embeddings_written_total`
- `vision.image_retrieval_hits_total`
- `vision.image_retrieval_errors_total`

This ADR only defines the rollout contract; metric instrumentation is introduced in later PRs.
