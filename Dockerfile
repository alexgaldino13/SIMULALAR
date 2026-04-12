# Use Python 3.12 slim
FROM python:3.12-slim

# Install system dependencies for PostgreSQL and Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn whitenoise dj-database-url psycopg2-binary

# Copy project files
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV DEBUG=False

# Collect static files
RUN python manage.py collectstatic --noinput

# Run with Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn ImobCalc.wsgi:application --bind 0.0.0.0:$PORT"]
