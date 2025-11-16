FROM python:3.11-alpine3.20 AS builder

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt --prefix=/install

COPY src ./src

FROM python:3.11-alpine3.20

RUN addgroup -S app && adduser -S app -G app

WORKDIR /app

RUN apk add --no-cache libpq wget sqlite

RUN mkdir -p /app/uploads /app/db \
    && chown -R app:app /app/uploads /app/db

COPY --from=builder /install /usr/local

COPY src ./src

RUN chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
