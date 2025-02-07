FROM python:3.9

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Expose the port (critical for Render to detect)
EXPOSE 8000

# Use shell form to pick up Render’s $PORT
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
