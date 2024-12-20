import wandb
import os
import pandas as pd
import json
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from pathlib import Path
from sklearn.base import BaseEstimator

class WandbHandler:
    """
    A class to handle interactions with Weights and Biases (wandb) for downloading and logging artifacts.

    Attributes:
        project_name (str): The name of the wandb project.
        artifact_root_path (Path): The root path for storing artifacts locally.
        api (wandb.Api): The wandb API object for interacting with wandb.
    """
    def __init__(self, project_name="IFT6758-2024-B05", artifact_root_path="../ift6758/ift6758/data/wandb_artifacts/"):
        self.project_name = project_name
        self.artifact_root_path = Path(artifact_root_path)
        self.api = wandb.Api()

    def download_artifact(self, artifact_name, artifact_version):
        """
        Downloads a specified artifact from wandb and saves it to a local directory.

        Args:
            artifact_name (str): The name of the artifact to download.
            artifact_version (str): The version of the artifact to download.

        Returns:
            Path: The local directory where the artifact is saved.
        """
        artifact = self.api.artifact(f"{self.project_name}/{artifact_name}:{artifact_version}")
        artifact_dir = self.artifact_root_path / artifact_name
        if not os.path.exists(artifact_dir):
            artifact_dir.mkdir(parents=True, exist_ok=True)
        artifact.download(root=str(artifact_dir))
        print(f"Artifact downloaded to: {artifact_dir}")
        return artifact_dir

    def log_artifact(self, artifact_name, artifact_type, file_path):
        """
        Logs a specified file as an artifact to wandb.

        Args:
            artifact_name (str): The name of the artifact.
            artifact_type (str): The type of the artifact (e.g., 'model', 'dataset').
            file_path (str): The path to the file to log as an artifact.
        """
        run = wandb.init(project=self.project_name)
        artifact = wandb.Artifact(artifact_name, type=artifact_type)
        artifact.add_file(file_path)
        run.log_artifact(artifact)
        run.finish()
    
    def upload_dataset_to_wandb(self, df, seasons, artifact_name, run_name, description=None):
        """
        Uploads a dataset to wandb as an artifact.

        Args:
            df (pd.DataFrame): The dataset to upload.
            artifact_name (str): The name of the artifact.
            run_name (str): The name of the wandb run.
            description (str): A description of the artifact.
        """
        with wandb.init(name=run_name, project=self.project_name, job_type="upload-data") as run:
            artifact = wandb.Artifact(artifact_name, type='dataset', description=description)
            for season in seasons:
                formatted_season = int(season.replace('-', '')) # 2016-2017 -> 20162017
                table = wandb.Table(dataframe=df[df["season"] == formatted_season])
                artifact.add(table, f"{season}")
            run.log_artifact(artifact)
    
    def __str__(self) -> str:
        return f"Project: {self.project_name}\nArtifact Root Path: {self.artifact_root_path}"


class DataLoader(WandbHandler):
    def __init__(self):
        super().__init__()

    def convert_artifact_to_df(self, file_path):
        """
        Converts a JSON file to a pandas DataFrame.

        Args:
            file_path (str): The path to the JSON file.

        Returns:
            pd.DataFrame: A DataFrame containing the data from the JSON file.
        """
        with open(file_path, "r") as file:
            table = json.load(file)
        df = pd.DataFrame(data=table['data'], columns=table['columns'])
        return df

    def load_season_dataframe(self, artifact_name, artifact_version, season, download_artifact=True):
        """
        Loads a DataFrame for a given season from a wandb artifact.

        Args:
            artifact_name (str): The name of the artifact.
            artifact_version (str): The version of the artifact.
            season (str): The season to load (format 'YYYY-YYYY').

        Returns:
            pd.DataFrame: A DataFrame containing the data for the specified season.
        """
        assert isinstance(season, str) and len(season) == 9 and season[4] == '-', "Season format should be 'YYYY-YYYY'"
        if download_artifact:
            self.download_artifact(artifact_name, artifact_version)
        artifact_dir = self.artifact_root_path / artifact_name
        file_path = artifact_dir / f"{season}.table.json"
        # file_path = next((artifact_dir / f for f in os.listdir(artifact_dir) if season in f), None) # find the file with the season in the name
        df = self.convert_artifact_to_df(file_path)
        return df

    def load_seasons_dataframe(self, artifact_name, artifact_version, seasons):
        """
        Loads DataFrames for multiple seasons from a wandb artifact and concatenates them.

        Args:
            artifact_name (str): The name of the artifact.
            artifact_version (str): The version of the artifact.
            seasons (list of str): List of seasons to load (format 'YYYY-YYYY').

        Returns:
            pd.DataFrame: A concatenated DataFrame containing the data for the specified seasons.
        """
        dataframes = []
        self.download_artifact(artifact_name, artifact_version)
        for season in seasons:
            df = self.load_season_dataframe(artifact_name, artifact_version, season, download_artifact=False)
            dataframes.append(df)
        return pd.concat(dataframes, ignore_index=True)

    def load_all_files_from_artifact(self, artifact_name, artifact_version):
        """
        Loads all JSON files from a wandb artifact and concatenates them into a single DataFrame.

        Args:
            artifact_name (str): The name of the artifact.
            artifact_version (str): The version of the artifact.

        Returns:
            pd.DataFrame: A concatenated DataFrame containing the data from all JSON files in the artifact.
        """
        artifact_dir = self.download_artifact(artifact_name, artifact_version)
        dataframes = []
        for file_name in artifact_dir.iterdir():
            if file_name.suffix == ".json":
                df = self.convert_artifact_to_df(file_name)
                dataframes.append(df)
        return pd.concat(dataframes, ignore_index=True)

