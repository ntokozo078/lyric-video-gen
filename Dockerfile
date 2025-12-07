# 1. Use an official Python runtime
FROM python:3.9-slim

# 2. Install System Dependencies (FFmpeg, ImageMagick, Redis)
# We also install 'findutils' to help locate the policy file dynamically
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# 3. Fix ImageMagick Policy (CRITICAL FIX)
# This command looks for ANY ImageMagick policy file (version 6 or 7) and unlocks it.
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-*/policy.xml

# 4. Set working directory
WORKDIR /app

# 5. Copy project files
COPY . /app

# 6. Install Python Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7. Expose Port
EXPOSE 5000

# 8. Start the App
# CHANGE: We use $PORT instead of hardcoding 5000
CMD redis-server --daemonize yes && \
    celery -A app.tasks.celery worker --loglevel=info --pool=gevent --concurrency=4 & \
    gunicorn --bind 0.0.0.0:$PORT run:app