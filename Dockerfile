# Use a modern, fast, and lightweight Python base image from Astral
FROM ghcr.io/astral-sh/uv:python3.11-alpine

# Set metadata labels for the image
LABEL name="Goonio" \
      description="Stremio's finest adult catalog and stream provider."

# Set the working directory inside the container
WORKDIR /app

# Copy only the dependency file first to leverage Docker's build cache
COPY pyproject.toml .

# Install the Python dependencies using the fast `uv` installer
RUN uv sync

# Copy the rest of the application source code into the container
COPY . .

# --- NEW HEALTHCHECK INSTRUCTION ---
# This tells Docker (and Render) how to check if our application is healthy.
# It will run 'wget' against our /health endpoint every 30 seconds.
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8000/health || exit 1

# Define the command that will run when the container starts
ENTRYPOINT ["uv", "run", "python", "-m", "goonio.main"]
