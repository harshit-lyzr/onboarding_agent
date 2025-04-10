# Use a base Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install necessary system packages: cron and tzdata for timezone handling
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set the timezone to Asia/Kolkata (IST)
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

# Copy requirements file first for better caching
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py database.py lyzr_agent.py send_email.py ./

# Create the cron job definition inside the container
# The cron job runs the Python script daily at 18:00 (6 PM) IST
# Output and errors are redirected to /var/log/cron.log
RUN echo "0 18 * * * root python /app/app.py >> /var/log/cron.log 2>&1" > /etc/cron.d/my-app-cronjob && \
    chmod 0644 /etc/cron.d/my-app-cronjob && \
    crontab /etc/cron.d/my-app-cronjob # Load the cron job

# Expose any necessary ports if your app was a server (not needed here)
# EXPOSE 80

# Start the cron daemon in the foreground
# This keeps the container running and allows cron to execute jobs
CMD ["cron", "-f"]