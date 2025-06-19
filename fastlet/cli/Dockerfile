# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN apt-get update && apt-get install -y git
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Command to run the FastAPI app using Uvicorn
CMD ["fastapi", "run", "--port", "8000"]