# 1. Use Python
FROM python:3.9-slim

# 2. Install FFmpeg and ImageMagick ONLY (No Redis)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# 3. Fix ImageMagick Policy
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-*/policy.xml

# 4. Setup App
WORKDIR /app
COPY . /app

# 5. Install Python Libs
RUN pip install --no-cache-dir -r requirements.txt

# 6. Expose Port
EXPOSE 5000

# 7. Start Web Server
# We restrict Gunicorn to 1 worker to ensure we don't accidentally double memory usage
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 300 run:app