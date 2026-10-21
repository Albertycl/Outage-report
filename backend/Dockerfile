# Backend: Flask under gunicorn. python 3.8 because jkb_status.py uses
# backports.zoneinfo, which only exists for Python < 3.9.
FROM python:3.8-slim

# tzdata: slim images ship without a tz database and ZoneInfo needs one.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Asia/Taipei \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 5410
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('127.0.0.1',5410),3).close()" || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
