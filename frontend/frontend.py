#!/usr/bin/env python3

import socket
import os
import requests
import json
import logging
import configparser
from flask import Flask, render_template, request

app = Flask(__name__)

# Global parameters
local_hostname = socket.gethostname()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')


# Load configuration
config_file = os.getenv('CONFIGFILE', '/config.ini')
if not os.path.exists(config_file):
    logging.error(f"Configuration file '{config_file}' not found.")
    raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
    
config = configparser.ConfigParser()
config.read(config_file)
correct_number = config.get('Answers', 'number')
correct_animal = config.get('Answers', 'animal').lower()


@app.route('/guess', methods=['GET', 'POST'])
def guess():
    result = None
    if request.method == 'POST':

        user_number = request.form.get('number')
        user_animal = request.form.get('animal').lower()

        logging.info(f"User guessed number: {user_number}, animal: {user_animal}")

        correct_num = user_number == correct_number
        correct_anim = user_animal == correct_animal

        if correct_num and correct_anim:
            result = "🎉 You guessed both correctly! 🎉"
        elif correct_num:
            result = "Correct number, but wrong animal."
        elif correct_anim:
            result = "Correct animal, but wrong number."
        else:
            result = "❌ Both guesses are incorrect. ❌"

        return render_template('guess.html',
                               number=user_number,
                               animal=user_animal,
                               result=result,
                               hostname=local_hostname)

    else:
        return render_template('guess.html',
                               result=result,
                               hostname=local_hostname)


@app.route('/')
def index():
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
