from sqlalchemy import text
from pgvector import Vector
from db import get_db
from embeddings import embed
from datetime import datetime
from typing import Optional


def find_similar_logs(
    query: str,
    top_k: int = 5,
    level: Optional[str] = None,
    service: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    """Find similar logs with optional structured filters."""
    db = get_db()
    embedding = embed(query)

    where_clauses = []
    params = {"embedding": Vector(embedding), "limit": top_k}

    if level:
        where_clauses.append("level = :level")
        params["level"] = level
    if service:
        where_clauses.append("service = :service")
        params["service"] = service
    if start_time:
        where_clauses.append("timestamp >= :start_time")
        params["start_time"] = start_time
    if end_time:
        where_clauses.append("timestamp <= :end_time")
        params["end_time"] = end_time

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    results = db.execute(
        text(f"""
        SELECT id, message, level, service, timestamp,
               embedding <=> :embedding AS distance
        FROM logs
        WHERE {where_sql}
        ORDER BY embedding <=> :embedding
        LIMIT :limit
        """),
        params,
    )

    rows = [dict(r._mapping) for r in results]
    db.close()
    return rows


def cluster_failure_patterns(n_clusters: int = 5, level: Optional[str] = None):
    """Cluster logs into failure patterns using embedding similarity."""
    import numpy as np
    from sklearn.cluster import KMeans

    db = get_db()
    where = "WHERE level = :level" if level else ""
    params = {"level": level} if level else {}

    rows = db.execute(
        text(f"""
        SELECT id, message, level, service, timestamp,
               embedding::text AS embedding_str
        FROM logs {where}
        """),
        params,
    ).fetchall()

    db.close()

    if len(rows) < n_clusters:
        n_clusters = max(1, len(rows))

    if not rows:
        return []

    embeddings = []
    for r in rows:
        vec_str = r.embedding_str.strip("[]")
        embeddings.append([float(x) for x in vec_str.split(",")])
    X = np.array(embeddings)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    clusters = []
    for i in range(n_clusters):
        indices = [j for j, l in enumerate(labels) if l == i]
        if not indices:
            continue
        cluster_logs = []
        for j in indices:
            d = dict(rows[j]._mapping)
            d.pop("embedding_str", None)
            cluster_logs.append(d)
        centroid = kmeans.cluster_centers_[i]
        clusters.append({
            "cluster_id": i,
            "size": len(indices),
            "logs": cluster_logs[:5],
        })

    return clusters


def correlate_with_deployments(service: str):
    db = get_db()

    results = db.execute(
        text("""
        SELECT d.service, d.version, d.deployed_at,
               l.message, l.timestamp, l.level
        FROM deployments d
        JOIN logs l ON l.service = d.service
        WHERE d.service = :service AND l.timestamp >= d.deployed_at
        ORDER BY l.timestamp DESC
        LIMIT 20
        """),
        {"service": service},
    )

    rows = [dict(r._mapping) for r in results]
    db.close()
    return rows