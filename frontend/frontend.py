#!/usr/bin/env python3

from flask import Flask, render_template
import requests
import socket
import os

app = Flask(__name__)


@app.route('/')
def index():
    local_hostname = socket.gethostname()
    api_server = os.getenv('API_SERVER', 'localhost:8000')

    # Send JSON data to the API endpoint
    json_data = {"hostname": local_hostname}
    try:
        response = requests.put(f'http://{ api_server }/redisdata', json=json_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        return render_template('error.html', error=str(error), hostname=local_hostname)
        
    # Query the same endpoint with a GET request
    response = requests.get(f'http://{ api_server }/redisdata')
    redisdata = response.json()
    
    # Render the data in a table on the webpage
    return render_template('redis.html', servers=redisdata['data'], hostname=local_hostname)


def create_app():
    return app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
