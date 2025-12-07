FROM python:3.9-slim

# Install system dependencies (FFmpeg + ImageMagick)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-*/policy.xml

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Start just the web server (with high timeout so it doesn't kill the render)
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 120 run:app