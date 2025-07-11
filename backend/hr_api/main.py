#!/usr/bin/env python3

import datetime
import os
import logging
import configparser
import hashlib
from typing import Annotated
from fastapi import FastAPI, Request, status, HTTPException, Query
from redis import Redis, RedisError
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path='')

# Connect to Redis
try:
    redis = Redis(host=os.getenv('REDIS_SERVER', 'localhost'),
                  db=0,
                  decode_responses=True,
                  socket_connect_timeout=2,
                  socket_timeout=2)
    logger.info("Connected to Redis")
except RedisError as e:
    logger.error("Failed to connect to Redis: %s", e)


class HealthCheck(BaseModel):
    status: str = "OK"


class HashedPassword(BaseModel):
    hashed_password: str
    salt_hashed_password: str


class Password(BaseModel):
    password: str


class Hostname(BaseModel):
    hostname: str


class RedisData(BaseModel):
    hostname: str
    first_seen: str
    last_seen: str
    counter: int


class RedisDataResponse(BaseModel):
    data: list[RedisData]


def get_salt():
    config_file = os.getenv('CONFIGFILE', '/config.ini')
    if not os.path.exists(config_file):
        logger.error(f"Configuration file '{config_file}' not found.")
        return None

    config = configparser.ConfigParser()
    config.read(config_file)
    try:
        return config['Secrets']['salt']
    except Exception as e:
        logger.error(f"Error reading salt from configuration file: {e}")
        return None


def insertdata(hostname):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if redis.exists(hostname):
            redis.hset(hostname, "last_seen", now)
            redis.hincrby(hostname, "counter", 1)
            logger.info("Updated data for hostname: %s", hostname)
        else:
            redis.hset(hostname, "first_seen", now)
            redis.hset(hostname, "last_seen", now)
            redis.hset(hostname, "counter", "1")
            logger.info("Inserted new data for hostname: %s", hostname)
    except RedisError as e:
        logger.error("Failed to insert data for hostname %s: %s", hostname, e)
        raise


@app.get("/", status_code=status.HTTP_200_OK)
def welcome(request: Request):
    logger.info("Welcome endpoint was called")
    return {"message": "Welcome to the HelloRedis API",
            "root_path": request.scope.get("root_path")}


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


@app.get("/redishealth", status_code=status.HTTP_200_OK)
def redishealth():
    try:
        redis.ping()
        logger.info("Redis health check passed")
        return {"redis": "Redis is healthy"}
    except RedisError:
        logger.error("Redis health check failed")
        return {"redis": "Redis is unhealthy"}


@app.get("/redisdata", response_model=RedisDataResponse,
         status_code=status.HTTP_200_OK)
def redisdata(order_by: Annotated[str | None, Query()] = None,
              order_by_reversed: bool = False):
    hostslist = []
    try:
        for key in redis.scan_iter():
            hostslist.append(RedisData(hostname=key,
                                       first_seen=redis.hget(key, "first_seen"),
                                       last_seen=redis.hget(key, "last_seen"),
                                       counter=redis.hget(key, "counter")))
        if order_by == "counter":
            hostslist.sort(key=lambda entry: (entry.counter,))
        elif order_by == "last_seen":
            hostslist.sort(key=lambda entry: (entry.last_seen,))
        elif order_by == "first_seen":
            hostslist.sort(key=lambda entry: (entry.first_seen,))
        elif order_by == "hostname":
            hostslist.sort(key=lambda entry: (entry.hostname,))
        else:
            hostslist.sort(key=lambda entry: (-entry.counter,
                                              entry.last_seen,
                                              entry.hostname,
                                              entry.first_seen))

        if order_by_reversed:
            hostslist.reverse()

        logger.info("Fetched redis data successfully")
        return RedisDataResponse(data=hostslist)
    except RedisError as e:
        logger.error("Failed to fetch redis data: %s", e)
        raise HTTPException(status_code=500, detail="Redis is unhealthy")


@app.put("/redisdata", status_code=status.HTTP_204_NO_CONTENT)
def submitdata(hostname: Hostname):
    try:
        insertdata(hostname.hostname)
        logger.info("Submitted data for hostname: %s", hostname.hostname)
    except RedisError as e:
        logger.error("Failed to submit data for hostname %s: %s",
                     hostname.hostname, e)
        raise HTTPException(status_code=500, detail="Redis is unhealthy")


@app.put("/password", response_model=HashedPassword,
         tags=["password"],
         status_code=status.HTTP_200_OK)
def hash_password(password: Password):
    try:
        # Hash the password
        hashed_password = hashlib.sha256(
            password.password.encode()).hexdigest()

        # Get the salt, and check if it exists
        salt = get_salt()

        if not salt:
            logger.error("Salt not found in configuration file.")
            raise ValueError("Salt not found")

        # Combine the password and salt
        salted_password = f'{salt}{password.password}'.encode()

        # Generate the hash
        salt_hashed_password = hashlib.sha256(salted_password).hexdigest()

        # Log the info message
        logger.info("Password successfully salted and hashed.")

        return {"hashed_password": hashed_password, "salt_hashed_password": salt_hashed_password}

    except Exception as e:
        # Log the error message
        logger.error(f"Error in salting and hashing password: {e}")
        raise HTTPException(status_code=500)
