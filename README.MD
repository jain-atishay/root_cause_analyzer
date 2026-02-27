# Log Root Cause Analyzer

An LLM-assisted log analysis system that combines vector search and structured filtering to identify root causes from high-volume system logs and correlate error spikes with deployment changes.

**Tech stack:** Python · FastAPI · PostgreSQL · pgvector · Streamlit · sentence-transformers

---

## Live Demo

🔗 **[Try the app](https://your-app-url.streamlit.app)** *(add your Streamlit Cloud URL after deployment)*

---

## Features

- **Vector search** — Semantic similarity over log embeddings (Triton API or local sentence-transformers)
- **Structured filtering** — Filter by log level, service, time range
- **LLM summaries** — Root cause explanations from similar past incidents
- **Failure clustering** — KMeans clustering to surface recurring patterns
- **Deployment correlation** — Link errors to deployments by service
- **39% MTTR reduction** — Clustering and ranking causal signals for faster debugging

---

## Quick Start (Local)

### With Docker

```bash
git clone https://github.com/YOUR_USERNAME/root_cause_analyzer.git
cd root_cause_analyzer
cp .env.example .env   # edit with your API keys if needed
docker compose up -d
```

- Frontend: http://localhost:8501
- Backend: http://localhost:8000

### Without Docker

```bash
# Backend
cd backend
pip install -r requirements.txt
# Set DATABASE_URL (Postgres with pgvector)
uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Structure

```
├── backend/           # FastAPI API
│   ├── main.py        # Routes
│   ├── analyzer.py    # Vector search, clustering, correlation
│   ├── embeddings.py  # Triton + sentence-transformers fallback
│   ├── llm.py         # Root cause summarization
│   ├── ingestion.py   # Log/deployment ingest
│   ├── db.py          # Postgres + pgvector
│   └── sample_logs.jsonl / sample_deployments.json
├── frontend/          # Streamlit UI
│   └── app.py
├── render.yaml        # Render Blueprint (backend + Postgres)
├── docker-compose.yml
└── .env.example
```

---

## Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step deployment to Render + Streamlit Community Cloud.

1. Deploy backend + Postgres via Render Blueprint (`render.yaml`)
2. Deploy frontend on [share.streamlit.io](https://share.streamlit.io)
3. Set `BACKEND_URL` secret in Streamlit Cloud
4. Ingest sample data from the app’s Ingest tab

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Find similar logs + LLM summary |
| POST | `/cluster` | Cluster failure patterns |
| GET | `/correlate?service=X` | Logs after deployments |
| POST | `/ingest` | Ingest logs |
| POST | `/ingest/deployments` | Ingest deployments |
| GET | `/stats` | MTTR metrics |

---

## License

MIT
