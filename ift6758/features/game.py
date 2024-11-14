from .utilities import *
from ift6758.data import get_data as gd


class Game(JsonToObject):

    games = {}
    attribute = [
        "id",
        "gameDate",
        "season",
        "homeTeam.abbrev",
        "homeTeam.score",
        "awayTeam.abbrev",
        "awayTeam.score",
        "awayTeam.id",
        "homeTeam.id",
    ]

    def __init__(self, play_by_play: dict, verbose: bool = False):
        self.setattr(play_by_play, Game.attribute, verbose=verbose)
        Game.games[play_by_play["id"]] = self
        if verbose:
            print(f"Game {self.get_id()} created")
            print("with value : ", self.to_dict())

    def __str__(self) -> str:
        return f"Game {self.get_id()} on {self.get_date()} between {self.get_home_data()} and {self.get_away_data()}"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def get_game(game_id: int, verbose: bool = False) -> Union["Game", None]:
        """get the game object from the game id

        Args:
            game_id (int): the game id

        Returns:
            (Game | None): the game object or None if the game id is not found
        """
        try:
            return Game.games[game_id]
        except KeyError:
            game_data = gd.retrieve_game_data(game_id, verbose=verbose)
            return Game(game_data, verbose=verbose)

    def get_id(self) -> int:
        """get game id

        Returns:
            int : game id
        """
        try:
            return self.id
        except AttributeError:
            print("Error: game id not found")
            print(self.to_dict())
            print(Game.games)

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
