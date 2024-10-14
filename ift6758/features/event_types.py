from typing import List, Dict, Tuple, Union, Any

def parse_json(json : Dict[str, Any], keys : List[str]) -> Dict[str, Any]:
    """get the values of the keys in the json

    Args:
        json (Dict[str, Any]): the original json
        keys (List[str]): the keys to get the values from the json (if the key is nested, use '.' to separate the keys)

    Returns:
        Dict[str, Any]: the values of the keys in the json
    """
    res = {}
    for key in keys:
        path = key.split(".")
        val = json
        for p in path:
            try:
                val = val[p]
            except KeyError:
                val = None
                break
        res["_".join(path)] = val
    return res

class JsonToObject:
    def setattr(self, json : Dict[str, Any], keys : List[str]):
        """set the attributes of the object from the json

        Args:
            json (Dict[str, Any]): the json to get the values from
            keys (List[str]): the keys to get the values from the json (if the key is nested, use '.' to separate the keys)
        """
        for key, value in parse_json(json, keys).items():
            self.__setattr__(key, value)
            
    def renameAttribute(self, old_attr, new_attr):
        """rename an attribute of the object

        Args:
            old_attr (str): the old attribute name
            new_attr (str): the new attribute name
        """
        self.__setattr__(new_attr, self.__getattribute__(old_attr))
        delattr(self, old_attr)
        
    def stripAttribute(self, name:str):
        """strip a part of the attribute name

        Args:
            name (str): the part to strip
        """
        for key in self.__dict__:
            if name in key:
                self.renameAttribute(key, key.strip(name))
    
    def to_dict(self) -> Dict[str, Any]:
        """convert the object to a dictionary

        Returns:
            Dict[str, Any]: the dictionary representation of the object
        """
        return {key: self.__getattribute__(key) for key in self.__dict__}

class Game(JsonToObject):
    
    games = {}
    attribute = ['id', 'gameDate', 'homeTeam.abbrev', 'homeTeam.score', 'awayTeam.abbrev', 'awayTeam.score', 'awayTeam.id', 'homeTeam.id']

    def __init__(self, play_by_play: dict):
        game = parse_json(play_by_play, Game.attribute)
        if game['id'] in Game.games:
            self = Game.games[game['id']]
        self.setattr(game, Game.attribute)
        Game.games[game['id']] = self
    
    def __str__(self) -> str:
        return f"Game {self.get_id()} on {self.get_date()} between {self.get_home_data()} and {self.get_away_data()}"
    
    def get_id(self) -> int:
        """get game id

        Returns:
            int : game id 
        """
        return self.id

    def get_date(self) -> str:
        """get game date

        Returns:
            str : game date
        """
        return self.gameDate
    
    def get_home_data(self) -> Tuple[int, str, int]:
        """get the home team data

        Returns:
            Tuple[int, str, int]: (id, abbrev, score)
        """
        return (self.homeTeam_id, self.homeTeam_abbrev, self.homeTeam_score)
    
    def get_away_data(self) -> Tuple[int, str, int]:
        """get the away team data

        Returns:
            Tuple[int, str, int]: (id, abbrev, score)
        """
        return (self.awayTeam_id, self.awayTeam_abbrev, self.awayTeam_score)
        
        
class ShotsEvent(JsonToObject):
    
    attributes = ['eventId', 'timeInPeriod', 'details.xCoord', 'details.yCoord', 'details.eventOwnerTeamId']
    
    def __init__(self, game : Game, event_json : Dict[str, Any]):
        self.game = game
        self.setattr(event_json, ShotsEvent.attributes)
        self.stripAttribute("details_")

    def __str__(self) -> str:
        return f"event id : {self.get_event_id()}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def get_game(self) -> Game:
        """get the game object

        Returns:
            Game: the game object
        """
        return self.game
    
    def get_event_id(self) -> int:
        """get the event id

        Returns:
            int: the event id
        """
        return self.eventId
    
    def get_time_in_period(self) -> str:
        """get the time in period

        Returns:
            str: the time in period
        """
        return self.timeInPeriod
    
    def get_coordinates(self) -> Tuple[int, int]:
        """get the coordinates of the event

        Returns:
            Tuple[int, int]: (x, y)
        """
        return (self.xCoord, self.yCoord)
    
    def get_owner_team_id(self) -> int:
        """get the owner team id

        Returns:
            int: the owner team id
        """
        return self.eventOwnerTeamId
    
    def to_dict(self) -> Dict[str, Any]:
        """convert the object to a dictionary

        Returns:
            Dict[str, Any]: the dictionary representation of the object
        """
        return self.__dict__

class PenaltyShotEvent(ShotsEvent):

    attributes = ["details"]
    
    def __init__(
        self,
        game_id,
        event_id,
        period,
        time,
        owner_team,
        x_coord,
        y_coord,
        
        defending_player,
        attacking_player,
    ):
        self.game_id = game_id
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.period = period
        self.time = time
        self.defending_player = defending_player  # commited the fault
        self.attacking_player = attacking_player  # who got the penalty shot
        self.owner_team = owner_team
        self.event_id = event_id
class ShotOnGoalEvent (ShotsEvent):
    
    attributes = ['details.shootingPlayerId', 'details.goalieInNetId', 'details.shotType', 'details.zoneCode']

    def __init__(self, game : Game, event_json : Dict[str, Any]):
        try:
            super().__init__(game, event_json)
            self.setattr(event_json, ShotOnGoalEvent.attributes)
            self.stripAttribute("details_")
        except KeyError as e:
            print(f"Error in ShotOnGoalEvent: {e}")
            
    def __str__(self) -> str:
        return super().__str__()

class GoalEvent(ShotsEvent):
    
    attributes = ['details.scoringPlayerId', 'details.goalieInNetId', 'details.shotType', 'details.zoneCode']

    def __init__(self, game : Game, event_json : Dict[str, Any]):
        super().__init__(game, event_json)
        self.setattr(event_json, GoalEvent.attributes)
        self.stripAttribute("details_")
        
    def __str__(self) -> str:
        return super().__str__()