# Use official Python 3.12 slim image (lightweight & stable)
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (better caching for builds)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your project files
COPY . .

# Expose port that Cloud Run expects
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]