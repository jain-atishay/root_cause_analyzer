import json
import os
from datetime import datetime
from sqlalchemy import text
from pgvector import Vector
from db import get_db
from embeddings import embed

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolve_path(path: str) -> str:
    """Resolve path relative to backend directory for cross-environment compatibility."""
    if os.path.isabs(path):
        return path
    return os.path.join(_BASE_DIR, path)


def ingest_deployments(file_path: str):
    db = get_db()
    path = _resolve_path(file_path)
    with open(path, "r") as f:
        deployments = json.load(f)
    for d in deployments:
        db.execute(
            text("""
            INSERT INTO deployments (service, version, deployed_at)
            VALUES (:service, :version, :deployed_at)
            """),
            {
                "service": d["service"],
                "version": d["version"],
                "deployed_at": datetime.fromisoformat(d["deployed_at"]),
            },
        )
    db.commit()
    db.close()


def ingest_logs(file_path: str):
    db = get_db()
    path = _resolve_path(file_path)
    with open(path, "r") as f:
        for line in f:
            log = json.loads(line)

            embedding = embed(log["message"])

            db.execute(text("""
                INSERT INTO logs (timestamp, level, service, message, embedding)
                VALUES (:timestamp, :level, :service, :message, :embedding)
            """), {
                "timestamp": datetime.fromisoformat(log["timestamp"]),
                "level": log["level"],
                "service": log["service"],
                "message": log["message"],
                "embedding": Vector(embedding)
            })

    db.commit()
    db.close()