import math
from .preprocess import import_game_stats
from ift6758.data.get_data import regular_season_game_id_generator, retrieve_game_data
from .trigonometry import determine_enemy_net_coords, compute_angle_from_net, compute_distance_from_net
from .event_types import ShotsEvent
from .game import Game
from typing import List, Dict, Any, Tuple , Optional
import pandas as pd


class Row:
    """ class to represent a row of the dataframe for the advanced features of the shots

    Raises:
        ValueError: if the home team side is not determined before computing the distance from the net or other related metrics
    """

    LEFT_NET = (-89, 0)
    RIGHT_NET = (89, 0)
    
    def __init__(self, shot : ShotsEvent, game : Game):
        self.game_id = game.get_id()
        self.home_team_id = game.get_home_data()[0]
        self.away_team_id = game.get_away_data()[0]
        self.event_id = shot.get_event_id()
        self.owner_team_id = shot.get_owner_team_id()
        self.event_type = shot.get_event_type()
        self.shot_type = shot.get_shot_type()
        self.time_period, self.period_number = shot.get_period_info()
        self.time_period = int(self.time_period.split(":")[0]) * 60 + int(self.time_period.split(":")[1])
        self.zone_code = shot.get_zone_code()
        self.x_coord, self.y_coord = shot.get_coordinates()
        self.flagged = True if self.x_coord is None or self.y_coord is None else False
        self.last_event_type = shot.get_previous_event_type()
        self.last_event_xCoord, self.last_event_yCoord = shot.get_previous_event_coords()
        prev_time, _prev_period = shot.get_previous_event_time_info()
        prev_time = int(prev_time.split(":")[0]) * 60 + int(prev_time.split(":")[1])
        self.time_passed_since_last_event = self.time_period - prev_time
        self.distance_from_last_event = None
        if not (self.last_event_xCoord is None or self.last_event_yCoord is None):
            self.distance_from_last_event = self.compute_distance_from_last_event()
        self.rebound = False
        if self.last_event_type == 'shot-on-goal':
            self.rebound = True
        self.distance_from_net = None
        self.angle_from_net = None
        self.speed = None
        self.change_in_shot_angle = None
        self.set_home_team_side(shot.approximate_homeTeamSide(game))
            
    def set_home_team_side(self, side : str):
        """set the home team side

        Args:
            side (str): the side of the home team
        """
        if side not in ['left', 'right', 'central']:
            raise ValueError(f"The side must be either left, right or central. Got {side}")
        if side == 'central':
            self.home_team_side = side
            return
        self.home_team_side = side
        self.compute_distance_from_net()
        self.compute_angle_from_net()
        self.compute_angle_from_last_event()
        self.compute_change_in_shot_angle()
        self.compute_speed()
        
    def compute_distance_from_last_event(self) -> float:
        """compute the distance from the last event

        Returns:
            float: the distance from the last event
        """
        if self.flagged:
            return None
        x = self.x_coord - self.last_event_xCoord
        y = self.y_coord - self.last_event_yCoord
        distance = (x**2 + y**2)**0.5
        self.distance_from_last_event = distance
        return distance
    
    def compute_angle_from_last_event(self) -> Optional[float]:
        """compute the angle from the last event

        Raises:
            ValueError: if the home team side is not determined before computing the distance from the net or other related metrics

        Returns:
            Optional[float]: the angle from the last event
        """
        if self.flagged or not self.rebound:
            return None
        net_x, net_y = Row.RIGHT_NET
        if self.home_team_side == 'central':
            raise ValueError("The home team side has not been determined")
        elif self.home_team_side == 'left':
            net_x, net_y = Row.LEFT_NET
        net_prev = (self.last_event_xCoord - net_x, self.last_event_yCoord - net_y)
        net_current = (self.x_coord - net_x, self.y_coord - net_y)
        dot_product = net_prev[0] * net_current[0] + net_prev[1] * net_current[1]
        magnitude_prev = (net_prev[0]**2 + net_prev[1]**2)**0.5
        magnitude_current = (net_current[0]**2 + net_current[1]**2)**0.5
        cos_angle = dot_product / (magnitude_prev * magnitude_current)
        angle_radian = math.acos(cos_angle)
        angle = math.degrees(angle_radian)
        self.change_in_shot_angle = angle
        return angle
    
    def compute_distance_from_net(self) -> float:
        """compute the distance from the net

        Raises:
            ValueError: if the home team side is not determined before computing the distance from the net or other related metrics

        Returns:
            float: the distance from the net
        """
        if self.flagged:
            return None
        if self.home_team_side == 'central':
            raise ValueError("The home team side has not been determined")
        net_x, net_y = Row.RIGHT_NET if self.home_team_side == 'left' else Row.LEFT_NET
        distance = ((self.x_coord - net_x)**2 + (self.y_coord - net_y)**2)**0.5
        self.distance_from_net = distance
        return distance

    def compute_angle_from_net(self) -> float:
        """compute the angle from the net

        Raises:
            ValueError: if the home team side is not determined before computing the distance from the net or other related metrics

        Returns:
            float: the angle from the net
        """
        if self.flagged:
            return None
        if self.home_team_side == 'central':
            raise ValueError("The home team side has not been determined")
        net_x, net_y = Row.RIGHT_NET if self.home_team_side == 'left' else Row.LEFT_NET
        dx = abs(net_x - self.x_coord)
        dy = abs(net_y - self.y_coord)
        angle_radian = math.atan2(dy, dx)
        angle = math.degrees(angle_radian)
        self.angle_from_net = angle
        return angle
    
    def compute_change_in_shot_angle(self) -> float:
        """compute the change in shot angle

        Returns:
            float: the change in shot angle
        """
        if self.flagged or not self.rebound:
            return None
        net_x, net_y = Row.RIGHT_NET if self.home_team_side == 'left' else Row.LEFT_NET
        net_prev = (self.last_event_xCoord - net_x, self.last_event_yCoord - net_y)
        net_current = (self.x_coord - net_x, self.y_coord - net_y)
        dot_product = net_prev[0] * net_current[0] + net_prev[1] * net_current[1]
        magnitude_prev = (net_prev[0]**2 + net_prev[1]**2)**0.5
        magnitude_current = (net_current[0]**2 + net_current[1]**2)**0.5
        cos_angle = max(min(dot_product / (magnitude_prev * magnitude_current), 1), -1)
        angle_radian = math.acos(cos_angle)
        self.change_in_shot_angle = math.degrees(angle_radian)
        return self.change_in_shot_angle
        
    
    def compute_speed(self) -> float:
        """compute the speed of the shot

        Returns:
            float: the speed of the shot
        """
        if self.flagged:
            return None
        if self.time_passed_since_last_event == 0 or self.distance_from_last_event == None:
            return None
        speed = self.distance_from_last_event / self.time_passed_since_last_event
        self.speed = speed
        return speed
        
        
