import requests
import os
import json
from pathlib import Path 

# https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md
# https://en.wikipedia.org/wiki/List_of_NHL_seasons

REGULAR_SEASON = "02"
PLAYOFFS = "03"

'''
1353 for seasons with 32 teams (2022 - Present)
1271 for seasons with 31 teams (2017 - 2020)
1230 for seasons with 30 team
For playoff games, the 2nd digit of the specific number gives the round of the playoffs, the 3rd digit specifies the matchup, and the 4th digit specifies the game (out of 7).
'''
game_number_per_year = {
    "2017": "1271", # 2016-2017
    "2018": "1271",
    "2019": "1271",
    "2020": "1271",
    "2021": "1353",
    "2022": "1353",
    "2023": "1353" # 2023-2024
    }

def retrieve_game_data(game_id) -> dict:
    
    data_dir = Path(__file__).resolve().parent.as_posix() + "/raw_data" # path to the raw data directory relative to this file
    filename = f"{game_id}.json"

    if os.path.exists(f"{data_dir}/{filename}"):
        with open(f"{data_dir}/{filename}", 'r') as file:
            print("using cached data")
            return json.load(file)

    response = requests.get(f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play")

    if response.status_code == 200:
        data = response.json()
        
        with open(f"{data_dir}/{filename}", 'w') as file:
            json.dump(data, file)
        
        return data
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None
    