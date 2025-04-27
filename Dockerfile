# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENVIRONMENT=production

# Set work directory
WORKDIR /app

# Install dependencies
# Copy the requirements file into the container
COPY requirements.txt /app/

# Copy project code into the container
COPY ./backend /app/

# Install the dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Expose port 8000 for the Django app
EXPOSE 8000
