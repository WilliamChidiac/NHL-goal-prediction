from flask import Flask, request, jsonify
from logging.handlers import RotatingFileHandler
import logging
from random import randrange
import os


# load_model = lambda w, m, v : str(w) + '/' +  str(m) + ':' + str(v)
# get_model_names = lambda workspace: ['model1:v1', 'model2:v1', 'model2:v2'] if workspace == 'workspace1' else \
#                                     ['model3:v1', 'model4:v1', 'model4:v2']
# get_workspace_lists = lambda : ['workspace1', 'workspace2']
# predict= lambda model, game_id : 0+game_id if model == 'workspace1/model1:v1' else \
#                                 (1+game_id if model == 'workspace1/model2:v1' else \
#                                 (2+game_id if model == 'workspace1/model2:v2' else \
#                                 (3+game_id if model == 'workspace2/model3:v1' else \
#                                 (4+game_id if model == 'workspace2/model4:v1' else \
#                                 (5+game_id if model == 'workspace2/model4:v2' else -1)))))
# from ift6758 import load_model, get_model_names, predict, get_workspace_lists
from ift6758.data.light_wandb_handler import LightWandbHandler

FLASK_LOG = os.environ.get('FLASK_LOG', 'flask.log')
FLASK_RUN_HOST = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
FLASK_RUN_PORT = os.environ.get('FLASK_RUN_PORT', 5000)
WANDB_API_KEY = os.environ.get('WANDB_API_KEY', None)
app = Flask(__name__)
logger = None
workspaces = {}
selections = False
current_model = None
current_model_name = None
fmt = lambda msg, code : f'{msg}   -   status code : {code}'
wandb_handler = LightWandbHandler()

def build_selections():
    ##get list of models from wandb
    try:
        repos = wandb_handler.get_workspaces_lists()
        logger.info(f'Workspaces: {repos}')
        for workspace in repos:
            models = wandb_handler.get_model_names(workspace)
            list_models = {}
            for model in models:
                name, version = model.split(':')
                try:
                    list_models[name][version] = None
                except KeyError:
                    list_models[name] = {version: None}
            if list_models != {}:
                workspaces[workspace] = list_models
        return True
    except Exception as e:
        logger.error(fmt(str(e), 500))
        return False

@app.before_request
def app_init():
    # Create a logger object
    global logger
    global selections
    global workspaces
    
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
    
    selections = build_selections()
    app.logger = logger

@app.route('/logs', methods=['GET'])
def log():
    with open(FLASK_LOG, 'r') as f:
        data = f.read().splitlines()
    return jsonify(data)

@app.route('/login/<apikey>', methods=['GET'])
def login(apikey):
    WANDB_API_KEY = apikey
    os.environ['WANDB_API_KEY'] = apikey
    if build_selections():
        app.logger.info(fmt('Login successful', 200))
        return jsonify({'apikey': WANDB_API_KEY}), 200
    else:
        app.logger.error(fmt('Invalid API key', 401))
        return jsonify({'error': 'Invalid API key'}), 401
    
@app.route('/is_login', methods=['GET'])
def is_login():
    if WANDB_API_KEY is None:
        return jsonify({'login': False}), 200
    else:
        return jsonify({'login': True}), 200


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
    global workspaces
    global logger
    global current_model
    global current_model_name
    
    try:
        # Get POST json data
        json = request.get_json()
        app.logger.info(json)
        workspace = json.get('workspace', None)
        model_name = json.get('model', None)
        version = json.get('version', None)
        # TODO: check to see if the model you are querying for is already downloaded
        if workspace is None or model_name is None or version is None:
            response = "Workspace, model, and version must be provided"
            code = 400
        if workspace not in workspaces:
            response = f"Workspace {workspace} not found"
            code = 404
        elif model_name not in workspaces[workspace]:
            response = f"Model {model_name} not found in workspace {workspace}"
            code = 404
        elif version not in workspaces[workspace][model_name]:
            response = f"Version {version} not found for model {workspace}/{model_name}"
            code = 404
        else:
            model = workspaces[workspace][model_name][version]
            if model is None:
                response = f"Downloading model {workspace}/{model_name}:{version}"
                model = wandb_handler.load_model(workspace, model_name, version)
                workspaces[workspace][model_name][version] = model
            else :
                response = f"Model {workspace}/{model_name}:{version} already downloaded"
            code = 200
            current_model = model
            current_model_name = model_name
        app.logger.info(fmt(response, code))
        return jsonify({'response': response}), code
    except Exception as e:
        logger.error(fmt(str(e), 500))
        return jsonify({'error': str(e), "workspace": workspace, "model_name" : model_name, "version" : version}), 500

@app.route("/workspaces/all", methods=["GET"])
def list_workspaces():
    """
    Handles GET requests made to http://IP_ADDRESS:PORT/workspaces/all

    Returns a list of workspaces
    """
    global workspaces
    all_selections = workspaces.copy()
    for workspace in all_selections:
        all_selections[workspace] = {model: list(versions.keys()) for model, versions in all_selections[workspace].items()}
    return jsonify(all_selections), 200

@app.route("/predict", methods=["POST"])
def model_predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """
    # Get POST json data
    json = request.get_json()
    app.logger.info(json)

    game_id = json.get('game_id', None)
    
    response = None
    if game_id is None:
        code = 400
        response = {
            'error': 'game_id must be provided'
        }
    else:
        logger.info(f'Predicting game {game_id} with model {current_model_name}')
        try:
            df = wandb_handler.predict(current_model_name, current_model, game_id)
            metrics = wandb_handler.get_metrics(df['is_goal'].to_numpy(), df['goal_probability'].to_numpy(), df['labels'].to_numpy())
            logger.info(f'{df.head()}')

            response = {
                'results': {'df': df.to_dict(), 'metrics': metrics}
            }
            code = 200
        except Exception as e:
            logger.error(fmt(str(e), 500))
            response = {
                'error': str(e)
            }
            code = 500
    
    return jsonify(response), code # response must be json serializable!


if __name__ == '__main__':
    print('Starting Flask app')
    app.run(host=FLASK_RUN_HOST, port=FLASK_RUN_PORT)