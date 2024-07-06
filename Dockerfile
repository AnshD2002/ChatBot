# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt requirements.txt

# Install the dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Specify the command to run the Flask application
CMD ["python", "app.py"]
