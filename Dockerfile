# Stage 1: build python env
FROM python:3.12-slim AS builder
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: runtime
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY --from=builder /install /usr/local
COPY backend/ ./backend/
COPY templates/ ./templates/
COPY static/ ./static/
COPY backend/app.py ./
EXPOSE 80
CMD ["python", "backend/app.py"]