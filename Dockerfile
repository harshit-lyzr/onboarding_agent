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

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py database.py lyzr_agent.py send_email.py ./

# Set the default command to run the script
CMD ["python", "app.py"]
