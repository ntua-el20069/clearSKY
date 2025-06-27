# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.9
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONASYNCIODEBUG=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ENV STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false
ENV STREAMLIT_GLOBAL_METRICS=false

WORKDIR /app

# Create the non-privileged user first
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \  
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser && \
    mkdir -p /home/appuser/.streamlit && \
    chown -R appuser:appuser /home/appuser

# Set HOME environment variable
ENV HOME=/home/appuser

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=frontend/requirements.txt,target=frontend/requirements.txt \
    python -m pip install -r frontend/requirements.txt

# Copy application files
COPY --chown=appuser:appuser . .

# Copy Streamlit config
COPY --chown=appuser:appuser frontend/config.toml /home/appuser/.streamlit/config.toml

# Switch to the non-privileged user
USER appuser

EXPOSE 8501

CMD streamlit run frontend/home.py