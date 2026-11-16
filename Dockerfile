FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY scripts ./scripts
COPY static ./static

ENV FINN_DATA_DIR=/app/data
EXPOSE 8000

CMD ["sh", "-c", "if [ \"${FINN_SEED_DEMO_SOURCES:-false}\" = \"true\" ]; then python -m scripts.ingest_demo_sources || exit $?; fi; exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
