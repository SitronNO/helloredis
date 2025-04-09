# Use an official Python runtime as a parent image
FROM python:3.13

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV API_SERVER="localhost:8000"

# Run app.py when the container launches
CMD ["waitress-serve", "--port=5000", "--call", "frontend:create_app"]
