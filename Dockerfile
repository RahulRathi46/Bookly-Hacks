# Use the official Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Generate SSL certificate
RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -subj "/CN=localhost" -days 365

# Expose port 5000 to the outside world
EXPOSE 5000

# Run app.py when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--certfile", "cert.pem", "--keyfile", "key.pem", "app:app"]