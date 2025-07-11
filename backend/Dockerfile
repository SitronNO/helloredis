FROM python:3.13

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./hr_api /code/hr_api

# Define environment variable
ENV REDIS_SERVER="redis"

# Healthcheck
HEALTHCHECK --interval=1m --timeout=5s --start-period=1m \
  CMD curl -f http://localhost/health || exit 1

CMD ["fastapi", "run", "hr_api/main.py", "--port", "80"]
