import ift6758.data.get_data as get_data
from ift6758.features.utilities import JsonToObject
from typing import Dict, Any, List, Tuple, Iterable
import pandas as pd
from ift6758.features.game import Game
from ift6758.features.player import Player
from ift6758.features.event_types import ShotsEvent, Goal, ShotOnGoal, Event

def convert_to_time(time:str) -> int:
    """convert the time in the period to seconds

    Args:
        time (str): the time in the period

    Returns:
        int: the time in seconds
    """
    return int(time.split(":")[0]) * 60 + int(time.split(":")[1])

def sort_event_by_time(events:List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """sort the events by time

    Args:
        events (List[Dict[str, Any]]): the list of events

    Returns:
        List[Dict[str, Any]]: the list of events sorted by time
    """
    return sorted(events, key=lambda x: (x['periodDescriptor']['number'], convert_to_time(x["timeInPeriod"])))

def extract_player_data(json_player_data:Dict[str, Any]) -> Dict[int, Player]:
    """extract player data from play by play json

    Args:
        json_player_data (Dict[str, Any]): the list of players directly from the json

    Returns:
        Dict[int, Player]: the dictionary of players
    """
    players_dict = {}
    for player in json_player_data:
        players_dict[player["playerId"]] = Player(player)
    return players_dict
        
def import_game_stats(game_id:int) -> Tuple[List[ShotsEvent], Dict[int, Player]]:
    """import the game stats from the json

    Args:
        game_id (int): the game id

    Returns:
        Tuple[List[ShotsEvent], Dict[int, Player]]: the list of events and the dictionary of players
    """
    game_data = get_data.retrieve_game_data(game_id, verbose=True)
    players_dict = extract_player_data(game_data["rosterSpots"])
    events = game_data["plays"]
    events = sort_event_by_time(events)
    game : Game = Game.get_game(game_id)
    print("printing game :", game)
    for event in events:
        try:
            if event["typeDescKey"] == "goal":
                Goal(game, event)
            elif event["typeDescKey"] == "shot-on-goal":
                ShotOnGoal(game, event)
            else:
                Event(game, event, prev_event=True)
        except KeyError:
            continue
    return ShotsEvent.get_shots_by_game(game_id), players_dict

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
