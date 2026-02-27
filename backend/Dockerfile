FROM python:3.10-slim

WORKDIR /app

COPY . /app/

# REQUIREMENTS_FILE: use requirements-railway.txt for Railway (4GB limit), requirements.txt for local
ARG REQUIREMENTS_FILE=requirements-railway.txt
RUN pip install --no-cache-dir -r ${REQUIREMENTS_FILE}

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]