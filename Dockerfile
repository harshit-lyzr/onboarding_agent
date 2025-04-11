# Use a base Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Optional: Set timezone
ENV TZ=Asia/Kolkata
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -r appuser && \
    chown appuser:appuser /app

# Install dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables (these should be overridden in ECS task definition)
ENV MONGODB_URI=""
ENV SMTP_HOST=""
ENV SMTP_PORT=""
ENV SMTP_USERNAME=""
ENV SMTP_PASSWORD=""

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys, socket; \
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); \
        result = sock.connect_ex(('127.0.0.1', 80)); \
        sys.exit(result)"

# Set the default command to run the script
CMD ["python", "app.py"]
