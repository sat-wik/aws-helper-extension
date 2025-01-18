# Use the official Python image as the base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files to the container
COPY backend/requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 8000
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
