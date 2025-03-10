# Use an official Python runtime as a parent image
FROM python:3.12-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV REDIS_SERVER "redis"

# Run app.py when the container launches
CMD ["python", "app.py"]
