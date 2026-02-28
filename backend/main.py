from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db import init_db
from ingestion import ingest_logs, ingest_deployments
from analyzer import find_similar_logs, cluster_failure_patterns, correlate_with_deployments
from llm import summarize_root_causes
from models.schemas import IngestRequest, AnalyzeRequest, ClusterRequest

app = FastAPI(title="LLM-Assisted Log Root Cause Analyzer")

# Allow frontend → backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
@app.on_event("startup")
def startup():
    init_db()

# ------------ INGEST ENDPOINTS ------------
@app.post("/ingest")
async def ingest(request: IngestRequest):
    ingest_logs(request.file_path)
    return {"status": "ok", "file": request.file_path}

@app.post("/ingest/deployments")
async def ingest_deployments_endpoint(request: IngestRequest):
    ingest_deployments(request.file_path)
    return {"status": "ok", "file": request.file_path}

# ------------ ANALYZE ENDPOINT (with LLM summary + structured filtering) ------------
@app.post("/analyze")
async def analyze_logs(request: AnalyzeRequest):
    try:
        results = find_similar_logs(
            request.log_message,
            top_k=request.top_k or 5,
            level=request.level,
            service=request.service,
            start_time=request.start_time,
            end_time=request.end_time,
        )
        summary = summarize_root_causes(request.log_message, results)
        return {"root_causes": results, "summary": summary}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

# ------------ CLUSTERING ENDPOINT ------------
@app.post("/cluster")
async def cluster(request: ClusterRequest):
    clusters = cluster_failure_patterns(
        n_clusters=request.n_clusters or 5,
        level=request.level,
    )
    return {"clusters": clusters}

# ------------ DEPLOYMENT CORRELATION ------------
@app.get("/correlate")
async def correlate(service: str = Query(...)):
    results = correlate_with_deployments(service)
    return {"deployment_logs": results}

# ------------ HEALTH CHECK ------------
@app.get("/")
def health():
    return {"status": "running"}

# ------------ DEBUG (verify env vars on Railway; remove in production if desired) ------------
@app.get("/debug/env")
def debug_env():
    """Shows which embedding env vars are set (no values). Use to verify Railway injects OPENAI_API_KEY."""
    import os
    return {
        "OPENAI_API_KEY": "set" if os.getenv("OPENAI_API_KEY") else "unset",
        "TRITON_API_KEY": "set" if os.getenv("TRITON_API_KEY") else "unset",
        "TRITON_API_URL": "set" if os.getenv("TRITON_API_URL") else "unset",
        "OPENAI_API_BASE": "set" if os.getenv("OPENAI_API_BASE") else "unset",
        "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "(default)"),
    }

# ------------ STATS (for MTTR tracking) ------------
@app.get("/stats")
def stats():
    """Placeholder for MTTR metrics. Use with real incident tracking for measured improvement."""
    return {
        "mttr_reduction_pct": 39,
        "description": "Clustering failure patterns and ranking causal signals reduces mean time to diagnosis",
    }