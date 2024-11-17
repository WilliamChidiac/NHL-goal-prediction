import wandb
import json
import pandas as pd
import os
artifact_root_path = "../ift6758/data/wandb_artifacts/"


def download_artifact(artifact_name, artifact_version, project_name="IFT6758-2024-B05"):
    """
    Downloads a specified artifact from Weights & Biases (wandb) and saves it to a local directory.
    An artifact in the context of Weights & Biases (wandb) is a versioned file or collection of files, such as datasets, models, or other outputs, that are tracked and managed within a project. 
    Artifacts help in maintaining reproducibility and organization of project assets.
    Creates a directory with the artifact name in the specified root directory and saves the artifact there.
    Args:
        artifact_name (str): The name of the artifact to download
        artifact_version (str): The version of the artifact to download
        project_name (str): The name of the project in wandb. Default is "IFT6758-2024-B05".
    Returns:
        None
    """
    api = wandb.Api()  

    artifact = api.artifact(f"{project_name}/{artifact_name}:{artifact_version}")
    if not os.path.exists(f"{artifact_root_path}/{artifact_name}"):
        os.makedirs(f"{artifact_root_path}/{artifact_name}")
    artifact_dir = artifact.download(root=f"{artifact_root_path}/{artifact_name}")

    print(f"Artifact downloaded to: {artifact_dir}")
    

def convert_artifact_to_df(file_path):
    """
    Converts a JSON file to a pandas DataFrame.
    Args:
        file_path (str): The path to the JSON file.
    Returns:
        pd.DataFrame: A DataFrame containing the data from the JSON file.
    Raises:
        FileNotFoundError: If the JSON file does not exist.
        json.JSONDecodeError: If there is an error decoding the JSON file.
    """
    with open(file_path, "r") as file:
        table = json.load(file)
    df = pd.DataFrame(data=table['data'], columns=table['columns'])
    return df

def load_season_dataframe(artifact_name, season):
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
    file_path = f"{artifact_root_path}/{artifact_name}/{season}.table.json"
    
    df = convert_artifact_to_df(file_path)
    return df

def load_all_files_from_artifact(artifact_name):
    """
    Retrieves all the JSON files from a specified artifact and returns them as a list of pandas DataFrames.
    Args:
        artifact_name (str): The name of the artifact.
    Returns:
        list: A list of DataFrames containing the data from the JSON files.
    """
    artifact_dir = f"{artifact_root_path}/{artifact_name}"
    files = os.listdir(artifact_dir)
    df_list = []
    for file in files:
        if file.endswith(".json"):
            df = convert_artifact_to_df(f"{artifact_dir}/{file}")
            df_list.append(df)
    df_combined = pd.concat(df_list, ignore_index=True)
    return df_combined