class PreprocessII:
    
    games_df : pd.DataFrame = pd.DataFrame()
    
    def __init__(self, game_id : int):
        not_processed : Dict[int, List[ShotsEvent]] = {}
        period_homeSide : Dict[int, str] = {}
        event_list, players_info = import_game_stats(game_id)
        game = Game.get_game(game_id)
        self.game_data = []
        for event in event_list:
            row : Row = Row(event, game)
            if row.home_team_side == 'central':
                if period_homeSide.get(row.period_number) is None:
                    try:
                        not_processed[row.period_number].append(row)
                    except KeyError:
                        not_processed[row.period_number] = [row]
                else:
                    row.set_home_team_side(period_homeSide[row.period_number])
            else:
                period_homeSide[row.period_number] = row.home_team_side
            self.game_data.append(row)
        for period, row_list in not_processed.items():
            home_side = period_homeSide.get(period, "central")
            if home_side == "central":
                home_side = "left" if period_homeSide.get(period-1) == "right" else "right"
            for row in row_list:
                row.set_home_team_side(home_side)
        
    def to_dataframe(self) -> pd.DataFrame:
        """convert the data to a dataframe

        Returns:
            pd.DataFrame: the dataframe
        """
        game_df = []
        for row in self.game_data:
            row_dict : Dict[str, Any] = row.__dict__
            game_df.append(row_dict)
        game_df = pd.DataFrame(game_df)
        PreprocessII.games_df = pd.concat([PreprocessII.games_df, game_df], ignore_index=True)
        return game_df
    
    @staticmethod
    def clear_games_df():
        """clear the games dataframe
        """
        PreprocessII.games_df = pd.DataFrame()
    
    @staticmethod
    def get_games_df(seasons : List[int], reset_df : bool = True) -> pd.DataFrame:
        """get the games dataframe

        Args:
            seasons (List[int]): the list of seasons

        Returns:
            pd.DataFrame: the games dataframe
        """
        if reset_df:
            PreprocessII.clear_games_df()
        for season in seasons:
            games = regular_season_game_id_generator(season)
            for id in games:
                data = PreprocessII(id)
                data.to_dataframe()
        return PreprocessII.games_df