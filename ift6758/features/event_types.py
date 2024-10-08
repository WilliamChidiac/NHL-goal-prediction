class PenaltyShotEvent:
    def __init__(
        self,
        game_id,
        event_id,
        period,
        time,
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
        self.time = time
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
        time,
        shooting_player,
        goalie,
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
        self.time = time
        self.shooting_player = shooting_player
        self.shot_type = shot_type
        self.goalie = goalie
        self.owner_team = owner_team
        self.event_id = event_id
        self.zone_code = zone_code

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "period": self.period,
            "time": self.time,
            "shooting_player": self.shooting_player,
            "x_coord": self.x_coord,
            "y_coord": self.y_coord,
            "owner_team": self.owner_team,
            "goalie": self.goalie,
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
        time,
        scoring_player,
        x_coord,
        y_coord,
        owner_team,
        goalie,
        shot_type,
        zone_code,
    ):
        self.game_id = game_id
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.period = period
        self.time = time
        self.scoring_player = scoring_player
        self.owner_team = owner_team
        self.goalie = goalie
        self.shot_type = shot_type
        self.event_id = event_id
        self.zone_code = zone_code

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "period": self.period,
            "time": self.time,
            "scoring_player": self.scoring_player,
            "x_coord": self.x_coord,
            "y_coord": self.y_coord,
            "owner_team": self.owner_team,
            "goalie": self.goalie,
            "shot_type": self.shot_type,
            "zone_code": self.zone_code,
            "event_id": self.event_id,
        }
