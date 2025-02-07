FROM python:3.9

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Use Render’s $PORT (default: 10000)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
