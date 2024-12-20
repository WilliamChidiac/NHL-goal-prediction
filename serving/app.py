from flask import Flask, request, jsonify, session, redirect, url_for
from logging.handlers import RotatingFileHandler
import logging
import os
from ift6758 import load_model, get_model_names

FLASK_LOG = os.environ.get('FLASK_LOG', 'flask.log')
app = Flask(__name__)
logger = None
downloaded_models = {}
loaded_model = None
loaded_model_name = None
names = None

def build_model_name(workspace, model, version):
    name = f"{workspace}/{model}:{version}"
    return name

@app.before_first_request
def app_init():
    # Create a logger object
    global logger
    global downloaded_models
    global loaded_model
    global names
    global loaded_model_name
    
    logger = logging.getLogger('backend')
    logger.setLevel(logging.INFO)

    # Create a file handler that logs even debug messages
    handler = RotatingFileHandler(FLASK_LOG, maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)
    
    
    ##get list of models from wandb
    names = get_model_names()
    downloaded_models = { name : None for name in names}
    loaded_model = None
    
    ##load default model
    logger.info('Loading default model')
    loaded_model = load_model(names[0])
    loaded_model_name = names[0]
    downloaded_models[names[0]] = loaded_model
    logger.info(f'Model {names[0]} loaded')

@app.route('/')
def home():
    logger.info('Home page accessed')
    return 'Hello World!'

@app.route('/logs', methods=['GET'])
def login():
    with open('app.log', 'r') as f:
        data = f.read().splitlines()
    return jsonify(data)


@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/download_registry_model

    The comet API key should be retrieved from the ${WANDB_API_KEY} environment variable.

    Recommend (but not required) json with the schema:

        {
            workspace: (required),
            model: (required),
            version: (required),
            ... (other fields if needed) ...
        }
    
    """
    global downloaded_models
    global logger
    global loaded_model
    global loaded_model_name
    global names
    # Get POST json data
    json = request.get_json()
    app.logger.info(json)

    # TODO: check to see if the model you are querying for is already downloaded
    name = build_model_name(json['workspace'], json['model'], json['version'])
    model = downloaded_models.get(name, model)
    # TODO: if yes, load that model and write to the log about the model change.  
    # eg: app.logger.info(<LOG STRING>)
    if model:
        response = f"Model {name} already downloaded"
        loaded_model = model
        logger.info(response)
    # TODO: if no, try downloading the model: if it succeeds, load that model and write to the log
    # about the model change. If it fails, write to the log about the failure and keep the 
    # currently loaded model
    else:
        if name not in names:
            response = f"Model {name} not found keeping current model {loaded_model}"
            logger.info(response)
        else:
            response = f"Downloading model {name}"
            logger.info(response)
            model = load_model(name)
            downloaded_models[name] = model
            loaded_model = model
            logger.info(f'Model {name} loaded')
    return jsonify(response)  # response must be json serializable!



@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """
    # Get POST json data
    json = request.get_json()
    app.logger.info(json)

    game_id = json.get('game_id', None)
    shot_id = json.get('shot_id', None)
    
    response = None
    if game_id is None or shot_id is None:
        response = {
            'error': 'game_id and game_state must be provided'
        }
    else:
        prediction = loaded_model.predict(game_id, shot_id)
        response = {
            'prediction': prediction
        }
    

    app.logger.info(response)
    return jsonify(response)  # response must be json serializable!


if __name__ == '__main__':
    app.run()