FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential cmake git libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app \
    && adduser --system --ingroup app --home /app app

COPY requirements.txt requirements.txt
COPY requirements-local-llm.txt requirements-local-llm.txt
COPY requirements-dev.txt requirements-dev.txt
RUN pip install --no-cache-dir -r requirements.txt -r requirements-local-llm.txt

COPY app app
COPY migrations migrations
COPY alembic.ini alembic.ini
COPY seed.py seed.py
COPY download_local_model.py download_local_model.py
COPY start.sh start.sh

RUN mkdir -p /models /tmp/app \
    && chmod +x /app/start.sh \
    && chown -R app:app /app /models /tmp/app

USER app

EXPOSE 8000

CMD ["/app/start.sh"]
