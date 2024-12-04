FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc postgresql-client \
    binutils libproj-dev gdal-bin \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE myproject.settings

# Run migrations and start the server
CMD ["sh", "-c", "python manage.py migrate && gunicorn myproject.wsgi:application --bind 0.0.0.0:8000"]