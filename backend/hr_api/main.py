#!/usr/bin/env python3

import datetime
import os
import logging
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


class Hostname(BaseModel):
    hostname: str


class RedisData(BaseModel):
    hostname: str
    first_seen: str
    last_seen: str
    counter: int


class RedisDataResponse(BaseModel):
    data: list[RedisData]


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
