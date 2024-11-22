import wandb
import os
import pandas as pd
import json
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from pathlib import Path

class WandbHandler:
    def __init__(self, project_name, artifact_root_path="../ift6758/data/wandb_artifacts/"):
        self.project_name = project_name
        self.artifact_root_path = Path(artifact_root_path)
        self.api = wandb.Api()

    def download_artifact(self, artifact_name, artifact_version):
        artifact = self.api.artifact(f"{self.project_name}/{artifact_name}:{artifact_version}")
        artifact_dir = self.artifact_root_path / artifact_name
        if not os.path.exists(artifact_dir):
            artifact_dir.mkdir(parents=True, exist_ok=True)
        artifact.download(root=str(artifact_dir))
        print(f"Artifact downloaded to: {artifact_dir}")
        return artifact_dir

    def log_artifact(self, artifact_name, artifact_type, file_path):
        run = wandb.init(project=self.project_name)
        artifact = wandb.Artifact(artifact_name, type=artifact_type)
        artifact.add_file(file_path)
        run.log_artifact(artifact)
        run.finish()
    
    def upload_dataset_to_wandb(self, df, seasons, artifact_name, run_name, description=None, tags=None):
        """
        Uploads a dataset to wandb as an artifact.

        Args:
            df (pd.DataFrame): The dataset to upload.
            artifact_name (str): The name of the artifact.
            run_name (str): The name of the wandb run.
            description (str): A description of the artifact.
            tags (list): A list of tags to add to the artifact.
        """
        with wandb.init(name=run_name, project=self.project_name, job_type="upload-data") as run:
            artifact = wandb.Artifact(artifact_name, type='dataset', description=description)
            for season in seasons:
                formatted_season = int(season.replace('-', '')) # 2016-2017 -> 20162017
                table = wandb.Table(dataframe=df[df["season"] == formatted_season])
                artifact.add(table, f"{season}")
            run.log_artifact(artifact)
            artifact.wait()
            artifact.tags = tags
            artifact.save()


class DataLoader(WandbHandler):
    def __init__(self, project_name, artifact_root_path="../ift6758/data/wandb_artifacts/"):
        super().__init__(project_name, artifact_root_path)

    def convert_artifact_to_df(self, file_path):
        with open(file_path, "r") as file:
            table = json.load(file)
        df = pd.DataFrame(data=table['data'], columns=table['columns'])
        return df

    def load_season_dataframe(self, artifact_name, artifact_version, season, download_artifact=True):
        assert isinstance(season, str) and len(season) == 9 and season[4] == '-', "Season format should be 'YYYY-YYYY'"
        if download_artifact:
            self.download_artifact(artifact_name, artifact_version)
        artifact_dir = self.artifact_root_path / artifact_name
        file_path = next((artifact_dir / f for f in os.listdir(artifact_dir) if season in f), None) # find the file with the season in the name
        df = self.convert_artifact_to_df(file_path)
        return df

    def load_seasons_dataframe(self, artifact_name, artifact_version, seasons):
        dataframes = []
        self.download_artifact(artifact_name, artifact_version)
        for season in seasons:
            df = self.load_season_dataframe(artifact_name, artifact_version, season, download_artifact=False)
            dataframes.append(df)
        return pd.concat(dataframes, ignore_index=True)

    def load_all_files_from_artifact(self, artifact_name, artifact_version):
        artifact_dir = self.download_artifact(artifact_name, artifact_version)
        dataframes = []
        for file_name in artifact_dir.iterdir():
            if file_name.suffix == ".json":
                df = self.convert_artifact_to_df(file_name)
                dataframes.append(df)
        return pd.concat(dataframes, ignore_index=True)

class ModelUploader(WandbHandler):
    def __init__(self, project_name, artifact_root_path="../ift6758/data/wandb_artifacts/"):
        super().__init__(project_name, artifact_root_path)

    def log_model(self, model, model_name, model_path, y_true, y_pred, features):
        joblib.dump(model, model_path)
        run = wandb.init(project=self.project_name)
        run.log({"confusion_matrix": wandb.plot.confusion_matrix(probs=None,
                                                                y_true=y_true.flatten().tolist(),
                                                                preds=y_pred.flatten().tolist(),
                                                                class_names=["Not Goal", "Goal"])})
        run.config.update({
            "model_type": model_name,
            "features": features
        })
        run.log({"accuracy": accuracy_score(y_true, y_pred)})
        run.log({"precision": precision_score(y_true, y_pred)})
        run.log({"recall": recall_score(y_true, y_pred)})
        run.log({"f1_score": f1_score(y_true, y_pred)})
        artifact = wandb.Artifact(model_name, type='model')
        artifact.add_file(model_path)
        run.log_artifact(artifact)
        run.finish()