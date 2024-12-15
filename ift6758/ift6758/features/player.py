from .utilities import *

class Player(JsonToObject):

    attributes = ['playerId', 'teamId', 'firstName.default', 'lastName.default', 'positionCode']
    
    def __init__(self, rosterSpots : Dict[str, Any]):
        self.setattr(rosterSpots, Player.attributes)
        self.stripAttribute('_default')
        
    def __str__(self) -> str:
        return f"{self.get_first_name()} {self.get_last_name()} ({self.get_position_code()})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def get_player_id(self) -> int:
        """get the player id

        Returns:
            int: player id
        """
        return self.playerId
    
    def get_team_id(self) -> int:
        """get the team id

        Returns:
            int: team id
        """
        return self.teamId
    
    def get_first_name(self) -> str:
        """get the first name

        Returns:
            str: first name
        """
        return self.firstName
    
    def get_last_name(self) -> str:
        """get the last name

        Returns:
            str: last name
        """
        return self.lastName
    
    def get_position_code(self) -> str:
        """get the position code

        Returns:
            str: position code
        """
        return self.positionCode