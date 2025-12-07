FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-*/policy.xml

WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Start Web Server
# We use a long timeout (300s) and restricted workers
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 300 run:app