# Challenge_1b/Dockerfile
FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the processing script
COPY process_documents.py .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set permissions
RUN chmod +x process_documents.py

# Run the processing script
CMD ["python", "process_documents.py"]