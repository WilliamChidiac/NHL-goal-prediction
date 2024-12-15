from flask import Flask, request, jsonify, session, redirect, url_for
from logging.handlers import RotatingFileHandler
import logging
import os 
print(os.getcwd())

app = Flask(__name__)

# Create a logger object
logger = logging.getLogger('backend')
logger.setLevel(logging.INFO)

# Create a file handler that logs even debug messages
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)



@app.route('/')
def home():
    logger.info('Home page accessed')
    return 'Hello World!'

@app.route('/log')
def login():
    with open('app.log', 'r') as f:
        data = f.read().splitlines()
    return data

@app.route('/predict', methods=['POST'])
def about():
    data = request.get_json()
    logger.info('Home page accessed')
    return 'The about page'

@app.route('/hello/<name>/hey')
def hello(name):
    logger.info('Home page accessed')
    return 'Hello, ' + name

if __name__ == '__main__':
    app.run()