class PenaltyShotEvent:
    def __init__(
        self,
        game_id,
        event_id,
        period,
        time_remaining,
        time_in_period,
        defending_player,
        attacking_player,
        x_coord,
        y_coord,
        owner_team,
    ):
        self.game_id = game_id
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.period = period
        self.time_remaining = time_remaining
        self.time_in_period = time_in_period
        self.defending_player = defending_player  # commited the fault
        self.attacking_player = attacking_player  # who got the penalty shot
        self.owner_team = owner_team
        self.event_id = event_id


class ShotOnGoalEvent:
    def __init__(
        self,
        game_id,
        event_id,
        period,
        time_remaining,
        time_in_period,
        shooting_player_id,
        shooting_player_name,
        goalie_id,
        goalie_name,
        x_coord,
        y_coord,
        shot_type,
        owner_team,
        zone_code,
    ):
        self.game_id = game_id
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.period = period
        self.time_remaining = time_remaining
        self.time_in_period = time_in_period
        self.shooting_player_id = shooting_player_id
        self.shooting_player_name = shooting_player_name
        self.goalie_id = goalie_id
        self.goalie_name = goalie_name
        self.shot_type = shot_type
        self.owner_team = owner_team
        self.event_id = event_id
        self.zone_code = zone_code

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "period": self.period,
            "time_remaining": self.time_remaining,
            "time_in_period": self.time_in_period,
            "shooting_player_id": self.shooting_player_id,
            "shooting_player_name": self.shooting_player_name,
            "goalie_id": self.goalie_id,
            "goalie_name": self.goalie_name,
            "x_coord": self.x_coord,
            "y_coord": self.y_coord,
            "owner_team": self.owner_team,
            "shot_type": self.shot_type,
            "zone_code": self.zone_code,
            "event_id": self.event_id,
        }


class GoalEvent:
    def __init__(
        self,
        game_id,
        event_id,
        period,
        time_remaining,
        time_in_period,
        shooting_player_id,
        shooting_player_name,
        goalie_id,
        goalie_name,
        x_coord,
        y_coord,
        owner_team,
        shot_type,
        zone_code,
    ):
        self.game_id = game_id
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.period = period
        self.time_remaining = time_remaining
        self.time_in_period = time_in_period
        self.shooting_player_id = shooting_player_id
        self.shooting_player_name = shooting_player_name
        self.goalie_id = goalie_id
        self.goalie_name = goalie_name
        self.owner_team = owner_team
        self.shot_type = shot_type
        self.event_id = event_id
        self.zone_code = zone_code

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "period": self.period,
            "time_remaining": self.time_remaining,
            "time_in_period": self.time_in_period,
            "shooting_player_id": self.shooting_player_id,
            "shooting_player_name": self.shooting_player_name,
            "goalie_id": self.goalie_id,
            "goalie_name": self.goalie_name,
            "x_coord": self.x_coord,
            "y_coord": self.y_coord,
            "owner_team": self.owner_team,
            "shot_type": self.shot_type,
            "zone_code": self.zone_code,
            "event_id": self.event_id,
        }