class ModelHandler(WandbHandler):
    def __init__(self, model_root_path="../ift6758/ift6758/models/"):
        super().__init__()
        self.model_root_path = Path(model_root_path)

    def dump(self, model: BaseEstimator, model_name: str):
        """
        Saves the trained model to disk.

        Args:
            model (BaseEstimator): The trained model.
            model_name (str): The name of the model.
        """
        model_path = self.model_root_path / Path(f"{model_name}.pkl")
        joblib.dump(model, model_path)
    
    def predict(self, model, X_eval):
        """
        Makes predictions using the trained model.

        Args:
            model (BaseEstimator): The trained model.
            X_eval (np.array): The evaluation features.

        Returns:
            tuple: A tuple containing the discrete predictions and the predicted probabilities.
        """
        y_pred_discrete = model.predict(X_eval)
        y_pred_proba = model.predict_proba(X_eval)
        return y_pred_discrete, y_pred_proba

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

    def log_wandb(self, model_name, X_eval, y_eval, features):
        """
        Logs the model and evaluation metrics to wandb.

        Args:
            model_name (str): Name of the model.
            X_eval (np.array): Evaluation features.
            y_eval (np.array): Evaluation labels.
            features (list): List of feature names.
        """
        model_path = self.model_root_path / Path(f"{model_name}.pkl")
        model = joblib.load(model_path) # load and predict to ensure model is correctly stored
        y_pred_discrete, y_pred_proba = self.predict(model, X_eval)
        with wandb.init(project=self.project_name) as run:
            metrics = self.get_metrics(y_pred_discrete, y_pred_proba, y_eval)
            run.log({"confusion_matrix": wandb.plot.confusion_matrix(probs=None,
                                                                    y_true=y_eval.flatten().tolist(),
                                                                    preds=y_pred_discrete.flatten().tolist(),
                                                                    class_names=["Not Goal", "Goal"])})
            run.config.update({
                "model_type": model_name,
                "features": features
            })
            run.log(metrics)
            artifact = wandb.Artifact(model_name, type='model')
            artifact.add_file(model_path)
            run.log_artifact(artifact)

    def load_model(self, model_name, model_version):
        """
        Loads a model from wandb and reproduces results.

        Args:
            artifact_name (str): Name of the artifact.
            artifact_version (str): Version of the artifact.
            X_eval (np.array): Evaluation features.
            y_eval (np.array): Evaluation labels.

        Returns:
            dict: Evaluation metrics.
        """
        model = None
        with wandb.init(project=self.project_name) as run:
            model_artifact = run.use_artifact(f'{model_name}:{model_version}', type='model')
            model_dir = model_artifact.download(root=str(self.model_root_path / model_name))
            model_path = Path(model_dir) / Path(f"{model_name}.pkl")
            model = joblib.load(model_path)
        return model
    

    def get_model_list(self):
        """
        https://stackoverflow.com/questions/68952727/wandb-get-a-list-of-all-artifact-collections-and-all-aliases-of-those-artifacts
        
        Retrieves a list of all models logged in the wandb project.

        Returns:
            list: A list of model names.
        """
        collections = [
            coll for coll in self.api.artifact_type(type_name="model", project=self.project_name).collections()
        ]
        return [artifact.name for coll in collections for artifact in coll.artifacts()]