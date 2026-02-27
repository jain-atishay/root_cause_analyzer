#!/bin/bash
# Root Cause Analyzer - Test Script
# Run from project root with: ./test_analyzer.sh

set -e
BACKEND="http://localhost:8000"

echo "=== 1. Health check ==="
curl -s "$BACKEND/" | jq .

echo ""
echo "=== 2. Ingest sample logs ==="
curl -s -X POST "$BACKEND/ingest" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/app/sample_logs.jsonl"}' | jq .

echo ""
echo "=== 3. Ingest sample deployments ==="
curl -s -X POST "$BACKEND/ingest/deployments" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/app/sample_deployments.json"}' | jq .

echo ""
echo "=== 4. Analyze - database connection timeout (with LLM summary) ==="
curl -s -X POST "$BACKEND/analyze" \
  -H "Content-Type: application/json" \
  -d '{"log_message": "database connection timed out", "top_k": 5}' | jq .

echo ""
echo "=== 5. Analyze with filter - ERROR level only ==="
curl -s -X POST "$BACKEND/analyze" \
  -H "Content-Type: application/json" \
  -d '{"log_message": "connection timeout", "level": "ERROR"}' | jq .

echo ""
echo "=== 6. Cluster failure patterns ==="
curl -s -X POST "$BACKEND/cluster" \
  -H "Content-Type: application/json" \
  -d '{"n_clusters": 4, "level": "ERROR"}' | jq .

echo ""
echo "=== 7. Correlate with deployments - api-gateway ==="
curl -s "$BACKEND/correlate?service=api-gateway" | jq .

echo ""
echo "=== 8. Stats (MTTR) ==="
curl -s "$BACKEND/stats" | jq .
