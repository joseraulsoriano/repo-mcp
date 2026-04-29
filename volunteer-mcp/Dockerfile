# Volunteer MCP - API FastAPI (voluntariados, empleos, educación MX)
FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema (lxml/bs4)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY scripts/ ./scripts/

# Directorio para SQLite y JSON educativos (persistir con volume)
RUN mkdir -p data

ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/app/data

EXPOSE 8011

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8011"]
