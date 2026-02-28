import os
import requests

# Schema expects 1536-dim vectors; local model produces 384, so we pad
EMBEDDING_DIM = 1536

_local_model = None

def _get_local_model():
    """Lazy-load sentence-transformers (optional, not in Railway slim build)."""
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

def _embed_openai(text: str) -> tuple[list | None, str | None]:
    """Use OpenAI-compatible API for embeddings (OpenAI, Triton, etc.). Returns (embedding, error_msg)."""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("TRITON_API_KEY")
    base_url = (os.getenv("OPENAI_API_BASE") or os.getenv("TRITON_API_URL") or "https://api.openai.com/v1").rstrip("/")
    if base_url.endswith("/embeddings"):
        base_url = base_url[: -len("/embeddings")]
    if not api_key:
        return None, None
    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        r = client.embeddings.create(model=model, input=text)
        return r.data[0].embedding, None
    except Exception as e:
        return None, str(e)

def embed(text: str):
    api_url = os.getenv("TRITON_API_URL")
    api_key = os.getenv("TRITON_API_KEY")
    last_error: str | None = None

    # 1. Try Triton API when configured (no sk- requirement; Triton keys may vary)
    if api_key and api_url:
        payload = {"model": "text-embedding-3-large", "input": text}
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        try:
            res = requests.post(api_url, json=payload, headers=headers, timeout=30)
            if res.status_code == 200:
                return res.json()["data"][0]["embedding"]
            last_error = f"Triton API returned {res.status_code}: {res.text[:200]}"
        except (requests.RequestException, KeyError) as e:
            last_error = str(e)

    # 2. Try OpenAI-compatible client (works with Triton base URL)
    vec, err = _embed_openai(text)
    if vec is not None:
        return vec
    if err:
        last_error = err

    # 3. Fallback to sentence-transformers (only if installed; not in Railway slim build)
    try:
        model = _get_local_model()
        vec = model.encode(text, convert_to_numpy=True).tolist()
        return _pad_to_dim(vec, EMBEDDING_DIM)
    except ImportError:
        cfg = (
            f"TRITON_API_KEY={'set' if os.getenv('TRITON_API_KEY') else 'unset'}, "
            f"TRITON_API_URL={'set' if os.getenv('TRITON_API_URL') else 'unset'}, "
            f"OPENAI_API_KEY={'set' if os.getenv('OPENAI_API_KEY') else 'unset'}"
        )
        msg = (
            "No embedding provider available. Set TRITON_API_KEY+TRITON_API_URL, "
            "or OPENAI_API_KEY, or install sentence-transformers for local fallback."
        )
        if last_error:
            msg += f" Last API error: {last_error}. "
        msg += f" Env check: {cfg}."
        raise RuntimeError(msg)