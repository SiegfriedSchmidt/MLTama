FROM node:lts-slim AS nodejs-builder

WORKDIR /app
COPY ./frontend /app
RUN npm ci && \
    npm run build
	
FROM python:3.13.2-slim AS python-builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY ./backend/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.13.2-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=python-builder /app/wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

USER app
STOPSIGNAL SIGINT

COPY ./backend /app
COPY --from=nodejs-builder /app/dist /app/dist

ENTRYPOINT ["python3", "main.py"] 