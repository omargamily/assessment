# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
# Copy the requirements file into the container
COPY requirements.txt /app/
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code into the container
COPY . /app/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Expose port 8000 for the Django app
EXPOSE 8000
