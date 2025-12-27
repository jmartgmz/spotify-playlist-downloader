# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories for volumes
RUN mkdir -p /app/downloaded_songs /app/playlist_songs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port for dashboard
EXPOSE 5000

# Default command runs the interactive launcher
CMD ["python", "launcher.py"]
