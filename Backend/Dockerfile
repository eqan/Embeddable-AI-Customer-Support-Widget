FROM python:3.12-slim-bullseye

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv venv .venv && \
    uv sync --frozen --no-cache

# Set the working directory to where the app module is located
WORKDIR /app/app

EXPOSE 8000

# Run the application
CMD ["../.venv/bin/python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]