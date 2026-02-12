FROM python:3.14-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files at build time
ENV DJANGO_SETTINGS_MODULE=config.settings.prod
RUN SECRET_KEY=build-placeholder ALLOWED_HOSTS=* python manage.py collectstatic --noinput

EXPOSE 8000

# Make entrypoint executable and set it
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
