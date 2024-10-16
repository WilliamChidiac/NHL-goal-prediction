import ift6758.data.get_data as get_data
from ift6758.features.utilities import JsonToObject
from typing import Dict, Any, List, Tuple, Iterable
import pandas as pd
from ift6758.features.game import Game
from ift6758.features.player import Player
from ift6758.features.event_types import ShotsEvent, Goal, ShotOnGoal


def extract_player_data(json_player_data:Dict[str, Any]) -> Dict[int, Player]:
    players_dict = {}
    for player in json_player_data:
        players_dict[player["playerId"]] = Player(player)
    return players_dict
        
def import_game_stats(game_id:int) -> Tuple[List[ShotsEvent], Dict[int, Player]]:
    game_data = get_data.retrieve_game_data(game_id, verbose=True)
    players_dict = extract_player_data(game_data["rosterSpots"])
    events = game_data["plays"]
    game : Game = Game.get_game(game_id)
    print("printing game :", game)
    for event in events:
        try:
            if event["typeDescKey"] == "goal":
                Goal(game, event)
            elif event["typeDescKey"] == "shot-on-goal":
                ShotOnGoal(game, event)
        except KeyError:
            continue
    return ShotsEvent.get_events_by_game(game_id), players_dict

def game_stats_to_table(game_id : int, df : List[Dict[str, Any]] = []) -> List[Dict[str, Any]]:
    event_list, players_dict = import_game_stats(game_id)
    game: Game = Game.get_game(game_id)
    game_dict = game.to_dict()
    for event in event_list:
        event_json = event.to_dict()
        event_json.update(game_dict)
        event_json['type'] = event.get_event_type()
        df.append(event_json)
    return df

def games_to_table(game_ids : Iterable) -> pd.DataFrame:
    df = []
    for game_id in game_ids:
        if len(str(game_id)) == 4:
            games = get_data.regular_season_game_id_generator(game_id)
            for game in games:
                print("game", game)
                df = game_stats_to_table(game, df)
        else:
            df = game_stats_to_table(game_id, df)
    return pd.DataFrame(df)
