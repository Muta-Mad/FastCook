FROM python:3.12.3-slim AS deps

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12.3-slim

RUN useradd -m -u 1000 -s /sbin/nologin appuser

WORKDIR /app

COPY --from=deps /install /usr/local
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
