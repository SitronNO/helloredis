FROM python:3.13

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./hr_api /code/hr_api

# Define environment variable
ENV REDIS_SERVER="redis"
ENV ROOT_PATH=""

CMD ["fastapi", "run", "hr_api/main.py", "--port", "80"]
