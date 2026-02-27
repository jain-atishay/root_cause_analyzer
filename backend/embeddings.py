import os
import requests

# Schema expects 1536-dim vectors; local model produces 384, so we pad
EMBEDDING_DIM = 1536
LOCAL_EMBEDDING_DIM = 384

_local_model = None

def _get_local_model():
    """Lazy-load sentence-transformers model for fallback embeddings."""
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _local_model

def _pad_to_dim(vec: list, target_dim: int) -> list:
    """Pad vector with zeros to match target dimension (for DB schema compatibility)."""
    if len(vec) >= target_dim:
        return vec[:target_dim]
    return vec + [0.0] * (target_dim - len(vec))

def embed(text: str):
    api_url = os.getenv("TRITON_API_URL")
    api_key = os.getenv("TRITON_API_KEY")

    # Try Triton API when configured
    if api_key and api_key.startswith("sk-") and api_url:
        payload = {
            "model": "text-embedding-3-large",
            "input": text
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            res = requests.post(api_url, json=payload, headers=headers, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["data"][0]["embedding"]
            # On auth or server error, fall through to local fallback
        except (requests.RequestException, KeyError):
            pass

    # Fallback to local sentence-transformers (works without API key)
    model = _get_local_model()
    vec = model.encode(text, convert_to_numpy=True).tolist()
    return _pad_to_dim(vec, EMBEDDING_DIM)