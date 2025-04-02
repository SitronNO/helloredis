# Helloredis API backend / hr_api

## Setup

1. For the first time, make a python3 venv and install required packages:
    1. `python3 -m venv venv`
    2. `. venv/bin/activate`
    3. `python3 -m pip install --upgrade -r requirements.txt`
2. If a python3 venv is already existing:
    1. `. venv/bin/activate`
3. Start the API service: `uvicorn hr_api.main:app --reload`


## Docker

Build the image:

    docker buildx build -t hr_api<:tag> .

Run the container:

    docker run --rm --name hr_api -p 8000:80 hr_api<:tag>
