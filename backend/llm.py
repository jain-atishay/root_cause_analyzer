"""LLM summarization for root cause analysis."""
import os
from openai import OpenAI

def summarize_root_causes(query: str, similar_logs: list) -> str:
    """Use LLM to summarize probable root causes from similar logs."""
    api_key = os.getenv("TRITON_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = (os.getenv("OPENAI_API_BASE") or "").rstrip("/")
    if base_url and not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    model = os.getenv("OPENAI_MODEL", "gpt-4")

    if not api_key or not base_url:
        return _fallback_summary(query, similar_logs)

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        logs_text = "\n".join(
            f"- [{r.get('level', '')}] {r.get('service', '')}: {r.get('message', '')}"
            for r in similar_logs[:5]
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a DevOps engineer analyzing log errors. Provide a concise root cause summary in 2-3 sentences."},
                {"role": "user", "content": f"Query log: {query}\n\nSimilar past logs:\n{logs_text}\n\nSummarize the probable root cause and recommended actions:"}
            ],
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return _fallback_summary(query, similar_logs)

def _fallback_summary(query: str, similar_logs: list) -> str:
    """Template-based summary when LLM is unavailable."""
    if not similar_logs:
        return "No similar past logs found. Consider expanding the search or ingesting more log data."
    services = {r.get("service") for r in similar_logs if r.get("service")}
    levels = {r.get("level") for r in similar_logs if r.get("level")}
    summary = f"Found {len(similar_logs)} similar past incidents. "
    if services:
        summary += f"Affected services: {', '.join(services)}. "
    if levels:
        summary += f"Log levels: {', '.join(levels)}. "
    summary += "Review the matches below for patterns. Common causes: connection timeouts, resource exhaustion, or deployment-related issues."
    return summary
