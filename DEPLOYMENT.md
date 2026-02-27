# Deploying the Log Root Cause Analyzer

To share a live link (e.g., for recruiters), you need to deploy both the **backend** (API + Postgres) and the **frontend** (Streamlit). Streamlit Community Cloud hosts only the frontend, so the backend must be hosted elsewhere.

---

## Railway quick start

1. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub** → select `root_cause_analyzer`
2. **Add Postgres with pgvector**: + New → Database → choose **Postgres with pgVector** (or the pgvector template)
3. **Add backend**: + New → GitHub Repo → select same repo
   - Settings → **Root Directory**: `backend`
   - Variables → **Add variable** → Reference `DATABASE_URL` from Postgres service
   - Settings → Networking → **Generate Domain**
4. Copy the backend URL and use it in Streamlit Cloud (Step 2 below) as `BACKEND_URL`

---

## Architecture

```
[Streamlit Cloud]  ──BACKEND_URL──►  [Railway/Render: Backend + Postgres]
     Frontend                              API + Database
```

---

## Step 1: Deploy backend + Postgres

### Option A: Render with Blueprint (recommended, one-click)

The repo includes `render.yaml` so you can deploy backend + Postgres in one step:

1. Push your repo to GitHub.
2. Go to [render.com](https://render.com) → sign in with GitHub.
3. **Dashboard → New → Blueprint**
4. Connect your `root_cause_analyzer` repo.
5. Render will create:
   - `root-cause-backend` (Python web service)
   - `root-cause-db` (PostgreSQL with pgvector support)
6. Click **Apply** and wait for the deploy.
7. Copy your backend URL (e.g. `https://root-cause-backend-xxx.onrender.com`).

Render uses the [deploy docs](https://render.com/docs/deploys) flow: build → start. Build command: `pip install -r requirements.txt`, start: `uvicorn main:app --host 0.0.0.0 --port $PORT`.

### Option B: Render (manual)

1. Go to [render.com](https://render.com) and sign up with GitHub.
2. **Create a PostgreSQL database**: Dashboard → New → PostgreSQL, name `root-cause-db`. Copy the **Internal Database URL**.
3. **Create a Web Service**: New → Web Service → connect your repo.
   - Root directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Env: `DATABASE_URL` = (Internal Database URL from step 2)
4. Deploy and copy the backend URL.

### Option C: Railway (no credit card for free tier)

**Important:** Use the **pgvector** Postgres template—standard Postgres doesn’t include the vector extension.

1. Go to [railway.app](https://railway.app) → sign in with GitHub.
2. **New Project** → **Deploy from GitHub repo** (select `root_cause_analyzer`).
3. Add **PostgreSQL with pgvector**:
   - Click **+ New** → **Database**
   - Choose **Postgres** → pick **“Postgres with pgVector”** (or `pgvector/pgvector:pg16` image) if offered
   - Or use [railway.com/deploy/postgres-with-pgvector-engine](https://railway.com/deploy/postgres-with-pgvector-engine)
4. Add the **backend** service:
   - **+ New** → **GitHub Repo** → select `root_cause_analyzer`
   - Open the new service → **Settings** → set **Root Directory** to `backend`
   - **Variables** → **+ New Variable** → Reference: `DATABASE_URL` from the Postgres service
   - Under **Settings** → **Networking** → **Generate Domain** (to get a public URL)
5. Deploy. The backend uses `Procfile` or `railway.json` in `backend/` for the start command.
6. Copy the backend URL (e.g. `https://root-cause-analyzer-production-xxxx.up.railway.app`).

**Railway build note:** The project uses `requirements-railway.txt` (slim, no sentence-transformers) to stay under the 4 GB image limit. Add **TRITON_API_KEY** + **TRITON_API_URL** or **OPENAI_API_KEY** as env vars for embeddings.

---

## Step 2: Deploy frontend on Streamlit Community Cloud

1. Push your repo to GitHub (make sure `.env` is in `.gitignore` and not committed).
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Sign in with GitHub.
4. Click **New app**.
5. **Repository**: select your `root_cause_analyzer` repo.
6. **Branch**: `main` (or your default).
7. **Main file path**: `frontend/app.py`
8. **Advanced settings** → Secrets → Add secret:
   ```
   BACKEND_URL = "https://your-backend-url.onrender.com"
   ```
   (Use your backend URL from Step 1; no trailing slash.)
9. Click **Deploy**.

---

## Step 3: Add sample data

After both are deployed:

1. Open your Streamlit app URL (e.g. `https://yourapp.streamlit.app`).
2. Go to the **Ingest** tab.
3. Click **Ingest logs**, then **Ingest deployments**.

The sample files are in the backend repo and are loaded automatically.

---

## Step 4: Add link to README

Add this to your README:

```markdown
## Live demo

🔗 **[Try the app](https://your-username-root-cause-analyzer-frontend-xxx.streamlit.app)**
```

Replace with your actual Streamlit Cloud URL (shown after deployment).

---

## Important notes

- **Secrets**: Never commit API keys. Use environment variables in Render/Railway and Streamlit Cloud Secrets.
- **Free tier limits**: Render free services sleep after ~15 min of inactivity; the first request may take 30–60 seconds. Railway’s free tier has usage limits.
- **Postgres + pgvector**: Your database must support the pgvector extension (Render, Neon, Railway do).
