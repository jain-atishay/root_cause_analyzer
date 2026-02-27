FROM python:3.10-slim

WORKDIR /app

COPY . /app/

# REQUIREMENTS_FILE: use requirements-railway.txt for Railway (4GB limit), requirements.txt for local
ARG REQUIREMENTS_FILE=requirements-railway.txt
RUN pip install --no-cache-dir -r ${REQUIREMENTS_FILE}

# Use shell so $PORT is expanded (Railway injects PORT; exec form would pass literal $PORT)
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]