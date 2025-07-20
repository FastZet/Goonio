# Use a modern, fast, and lightweight Python base image from Astral (the makers of uv and ruff)
FROM ghcr.io/astral-sh/uv:python3.11-alpine

# Set metadata labels for the image
LABEL name="Goonio" \
      description="Stremio's finest adult catalog and stream provider."

# Set the working directory inside the container
WORKDIR /app

# Copy only the dependency file first to leverage Docker's build cache.
# This layer will only be rebuilt if the dependencies change.
COPY pyproject.toml .

# Install the Python dependencies using the fast `uv` installer
RUN uv sync

# Copy the rest of the application source code into the container
COPY . .

# Define the command that will run when the container starts.
# This command runs the `main.py` file located inside the `goonio` directory.
ENTRYPOINT ["uv", "run", "python", "-m", "goonio.main"]
