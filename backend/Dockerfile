FROM python:3.11-slim

# Install system dependencies
COPY packages.txt .
RUN apt-get update && \
    apt-get install -y $(grep -v '^#' packages.txt | tr '\n' ' ') && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000

