FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime AS base


ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HF_HOME=/app/cache/huggingface

WORKDIR /app

FROM base AS development
COPY . .

RUN pip install  --no-cache-dir ".[dev]"
CMD ["pytest"]

FROM base AS production
COPY . .
RUN pip install --no-cache-dir .
CMD ["python", "-m", "tessax"]