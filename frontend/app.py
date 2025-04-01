#!/usr/bin/env python3

from flask import Flask, jsonify, render_template, request
import requests
import socket

app = Flask(__name__)

@app.route('/')
def index():
    # Send JSON data to the API endpoint
    json_data = {"hostname": socket.gethostname()}
    try:
        response = requests.put('http://localhost:8000/redisdata', json=json_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        return render_template('error.html', error=str(error))
        
    # Query the same endpoint with a GET request
    response = requests.get('http://localhost:8000/redisdata')
    redisdata = response.json()
    
    # Render the data in a table on the webpage
    return render_template('redis.html', servers=redisdata['data'], hostname=socket.gethostname())

if __name__ == '__main__':
    app.run(debug=True)
