# Helloredis frontend

## Setup

1. For the first time, make a python3 venv and install required packages:
    1. `python3 -m venv venv`
    2. `. venv/bin/activate`
    3. `python3 -m pip install --upgrade -r requirements.txt`
2. If a python3 venv is already existing:
    1. `. venv/bin/activate`
3. Start the web frontend: `python3 ./frontend.py`

## Docker

Build the image:

    docker buildx build -t helloredis_frontend<:tag> .


Run the container:

    docker run --rm --name helloredis_frontend -p 5000:5000 helloredis_frontend<:tag>
