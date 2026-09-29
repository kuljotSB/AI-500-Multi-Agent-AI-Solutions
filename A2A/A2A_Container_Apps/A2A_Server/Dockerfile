# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements if present
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the server code
COPY . .

# Expose the port your server will run on
EXPOSE 8080

# Start the server
CMD ["python", "server.py"]