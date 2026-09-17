FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gettext \
        libjpeg62-turbo \
        libpng16-16 \
        libpq5 \
        libwebp7 \
        zlib1g && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY . .
RUN mkdir -p /app/staticfiles /app/media /app/locale

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
# 1 GB Droplet: один worker + threads (700c). На 2 GB можна підняти --workers 2.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
