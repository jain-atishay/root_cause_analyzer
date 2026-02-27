FROM python:3.10-slim

WORKDIR /app

COPY . /app/

# REQUIREMENTS_FILE: use requirements-railway.txt for Railway (4GB limit), requirements.txt for local
ARG REQUIREMENTS_FILE=requirements-railway.txt
RUN pip install --no-cache-dir -r ${REQUIREMENTS_FILE}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]