#!/usr/bin/env python3

import requests
import socket
import os
import logging
from flask import Flask, render_template

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')


@app.route('/')
def index():
    local_hostname = socket.gethostname()
    api_server = os.getenv('API_SERVER', 'localhost:8000')

    logging.info(f'Hostname: {local_hostname}')
    logging.info(f'API Server: {api_server}')

    # Send JSON data to the API endpoint
    json_data = {"hostname": local_hostname}
    try:
        response = requests.put(f'http://{ api_server }/redisdata', json=json_data)
        response.raise_for_status()
        logging.info('PUT request to /redisdata successful')
    except requests.exceptions.RequestException as error:
        logging.error(f'Error during PUT request to /redisdata: {error}')
        return render_template('error.html', error=str(error), hostname=local_hostname)
        
    # Query the same endpoint with a GET request
    try:
        response = requests.get(f'http://{api_server}/redisdata')
        response.raise_for_status()
        logging.info('GET request to /redisdata successful')
    except requests.exceptions.RequestException as error:
        logging.error(f'Error during GET request to /redisdata: {error}')
        return render_template('error.html', error=str(error), hostname=local_hostname)
    
    redisdata = response.json()
    
    # Render the data in a table on the webpage
    return render_template('redis.html', servers=redisdata['data'], hostname=local_hostname)


def create_app():
    return app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
