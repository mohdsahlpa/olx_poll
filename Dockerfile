# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=. \
    PORT=7860

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY README.md ./

# Install dependencies globally (in the container)
RUN uv pip install --system .

# Create an empty database file and set permissions
RUN touch olx_bot.db && chmod 666 olx_bot.db

# Expose the port Hugging Face expects
EXPOSE 7860

# Start the application
# Binding to 0.0.0.0 is critical for HF proxy access
CMD ["python", "src/main.py"]
