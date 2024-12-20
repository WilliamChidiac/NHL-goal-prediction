# TO DO
--> make this command valid :
```
from ift6758 import load_model, get_model_names, get_workspace_lists, predict
```

Here are the signatures of the above imported functions:

```python
def load_model(workspace_name:str, model_name:str, version:str) -> Model
    """
    load the model from wandb

    Args:
        workspace_name (str) : the name of the workspace
        model_name (str) : the name of the model
        version (str) : the model's version 
    
    Returns:
        Model : the desired model.
    """
    pass
```

```python
def get_model_names(worksapce_name:str) -> List[str]
    """
    get the list of existing models in a given workspace.

    Args:
        workspace_name (str) : the name of the workspace
    
    Returns:
        List[str] : the list of the models available in the following format "{model_name}:{version}"
    """
    pass
```

```python
def get_workspaces_lists() -> List[str]
    """
    get the list of existing workspaces .

    Returns:
        List[str] : the list of the existing workspaces
    """
    pass
```

```python
def predict(model : Model, game_id : int) -> pd.Dataframe
    """
    predicts the probability of goal for every shots in a game

    Args:
        model (Model) : the model to use for predictions
        game_id (int) : the id of the game in question

    Returns:
        pd.Dataframe : A dataframing containing all the features used for training for columns + the predicted probability, and where each row represents the features of a given shot event.
    """
    pass
```

# TO TEST

go to file Dockerfile.serving and uncomment the line 
```
# RUN pip install --no-cache-dir -e ift6758
```

go to file serving/app.py and uncomment the line ~18
```
# from ift6758 import load_model, get_model_names, predict, get_workspace_lists
```

## BUILD
```
docker-compose build
```

## Run
```
docker-compose up
```
