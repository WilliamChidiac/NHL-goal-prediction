class Player:
    def __init__(self, player_id, team_id, first_name, last_name, position_code):
        self.player_id = player_id
        self.team_id = team_id
        self.first_name = first_name
        self.last_name = last_name
        self.position_code = position_code

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "team_id": self.team_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "position_code": self.position_code,
        }
