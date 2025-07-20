# Use a modern, fast, and lightweight Python base image from Astral
FROM ghcr.io/astral-sh/uv:python3.11-alpine

# Set metadata labels for the image
LABEL name="Goonio" \
      description="Stremio's finest adult catalog and stream provider."

# Set the working directory inside the container
WORKDIR /app

COPY pyproject.toml .
RUN uv sync
COPY . .

# HEALTHCHECK remains the same
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8000/health || exit 1

# --- UPDATED COMMAND ---
# This command starts the Gunicorn server, telling it to use our silent config file.
CMD ["gunicorn", "-c", "gunicorn_config.py", "goonio.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
