from ift6758.data import get_data as gd
from .utilities import *
from .game import Game


class ShotsEvent(JsonToObject):

    attributes = [
        "eventId",
        "timeInPeriod",
        "details.xCoord",
        "details.yCoord",
        "details.eventOwnerTeamId",
        "periodDescriptor.number",
        "homeTeamDefendingSide",
    ]
    events_by_game: Dict[int, List["ShotsEvent"]] = {}

    def __init__(self, game: Game, event_json: Dict[str, Any]):
        self.setattr(event_json, ShotsEvent.attributes)
        self.stripAttribute("details_")
        id = game.get_id()
        try:
            ShotsEvent.events_by_game[id].append(self)
        except KeyError:
            ShotsEvent.events_by_game[id] = [self]

    @staticmethod
    def get_events_by_game(game_id: int) -> List["ShotsEvent"]:
        """get the events by game id

        Args:
            game_id (int): the game id

        Returns:
            List['ShotsEvent']: the list of events
        """
        return ShotsEvent.events_by_game[game_id]

    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return f"event_{self.get_event_id()}"

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

    def get_event_type(self) -> str:
        """get the event type

        Returns:
            str: the event type
        """
        return self.__class__.__name__


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


class ShotOnGoal(ShotsEvent):

    attributes = [
        "details.shootingPlayerId",
        "details.goalieInNetId",
        "details.shotType",
        "details.zoneCode",
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
        "details.goalieInNetId",
        "details.shotType",
        "details.zoneCode",
    ]

    def __init__(self, game: Game, event_json: Dict[str, Any], verbose: bool = False):
        super().__init__(game, event_json)
        self.setattr(event_json, Goal.attributes)
        if verbose:
            print(event_json)
        self.stripAttribute("details_", verbose=verbose)

    def __str__(self) -> str:
        return super().__str__()
