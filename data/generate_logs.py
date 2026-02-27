import json
import random
from datetime import datetime, timedelta

services = ["auth", "billing", "search", "analytics", "gateway"]
errors = [
    "database timeout while verifying session",
    "cannot reach postgres instance",
    "upstream service returned 502",
    "cache miss caused elevated latency",
    "null pointer in user handler",
    "model inference took too long",
    "queue backlog growing beyond threshold",
    "deployment version mismatch detected"
]

info_logs = [
    "request completed successfully",
    "heartbeat OK",
    "cache warmed",
    "connected to upstream pool",
    "background job finished"
]

def generate_logs(n=5000, path="sample_logs.jsonl"):
    now = datetime.utcnow()
    with open(path, "w") as f:
        for _ in range(n):
            ts = now - timedelta(seconds=random.randint(0, 200000))
            service = random.choice(services)
            level = random.choice(["INFO", "INFO", "INFO", "ERROR"])  # 25% errors

            msg = random.choice(errors if level == "ERROR" else info_logs)

            f.write(json.dumps({
                "timestamp": ts.isoformat(),
                "level": level,
                "service": service,
                "message": msg
            }) + "\n")

if __name__ == "__main__":
    generate_logs()
    print("Generated sample_logs.jsonl")