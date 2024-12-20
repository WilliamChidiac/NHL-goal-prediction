from .preprocess_II import PreprocessII
import pandas as pd
from typing import List, Dict, Any, Tuple, Union, Optional, Iterable


class FeatureEngineeringII:
    def __init__(self, data : Union[pd.DataFrame, Iterable[int]]):
        self.df = None
        if isinstance(data, pd.DataFrame):
            self.df = data.copy(deep=True)
        else:
            self.df = PreprocessII.get_games_df(data)
        self.irrelevant_columns = ["away_team_id", "flagged", "season"]
        
    def remove_irrelevant_columns(self):
        """remove irrelevant columns from the dataframe
        """
        self.df.drop(columns=self.irrelevant_columns, inplace=True)
        self.irrelevant_columns = []
        
    def add_labels(self):
        """add labels to the dataframe
        """
        self.df['labels'] = self.df['event_type'].apply(lambda x: 1 if x == "goal" else 0)
        self.df.drop(columns=["event_type"], inplace=True)
        
    def numerise_column(self, column : str, key_val : Dict[Any, Any], one_hot : bool = False, prefix : str = None):
        """numerise a column of the dataframe with the option to one hot encode it

        Args:
            column (str): the column to numerise
            key_val (Dict[Any, Any]): the mapping of the values to the one hot encoded values
            one_hot_encode (bool): whether to one hot encode the column
            prefix (str): the prefix of the one hot encoded columns
        """
        if one_hot:
            key_val = { i : i for i in key_val.keys() }
        self.df[column] = self.df[column].apply(lambda x: key_val.get(x, key_val['other']))
        if one_hot:
            self.df = pd.get_dummies(self.df, columns=[column], prefix=prefix)
            
    
    def numerise_shotType(self, one_hot_encode=False):
        """numerise the shotType column
        
        NOTE: the shot type are ordered by there occurence in the data
        
        Args:
            one_hot_encode (bool, optional): option to one-hot-encode . Defaults to False.
        """
        types = {
            'wrist': 0,
            'slap': 1,
            'snap': 2,
            'backhand': 3,
            'tip-in': 4,
            'deflected': 5,
            'wrap-around': 6,
            'other': 0
        }
        self.numerise_column("shot_type", types, one_hot_encode, "shot_type")
        
    def numerise_zoneCode(self, one_hot_encode=False):
        """numerise the zoneCode column
        
        NOTE: the ratio of shot per zone is ~97% in the offensive zone, ~3% in the neutral zone and less than 1% in the defensive zone

        Args:
            one_hot_encode (bool, optional): option to one-hot-encode . Defaults to False.
        
        """
        zones = {
            "O": 2,
            "N": 1,
            "D": 0,
            "other": 2
        }
        self.numerise_column("zone_code", zones, one_hot_encode, "zone_code")
        
    def numerise_previous_event(self, one_hot_encode=False):
        """numerise the previous event column

        Args:
            one_hot_encode (bool, optional): option to one-hot encode the feature. Defaults to False.
        """
        event_types = {
            'faceoff': 0,
            'hit': 1,
            'blocked-shot': 2,
            'missed-shot': 3,
            'stoppage': 4,
            'takeaway': 5,
            'giveaway': 6,
            'penalty': 7,
            'other': 8
        }
        column = 'last_event_type'
        self.numerise_column(column, event_types, one_hot_encode, column)
        
    def align_coord(self):
        """align the coordinates of the events to the owner team
        """
        self.df['current_x'] = self.df.apply(lambda x: x['x_coord'] if ((x['owner_team_id'] == x['home_team_id'] and x['home_team_side'] == "left") or (x['owner_team_id'] != x['home_team_id'] and x['home_team_side'] == "right")) else -x['x_coord'], axis=1)
        self.df['current_y'] = self.df.apply(lambda x: x['y_coord'] if ((x['owner_team_id'] == x['home_team_id'] and x['home_team_side'] == "left") or (x['owner_team_id'] != x['home_team_id'] and x['home_team_side'] == "right")) else -x['y_coord'], axis=1)
        self.df['prev_x'] = self.df.apply(lambda x: x['last_event_xCoord'] if ((x['owner_team_id'] == x['home_team_id'] and x['home_team_side'] == "left") or (x['owner_team_id'] != x['home_team_id'] and x['home_team_side'] == "right")) else -x['last_event_xCoord'], axis=1)
        self.df['prev_y'] = self.df.apply(lambda x: x['last_event_yCoord'] if ((x['owner_team_id'] == x['home_team_id'] and x['home_team_side'] == "left") or (x['owner_team_id'] != x['home_team_id'] and x['home_team_side'] == "right")) else -x['last_event_yCoord'], axis=1)
        self.irrelevant_columns += ["x_coord", "y_coord", "last_event_xCoord", "last_event_yCoord","home_team_id", "owner_team_id"]

    def split_train_test(self, test_frac=0.2):
        """split the dataframe into train and test set by keeping the ratio of goals in the two sets
        
        Args:
            test_size (float, optional): the size of the test set. Defaults to 0.2.
        """
        train_size = 1 - test_frac
        df_goal : pd.DataFrame = self.df[self.df['labels'] == 1]
        df_no_goal : pd.DataFrame = self.df[self.df['labels'] == 0]
        train_goal = df_goal.sample(frac=train_size, random_state=200)
        test_goal = df_goal.drop(train_goal.index)
        train_no_goal = df_no_goal.sample(frac=train_size, random_state=200)
        test_no_goal = df_no_goal.drop(train_no_goal.index)
        
        self.train_df = pd.concat([train_goal, train_no_goal])
        self.test_df = pd.concat([test_goal, test_no_goal])
        
        return self.train_df, self.test_df
    
    def replace_na(self):
        """replace the missing values in the dataframe with the mean of the column for numerical columns and the max occurence for categorical columns
        """
        for column in self.df.columns:
            if self.df[column].dtype == 'float64':
                self.df[column].fillna(self.df[column].mean(), inplace=True)
            else:
                try:
                    self.df[column].fillna(self.df[column].value_counts().idxmax(), inplace=True)
                except ValueError as e:
                    print(f"Error on column : {column}")
                    print(f" row : {self.df[column]}")
                    raise e
              
    def keep_columns(self, columns: List[str]):
        """keep only the specified columns in the dataframe

        Args:
            columns (List[str]): the list of columns to keep
        """
        self.df = self.df[columns]

    
    def extract_empty_net_feature(self, df):
        """
        Extracts the empty net feature from the situationCode and eventOwnerTeamId.

        Args:
            df (pd.DataFrame): DataFrame containing the game data.

        Returns:
            pd.DataFrame: DataFrame with the empty net feature added.
        """
        def is_empty_net(row):
            situation_code = str(row['situation_code']).zfill(4)
            event_owner_team_id = row['owner_team_id']
            
            # Parse the situation code
            away_goalie_on_ice = situation_code[0] == '1'
            away_skaters = int(situation_code[1])
            home_skaters = int(situation_code[2])
            home_goalie_on_ice = situation_code[3] == '1'
            
            # Determine if the goal was scored into an empty net
            if event_owner_team_id == row['away_team_id']:
                # Away team scored
                return 1 if not home_goalie_on_ice else 0
            elif event_owner_team_id == row['home_team_id']:
                # Home team scored
                return 1 if not away_goalie_on_ice else 0
            else:
                return 0

        # Apply the function to each row
        df['empty_net'] = df.apply(is_empty_net, axis=1)
        
        # Fill NaNs with 0
        df['empty_net'].fillna(0, inplace=True)
        return df

    def clean_df(self, remove_irrelevant=False, columns=None):    
        """clean the dataframe by removing irrelevant columns, adding labels, numerising the columns and aligning the coordinates
        """
        self.replace_na()
        self.add_labels()
        self.numerise_zoneCode(one_hot_encode=False)
        self.numerise_shotType(one_hot_encode=True)
        # self.numerise_previous_event(one_hot_encode=True)
        self.align_coord()
        self.extract_empty_net_feature(self.df)
        self.keep_columns(columns)
        if remove_irrelevant:
            self.remove_irrelevant_columns()
