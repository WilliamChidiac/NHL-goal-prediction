import requests
import os
import json
from pathlib import Path
from json.decoder import JSONDecodeError

# https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md
# https://en.wikipedia.org/wiki/List_of_NHL_seasons

REGULAR_SEASON = "02"
PLAYOFFS = "03"

"""
1353 for seasons with 32 teams (2022 - Present)
1271 for seasons with 31 teams (2017 - 2020)
1230 for seasons with 30 team
For playoff games, the 2nd digit of the specific number gives the round of the playoffs, the 3rd digit specifies the matchup, and the 4th digit specifies the game (out of 7).
"""
game_number_per_year = {
    "2017": "1271",  # 31 teams that play 82 games
    "2018": "1271",
    "2019": "1082",  # trial and error on the NHL API
    "2020": "868",  # trial and error on the NHL API
    "2021": "1312",  # 32 teams that play 82 games
    "2022": "1312",
    "2023": "1312",
}


# will generate all playoff games, but some might not work
# ex: if team wins 4 games in a row -> will advance to next game
def playoff_game_id_generator(season) -> list[str]:
    game_ids = []
    for round in range(1, 4 + 1):
        if round == 1:
            game_ids += matchups(season, round, 8)  # 8 games in round 1 for 16 teams
        elif round == 2:
            game_ids += matchups(season, round, 4)  # 4 games in round 2 for 8 teams
        elif round == 3:
            game_ids += matchups(season, round, 2)  # 2 games in round 3 for 4 teams
        elif round == 4:
            game_ids += matchups(season, round, 1)  # 1 games in round 4 for 2 teams
    return game_ids


def matchups(season, round, matchup_range):
    game_ids = []
    for matchup in range(1, matchup_range + 1):
        for best_of_seven in range(1, 7 + 1):
            game_ids.append(f"{season}_{PLAYOFFS}_0-{round}-{matchup}-{best_of_seven}")
    return game_ids


def clean_playoff_game_id(game_id) -> str:
    return game_id.replace("_", "").replace("-", "")


def regular_season_game_id_generator(season) -> list[str]:
    game_ids = []
    for game_number in range(1, int(game_number_per_year[season]) + 1):
        game_id = f"{season}{REGULAR_SEASON}{game_number:04d}"
        game_ids.append(game_id)
    return game_ids


def download_data(game_id) -> dict:
    response = requests.get(
        f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    )

    if response.status_code == 200:
        data = response.json()
        print("Downloaded game id: ", game_id)
        return data
    else:
        print(f"Failed to retrieve game ID {game_id}: {response.status_code}")
        return None


def load_cached_data(file_path) -> dict:
    with open(file_path, "r") as file:
        print("using cached data for game id: ", file_path.split("/")[-1])
        try:
            data = json.load(file)
            return data
        except JSONDecodeError:
            print(
                f"Error decoding JSON from response for game ID: {file_path.split('/')[-1]}"
            )
        return None


def retrieve_game_data(game_id) -> dict:
    data_dir = (
        Path(__file__).resolve().parent.as_posix() + "/raw_data"
    )  # path to the raw data directory relative to this file
    filename = f"{game_id}.json"
    file_path = f"{data_dir}/{filename}"

    if os.path.exists(file_path):
        data = load_cached_data(file_path)
        if data:
            return data
        else:  # file is present but corrupted: remove it, and redownload
            os.remove(file_path)

    data = download_data(game_id)
    if data:  # do not create a file if the download failed
        with open(f"{data_dir}/{filename}", "w") as file:
            json.dump(data, file)

    return data
