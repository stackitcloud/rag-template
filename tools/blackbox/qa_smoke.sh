#!/usr/bin/env bash
set -euo pipefail

# Minimal black-box smoke harness.
# Required env:
#   QA_BASE_URL           - base URL of the QA deployment (e.g. https://qa.example.com)
# Optional env:
#   QA_DOC_UPLOAD_URL     - full URL to upload documents (multipart/form-data)
#   QA_DOC_PATHS          - whitespace-separated local file paths to upload (if empty, upload is skipped)
#   QA_CHAT_URL           - full URL to ask a question (expects JSON POST)
#   QA_QUESTION           - question to ask (default: "What is 2+2?")
#   QA_EXPECTED_ANSWER    - substring expected in the chat response (if set, assert)
#   QA_ADMIN_TOKEN        - bearer token added to requests (optional)

if [ -z "${QA_BASE_URL:-}" ]; then
  echo "QA_BASE_URL must be set for black-box smoke tests." >&2
  exit 1
fi

AUTH_HEADER=()
if [ -n "${QA_ADMIN_TOKEN:-}" ]; then
  AUTH_HEADER=(-H "Authorization: Bearer ${QA_ADMIN_TOKEN}")
fi

# Optional document upload
if [ -n "${QA_DOC_UPLOAD_URL:-}" ] && [ -n "${QA_DOC_PATHS:-}" ]; then
  echo "Uploading documents to ${QA_DOC_UPLOAD_URL}"
  for doc in ${QA_DOC_PATHS}; do
    if [ ! -f "$doc" ]; then
      echo "Document not found: $doc" >&2
      exit 1
    fi
    curl -fsS "${AUTH_HEADER[@]}" \
      -F "file=@${doc}" \
      "$QA_DOC_UPLOAD_URL" >/dev/null
    echo "Uploaded $doc"
  done
else
  echo "Skipping document upload (QA_DOC_UPLOAD_URL or QA_DOC_PATHS not set)"
fi

# Optional question/answer check
if [ -n "${QA_CHAT_URL:-}" ]; then
  QUESTION="${QA_QUESTION:-What is 2+2?}"
  echo "Asking question against ${QA_CHAT_URL}"
  RESPONSE=$(curl -fsS "${AUTH_HEADER[@]}" \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"${QUESTION}\"}" \
    "$QA_CHAT_URL")
  echo "Response: $RESPONSE"
  if [ -n "${QA_EXPECTED_ANSWER:-}" ]; then
    echo "$RESPONSE" | grep -qi --fixed-strings "${QA_EXPECTED_ANSWER}" || {
      echo "Expected answer fragment not found: ${QA_EXPECTED_ANSWER}" >&2
      exit 1
    }
  fi
else
  echo "Skipping Q&A check (QA_CHAT_URL not set)"
fi

echo "Black-box smoke tests completed."
