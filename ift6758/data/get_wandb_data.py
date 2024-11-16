import wandb
import json
import pandas as pd

artifact_path = "../ift6758/data/wandb_artifacts/shot_events"


def download_artifact(artifact_name, project_name="IFT6758-2024-B05"):
    """
    Downloads a specified artifact from Weights & Biases (wandb) and saves it to a local directory.
    An artifact in the context of Weights & Biases (wandb) is a versioned file or collection of files, such as datasets, models, or other outputs, that are tracked and managed within a project. 
    Artifacts help in maintaining reproducibility and organization of project assets.
    Args:
        project_name (str): The name of the project in wandb. Default is "IFT6758-2024-B05".
        artifact_name (str): The name of the artifact to download, including the version. Default is "shot_events:latest".
    Returns:
        None
    """
    api = wandb.Api()  

    artifact = api.artifact(f"{project_name}/{artifact_name}")
    artifact_dir = artifact.download(root=artifact_path)

    print(f"Artifact downloaded to: {artifact_dir}")
    

def load_season_dataframe(season):
    """
    Retrieves a pandas DataFrame for a given NHL season from a JSON file.
    Args:
        season (str): The season in 'YYYY-YYYY' format.
    Returns:
        pd.DataFrame: A DataFrame containing the data for the specified season.
    Raises:
        AssertionError: If the season format is incorrect.
        FileNotFoundError: If the JSON file for the specified season does not exist.
        json.JSONDecodeError: If there is an error decoding the JSON file.
    """

    assert isinstance(season, str) and len(season) == 9 and season[4] == '-', "Season format should be 'YYYY-YYYY'"
    file_path = f"{artifact_path}/{season}.table.json"
    with open(file_path, "r") as file:
        table = json.load(file)
    df = pd.DataFrame(data=table['data'], columns=table['columns'])
    return df