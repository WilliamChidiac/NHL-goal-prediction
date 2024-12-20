from ift6758.data import get_data as gd
from .utilities import *
from .game import Game

class Event(JsonToObject):
    
    attributes = [
        "eventId",
        "timeInPeriod",
        "details.xCoord",
        "details.yCoord",
        "details.reason",
        "periodDescriptor.number",
        "typeDescKey"
    ]

    previous_event: Optional["Event"] = None

    def __init__(self, game: Game, event_json: Dict[str, Any], prev_event : bool = False):
        self.game = game
        self.setattr(event_json, Event.attributes)
        self.stripAttribute("details_")
        if prev_event:
            self.addPrefix("prev_")
            Event.previous_event = self
        else:
            for key,value in Event.previous_event.__dict__.items():
                self.__setattr__(key, value)
        
    def get_event_id(self) -> int:
        """get the event id

        Returns:
            int: the event id
        """
        return self.eventId

    def get_period_info(self) -> Tuple[str, int]:
        """get the time in period

        Returns:
            Tuple[str, int]: (time in period, period number)
        """
        return self.timeInPeriod, self.periodDescriptor_number

    def get_coordinates(self) -> Optional[Tuple[int, int]]:
        """get the coordinates of the event

        Returns:
            Tuple[int, int]: (x, y)
        """
        return (self.xCoord, self.yCoord)

    def get_reason(self) -> Optional[str]:
        """get the reason of the event

        Returns:
            Optional[str]: the reason
        """
        return self.reason

class ShotsEvent(Event):

    attributes = [
        "details.eventOwnerTeamId",
        "details.goalieInNetId",
        "details.shotType",
        "details.zoneCode",
    ]
    shots_by_game: Dict[int, List["ShotsEvent"]] = {}
    
    def __init__(self, game: Game, event_json: Dict[str, Any]):
        super().__init__(game, event_json)
        self.setattr(event_json, ShotsEvent.attributes)
        self.stripAttribute("details_")
        id = game.get_id()
        try:
            ShotsEvent.shots_by_game[id].append(self)
        except KeyError:
            ShotsEvent.shots_by_game[id] = [self]

    @staticmethod
    def get_shots_by_game(game_id: int) -> List["ShotsEvent"]:
        """get the events by game id

        Args:
            game_id (int): the game id

        Returns:
            List['ShotsEvent']: the list of events
        """
        return ShotsEvent.shots_by_game[game_id]
    
    
    def approximate_homeTeamSide(self, game : Game) -> str:
        home_team_id = game.get_home_data()[0]
        ower_team_id = self.get_owner_team_id()
        side, _ = self.get_coordinates()
        zone_code = self.get_zone_code()
        if side == None:
            return 'central'
        if home_team_id == ower_team_id:
            if zone_code == "O" and side > 0: 
                return 'left'
            elif zone_code == "D" and side < 0:
                return 'left'
        else:
            if  zone_code == "O" and side > 0:
                return 'right'
            elif zone_code == "D" and side < 0:
                return 'right'
        return 'central'

    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return f"event_{self.get_event_id()}"

 

    def get_owner_team_id(self) -> int:
        """get the owner team id

        Returns:
            int: the owner team id
        """
        return self.eventOwnerTeamId

    def get_event_type(self) -> str:
        """get the event type

        Returns:
            str: the event type
        """
        return self.typeDescKey

    def get_situation_code(self) -> str:
        """get the situation code

        Returns:
            str: the situation code
        """
        return self.situationCode
    
    def get_shot_type(self) -> str:
        """get the shot type

        Returns:
            str: the shot type
        """
        return self.shotType
    
    def get_zone_code(self) -> str:
        """get the zone code

        Returns:
            str: the zone code
        """
        return self.zoneCode
    
    def get_previous_event_type(self) -> Optional[str]:
        """get the previous event's type

        Returns:
            Optional['ShotsEvent']: the previous event
        """
        return self.prev_typeDescKey
    
    def get_previous_event_coords(self) -> Optional[Tuple[int, int]]:
        """get the previous event's coordinates

        Returns:
            Optional[Tuple[int, int]]: the previous event
        """
        return self.prev_xCoord, self.prev_yCoord
    
    def get_previous_event_time_info(self) -> Optional[Tuple[str, int]]:
        """get the previous event

        Returns:
            Optional[Tuple[str, int]]: the previous event           
        """
        return self.prev_timeInPeriod, self.prev_periodDescriptor_number

    def is_rebound(self) -> bool:
        """check if the event is a rebound

        Returns:
            bool: True if the event is a rebound
        """
        return self.typeDescKey == "rebound"

class ShotOnGoal(ShotsEvent):

    attributes = [
        "details.shootingPlayerId",
        "situationCode"
    ]

    def __init__(self, game: Game, event_json: Dict[str, Any], verbose: bool = False):
        try:
            super().__init__(game, event_json)
            self.setattr(event_json, ShotOnGoal.attributes)
            self.stripAttribute("details_", verbose=verbose)
        except KeyError as e:
            print(f"Error in ShotOnGoalEvent: {e}")

    def __str__(self) -> str:
        return super().__str__()


class Goal(ShotsEvent):

    attributes = [
        "details.scoringPlayerId",
        "situationCode"
    ]

    def __init__(self, game: Game, event_json: Dict[str, Any], verbose: bool = False):
        super().__init__(game, event_json)
        self.setattr(event_json, Goal.attributes)
        if verbose:
            print(event_json)
        self.stripAttribute("details_", verbose=verbose)

    def __str__(self) -> str:
        return super().__str__()
