# Use Python 3.9-slim as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (Git)
RUN apt-get update && apt-get install -y git

# Copy the requirements.txt first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 5000

# Set the default command to run the app
CMD ["python", "app.py"]
