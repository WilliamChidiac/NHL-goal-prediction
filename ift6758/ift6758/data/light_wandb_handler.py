import wandb
from pathlib import Path
import joblib
import os
from ift6758.features.preprocess_II import PreprocessII  as pp2
from ift6758.features.feature_engineering_II import  FeatureEngineeringII as fe2
from typing import List, Tuple, Any
from sklearn.base import BaseEstimator
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

class LightWandbHandler:
    """
    A class to handle interactions with Weights and Biases (wandb) for downloading and logging artifacts.

    Attributes:
        project_name (str): The name of the wandb project.
        artifact_root_path (Path): The root path for storing artifacts locally.
        api (wandb.Api): The wandb API object for interacting with wandb.
    """
    def __init__(self):
        self.model_root_path =  Path("../ift6758/ift6758/models/")
        self.login()
        self.api = wandb.Api()
    
    def login(self):
        """
        Logs into wandb using the API key stored in WANDB_API_KEY environmental variable.
        """
        wandb_api_key = os.getenv('WANDB_API_KEY')
        if wandb_api_key:
            wandb.login(key=wandb_api_key, relogin=True, force=True)
        else:
            raise ValueError("WANDB_API_KEY environment variable not set")
    
    
    def load_model(self, workspace_name:str, model_name:str, version:str) -> BaseEstimator:
        """
        Loads a model from wandb and reproduces results.

        Args:
            artifact_name (str): Name of the artifact.
            artifact_version (str): Version of the artifact.
            workspace (str): Name of the workspace.
        Returns:
            dict: Evaluation metrics.
        """
        model = None
        model_path = self.model_root_path / model_name / f"{model_name}.pkl"
        if model_path.exists():
            print("Model already exists locally, returnning cached model")
            return joblib.load(model_path)
        with wandb.init(project=workspace_name) as run:
            model_artifact = run.use_artifact(f'{model_name}:{version}', type='model')
            model_dir = model_artifact.download(root=str(self.model_root_path / model_name))
            model_path = Path(model_dir) / Path(f"{model_name}.pkl")
            model = joblib.load(model_path)
        return model
    
    def get_metrics(self, y_pred_discrete, y_pred_proba, y_eval):
        """
        Calculates evaluation metrics for the model.

        Args:
            y_pred_discrete (np.array): The discrete predictions.
            y_pred_proba (np.array): The predicted probabilities.
            y_eval (np.array): The evaluation labels.

        Returns:
            dict: A dictionary containing the evaluation metrics.
        """
        metrics = {
            "auc": roc_auc_score(y_eval, y_pred_proba[:, 1]),
            "accuracy": accuracy_score(y_eval, y_pred_discrete),
            "precision": precision_score(y_eval, y_pred_discrete),
            "recall": recall_score(y_eval, y_pred_discrete),
            "f1_score": f1_score(y_eval, y_pred_discrete)
        }
        return metrics

    def get_model_names(self, worksapce_name:str) -> List[str] :
        """
        https://stackoverflow.com/questions/68952727/wandb-get-a-list-of-all-artifact-collections-and-all-aliases-of-those-artifacts
        
        Retrieves a list of all models logged in the wandb project.

        Returns:
            list: A list of model names.
        """
        collections = [
            coll for coll in self.api.artifact_type(type_name="model", project=worksapce_name).collections()
        ]
        return [artifact.name for coll in collections for artifact in coll.artifacts()]
    
    def predict(self, model_name:str, model: BaseEstimator, game_id: int) -> Tuple[np.array, np.array, np.array]:	
        """
        Makes predictions using the trained model.

        Args:
            model (BaseEstimator): The trained model.
            X_eval (np.array): The evaluation features.

        Returns:
            tuple: A tuple containing the discrete predictions and the predicted probabilities.
        """
        game_data = self.get_game_id(game_id)

        features = []
        if "distance" in model_name and "angle" in model_name:
            features = ['distance_from_net', 'angle_from_net']
        elif "distance" in model_name:
            features = ['distance_from_net']
        elif "angle" in model_name:
            features = ['angle_from_net']
        
        X = game_data[features].to_numpy()
        y_true = game_data['labels'].to_numpy().reshape(-1, 1)

        y_pred_discrete = model.predict(X)
        y_pred_proba = model.predict_proba(X)
        return y_pred_discrete, y_pred_proba, y_true
    

    def get_workspaces_lists(self) -> List[str]:
        """
        Retrieves a list of all wandb workspaces.

        Returns:
            list: A list of workspace names.
        """

        # Get the list of workspaces
        workspaces = self.api.projects()
        workspace_names = [workspace.__name__ for workspace in workspaces]

        return workspace_names

    def get_game_id(self, game_id):
        """
        Retrieves the game data from NHL API and preprocesses it.
        """

        df = pp2.get_game_df(game_id)
        cleaned_df = fe2(df)
        cleaned_df.clean_df(columns=['game_id', 'event_id', 'distance_from_net', 'angle_from_net', 'labels', 'empty_net'])
        return cleaned_df.df
    
