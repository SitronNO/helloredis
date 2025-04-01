#!/usr/bin/env python3

from typing import Annotated
from fastapi import FastAPI, Request, status, HTTPException, Query
from redis import Redis, RedisError
from pydantic import BaseModel
import configparser
import datetime

# Configparser
config = configparser.ConfigParser()
config.read('config.ini')

# FastAPI setup:
app = FastAPI(root_path=config['Web']['root_path'])

# Connect to Redis
redis = Redis(host=config['Redis']['host'], db=0, decode_responses=True, socket_connect_timeout=2, socket_timeout=2)

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
    if redis.exists(hostname):
        redis.hset(hostname, "last_seen", now)
        redis.hincrby(hostname, "counter", 1)
    else:
        redis.hset(hostname, "first_seen", now)
        redis.hset(hostname, "last_seen", now)
        redis.hset(hostname, "counter", "1")

@app.get("/", status_code=status.HTTP_200_OK)
def welcome(request: Request):
    return {"message": "Welcome to the HelloRedis API",
            "root_path": request.scope.get("root_path")}

@app.get("/redishealth", status_code=status.HTTP_200_OK)
def redishealth():
    try:
        redis.ping()
        return {"redis": "Redis is healthy"}
    except RedisError:
        return {"redis": "Redis is unhealthy"}

@app.get("/redisdata", response_model=RedisDataResponse, status_code=status.HTTP_200_OK)
def redisdata(order_by: Annotated[ str | None, Query() ] = None, order_by_reversed: bool = False):
    hostslist = []
    try:
        for key in redis.scan_iter():
            hostslist.append(RedisData(hostname=key, first_seen=redis.hget(key, "first_seen"), last_seen=redis.hget(key, "last_seen"), counter=redis.hget(key, "counter")))
        if order_by == "counter":
            hostslist.sort(key=lambda entry: (
                entry.counter,
            ))
        elif order_by == "last_seen":
            hostslist.sort(key=lambda entry: (
                entry.last_seen,
            ))
        elif order_by == "first_seen":
            hostslist.sort(key=lambda entry: (
                entry.first_seen,
            ))
        elif order_by == "hostname":
            hostslist.sort(key=lambda entry: (
                entry.hostname,
            ))
        else:
            hostslist.sort(key=lambda entry: (
                entry.counter,
                entry.last_seen,
                entry.hostname,
                entry.first_seen,
            ))
        if order_by_reversed:
            hostslist.reverse()

        return RedisDataResponse(data=hostslist)
    except RedisError:
        raise HTTPException(status_code=500, detail="Redis is unhealthy")

@app.put("/redisdata", status_code=status.HTTP_204_NO_CONTENT)
def submitdata(hostname: Hostname):
    try:
        insertdata(hostname.hostname)
    except RedisError:
        raise HTTPException(status_code=500, detail="Redis is unhealthy")

