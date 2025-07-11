#!/usr/bin/env python3

import socket
import os
import requests
import json
import logging
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')


@app.route('/healthz', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    Returns a 200 OK status with a JSON payload if the application is healthy.
    """
    return jsonify({'status': 'healthy'}), 200


@app.route('/password', methods=['GET', 'POST'])
def password():
    local_hostname = socket.gethostname()
    api_server = os.getenv('API_SERVER', 'localhost:8000')
    logging.info(f'Hostname: {local_hostname}')
    logging.info(f'API Server: {api_server}')

    if request.method == 'POST':
        user_string = request.form['user_string']
        logging.info(f"Received string from user: {user_string}")

        try:
            response = requests.put(f'http://{ api_server }/password',
                                     json={'password': user_string})
            response.raise_for_status()
            salted_hash = response.json().get('salt_hashed_password')
            unsalted_hash = response.json().get('hashed_password')
            logging.info("Successfully received the hashed strings from API server.")
            return render_template('password.html',
                                   hostname=local_hostname,
                                   original_string=user_string,
                                   unsalted_hash=unsalted_hash,
                                   salted_hash=salted_hash)
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get the hashed strings from API server: {e}")
            return render_template('password.html',
                                   hostname=local_hostname,
                                   original_string=user_string,
                                   error='Failed to get the hashed strings from API server.')
    return render_template('password.html', hostname=local_hostname)


@app.route('/')
def index():
    local_hostname = socket.gethostname()
    api_server = os.getenv('API_SERVER', 'localhost:8000')

    logging.info(f'Hostname: {local_hostname}')
    logging.info(f'API Server: {api_server}')

    # Send JSON data to the API endpoint
    json_data = {"hostname": local_hostname}
    try:
        response = requests.put(f'http://{ api_server }/redisdata',
                                json=json_data)
        response.raise_for_status()
        logging.info('PUT request to /redisdata successful')
    except requests.exceptions.HTTPError as error:
        logging.error(f'Error during PUT request to /redisdata: {error}')
        if response.status_code == 500:
            # Parsing the JSON response
            response_dict = json.loads(response.text)
            errormsg = response_dict['detail']
        else:
            errormsg = 'Unknown error from API server'

        return render_template('error.html',
                               errormsg=errormsg,
                               hostname=local_hostname)
    except requests.exceptions.RequestException as error:
        logging.error(f'Error during PUT request to /redisdata: {error}')
        return render_template('error.html',
                               errormsg='Unable to connect to API server',
                               hostname=local_hostname)

    # Query the same endpoint with a GET request
    try:
        response = requests.get(f'http://{api_server}/redisdata')
        response.raise_for_status()
        logging.info('GET request to /redisdata successful')
    except requests.exceptions.RequestException as error:
        logging.error(f'Error during GET request to /redisdata: {error}')
        return render_template('error.html',
                               errormsg=str(error),
                               hostname=local_hostname)
    redisdata = response.json()

    # Render the data in a table on the webpage
    return render_template('redis.html',
                           servers=redisdata['data'],
                           hostname=local_hostname)


def create_app():
    return app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
