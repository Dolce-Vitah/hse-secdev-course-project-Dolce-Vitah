FROM python:3.11-alpine3.20 AS builder

RUN apk add --no-cache \
    gcc=13.2.1_git20240309-r1 \
    musl-dev=1.2.5-r1 \
    libffi-dev=3.4.6-r0 \
    openssl-dev=3.3.5-r0

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip==23.3.1 \
    && pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt --prefix=/install

COPY src ./src

FROM python:3.11-alpine3.20

RUN addgroup -S app && adduser -S app -G app

WORKDIR /app

RUN apk add --no-cache \
    libpq=16.4-r0 \
    wget=1.24.5-r0 \
    sqlite=3.46.1-r2

RUN mkdir -p /app/uploads /app/db \
    && chown -R app:app /app/uploads /app/db

COPY --from=builder /install /usr/local

COPY src ./src

ENV PYTHONPATH="/app/src"

RUN chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8000/health || exit 1

CMD ["uvicorn", "wishlist_api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
