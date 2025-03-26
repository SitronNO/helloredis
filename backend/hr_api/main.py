#!/usr/bin/env python3

from fastapi import FastAPI, Request, status
import configparser

# Configparser
config = configparser.ConfigParser()
config.read('config.ini')

# FastAPI setup:
app = FastAPI(root_path=config['Web']['root_path'])


@app.get("/", status_code=status.HTTP_200_OK)
def welcome(request: Request):
    return {"message": "Welcome to the HelloRedis API",
            "root_path": request.scope.get("root_path")}
