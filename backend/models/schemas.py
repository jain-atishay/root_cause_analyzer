from pydantic import BaseModel
from typing import List, Any, Optional
from datetime import datetime


class IngestRequest(BaseModel):
    file_path: str


class AnalyzeRequest(BaseModel):
    log_message: str
    top_k: Optional[int] = 5
    level: Optional[str] = None
    service: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ClusterRequest(BaseModel):
    n_clusters: Optional[int] = 5
    level: Optional[str] = None


class CorrelateQuery(BaseModel):
    service: str